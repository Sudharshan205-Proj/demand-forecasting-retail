"""Tests for the Phase 7 exploratory data analysis module."""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.exploratory_data_analysis import (
    REQUIRED_COLUMNS,
    validate_input_columns,
)


def test_required_columns_are_defined() -> None:
    assert REQUIRED_COLUMNS == [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]


def test_valid_schema_passes() -> None:
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]

    validate_input_columns(columns)


def test_missing_required_column_fails() -> None:
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "store_id",
    ]

    with pytest.raises(ValueError):
        validate_input_columns(columns)


def test_extra_columns_are_allowed() -> None:
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
        "dept_name",
        "online_quantity",
    ]

    validate_input_columns(columns)


def test_monthly_grouping() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-15",
                    "2024-02-01",
                ]
            ),
            "quantity": [10, 20, 30],
            "sum_total": [100, 200, 300],
        }
    )

    frame["year_month"] = (
        frame["date"]
        .dt.to_period("M")
        .astype("string")
    )

    result = (
        frame.groupby(
            "year_month",
            as_index=False,
        )
        .agg(
            quantity=("quantity", "sum"),
            revenue=("sum_total", "sum"),
        )
    )

    january = result.loc[
        result["year_month"] == "2024-01"
    ].iloc[0]

    assert january["quantity"] == 30
    assert january["revenue"] == 300


def test_store_aggregation() -> None:
    frame = pd.DataFrame(
        {
            "store_id": [1, 1, 2],
            "quantity": [10, 20, 30],
            "sum_total": [100, 200, 300],
        }
    )

    result = (
        frame.groupby(
            "store_id",
            as_index=False,
        )
        .agg(
            quantity=("quantity", "sum"),
            revenue=("sum_total", "sum"),
        )
    )

    store_one = result.loc[
        result["store_id"] == 1
    ].iloc[0]

    assert store_one["quantity"] == 30
    assert store_one["revenue"] == 300


def test_item_aggregation() -> None:
    frame = pd.DataFrame(
        {
            "item_id": ["a", "a", "b"],
            "quantity": [5, 7, 10],
        }
    )

    result = (
        frame.groupby(
            "item_id",
            as_index=False,
        )["quantity"]
        .sum()
    )

    item_a = result.loc[
        result["item_id"] == "a",
        "quantity",
    ].iloc[0]

    assert item_a == 12


def test_correlation_uses_numeric_columns() -> None:
    frame = pd.DataFrame(
        {
            "quantity": [1, 2, 3],
            "price_base": [10, 20, 30],
            "item_id": ["a", "b", "c"],
        }
    )

    result = frame.corr(
        numeric_only=True
    )

    assert "quantity" in result.columns
    assert "price_base" in result.columns
    assert "item_id" not in result.columns


def test_sample_is_reproducible() -> None:
    frame = pd.DataFrame(
        {
            "value": range(100)
        }
    )

    first = frame.sample(
        n=10,
        random_state=42,
    )

    second = frame.sample(
        n=10,
        random_state=42,
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_empty_category_result_has_expected_columns() -> None:
    result = pd.DataFrame(
        columns=[
            "dept_name",
            "quantity",
            "revenue",
            "records",
        ]
    )

    assert list(result.columns) == [
        "dept_name",
        "quantity",
        "revenue",
        "records",
    ]
