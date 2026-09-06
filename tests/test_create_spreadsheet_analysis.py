"""Tests for the Phase 3 spreadsheet-analysis pipeline."""

import pandas as pd
import pytest
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from scripts.create_spreadsheet_analysis import (
    aggregate_sales,
    create_workbook,
    load_stores,
    table_reference,
)


def test_load_stores(tmp_path):
    """Store lookup data should load with the expected fields."""
    stores_path = tmp_path / "stores.csv"

    dataframe = pd.DataFrame(
        {
            "store_id": [1, 2],
            "division": ["A", "B"],
            "format": ["Large", "Small"],
            "city": ["City A", "City B"],
            "area": [100, 200],
        }
    )

    dataframe.to_csv(stores_path, index=False)

    result = load_stores(stores_path)

    assert list(result.columns) == [
        "store_id",
        "division",
        "format",
        "city",
        "area",
    ]

    assert len(result) == 2


def _make_store_fixture():
    return pd.DataFrame(
        {
            "store_id": [1, 2],
            "division": ["A", "B"],
            "format": ["Large", "Small"],
            "city": ["City A", "City B"],
            "area": [100, 200],
        }
    )


def test_create_workbook_creates_required_sheets(tmp_path):
    """The workbook should contain all Phase 3 analytical sheets."""
    output_path = tmp_path / "analysis.xlsx"

    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_items": [20, 22],
        }
    )

    store_summary = pd.DataFrame(
        {
            "store_id": [1, 2],
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_items": [20, 22],
        }
    )

    item_summary = pd.DataFrame(
        {
            "item_id": ["A", "B"],
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_store_count": [1, 2],
        }
    )

    stores = _make_store_fixture()

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=output_path,
    )

    assert output_path.exists()

    workbook = load_workbook(
        output_path,
        data_only=False,
    )

    expected_sheets = {
        "Workbook_ReadMe",
        "Daily_Analysis",
        "Store_Summary",
        "Item_Summary",
        "Formula_Analysis",
        "Data_Validation",
    }

    assert expected_sheets.issubset(set(workbook.sheetnames))


def test_workbook_contains_required_course_formulas(tmp_path):
    """The workbook should demonstrate course spreadsheet formulas."""
    output_path = tmp_path / "analysis.xlsx"

    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_items": [20],
        }
    )

    store_summary = pd.DataFrame(
        {
            "store_id": [1],
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_items": [20],
        }
    )

    item_summary = pd.DataFrame(
        {
            "item_id": ["A"],
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_store_count": [1],
        }
    )

    stores = pd.DataFrame(
        {
            "store_id": [1],
            "division": ["A"],
            "format": ["Large"],
            "city": ["City A"],
            "area": [100],
        }
    )

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=output_path,
    )

    workbook = load_workbook(
        output_path,
        data_only=False,
    )

    worksheet = workbook["Formula_Analysis"]

    formulas = [
        worksheet["B2"].value,
        worksheet["B3"].value,
        worksheet["B4"].value,
        worksheet["B5"].value,
        worksheet["B6"].value,
        worksheet["B7"].value,
        worksheet["B8"].value,
    ]

    assert any("SUMPRODUCT" in str(formula) for formula in formulas)
    assert any("VLOOKUP" in str(formula) for formula in formulas)


# ---------------------------------------------------------------------------
# New tests: aggregate_sales correctness across chunk boundaries.
#
# These are the tests the original suite was missing -- every bug that was
# found and fixed (nunique overcounting, mean-of-means averaging, Kahan
# summation) lived inside aggregate_sales, and none of the tests above ever
# call it. A regression in that function would pass the whole suite above
# without a single failure.
# ---------------------------------------------------------------------------


def _write_sales_csv(tmp_path):
    """Six rows deliberately arranged so that, with chunksize=2, every
    group (date, store, item) has members split across more than one
    chunk. This is what actually exercises the cross-chunk accumulation
    logic -- a dataset that happens to fit in one chunk would pass even
    with the old overcount/mean-of-means bugs.
    """
    rows = [
        # date,        item, qty, price, sum_total, store
        ("2024-01-01", "A", 5, 10, 50, 1),   # chunk 1
        ("2024-01-01", "B", 3, 20, 60, 1),   # chunk 1
        # chunk 2 (item A repeats on same date, diff store)
        ("2024-01-01", "A", 2, 10, 20, 2),
        # chunk 2 (item A repeats at same store as row 1)
        ("2024-01-02", "A", 1, 30, 30, 1),
        ("2024-01-02", "C", 4, 5, 20, 3),    # chunk 3
        # chunk 3 (item B repeats at same store as row 2)
        ("2024-01-03", "B", 1, 25, 25, 1),
    ]

    dataframe = pd.DataFrame(
        rows,
        columns=["date", "item_id", "quantity",
                 "price_base", "sum_total", "store_id"],
    )

    sales_path = tmp_path / "sales.csv"
    dataframe.to_csv(sales_path, index=False)
    return sales_path


def test_aggregate_sales_is_exact_across_chunk_boundaries(tmp_path):
    """Sums, unique-id counts, and average price must be correct even
    when a single date/store/item's rows are split across several
    chunks -- this is the scenario the old code got wrong."""
    sales_path = _write_sales_csv(tmp_path)

    daily, store_summary, item_summary = aggregate_sales(
        sales_path, chunksize=2
    )

    daily = daily.set_index(daily["date"].dt.strftime("%Y-%m-%d"))

    # 2024-01-01: rows for item A (x2, different stores) + item B (x1)
    row = daily.loc["2024-01-01"]
    assert row["total_quantity"] == pytest.approx(10)          # 5 + 3 + 2
    assert row["total_sales_value"] == pytest.approx(130)      # 50 + 60 + 20
    assert row["average_price"] == pytest.approx(40 / 3)       # (10+20+10)/3
    assert row["active_items"] == 2                             # {A, B}, NOT 3

    # 2024-01-02: item A (repeat) + item C
    row = daily.loc["2024-01-02"]
    assert row["total_quantity"] == pytest.approx(5)            # 1 + 4
    assert row["total_sales_value"] == pytest.approx(50)        # 30 + 20
    assert row["average_price"] == pytest.approx(17.5)          # (30+5)/2
    assert row["active_items"] == 2                              # {A, C}

    store_summary = store_summary.set_index("store_id")

    # store 1: rows 1, 2, 4, 6 -> items {A, B} despite A and B each
    # appearing twice across different chunks
    row = store_summary.loc[1]
    assert row["total_quantity"] == pytest.approx(10)           # 5+3+1+1
    assert row["total_sales_value"] == pytest.approx(165)       # 50+60+30+25
    assert row["average_price"] == pytest.approx(
        85 / 4)        # (10+20+30+25)/4
    # {A, B}, NOT 4
    assert row["active_items"] == 2

    item_summary = item_summary.set_index("item_id")

    # item A: rows 1, 3, 4 across three different chunks -> stores {1, 2}
    row = item_summary.loc["A"]
    assert row["total_quantity"] == pytest.approx(8)            # 5+2+1
    assert row["total_sales_value"] == pytest.approx(100)       # 50+20+30
    assert row["average_price"] == pytest.approx(50 / 3)        # (10+10+30)/3
    # {1, 2}, NOT 3
    assert row["active_store_count"] == 2

    # item B: rows 2, 6, both at store 1, in different chunks -> {1}, not 2
    row = item_summary.loc["B"]
    assert row["active_store_count"] == 1


def test_aggregate_sales_excludes_invalid_dates_from_daily_only(
    tmp_path, capsys
):
    """A row with an unparseable date should be dropped from
    Daily_Analysis but must still be counted in Store_Summary and
    Item_Summary, and the drop should be reported to the user."""
    rows = [
        ("2024-01-01", "A", 5, 10, 50, 1),
        ("not-a-date", "A", 3, 10, 30, 1),
    ]

    dataframe = pd.DataFrame(
        rows,
        columns=["date", "item_id", "quantity",
                 "price_base", "sum_total", "store_id"],
    )

    sales_path = tmp_path / "sales.csv"
    dataframe.to_csv(sales_path, index=False)

    daily, store_summary, item_summary = aggregate_sales(
        sales_path, chunksize=10
    )

    # Only the one valid-date row should show up in Daily_Analysis.
    assert len(daily) == 1
    assert daily.iloc[0]["total_quantity"] == pytest.approx(5)

    # Both rows should still be reflected for store/item -- the bad
    # date shouldn't cause the whole row to vanish from the workbook.
    store_summary = store_summary.set_index("store_id")
    assert store_summary.loc[1]["total_quantity"] == pytest.approx(8)

    item_summary = item_summary.set_index("item_id")
    assert item_summary.loc["A"]["total_quantity"] == pytest.approx(8)

    captured = capsys.readouterr()
    assert "unparseable date" in captured.out


def test_table_reference_handles_more_than_26_columns():
    """table_reference must not break past column Z (the old
    chr(64 + n) approach silently produced garbage beyond 26
    columns)."""
    wide_dataframe = pd.DataFrame(
        [[0] * 30, [0] * 30],
        columns=[f"col_{i}" for i in range(30)],
    )

    reference = table_reference(wide_dataframe)

    assert reference == f"A1:{get_column_letter(30)}3"
    assert reference == "A1:AD3"


def test_daily_sheet_table_has_no_conflicting_autofilter(tmp_path):
    """Regression guard for the 'Removed Feature: AutoFilter / Table'
    corruption: a sheet that gets an Excel Table must not also have a
    manual worksheet-level AutoFilter over the same range."""
    output_path = tmp_path / "analysis.xlsx"

    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_items": [20, 22],
        }
    )
    store_summary = pd.DataFrame(
        {
            "store_id": [1, 2],
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_items": [20, 22],
        }
    )
    item_summary = pd.DataFrame(
        {
            "item_id": ["A", "B"],
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_store_count": [1, 2],
        }
    )
    stores = _make_store_fixture()

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=output_path,
    )

    workbook = load_workbook(output_path, data_only=False)
    daily_sheet = workbook["Daily_Analysis"]

    assert "DailySalesTable" in daily_sheet.tables
    # The Table already carries its own AutoFilter; a worksheet-level
    # one over the same range is what triggered the OOXML corruption.
    assert daily_sheet.auto_filter.ref is None


def test_vlookup_formula_targets_the_selected_store_cell(tmp_path):
    """The VLOOKUP demo must look up the store id the user actually
    selects (D2) against the correct, dynamically computed city
    column -- not a hardcoded/incorrect range like the original
    Store_Summary!A:E / index 4."""
    output_path = tmp_path / "analysis.xlsx"

    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_items": [20],
        }
    )
    store_summary = pd.DataFrame(
        {
            "store_id": [1, 2],
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_items": [20, 22],
        }
    )
    item_summary = pd.DataFrame(
        {
            "item_id": ["A"],
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_store_count": [1],
        }
    )
    stores = _make_store_fixture()

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=output_path,
    )

    workbook = load_workbook(output_path, data_only=False)
    formula_sheet = workbook["Formula_Analysis"]

    # store_output = store_id, total_quantity, total_sales_value,
    # average_price, active_items, division, format, city, area
    # -> 9 columns, city at position 8.
    assert formula_sheet["B7"].value == "=VLOOKUP(D2,Store_Summary!A:I,8,FALSE)"

    # D2 should hold an actual store id from Store_Summary, not a
    # placeholder.
    assert formula_sheet["D2"].value == store_summary["store_id"].iloc[0]


def test_data_validation_uses_bounded_table_references(tmp_path):
    """Regression guard for the whole-column COUNTBLANK/COUNTIF bug:
    these checks must reference the table, not an unbounded column."""
    output_path = tmp_path / "analysis.xlsx"

    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_items": [20],
        }
    )
    store_summary = pd.DataFrame(
        {
            "store_id": [1],
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_items": [20],
        }
    )
    item_summary = pd.DataFrame(
        {
            "item_id": ["A"],
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_store_count": [1],
        }
    )
    stores = pd.DataFrame(
        {
            "store_id": [1],
            "division": ["A"],
            "format": ["Large"],
            "city": ["City A"],
            "area": [100],
        }
    )

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=output_path,
    )

    workbook = load_workbook(output_path, data_only=False)
    validation_sheet = workbook["Data_Validation"]

    assert validation_sheet["B5"].value == "=COUNTBLANK(DailySalesTable[date])"
    assert (
        validation_sheet["B6"].value
        == '=COUNTIF(DailySalesTable[total_quantity],"<0")'
    )


def test_store_selection_dropdown_is_dynamic_not_hardcoded(tmp_path):
    """Regression guard for the hardcoded '1,2,3,4' store list: the
    dropdown's source range must scale with the actual number of
    stores in Store_Summary."""
    output_path = tmp_path / "analysis.xlsx"

    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_items": [20],
        }
    )
    store_summary = pd.DataFrame(
        {
            "store_id": [1, 2],
            "total_quantity": [100.0, 120.0],
            "total_sales_value": [1000.0, 1200.0],
            "average_price": [10.0, 10.0],
            "active_items": [20, 22],
        }
    )
    item_summary = pd.DataFrame(
        {
            "item_id": ["A"],
            "total_quantity": [100.0],
            "total_sales_value": [1000.0],
            "average_price": [10.0],
            "active_store_count": [1],
        }
    )
    stores = _make_store_fixture()

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=output_path,
    )

    workbook = load_workbook(output_path, data_only=False)
    formula_sheet = workbook["Formula_Analysis"]

    validations = list(formula_sheet.data_validations.dataValidation)
    assert len(validations) == 1
    assert validations[0].formula1 == "Store_Summary!$A$2:$A$3"
