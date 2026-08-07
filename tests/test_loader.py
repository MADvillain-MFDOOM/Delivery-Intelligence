from datetime import date
from pathlib import Path

from src.jira.loader import load_dataset


DATA_DIR = Path(__file__).parents[1] / "examples" / "synthetic-data"


def test_csv_loading_and_normalisation():
    dataset = load_dataset(DATA_DIR)

    assert len(dataset["issues"]) == 14
    issue = next(item for item in dataset["issues"] if item["issue_key"] == "DEMO-104")
    assert issue["story_points"] is None
    assert issue["parent_key"] == "DEMO-102"
    assert issue["created_date"] == date(2026, 1, 8)
    assert issue["blocked"] is False
    assert issue["excluded"] is False


def test_numeric_boolean_and_missing_values_are_typed():
    dataset = load_dataset(DATA_DIR)
    issue = next(item for item in dataset["issues"] if item["issue_key"] == "DEMO-114")
    excluded = next(item for item in dataset["issues"] if item["issue_key"] == "DEMO-110")

    assert issue["story_points"] == 1.5
    assert isinstance(issue["story_points"], float)
    assert issue["blocked"] is False
    assert excluded["excluded"] is True
    assert excluded["resolution_date"] is None
