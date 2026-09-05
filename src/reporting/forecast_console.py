"""Console and JSON reporting for the public synthetic forecast example."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.analysis.evidence_quality import load_rules
from src.forecasting import build_delivery_forecast
from src.jira.loader import load_dataset


def render_console(result: dict) -> str:
    scope = result["scope"]
    lines = [
        "Delivery Forecast",
        f"Status: {result['status']}",
        f"As of: {result['as_of_date']}",
        f"Forecast-ready remaining scope: {scope['remaining_items']} items / {scope['remaining_points']} points",
        f"Excluded or invalid items: {scope['excluded_or_invalid_items']}",
        "",
        "Scenarios",
    ]
    if not result["scenarios"]:
        lines.append("No scenarios available: there is no usable closed-sprint history.")
    for name, scenario in result["scenarios"].items():
        cycles = scenario["sprints_to_complete"]
        completion = scenario["projected_completion_date"]
        outcome = f"{cycles} sprints / {completion}" if cycles is not None else "not projectable"
        lines.append(f"{name.title()}: {scenario['points_per_sprint']} points/sprint -> {outcome}")
    if result["caveats"]:
        lines.extend(["", "Caveats"])
        lines.extend(f"- {caveat}" for caveat in result["caveats"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit the full machine-readable forecast")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    result = build_delivery_forecast(
        load_dataset(root / "examples" / "synthetic-data"),
        load_rules(root / "config" / "example.yaml"),
    )
    print(json.dumps(result, indent=2) if args.json else render_console(result))


if __name__ == "__main__":
    main()
