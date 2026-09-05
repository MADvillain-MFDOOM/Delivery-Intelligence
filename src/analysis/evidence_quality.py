"""Evidence-quality checks and forecast-readiness classification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "example.yaml"


def load_rules(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load analysis rules from a YAML configuration file."""

    with Path(path).open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    return config


def _as_set(values: Iterable[str] | None) -> set[str]:
    return {value for value in (values or []) if value}


def _delivery_types(rules: dict[str, Any]) -> set[str]:
    delivery = rules.get("delivery", {})
    readiness = rules.get("forecast_readiness", {})
    return _as_set(delivery.get("estimated_issue_types")) | _as_set(readiness.get("require_parent"))


def _valid_parent(issue: dict[str, Any], issues_by_key: dict[str, dict[str, Any]], rules: dict[str, Any]) -> bool:
    parent_key = issue.get("parent_key")
    parent = issues_by_key.get(parent_key)
    hierarchy = rules.get("hierarchy", {}) or {}
    allowed_parent_types = {
        parent_type
        for parent_type, child_types in hierarchy.items()
        if issue.get("issue_type") in _as_set(child_types)
    }
    return parent is not None and parent.get("issue_type") in allowed_parent_types


def evaluate_forecast_readiness(issues: list[dict[str, Any]], rules: dict[str, Any]) -> dict[str, Any]:
    """Return a transparent evidence-quality and readiness result.

    Invalid records remain represented in ``violations``. Only records with no
    non-exclusion violations are included in ``forecast_ready_items``.
    """

    delivery = rules.get("delivery", {})
    readiness = rules.get("forecast_readiness", {})
    estimated_types = _as_set(delivery.get("estimated_issue_types"))
    required_parent_types = _as_set(readiness.get("require_parent"))
    delivery_types = _delivery_types(rules)
    excluded_statuses = _as_set(delivery.get("excluded_statuses"))
    require_team = bool(readiness.get("require_team", False))
    issues_by_key = {issue["issue_key"]: issue for issue in issues if issue.get("issue_key")}

    violations: list[dict[str, str]] = []
    unestimated_items: list[str] = []
    hierarchy_violations: list[str] = []
    ownership_violations: list[str] = []
    excluded_items: list[str] = []
    ready_items: list[str] = []

    def add_violation(issue_key: str, problem_type: str, reason: str) -> None:
        violations.append({"issue_key": issue_key, "problem_type": problem_type, "reason": reason})

    for issue in issues:
        issue_key = issue.get("issue_key")
        issue_type = issue.get("issue_type")
        if not issue_key or issue_type not in delivery_types:
            continue

        issue_violations: list[str] = []
        is_excluded = bool(issue.get("excluded")) or issue.get("status") in excluded_statuses
        if is_excluded:
            excluded_items.append(issue_key)
            add_violation(issue_key, "excluded", "Item is excluded from forecast-ready scope.")

        if issue_type in estimated_types and issue.get("story_points") is None:
            unestimated_items.append(issue_key)
            issue_violations.append("missing_estimate")
            add_violation(issue_key, "missing_estimate", f"{issue_type} requires a numeric estimate.")

        if issue_type in required_parent_types and not _valid_parent(issue, issues_by_key, rules):
            hierarchy_violations.append(issue_key)
            issue_violations.append("invalid_hierarchy")
            hierarchy = rules.get("hierarchy", {}) or {}
            expected = ", ".join(
                sorted(parent_type for parent_type, child_types in hierarchy.items() if issue_type in _as_set(child_types))
            ) or "valid"
            add_violation(issue_key, "invalid_hierarchy", f"{issue_type} requires a valid {expected} parent.")

        if require_team and not issue.get("team"):
            ownership_violations.append(issue_key)
            issue_violations.append("missing_team")
            add_violation(issue_key, "missing_team", "Delivery item has no team ownership.")

        if not is_excluded and not issue_violations:
            ready_items.append(issue_key)

    non_excluded_violation_keys = {
        violation["issue_key"]
        for violation in violations
        if violation["problem_type"] != "excluded"
    }
    excluded_points = sum(
        issue.get("story_points") or 0
        for issue in issues
        if issue.get("issue_key") in excluded_items
    )

    return {
        "forecast_ready_item_keys": ready_items,
        "forecast_ready_items": len(ready_items),
        "records_needing_correction": len(non_excluded_violation_keys),
        "impacted_delivery_items": len(non_excluded_violation_keys),
        "excluded_points": excluded_points,
        "unestimated_items": unestimated_items,
        "hierarchy_violations": hierarchy_violations,
        "ownership_violations": ownership_violations,
        "excluded_items": excluded_items,
        "violations": violations,
    }


def analyse_dataset(dataset: dict[str, list[dict[str, Any]]], rules: dict[str, Any]) -> dict[str, Any]:
    """Convenience wrapper for the loader's dataset structure."""

    return evaluate_forecast_readiness(dataset.get("issues", []), rules)


def write_result(result: dict[str, Any], path: str | Path) -> None:
    """Write a stable, indented JSON result for public behavioural contracts."""

    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    from src.jira.loader import load_dataset

    root = Path(__file__).resolve().parents[2]
    result = analyse_dataset(load_dataset(root / "examples" / "synthetic-data"), load_rules())
    print(json.dumps(result, indent=2))
