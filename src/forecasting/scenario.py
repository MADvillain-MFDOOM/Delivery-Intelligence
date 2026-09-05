"""Deterministic, evidence-gated delivery forecasting.

The engine intentionally produces scenarios rather than claiming a calibrated
probability. Historical completed points are assigned to the sprint window in
which resolution occurred, not the sprint label currently held by an issue.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from statistics import median
from typing import Any, Iterable

from src.analysis.evidence_quality import evaluate_forecast_readiness


def _percentile(values: Iterable[float], percentile: float) -> float:
    """Return a linearly interpolated percentile without external libraries."""

    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("At least one value is required")
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    position = (len(ordered) - 1) * percentile / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _closed_sprints(sprints: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    closed = [
        sprint
        for sprint in sprints
        if sprint.get("state") == "closed" and sprint.get("start_date") and sprint.get("end_date")
    ]
    closed.sort(key=lambda sprint: sprint["end_date"])
    return closed[-limit:]


def _sprint_days(sprints: list[dict[str, Any]]) -> int:
    durations = [(sprint["end_date"] - sprint["start_date"]).days + 1 for sprint in sprints]
    return max(1, round(median(durations))) if durations else 14


def _capacity_by_sprint(capacity: list[dict[str, Any]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for row in capacity:
        sprint = row.get("sprint")
        points = row.get("capacity_points")
        if sprint and points is not None:
            totals[sprint] = totals.get(sprint, 0.0) + float(points)
    return totals


def _observation_date(dataset: dict[str, list[dict[str, Any]]]) -> date:
    candidates = [
        value
        for issue in dataset.get("issues", [])
        for value in (issue.get("updated_date"), issue.get("resolution_date"))
        if value is not None
    ]
    candidates.extend(
        sprint["end_date"]
        for sprint in dataset.get("sprints", [])
        if sprint.get("end_date") is not None
    )
    if not candidates:
        raise ValueError("A forecast requires at least one dated issue or sprint")
    return max(candidates)


def build_delivery_forecast(
    dataset: dict[str, list[dict[str, Any]]], rules: dict[str, Any]
) -> dict[str, Any]:
    """Build auditable delivery scenarios from forecast-ready evidence.

    A scenario with zero historical throughput has no projected completion
    date. This preserves the risk signal rather than dividing by zero or
    silently substituting a favourable rate.
    """

    config = rules.get("forecasting", {}) or {}
    history_limit = int(config.get("history_sprints", 8))
    minimum_history = int(config.get("minimum_history_observations", 3))
    percentiles = config.get("scenario_percentiles", {}) or {
        "conservative": 25,
        "expected": 50,
        "optimistic": 75,
    }
    completed_statuses = set(rules.get("delivery", {}).get("completed_statuses", []))
    estimated_types = set(rules.get("delivery", {}).get("estimated_issue_types", []))
    readiness = evaluate_forecast_readiness(dataset.get("issues", []), rules)
    ready_keys = set(readiness["forecast_ready_item_keys"])
    issues = [
        issue
        for issue in dataset.get("issues", [])
        if issue.get("issue_key") in ready_keys and issue.get("issue_type") in estimated_types
    ]
    closed_sprints = _closed_sprints(dataset.get("sprints", []), history_limit)
    capacity_by_sprint = _capacity_by_sprint(dataset.get("capacity", []))

    observations: list[dict[str, Any]] = []
    for sprint in closed_sprints:
        completed = [
            issue
            for issue in issues
            if issue.get("status") in completed_statuses
            and issue.get("resolution_date")
            and sprint["start_date"] <= issue["resolution_date"] <= sprint["end_date"]
        ]
        completed_points = sum(float(issue.get("story_points") or 0) for issue in completed)
        available_capacity = capacity_by_sprint.get(sprint["sprint"])
        observations.append(
            {
                "sprint": sprint["sprint"],
                "start_date": sprint["start_date"].isoformat(),
                "end_date": sprint["end_date"].isoformat(),
                "completed_item_keys": [issue["issue_key"] for issue in completed],
                "completed_points": completed_points,
                "capacity_points": available_capacity,
                "capacity_realisation": (
                    round(completed_points / available_capacity, 4) if available_capacity else None
                ),
            }
        )

    remaining = [issue for issue in issues if issue.get("status") not in completed_statuses]
    remaining_points = sum(float(issue.get("story_points") or 0) for issue in remaining)
    throughput = [observation["completed_points"] for observation in observations]
    sprint_days = _sprint_days(closed_sprints)
    as_of = _observation_date(dataset)

    scenarios: dict[str, dict[str, Any]] = {}
    if throughput:
        for name, percentile in percentiles.items():
            rate = _percentile(throughput, float(percentile))
            cycles = math.ceil(remaining_points / rate) if rate > 0 and remaining_points > 0 else (0 if not remaining_points else None)
            scenarios[name] = {
                "historical_percentile": float(percentile),
                "points_per_sprint": round(rate, 2),
                "sprints_to_complete": cycles,
                "projected_completion_date": (
                    (as_of + timedelta(days=cycles * sprint_days)).isoformat() if cycles is not None else None
                ),
            }

    history_status = "sufficient" if len(observations) >= minimum_history else "insufficient_history"
    caveats = []
    if history_status != "sufficient":
        caveats.append(
            f"Only {len(observations)} closed sprint observations are available; at least {minimum_history} are required."
        )
    if any(value == 0 for value in throughput):
        caveats.append("At least one observed sprint has zero forecast-ready completed points.")
    if readiness["records_needing_correction"]:
        caveats.append(
            f"{readiness['records_needing_correction']} delivery records are excluded pending evidence correction."
        )

    return {
        "schema_version": "DeliveryForecast.v1",
        "as_of_date": as_of.isoformat(),
        "status": history_status,
        "scope": {
            "remaining_item_keys": [issue["issue_key"] for issue in remaining],
            "remaining_items": len(remaining),
            "remaining_points": remaining_points,
            "excluded_or_invalid_items": readiness["records_needing_correction"] + len(readiness["excluded_items"]),
        },
        "history": {
            "requested_sprints": history_limit,
            "minimum_required_observations": minimum_history,
            "observations": observations,
        },
        "scenarios": scenarios,
        "assumptions": {
            "method": "historical_completed_points_percentiles",
            "completion_assignment": "resolution_date_within_sprint_window",
            "sprint_duration_days": sprint_days,
            "estimation_unit": rules.get("analysis", {}).get("estimation_unit", "units"),
            "scope_change": "none_assumed",
        },
        "caveats": caveats,
        "evidence_quality": readiness,
    }
