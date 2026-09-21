"""Tests for Phase 6 retail data integration."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import integrate_retail_data
from scripts.integrate_retail_data import (
    KEY_COLUMNS,
    aggregate_actual_matrix,
    aggregate_catalog,
    aggregate_discounts,
    aggregate_markdowns,
    aggregate_online,
    aggregate_price_history,
    aggregate_stores,
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


def test_online_aggregation_returns_only_online_features(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Online aggregation must expose online-channel features only."""
    online_path = tmp_path / "online.csv"

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "item_id": ["item-1", "item-1"],
            "quantity": [3, 2],
            "price_base": [4.5, 4.5],
            "sum_total": [13.5, 9.0],
            "store_id": [1, 1],
        }
    ).to_csv(online_path, index=False)

    monkeypatch.setattr(integrate_retail_data, "ONLINE_PATH", online_path)

    result = aggregate_online()

    assert set(result.columns) == {
        "date",
        "item_id",
        "store_id",
        "online_quantity",
        "online_sales_value",
        "online_average_price",
    }
    assert "quantity" not in result.columns
    assert result.loc[0, "online_quantity"] == 5
    assert result.loc[0, "online_sales_value"] == pytest.approx(22.5)


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


def write_stores(path: Path) -> None:
    """Write a two-store lookup fixture."""
    pd.DataFrame(
        {
            "store_id": [1, 2],
            "division": ["Div1", "Div1"],
            "format": ["Format-1", "Format-2"],
            "city": ["City1", "City2"],
            "area": [100, 200],
        }
    ).to_csv(path, index=False)


def write_catalog(path: Path) -> None:
    """Write a two-item catalog fixture."""
    pd.DataFrame(
        {
            "item_id": ["item-1", "item-2"],
            "dept_name": ["Dept A", "Dept B"],
            "class_name": ["C1", "C2"],
            "subclass_name": ["S1", "S2"],
            "item_type": ["T1", "T2"],
            "weight_volume": [1.0, 2.0],
            "weight_netto": [1.0, 2.0],
            "fatness": [1.0, 2.0],
        }
    ).to_csv(path, index=False)


def write_sales(path: Path) -> None:
    """Write a three-row cleaned-sales fixture (item-9 is not catalogued)."""
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "item_id": ["item-1", "item-2", "item-9"],
            "quantity": [10, 3, 2],
            "price_base": [5.0, 10.0, 4.0],
            "sum_total": [50.0, 30.0, 8.0],
            "store_id": [1, 1, 2],
        }
    ).to_csv(path, index=False)


def test_catalog_aggregation_deduplicates_items(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The catalog dimension must keep one row per item."""
    catalog_path = tmp_path / "catalog.csv"

    pd.DataFrame(
        {
            "item_id": ["item-1", "item-1", "item-2"],
            "dept_name": ["First", "Second", "Other"],
            "class_name": ["C1", "C1", "C2"],
            "subclass_name": ["S1", "S1", "S2"],
            "item_type": ["T1", "T1", "T2"],
            "weight_volume": [1.0, 1.0, 2.0],
            "weight_netto": [1.0, 1.0, 2.0],
            "fatness": [1.0, 1.0, 2.0],
        }
    ).to_csv(catalog_path, index=False)

    monkeypatch.setattr(integrate_retail_data, "CATALOG_PATH", catalog_path)

    result = aggregate_catalog()

    assert len(result) == 2
    assert result["item_id"].is_unique
    assert (
        result.loc[result["item_id"] == "item-1", "dept_name"].iloc[0]
        == "First"
    )


def test_store_aggregation_deduplicates_stores(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The store dimension must keep one row per store."""
    stores_path = tmp_path / "stores.csv"

    pd.DataFrame(
        {
            "store_id": [1, 1, 2],
            "division": ["Div1", "Div1", "Div1"],
            "format": ["F1", "F1", "F2"],
            "city": ["City1", "City1", "City2"],
            "area": [100, 100, 200],
        }
    ).to_csv(stores_path, index=False)

    monkeypatch.setattr(integrate_retail_data, "STORES_PATH", stores_path)

    result = aggregate_stores()

    assert len(result) == 2
    assert result["store_id"].is_unique


def test_price_history_aggregation_counts_events_and_takes_last_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Price events should be counted and collapsed to one row per key."""
    price_path = tmp_path / "price_history.csv"

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01", "2024-01-02"],
            "item_id": ["item-1", "item-1", "item-2"],
            "price": [4.5, 5.0, 9.0],
            "code": [1, 2, 3],
            "store_id": [1, 1, 1],
        }
    ).to_csv(price_path, index=False)

    monkeypatch.setattr(
        integrate_retail_data, "PRICE_HISTORY_PATH", price_path
    )

    result = aggregate_price_history()
    row = result.loc[
        (result["item_id"] == "item-1") & (result["date"] == "2024-01-01")
    ].iloc[0]

    assert len(result) == 2
    assert row["price_change_count"] == 2
    assert row["price_history_price"] == 5.0
    assert row["price_change_code"] == 2


def test_markdown_aggregation_computes_discount(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Markdown discount should be 1 - price / normal_price."""
    markdown_path = tmp_path / "markdowns.csv"

    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item-1"],
            "normal_price": [10.0],
            "price": [8.0],
            "quantity": [2.0],
            "store_id": [1],
        }
    ).to_csv(markdown_path, index=False)

    monkeypatch.setattr(integrate_retail_data, "MARKDOWNS_PATH", markdown_path)

    result = aggregate_markdowns()

    assert result.loc[0, "markdown_record_count"] == 1
    assert result.loc[0, "markdown_discount"] == pytest.approx(0.2)


def test_markdown_discount_is_missing_when_normal_price_is_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A zero normal price must leave the discount missing, never infinite."""
    markdown_path = tmp_path / "markdowns.csv"

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "item_id": ["item-1", "item-2"],
            "normal_price": [0.0, 10.0],
            "price": [4.0, 8.0],
            "quantity": [2.0, 2.0],
            "store_id": [1, 1],
        }
    ).to_csv(markdown_path, index=False)

    monkeypatch.setattr(integrate_retail_data, "MARKDOWNS_PATH", markdown_path)

    result = aggregate_markdowns().set_index("item_id")

    assert pd.isna(result.loc["item-1", "markdown_discount"])
    assert result.loc["item-2", "markdown_discount"] == pytest.approx(0.2)
    assert not np.isinf(
        result["markdown_discount"].dropna().to_numpy(dtype=float)
    ).any()
    assert (
        integrate_retail_data.UNDEFINED_RATE_RECORDS["markdown_discount"]
        == 1
    )


def test_promo_rate_is_missing_when_price_before_promo_is_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A zero promotional base price must leave the rate missing."""
    discounts_path = tmp_path / "discounts_history.csv"

    pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03"],
            "item_id": ["item-2", "item-3"],
            "sale_price_before_promo": [0.0, 10.0],
            "sale_price_time_promo": [5.0, 8.0],
            "promo_type_code": [1, 1],
            "doc_id": [100, 101],
            "number_disc_day": [3, 5],
            "store_id": [1, 1],
        }
    ).to_csv(discounts_path, index=False)

    monkeypatch.setattr(
        integrate_retail_data, "DISCOUNTS_PATH", discounts_path
    )

    result = aggregate_discounts().set_index("item_id")

    assert pd.isna(result.loc["item-2", "promo_discount_rate"])
    assert result.loc["item-2", "discount_record_count"] == 1
    assert result.loc["item-3", "promo_discount_rate"] == pytest.approx(0.2)
    assert not np.isinf(
        result["promo_discount_rate"].dropna().to_numpy(dtype=float)
    ).any()
    assert (
        integrate_retail_data.UNDEFINED_RATE_RECORDS["promo_discount_rate"]
        == 1
    )


def test_discount_aggregation_computes_rate_and_record_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Promotion records should collapse to counts and a mean rate."""
    discounts_path = tmp_path / "discounts_history.csv"

    pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-02"],
            "item_id": ["item-2", "item-2"],
            "sale_price_before_promo": [10.0, 10.0],
            "sale_price_time_promo": [8.0, 9.0],
            "promo_type_code": [1, 1],
            "doc_id": [100, 101],
            "number_disc_day": [3, 5],
            "store_id": [1, 1],
        }
    ).to_csv(discounts_path, index=False)

    monkeypatch.setattr(
        integrate_retail_data, "DISCOUNTS_PATH", discounts_path
    )

    result = aggregate_discounts()

    assert len(result) == 1
    assert result.loc[0, "discount_record_count"] == 2
    assert result.loc[0, "promo_price_before"] == pytest.approx(10.0)
    assert result.loc[0, "promo_price_during"] == pytest.approx(8.5)
    assert result.loc[0, "promo_discount_rate"] == pytest.approx(0.15)
    assert result.loc[0, "promo_day_number"] == 5


def test_actual_matrix_indicator_marks_exact_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The actual-matrix indicator should be defined only for exact keys."""
    matrix_path = tmp_path / "actual_matrix.csv"

    pd.DataFrame(
        {
            "item_id": ["item-1", "item-2"],
            "date": ["2024-01-01", "2024-01-02"],
            "store_id": [1, 1],
        }
    ).to_csv(matrix_path, index=False)

    monkeypatch.setattr(
        integrate_retail_data, "ACTUAL_MATRIX_PATH", matrix_path
    )

    result = aggregate_actual_matrix()

    assert len(result) == 2
    assert set(result["matrix_record_flag"]) == {1}
    assert not result.duplicated(subset=KEY_COLUMNS).any()


def test_build_integration_preserves_rows_and_grain(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The pipeline should preserve sales rows and keep channels separate."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    write_sales(raw_dir / "sales_clean.csv")
    write_stores(raw_dir / "stores.csv")
    write_catalog(raw_dir / "catalog.csv")

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "item_id": ["item-1", "item-2"],
            "price": [4.5, 9.0],
            "code": [1, 2],
            "store_id": [1, 1],
        }
    ).to_csv(raw_dir / "price_history.csv", index=False)

    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item-1"],
            "normal_price": [10.0],
            "price": [8.0],
            "quantity": [2.0],
            "store_id": [1],
        }
    ).to_csv(raw_dir / "markdowns.csv", index=False)

    pd.DataFrame(
        {
            "date": ["2024-01-02"],
            "item_id": ["item-2"],
            "sale_price_before_promo": [10.0],
            "sale_price_time_promo": [8.0],
            "promo_type_code": [1],
            "doc_id": [100],
            "number_disc_day": [3],
            "store_id": [1],
        }
    ).to_csv(raw_dir / "discounts_history.csv", index=False)

    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "item_id": ["item-1"],
            "quantity": [5],
            "price_base": [4.5],
            "sum_total": [22.5],
            "store_id": [1],
        }
    ).to_csv(raw_dir / "online.csv", index=False)

    pd.DataFrame(
        {
            "item_id": ["item-1"],
            "date": ["2024-01-01"],
            "store_id": [1],
        }
    ).to_csv(raw_dir / "actual_matrix.csv", index=False)

    monkeypatch.setattr(
        integrate_retail_data, "SALES_PATH", raw_dir / "sales_clean.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "STORES_PATH", raw_dir / "stores.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "CATALOG_PATH", raw_dir / "catalog.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "PRICE_HISTORY_PATH", raw_dir / "price_history.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "MARKDOWNS_PATH", raw_dir / "markdowns.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data,
        "DISCOUNTS_PATH",
        raw_dir / "discounts_history.csv",
    )
    monkeypatch.setattr(
        integrate_retail_data, "ONLINE_PATH", raw_dir / "online.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "ACTUAL_MATRIX_PATH", raw_dir / "actual_matrix.csv"
    )
    monkeypatch.setattr(integrate_retail_data, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(
        integrate_retail_data, "OUTPUT_PATH", processed_dir / "integrated.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data,
        "QUALITY_REPORT_PATH",
        processed_dir / "integration_quality_report.csv",
    )
    monkeypatch.setattr(integrate_retail_data, "CHUNK_SIZE", 2)

    metrics = integrate_retail_data.build_integration()

    assert metrics["sales_rows"] == 3
    assert metrics["output_rows"] == 3
    assert metrics["duplicate_rows"] == 0

    integrated = pd.read_csv(processed_dir / "integrated.csv")

    assert len(integrated) == 3
    assert not integrated.duplicated(subset=KEY_COLUMNS).any()
    assert set(integrated["item_id"]) == {"item-1", "item-2", "item-9"}

    unmatched = integrated.loc[integrated["item_id"] == "item-9"]
    assert len(unmatched) == 1
    assert pd.isna(unmatched.iloc[0]["dept_name"])

    quantities = dict(zip(integrated["item_id"], integrated["quantity"]))
    assert quantities["item-1"] == 10
    assert "online_quantity" in integrated.columns

    online_row = integrated.loc[integrated["item_id"] == "item-1"].iloc[0]
    assert online_row["online_quantity"] == 5

    matrix_row = integrated.loc[integrated["item_id"] == "item-1"].iloc[0]
    assert matrix_row["matrix_record_flag"] == 1
    assert (
        integrated.loc[integrated["item_id"] == "item-9"].iloc[0][
            "matrix_record_flag"
        ]
        == 0
    )

    report = pd.read_csv(processed_dir / "integration_quality_report.csv")
    values = dict(zip(report["metric"], report["value"]))

    assert int(values["sales_rows_read"]) == 3
    assert int(values["integrated_rows_written"]) == 3
    assert int(values["row_count_difference"]) == 0
    assert int(values["unknown_store_rows"]) == 0
    assert int(values["unmatched_catalog_rows"]) == 1
    assert values["date_min"] == "2024-01-01"
    assert values["date_max"] == "2024-01-03"
    assert int(values["unique_items"]) == 3
    assert int(values["unique_stores"]) == 2
    assert float(values["total_demand_quantity"]) == pytest.approx(15.0)
    assert float(values["total_sales_revenue"]) == pytest.approx(88.0)
    assert int(values["undefined_markdown_discount_records"]) == 0
    assert int(values["undefined_promo_discount_rate_records"]) == 0
    assert int(values["promoted_rows_with_undefined_discount_rate"]) == 0


def test_build_integration_rejects_row_multiplication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A non-unique auxiliary key must fail the many-to-one guard."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    write_sales(raw_dir / "sales_clean.csv")
    write_stores(raw_dir / "stores.csv")
    write_catalog(raw_dir / "catalog.csv")

    empty_sources = [
        ("price_history.csv", ["date", "item_id", "price", "code", "store_id"]),
        (
            "markdowns.csv",
            [
                "date",
                "item_id",
                "normal_price",
                "price",
                "quantity",
                "store_id",
            ],
        ),
        (
            "discounts_history.csv",
            [
                "date",
                "item_id",
                "sale_price_before_promo",
                "sale_price_time_promo",
                "promo_type_code",
                "doc_id",
                "number_disc_day",
                "store_id",
            ],
        ),
        (
            "online.csv",
            [
                "date",
                "item_id",
                "quantity",
                "price_base",
                "sum_total",
                "store_id",
            ],
        ),
        ("actual_matrix.csv", ["item_id", "date", "store_id"]),
    ]

    for name, columns in empty_sources:
        pd.DataFrame(columns=columns).to_csv(raw_dir / name, index=False)

    monkeypatch.setattr(
        integrate_retail_data, "SALES_PATH", raw_dir / "sales_clean.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "STORES_PATH", raw_dir / "stores.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "CATALOG_PATH", raw_dir / "catalog.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "PRICE_HISTORY_PATH", raw_dir / "price_history.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "MARKDOWNS_PATH", raw_dir / "markdowns.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data,
        "DISCOUNTS_PATH",
        raw_dir / "discounts_history.csv",
    )
    monkeypatch.setattr(
        integrate_retail_data, "ONLINE_PATH", raw_dir / "online.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data, "ACTUAL_MATRIX_PATH", raw_dir / "actual_matrix.csv"
    )
    monkeypatch.setattr(integrate_retail_data, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(
        integrate_retail_data, "OUTPUT_PATH", processed_dir / "integrated.csv"
    )
    monkeypatch.setattr(
        integrate_retail_data,
        "QUALITY_REPORT_PATH",
        processed_dir / "integration_quality_report.csv",
    )
    monkeypatch.setattr(integrate_retail_data, "CHUNK_SIZE", 2)

    def duplicated_online() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-01"],
                "item_id": ["item-1", "item-1"],
                "store_id": [1, 1],
                "online_quantity": [5, 6],
                "online_sales_value": [22.5, 27.0],
                "online_average_price": [4.5, 4.5],
            }
        )

    monkeypatch.setattr(
        integrate_retail_data, "aggregate_online", duplicated_online
    )

    with pytest.raises(pd.errors.MergeError):
        integrate_retail_data.build_integration()


def test_missing_source_file_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing source file should fail explicitly."""
    monkeypatch.setattr(
        integrate_retail_data,
        "CATALOG_PATH",
        tmp_path / "missing_catalog.csv",
    )

    with pytest.raises(FileNotFoundError):
        aggregate_catalog()