"""Tests for Phase 9 time-series preparation."""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.prepare_time_series import (
    assign_split,
    calculate_gap_summary,
    calculate_split_boundaries,
    calculate_split_summary,
    validate_columns,
    validate_unique_keys,
)


def test_required_columns_are_validated() -> None:
    """Required forecasting columns must be accepted."""
    validate_columns(
        [
            "date",
            "item_id",
            "quantity",
            "store_id",
        ]
    )


def test_missing_column_fails_validation() -> None:
    """Missing required fields must raise an error."""
    with pytest.raises(ValueError):
        validate_columns(
            [
                "date",
                "item_id",
                "quantity",
            ]
        )


def test_duplicate_date_item_store_keys_are_detected() -> None:
    """Duplicate forecasting keys must be counted."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01"]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    assert validate_unique_keys(data) == 1


def test_unique_date_item_store_keys_have_zero_duplicates() -> None:
    """Unique forecasting keys should have no duplicates."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    assert validate_unique_keys(data) == 0


def test_gap_summary_detects_missing_day() -> None:
    """An absent intermediate date should be reported."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-03",
                ]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    result = calculate_gap_summary(data)

    assert result.iloc[0]["maximum_gap_days"] == 2
    assert result.iloc[0]["missing_intermediate_days"] == 1


def test_no_gap_is_reported_for_consecutive_dates() -> None:
    """Consecutive dates should not produce missing days."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    result = calculate_gap_summary(data)

    assert result.iloc[0]["maximum_gap_days"] == 1
    assert result.iloc[0]["missing_intermediate_days"] == 0


def test_split_boundaries_are_chronological() -> None:
    """Train boundary must precede validation boundary."""
    dates = pd.Series(
        pd.date_range(
            "2024-01-01",
            periods=100,
            freq="D",
        )
    )

    train_end, validation_end = calculate_split_boundaries(
        dates
    )

    assert train_end < validation_end


def test_split_assignment_is_time_aware() -> None:
    """Rows must be assigned without temporal shuffling."""
    dates = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "item_id": ["A"] * 100,
            "store_id": [1] * 100,
            "quantity": range(100),
        }
    )

    train_end, validation_end = calculate_split_boundaries(
        data["date"]
    )

    result = assign_split(
        data,
        train_end,
        validation_end,
    )

    assert result.iloc[0]["split"] == "train"
    assert result.iloc[-1]["split"] == "test"


def test_split_summary_has_all_partitions() -> None:
    """The split summary should contain train, validation and test."""
    data = pd.DataFrame(
        {
            "date": pd.date_range(
                "2024-01-01",
                periods=100,
                freq="D",
            ),
            "item_id": ["A"] * 100,
            "store_id": [1] * 100,
            "quantity": range(100),
            "split": (
                ["train"] * 70
                + ["validation"] * 15
                + ["test"] * 15
            ),
        }
    )

    result = calculate_split_summary(data)

    assert set(result["split"]) == {
        "train",
        "validation",
        "test",
    }


def test_chronological_split_has_no_overlap() -> None:
    """Partition date ranges must not overlap."""
    dates = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "item_id": ["A"] * 100,
            "store_id": [1] * 100,
            "quantity": range(100),
        }
    )

    train_end, validation_end = calculate_split_boundaries(
        data["date"]
    )

    result = assign_split(
        data,
        train_end,
        validation_end,
    )

    train_max = result.loc[
        result["split"] == "train",
        "date",
    ].max()

    validation_min = result.loc[
        result["split"] == "validation",
        "date",
    ].min()

    validation_max = result.loc[
        result["split"] == "validation",
        "date",
    ].max()

    test_min = result.loc[
        result["split"] == "test",
        "date",
    ].min()

    assert train_max < validation_min
    assert validation_max < test_min
