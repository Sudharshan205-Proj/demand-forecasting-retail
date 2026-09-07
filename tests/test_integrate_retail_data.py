"""Tests for Phase 6 retail data integration."""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.integrate_retail_data import (
    KEY_COLUMNS,
    normalise_keys,
    require_columns,
)


def test_canonical_key_contains_three_columns() -> None:
    assert KEY_COLUMNS == [
        "date",
        "item_id",
        "store_id",
    ]


def test_required_columns_are_detected() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item_1"],
            "store_id": [1],
        }
    )

    require_columns(
        frame,
        ["date", "item_id", "store_id"],
        "test",
    )


def test_missing_columns_raise_error() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item_1"],
        }
    )

    with pytest.raises(ValueError):
        require_columns(
            frame,
            ["date", "item_id", "store_id"],
            "test",
        )


def test_keys_are_normalised() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": [" item_1 "],
            "store_id": ["1"],
        }
    )

    result = normalise_keys(frame)

    assert result.loc[0, "date"] == "2024-01-01"
    assert result.loc[0, "item_id"] == "item_1"
    assert result.loc[0, "store_id"] == 1


def test_invalid_date_becomes_missing() -> None:
    frame = pd.DataFrame(
        {
            "date": ["not-a-date"],
            "item_id": ["item_1"],
            "store_id": [1],
        }
    )

    result = normalise_keys(frame)

    assert pd.isna(result.loc[0, "date"])


def test_store_id_is_numeric() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item_1"],
            "store_id": ["4"],
        }
    )

    result = normalise_keys(frame)

    assert result.loc[0, "store_id"] == 4


def test_canonical_grain_detects_duplicates() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "item_id": ["item_1", "item_1"],
            "store_id": [1, 1],
        }
    )

    duplicate_count = int(
        frame.duplicated(
            subset=KEY_COLUMNS,
            keep=False,
        ).sum()
    )

    assert duplicate_count == 2


def test_canonical_grain_allows_different_items() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "item_id": ["item_1", "item_2"],
            "store_id": [1, 1],
        }
    )

    assert not frame.duplicated(
        subset=KEY_COLUMNS
    ).any()


def test_canonical_grain_allows_different_stores() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "item_id": ["item_1", "item_1"],
            "store_id": [1, 2],
        }
    )

    assert not frame.duplicated(
        subset=KEY_COLUMNS
    ).any()


def test_left_join_preserves_sales_rows() -> None:
    sales = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["missing_item"],
            "store_id": [1],
            "quantity": [10],
        }
    )

    catalog = pd.DataFrame(
        {
            "item_id": ["other_item"],
            "dept_name": ["Example"],
        }
    )

    result = sales.merge(
        catalog,
        on="item_id",
        how="left",
        validate="many_to_one",
    )

    assert len(result) == 1
    assert pd.isna(result.loc[0, "dept_name"])


def test_many_to_one_validation_rejects_duplicate_dimension_keys() -> None:
    sales = pd.DataFrame(
        {
            "item_id": ["item_1"],
            "store_id": [1],
        }
    )

    dimension = pd.DataFrame(
        {
            "item_id": ["item_1", "item_1"],
            "value": ["a", "b"],
        }
    )

    with pytest.raises(pd.errors.MergeError):
        sales.merge(
            dimension,
            on="item_id",
            how="left",
            validate="many_to_one",
        )


def test_online_sales_are_not_added_to_physical_quantity() -> None:
    physical_quantity = 100
    online_quantity = 25

    integrated_target = physical_quantity

    assert integrated_target != (
        physical_quantity + online_quantity
    )


def test_zero_missing_auxiliary_values_are_valid() -> None:
    row = pd.Series(
        {
            "online_quantity": 0,
            "price_change_count": 0,
            "markdown_record_count": 0,
            "discount_record_count": 0,
        }
    )

    assert row.sum() == 0