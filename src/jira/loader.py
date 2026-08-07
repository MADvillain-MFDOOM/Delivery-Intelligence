"""Load and normalise the public synthetic Jira-like CSV dataset."""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Any


DATASET_FILES = {
    "issues": "issues.csv",
    "changelog": "changelog.csv",
    "sprints": "sprints.csv",
    "capacity": "capacity.csv",
    "dependencies": "dependencies.csv",
}

DATE_FIELDS = {"created_date", "updated_date", "resolution_date", "transition_date", "start_date", "end_date"}
NUMBER_FIELDS = {"story_points", "capacity_points"}
BOOLEAN_FIELDS = {"blocked", "excluded"}


def normalise_empty(value: str | None) -> str | None:
    """Return ``None`` for CSV values that contain no meaningful text."""

    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_date(value: str | None) -> date | None:
    value = normalise_empty(value)
    return date.fromisoformat(value) if value else None


def parse_number(value: str | None) -> int | float | None:
    value = normalise_empty(value)
    if value is None:
        return None
    number = float(value)
    return int(number) if number.is_integer() else number


def parse_bool(value: str | None) -> bool | None:
    value = normalise_empty(value)
    if value is None:
        return None
    lowered = value.lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value}")


def _parse_value(field: str, value: str | None) -> Any:
    if field in DATE_FIELDS:
        return parse_date(value)
    if field in NUMBER_FIELDS:
        return parse_number(value)
    if field in BOOLEAN_FIELDS:
        return parse_bool(value)
    return normalise_empty(value)


def load_csv(path: str | Path) -> list[dict[str, Any]]:
    """Load one CSV file into dictionaries with consistently typed values."""

    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{field: _parse_value(field, value) for field, value in row.items()} for row in reader]


def load_dataset(directory: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Load all known synthetic dataset files from ``directory``."""

    directory = Path(directory)
    return {name: load_csv(directory / filename) for name, filename in DATASET_FILES.items()}
