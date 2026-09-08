"""Tests for the Streamlit application support components."""

from pathlib import Path

import pandas as pd
import pytest

from app.data_loader import load_csv
from app.formatting import format_number, format_percent


def test_format_number():
    assert format_number(1234.5) == "1,234.50"


def test_format_percent():
    assert format_percent(95.5) == "95.50%"


def test_load_csv(tmp_path: Path):
    path = tmp_path / "example.csv"

    pd.DataFrame(
        {
            "store_id": [1, 2],
            "value": [10.0, 20.0],
        }
    ).to_csv(path, index=False)

    frame = load_csv(path)

    assert len(frame) == 2
    assert list(frame.columns) == ["store_id", "value"]


def test_load_csv_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "missing.csv")


def test_load_csv_empty_file(tmp_path: Path):
    path = tmp_path / "empty.csv"
    pd.DataFrame(columns=["store_id"]).to_csv(path, index=False)

    with pytest.raises(ValueError):
        load_csv(path)
