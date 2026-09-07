"""Tests for the Phase 5 retail data-cleaning pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from scripts.clean_retail_data import (
    REQUIRED_COLUMNS,
    initialise_quality_metrics,
    load_store_ids,
    update_quality_metrics,
    validate_required_columns,
)


def make_sales_fixture() -> pd.DataFrame:
    """Create a small sales dataset containing valid and invalid records."""
    return pd.DataFrame(
        {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "invalid-date",
                "2024-01-04",
            ],
            "item_id": [
                "item-1",
                "item-2",
                "item-3",
                "item-4",
            ],
            "quantity": [
                10,
                -5,
                4,
                2,
            ],
            "price_base": [
                5.0,
                10.0,
                2.0,
                -1.0,
            ],
            "sum_total": [
                50.0,
                -50.0,
                8.0,
                -2.0,
            ],
            "store_id": [
                "1",
                "1",
                "1",
                "99",
            ],
        }
    )


def test_required_columns_are_present():
    """Valid sales schema should pass validation."""
    validate_required_columns(REQUIRED_COLUMNS)


def test_missing_required_column_raises_error():
    """Missing analytical columns should fail explicitly."""
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "store_id",
    ]

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_required_columns(columns)


def test_store_ids_are_loaded(tmp_path: Path):
    """Store identifiers should be read from the lookup table."""
    stores_path = tmp_path / "stores.csv"

    pd.DataFrame(
        {
            "store_id": [1, 2, 3, 4],
        }
    ).to_csv(
        stores_path,
        index=False,
    )

    result = load_store_ids(stores_path)

    assert result == {"1", "2", "3", "4"}


def test_negative_quantity_is_detected():
    """Negative demand quantities should be counted."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    cleaned = update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert metrics["negative_quantity_rows"] == 1
    assert len(cleaned) == 1


def test_invalid_dates_are_detected():
    """Invalid dates should be counted."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert metrics["invalid_date_rows"] == 1


def test_negative_prices_are_detected():
    """Negative prices should be counted."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert metrics["negative_price_rows"] == 1


def test_unknown_store_is_detected():
    """Unknown store identifiers should be counted."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert metrics["unknown_store_rows"] == 1


def test_cleaning_removes_invalid_records():
    """Only records passing all documented validity rules remain."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    cleaned = update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["item_id"] == "item-1"


def test_revenue_mismatch_is_reported():
    """Revenue inconsistencies should be reported rather than overwritten."""
    chunk = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item-1"],
            "quantity": [10],
            "price_base": [5.0],
            "sum_total": [40.0],
            "store_id": ["1"],
        }
    )

    metrics = initialise_quality_metrics()

    cleaned = update_quality_metrics(
        metrics,
        chunk,
        {"1"},
    )

    assert metrics["revenue_mismatch_rows"] == 1
    assert len(cleaned) == 1


def test_valid_record_is_retained():
    """A valid record should survive the cleaning rules."""
    chunk = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item-1"],
            "quantity": [10],
            "price_base": [5.0],
            "sum_total": [50.0],
            "store_id": ["1"],
        }
    )

    metrics = initialise_quality_metrics()

    cleaned = update_quality_metrics(
        metrics,
        chunk,
        {"1"},
    )

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["quantity"] == 10


def test_quality_metrics_start_at_zero():
    """Quality counters should initialise deterministically."""
    metrics = initialise_quality_metrics()

    assert metrics["rows_read"] == 0
    assert metrics["rows_written"] == 0
    assert metrics["duplicate_rows"] == 0
