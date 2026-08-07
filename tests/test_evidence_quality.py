import json
from pathlib import Path

import yaml

from src.analysis.evidence_quality import analyse_dataset
from src.jira.loader import load_dataset


ROOT = Path(__file__).parents[1]
DATA_DIR = ROOT / "examples" / "synthetic-data"
CONFIG_PATH = ROOT / "config" / "example.yaml"
EXPECTED_PATH = ROOT / "examples" / "expected-output" / "evidence-quality.json"


def _result():
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        rules = yaml.safe_load(handle)
    return analyse_dataset(load_dataset(DATA_DIR), rules)


def test_forecast_readiness_and_evidence_groups():
    result = _result()

    assert result["forecast_ready_items"] == 6
    assert result["unestimated_items"] == ["DEMO-104", "DEMO-107", "DEMO-113"]
    assert result["hierarchy_violations"] == ["DEMO-106", "DEMO-112", "DEMO-113"]
    assert result["ownership_violations"] == ["DEMO-109", "DEMO-113"]


def test_excluded_items_and_points_do_not_enter_ready_scope():
    result = _result()

    assert result["excluded_items"] == ["DEMO-110"]
    assert result["excluded_points"] == 5
    assert all(entry["issue_key"] != "DEMO-110" for entry in result["violations"] if entry["problem_type"] != "excluded")


def test_invalid_scope_remains_visible_without_double_counting():
    result = _result()

    assert result["records_needing_correction"] == 6
    assert result["impacted_delivery_items"] == 6
    demo_113 = [entry for entry in result["violations"] if entry["issue_key"] == "DEMO-113"]
    assert {entry["problem_type"] for entry in demo_113} == {"missing_estimate", "invalid_hierarchy", "missing_team"}
    assert len({entry["issue_key"] for entry in result["violations"] if entry["problem_type"] != "excluded"}) == 6


def test_result_matches_public_behavioural_contract():
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    assert _result() == expected
