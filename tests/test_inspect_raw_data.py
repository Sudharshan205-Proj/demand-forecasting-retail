"""Tests for raw-data inspection utilities."""

from pathlib import Path

import pandas as pd
import pytest

from scripts.inspect_raw_data import inspect_directory, profile_csv


def create_sample_csv(file_path: Path) -> None:
    """Create a small CSV fixture for testing."""
    dataframe = pd.DataFrame(
        {
            "date": [
                "2025-01-01",
                "2025-01-02",
                "2025-01-02",
            ],
            "item_id": [1, 1, 2],
            "quantity": [10, 12, 5],
            "store_id": [1, 1, 2],
        }
    )

    dataframe.to_csv(file_path, index=False)


def test_profile_csv_reports_basic_structure(tmp_path):
    """The profiler should report dimensions and columns."""
    file_path = tmp_path / "sample.csv"
    create_sample_csv(file_path)

    profile = profile_csv(file_path)

    assert profile["rows"] == 3
    assert profile["columns"] == 4
    assert profile["column_names"] == [
        "date",
        "item_id",
        "quantity",
        "store_id",
    ]
    assert profile["duplicate_rows"] == 0
    assert profile["date_min"] == "2025-01-01"
    assert profile["date_max"] == "2025-01-02"


def test_profile_csv_counts_missing_values(tmp_path):
    """The profiler should report missing values."""
    file_path = tmp_path / "missing.csv"

    dataframe = pd.DataFrame(
        {
            "date": ["2025-01-01", None],
            "item_id": [1, 2],
            "quantity": [10, None],
            "store_id": [1, 1],
        }
    )

    dataframe.to_csv(file_path, index=False)

    profile = profile_csv(file_path)

    assert profile["missing_values"]["date"] == 1
    assert profile["missing_values"]["quantity"] == 1
    assert profile["invalid_date_values"] == 1


def test_inspect_directory_requires_csv_files(tmp_path):
    """The directory inspector should reject empty directories."""
    with pytest.raises(FileNotFoundError):
        inspect_directory(tmp_path)
