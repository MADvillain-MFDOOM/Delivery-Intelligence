"""Minimal console report for the public synthetic evidence example."""

from __future__ import annotations

from pathlib import Path

from src.analysis.evidence_quality import analyse_dataset, load_rules
from src.jira.loader import load_dataset


def render_console(result: dict) -> str:
    lines = [
        "Delivery Intelligence",
        f"Forecast-ready items: {result['forecast_ready_items']}",
        f"Records needing correction: {result['records_needing_correction']}",
        f"Impacted delivery items: {result['impacted_delivery_items']}",
        f"Excluded points: {result['excluded_points']}",
        f"Unestimated Stories/Bugs: {len(result['unestimated_items'])}",
        "",
        "What needs attention",
    ]
    grouped = {
        "Missing estimates": "missing_estimate",
        "Hierarchy": "invalid_hierarchy",
        "Ownership": "missing_team",
    }
    for heading, problem_type in grouped.items():
        entries = [violation for violation in result["violations"] if violation["problem_type"] == problem_type]
        if not entries:
            continue
        lines.append(heading)
        for entry in entries:
            lines.append(f"{entry['issue_key']}: {entry['reason']}")
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    dataset = load_dataset(root / "examples" / "synthetic-data")
    result = analyse_dataset(dataset, load_rules(root / "config" / "example.yaml"))
    print(render_console(result))


if __name__ == "__main__":
    main()
