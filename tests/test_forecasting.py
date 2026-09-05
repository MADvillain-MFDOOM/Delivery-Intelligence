from pathlib import Path

from src.analysis.evidence_quality import load_rules
from src.forecasting import build_delivery_forecast
from src.forecasting.scenario import _percentile
from src.jira.loader import load_dataset


ROOT = Path(__file__).parents[1]


def _forecast():
    return build_delivery_forecast(
        load_dataset(ROOT / "examples" / "synthetic-data"),
        load_rules(ROOT / "config" / "example.yaml"),
    )


def test_percentile_interpolates_deterministically():
    assert _percentile([0, 3], 25) == 0.75
    assert _percentile([0, 3], 50) == 1.5
    assert _percentile([0, 3], 75) == 2.25


def test_forecast_uses_resolution_windows_and_ready_evidence_only():
    result = _forecast()
    observations = result["history"]["observations"]

    assert observations[0]["sprint"] == "Sprint-Alpha"
    assert observations[0]["completed_item_keys"] == ["DEMO-103"]
    assert observations[0]["completed_points"] == 3
    assert observations[1]["completed_points"] == 0
    assert "DEMO-104" not in observations[1]["completed_item_keys"]


def test_forecast_exposes_scope_scenarios_and_insufficient_history():
    result = _forecast()

    assert result["schema_version"] == "DeliveryForecast.v1"
    assert result["status"] == "insufficient_history"
    assert result["scope"]["remaining_item_keys"] == ["DEMO-105", "DEMO-111", "DEMO-114"]
    assert result["scope"]["remaining_points"] == 11.5
    assert result["scenarios"]["expected"]["sprints_to_complete"] == 8
    assert result["scenarios"]["expected"]["projected_completion_date"] == "2026-06-19"
    assert len(result["caveats"]) == 3


def test_zero_rate_scenario_is_visible_but_not_projected():
    rules = load_rules(ROOT / "config" / "example.yaml")
    rules["forecasting"]["scenario_percentiles"]["stalled"] = 0
    result = build_delivery_forecast(load_dataset(ROOT / "examples" / "synthetic-data"), rules)

    assert result["scenarios"]["stalled"]["points_per_sprint"] == 0
    assert result["scenarios"]["stalled"]["sprints_to_complete"] is None
    assert result["scenarios"]["stalled"]["projected_completion_date"] is None
