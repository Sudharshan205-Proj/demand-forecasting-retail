"""Tests for the Phase 5 retail data-cleaning pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from scripts import clean_retail_data
from scripts.clean_retail_data import (
    REQUIRED_COLUMNS,
    initialise_quality_metrics,
    load_catalog_item_ids,
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
    assert metrics["unmatched_catalog_rows"] == 0
    assert metrics["earliest_valid_date"] is None
    assert metrics["latest_valid_date"] is None


def test_negative_revenue_is_detected():
    """Negative revenue should be counted."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert metrics["negative_revenue_rows"] == 2


def test_duplicate_rows_are_detected():
    """Exact duplicate rows should be counted and only the first kept."""
    chunk = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "item_id": ["item-1", "item-1"],
            "quantity": [10, 10],
            "price_base": [5.0, 5.0],
            "sum_total": [50.0, 50.0],
            "store_id": ["1", "1"],
        }
    )

    metrics = initialise_quality_metrics()

    cleaned = update_quality_metrics(
        metrics,
        chunk,
        {"1"},
    )

    assert metrics["duplicate_rows"] == 1
    assert len(cleaned) == 1


def test_non_numeric_measures_are_treated_as_invalid():
    """Non-numeric required measures should be coerced and removed."""
    chunk = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item-1"],
            "quantity": ["not-a-number"],
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

    assert metrics["rows_read"] == 1
    assert len(cleaned) == 0


def test_catalog_reference_check_counts_unmatched_rows():
    """Catalog membership should be reported, not used as a deletion rule."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()
    unmatched_items: set[str] = set()

    cleaned = update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
        {"item-1"},
        unmatched_items,
    )

    assert metrics["unmatched_catalog_rows"] == 3
    assert unmatched_items == {"item-2", "item-3", "item-4"}
    assert len(cleaned) == 1


def test_date_coverage_is_recorded():
    """Valid-date coverage should be recorded for the chunk."""
    chunk = make_sales_fixture()
    metrics = initialise_quality_metrics()

    update_quality_metrics(
        metrics,
        chunk,
        {"1", "2", "3", "4"},
    )

    assert metrics["earliest_valid_date"] == "2024-01-01"
    assert metrics["latest_valid_date"] == "2024-01-04"


def test_load_catalog_item_ids_reads_item_column(tmp_path: Path):
    """Catalogued item identifiers should be read from the catalog."""
    catalog_path = tmp_path / "catalog.csv"

    pd.DataFrame(
        {
            "item_id": ["item-1", "item-2", "item-2"],
            "dept_name": ["Dept A", "Dept B", "Dept B"],
        }
    ).to_csv(
        catalog_path,
        index=False,
    )

    result = load_catalog_item_ids(catalog_path)

    assert result == {"item-1", "item-2"}


def test_clean_sales_writes_output_across_chunks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """The pipeline should write one header and the expected rows."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    pd.DataFrame(
        {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "invalid-date",
                "2024-01-04",
                "2024-01-05",
            ],
            "item_id": ["item-1", "item-2", "item-3", "item-4", "item-5"],
            "quantity": [10, -5, 4, 2, 7],
            "price_base": [5.0, 10.0, 2.0, -1.0, 3.0],
            "sum_total": [50.0, -50.0, 8.0, -2.0, 21.0],
            "store_id": ["1", "1", "1", "99", "1"],
        }
    ).to_csv(
        raw_dir / "sales.csv",
        index=False,
    )

    pd.DataFrame(
        {
            "store_id": [1, 2, 3, 4],
        }
    ).to_csv(
        raw_dir / "stores.csv",
        index=False,
    )

    pd.DataFrame(
        {
            "item_id": ["item-1", "item-2", "item-3", "item-5"],
        }
    ).to_csv(
        raw_dir / "catalog.csv",
        index=False,
    )

    monkeypatch.setattr(clean_retail_data, "PROCESSED_DATA_DIR", processed_dir)
    monkeypatch.setattr(
        clean_retail_data, "SALES_PATH", raw_dir / "sales.csv"
    )
    monkeypatch.setattr(
        clean_retail_data, "STORES_PATH", raw_dir / "stores.csv"
    )
    monkeypatch.setattr(
        clean_retail_data, "CATALOG_PATH", raw_dir / "catalog.csv"
    )
    monkeypatch.setattr(
        clean_retail_data,
        "CLEAN_SALES_PATH",
        processed_dir / "sales_clean.csv",
    )
    monkeypatch.setattr(
        clean_retail_data,
        "QUALITY_REPORT_PATH",
        processed_dir / "data_quality_report.csv",
    )
    monkeypatch.setattr(
        clean_retail_data,
        "CLEANING_SUMMARY_PATH",
        processed_dir / "cleaning_summary.csv",
    )
    monkeypatch.setattr(clean_retail_data, "CHUNK_SIZE", 2)

    metrics = clean_retail_data.clean_sales()

    clean_file = processed_dir / "sales_clean.csv"
    assert clean_file.exists()

    cleaned = pd.read_csv(clean_file)
    assert list(cleaned.columns) == REQUIRED_COLUMNS
    # Row 2 fails the negative-quantity rule, row 3 has an invalid date,
    # row 4 fails the negative-price and unknown-store rules.
    assert len(cleaned) == 2

    assert clean_file.read_text().count("date,item_id") == 1

    assert metrics["rows_read"] == 5
    assert metrics["rows_written"] == 2
    assert metrics["unmatched_catalog_rows"] == 1
    assert metrics["earliest_valid_date"] == "2024-01-01"
    assert metrics["latest_valid_date"] == "2024-01-05"

    summary = pd.read_csv(processed_dir / "cleaning_summary.csv")
    removed = summary.loc[summary["action"] == "Rows removed"]
    assert int(removed["count"].iloc[0]) == 3

    report = pd.read_csv(processed_dir / "data_quality_report.csv")
    metric_names = set(report["metric"])
    assert "unmatched_catalog_rows" in metric_names
    assert "unmatched_catalog_item_ids" in metric_names
    assert "earliest_valid_date" in metric_names


def test_clean_sales_raises_when_sales_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """A missing sales file should fail explicitly."""
    monkeypatch.setattr(
        clean_retail_data,
        "SALES_PATH",
        tmp_path / "missing_sales.csv",
    )

    with pytest.raises(FileNotFoundError, match="Sales file not found"):
        clean_retail_data.clean_sales()
