"""Create the Phase 3 spreadsheet-analysis workbook.

The script reads the large raw sales dataset in chunks so that the
entire 7.4M-row file does not need to be loaded into memory at once.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_SALES_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"
RAW_STORES_PATH = PROJECT_ROOT / "data" / "raw" / "stores.csv"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "retail_spreadsheet_analysis.xlsx"
)

CHUNK_SIZE = 250_000


def _new_accumulator(extra_key: str) -> dict:
    """Return a fresh running-aggregate record for one group.

    quantity / sales_value / price_sum are tracked as Kahan
    (total, compensation) pairs rather than plain floats -- see
    `_kahan_add` for why.
    """
    return {
        "quantity": (0.0, 0.0),
        "sales_value": (0.0, 0.0),
        "price_sum": (0.0, 0.0),
        "price_count": 0,
        extra_key: set(),
    }


def _kahan_add(total: float, compensation: float, value: float) -> tuple[float, float]:
    """Add `value` to a running `total` using Kahan summation.

    Plain `total += value`, repeated once per chunk for every group,
    is ordinary floating-point addition: each addition can lose a
    few low-order bits, and that rounding error compounds as more
    chunks are added. The error grows with the number of chunks, and
    gets worse the more a group's per-chunk sums differ in
    magnitude (e.g. a date with many small transactions plus a few
    very large ones).

    Kahan summation keeps a small running "compensation" term that
    captures the bits lost on each addition and feeds them back in
    on the next one, so the accumulated error stays at roughly one
    machine epsilon regardless of how many chunks are summed --
    important here since the whole point of chunking is to keep
    adding more, smaller pieces over the life of a run.
    """
    y = value - compensation
    t = total + y
    new_compensation = (t - total) - y
    return t, new_compensation


def _accumulate(acc: dict, group: pd.DataFrame) -> None:
    """Fold one chunk's group of rows into a running accumulator."""
    quantity_total, quantity_comp = acc["quantity"]
    acc["quantity"] = _kahan_add(
        quantity_total, quantity_comp, group["quantity"].sum()
    )

    sales_total, sales_comp = acc["sales_value"]
    acc["sales_value"] = _kahan_add(
        sales_total, sales_comp, group["sum_total"].sum()
    )

    price_total, price_comp = acc["price_sum"]
    acc["price_sum"] = _kahan_add(
        price_total, price_comp, group["price_base"].sum()
    )

    acc["price_count"] += int(group["price_base"].count())


def aggregate_sales(
    sales_path: Path,
    chunksize: int = CHUNK_SIZE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Aggregate raw sales into spreadsheet-sized analytical datasets.

    Uses running accumulators keyed by date / store_id / item_id so
    that sums are exact and "unique count" fields (active items per
    date, active stores per item, etc.) are true unique counts across
    the whole file rather than an overcounted sum of per-chunk
    unique counts.
    """
    required_columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]

    daily_acc: dict = defaultdict(lambda: _new_accumulator("items"))
    store_acc: dict = defaultdict(lambda: _new_accumulator("items"))
    item_acc: dict = defaultdict(lambda: _new_accumulator("stores"))

    dropped_invalid_dates = 0

    for chunk in pd.read_csv(
        sales_path,
        usecols=required_columns,
        chunksize=chunksize,
    ):
        chunk["date"] = pd.to_datetime(
            chunk["date"], errors="coerce"
        ).dt.normalize()

        invalid_mask = chunk["date"].isna()
        dropped_invalid_dates += int(invalid_mask.sum())

        # --- daily accumulation (rows with an unparseable date are
        # excluded here, same as they would be excluded by a
        # groupby("date") with dropna=True) ---
        valid_chunk = chunk.loc[~invalid_mask]
        for date, group in valid_chunk.groupby("date", sort=False):
            acc = daily_acc[date]
            _accumulate(acc, group)
            acc["items"].update(group["item_id"].unique())

        # --- store accumulation ---
        for store_id, group in chunk.groupby("store_id", sort=False):
            acc = store_acc[store_id]
            _accumulate(acc, group)
            acc["items"].update(group["item_id"].unique())

        # --- item accumulation ---
        for item_id, group in chunk.groupby("item_id", sort=False):
            acc = item_acc[item_id]
            _accumulate(acc, group)
            acc["stores"].update(group["store_id"].unique())

    if dropped_invalid_dates:
        print(
            f"Warning: {dropped_invalid_dates:,} rows had an "
            "unparseable date and were excluded from Daily_Analysis "
            "(they are still included in Store_Summary / Item_Summary)."
        )

    def _total(acc: dict, key: str) -> float:
        """Read the running Kahan total (ignoring the compensation term)."""
        return acc[key][0]

    def _mean_price(acc: dict):
        price_count = acc["price_count"]
        return _total(acc, "price_sum") / price_count if price_count else None

    daily_combined = pd.DataFrame(
        [
            {
                "date": date,
                "total_quantity": _total(acc, "quantity"),
                "total_sales_value": _total(acc, "sales_value"),
                "average_price": _mean_price(acc),
                "active_items": len(acc["items"]),
            }
            for date, acc in daily_acc.items()
        ]
    ).sort_values("date").reset_index(drop=True)

    store_combined = pd.DataFrame(
        [
            {
                "store_id": store_id,
                "total_quantity": _total(acc, "quantity"),
                "total_sales_value": _total(acc, "sales_value"),
                "average_price": _mean_price(acc),
                "active_items": len(acc["items"]),
            }
            for store_id, acc in store_acc.items()
        ]
    ).sort_values("store_id").reset_index(drop=True)

    item_combined = pd.DataFrame(
        [
            {
                "item_id": item_id,
                "total_quantity": _total(acc, "quantity"),
                "total_sales_value": _total(acc, "sales_value"),
                "average_price": _mean_price(acc),
                "active_store_count": len(acc["stores"]),
            }
            for item_id, acc in item_acc.items()
        ]
    ).sort_values("total_quantity", ascending=False).reset_index(drop=True)

    return daily_combined, store_combined, item_combined


def load_stores(stores_path: Path) -> pd.DataFrame:
    """Load the small store lookup table."""
    columns = [
        "store_id",
        "division",
        "format",
        "city",
        "area",
    ]

    return pd.read_csv(stores_path, usecols=columns).sort_values(
        "store_id"
    )


def add_table(worksheet, reference: str, name: str) -> None:
    """Add an Excel table with filtering and styling."""
    table = Table(displayName=name, ref=reference)

    style = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )

    table.tableStyleInfo = style
    worksheet.add_table(table)


def table_reference(dataframe: pd.DataFrame) -> str:
    """Build an 'A1:<last col><last row>' reference for a dataframe's
    written range, handling more than 26 columns correctly."""
    last_column_letter = get_column_letter(dataframe.shape[1])
    last_row = dataframe.shape[0] + 1  # +1 for the header row
    return f"A1:{last_column_letter}{last_row}"


def write_dataframe(
    worksheet,
    dataframe: pd.DataFrame,
    start_row: int = 1,
) -> None:
    """Write a DataFrame into a worksheet."""
    for column_index, column_name in enumerate(
        dataframe.columns,
        start=1,
    ):
        worksheet.cell(
            row=start_row,
            column=column_index,
            value=column_name,
        )

    for row_offset, row in enumerate(
        dataframe.itertuples(index=False),
        start=1,
    ):
        for column_index, value in enumerate(row, start=1):
            if pd.isna(value):
                value = None

            worksheet.cell(
                row=start_row + row_offset,
                column=column_index,
                value=value,
            )


def format_worksheet(worksheet) -> None:
    """Apply standard spreadsheet usability settings.

    Note: this does NOT set worksheet.auto_filter.ref. Sheets that
    get an Excel Table (via add_table) already have filtering built
    into the table itself -- a Table's range already carries its own
    AutoFilter definition. Also setting a worksheet-level AutoFilter
    over the same range produces two overlapping AutoFilter
    definitions in the saved .xlsx, which is invalid OOXML: Excel
    detects the corruption on open and silently strips out the
    Table/AutoFilter features ("Removed Feature: AutoFilter ...",
    "Removed Feature: Table ..."). If a sheet does NOT get a table,
    call worksheet.auto_filter.ref = worksheet.dimensions on it
    separately after this function returns.
    """
    worksheet.freeze_panes = "A2"

    for column in worksheet.columns:
        maximum_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            value = cell.value

            if value is not None:
                maximum_length = max(
                    maximum_length,
                    len(str(value)),
                )

        worksheet.column_dimensions[column_letter].width = min(
            maximum_length + 2,
            30,
        )


def create_workbook(
    daily: pd.DataFrame,
    store_summary: pd.DataFrame,
    item_summary: pd.DataFrame,
    stores: pd.DataFrame,
    output_path: Path,
) -> None:
    """Create the complete Phase 3 Excel workbook."""
    workbook = Workbook()

    readme = workbook.active
    readme.title = "Workbook_ReadMe"

    readme_rows = [
        ["Retail Demand Forecasting — Phase 3"],
        ["Purpose", "Spreadsheet-based analysis of historical sales."],
        [
            "Source",
            "data/raw/sales.csv",
        ],
        [
            "Important",
            "Raw transaction data is aggregated before entering Excel.",
        ],
        [
            "Course techniques",
            "Sorting, filtering, formulas, VLOOKUP, SUMPRODUCT, ",
            "data validation, conditional formatting, pivot-style summaries.",
        ],
        [
            "Forecasting note",
            "This workbook supports historical analysis. ",
            "Forecasting is performed in later phases.",
        ],
        [
            "Data integrity",
            "Raw source files are not modified.",
        ],
    ]

    for row_index, row in enumerate(readme_rows, start=1):
        for column_index, value in enumerate(row, start=1):
            readme.cell(
                row=row_index,
                column=column_index,
                value=value,
            )

    # Daily analysis
    daily_sheet = workbook.create_sheet("Daily_Analysis")

    daily_output = daily.copy()
    daily_output["day_of_week"] = daily_output["date"].dt.day_name()
    daily_output["month"] = daily_output["date"].dt.month
    daily_output["year"] = daily_output["date"].dt.year

    write_dataframe(daily_sheet, daily_output)
    format_worksheet(daily_sheet)

    if daily_output.shape[0] > 0:
        add_table(
            daily_sheet,
            table_reference(daily_output),
            "DailySalesTable",
        )

    # Store analysis
    store_sheet = workbook.create_sheet("Store_Summary")

    store_output = store_summary.merge(
        stores,
        on="store_id",
        how="left",
    )

    write_dataframe(store_sheet, store_output)
    format_worksheet(store_sheet)

    if not store_output.empty:
        add_table(
            store_sheet,
            table_reference(store_output),
            "StoreSummaryTable",
        )

    # Item analysis
    item_sheet = workbook.create_sheet("Item_Summary")

    write_dataframe(item_sheet, item_summary)
    format_worksheet(item_sheet)

    if not item_summary.empty:
        add_table(
            item_sheet,
            table_reference(item_summary),
            "ItemSummaryTable",
        )

        quantity_column = "B"

        item_sheet.conditional_formatting.add(
            f"{quantity_column}2:{quantity_column}{item_summary.shape[0] + 1}",
            ColorScaleRule(
                start_type="min",
                start_color="FFFFFF",
                mid_type="percentile",
                mid_value=50,
                mid_color="FFFF00",
                end_type="max",
                end_color="63BE7B",
            ),
        )

    # Formula demonstrations
    formula_sheet = workbook.create_sheet("Formula_Analysis")

    # store_output column order is:
    # store_id, total_quantity, total_sales_value, average_price,
    # active_items, division, format, city, area
    store_last_column = get_column_letter(store_output.shape[1])
    city_column_index = list(store_output.columns).index("city") + 1

    formula_rows = [
        ["Spreadsheet Technique", "Example / Result"],
        [
            "SUM",
            "=SUM(Daily_Analysis!B2:B100)",
        ],
        [
            "AVERAGE",
            "=AVERAGE(Daily_Analysis!D2:D100)",
        ],
        [
            "MAX",
            "=MAX(Daily_Analysis!B2:B100)",
        ],
        [
            "MIN",
            "=MIN(Daily_Analysis!B2:B100)",
        ],
        [
            "SUMPRODUCT",
            ("=SUMPRODUCT(Daily_Analysis!B2:B100,"
            "Daily_Analysis!D2:D100)"),
        ],
        [
            "VLOOKUP (city by store_id)",
            (f"=VLOOKUP(D2,Store_Summary!A:{store_last_column},"
            f"{city_column_index},FALSE)"),
        ],
        [
            "COUNTIF",
            '=COUNTIF(Daily_Analysis!F:F,"Monday")',
        ],
    ]

    for row_index, row in enumerate(formula_rows, start=1):
        for column_index, value in enumerate(row, start=1):
            formula_sheet.cell(
                row=row_index,
                column=column_index,
                value=value,
            )

    formula_sheet.freeze_panes = "A2"

    # Interactive selection demonstrating data validation. The list
    # source references the actual Store_Summary store_id column
    # instead of a hardcoded set of ids, so it stays correct if the
    # store list changes.
    formula_sheet["D1"] = "Store Selection"
    formula_sheet["D2"] = (
        store_output["store_id"].iloc[0] if not store_output.empty else None
    )

    validation = DataValidation(
        type="list",
        formula1=f"Store_Summary!$A$2:$A${store_output.shape[0] + 1}",
        allow_blank=False,
    )

    validation.error = "Select a valid store ID."
    validation.errorTitle = "Invalid Store"
    validation.prompt = "Select a store ID from the list."
    validation.promptTitle = "Store Selection"

    formula_sheet.add_data_validation(validation)
    validation.add(formula_sheet["D2"])

    # Validation sheet — bounded to the actual table ranges instead
    # of scanning whole (effectively unbounded) columns.
    validation_sheet = workbook.create_sheet("Data_Validation")

    validation_rows = [
        ["Check", "Value"],
        [
            "Daily records",
            "=COUNTA(Daily_Analysis!A:A)-1",
        ],
        [
            "Store records",
            "=COUNTA(Store_Summary!A:A)-1",
        ],
        [
            "Item records",
            "=COUNTA(Item_Summary!A:A)-1",
        ],
        [
            "Missing daily dates",
            "=COUNTBLANK(DailySalesTable[date])",
        ],
        [
            "Negative daily quantity records",
            '=COUNTIF(DailySalesTable[total_quantity],"<0")',
        ],
    ]

    for row_index, row in enumerate(validation_rows, start=1):
        for column_index, value in enumerate(row, start=1):
            validation_sheet.cell(
                row=row_index,
                column=column_index,
                value=value,
            )

    validation_sheet.freeze_panes = "A2"

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook.save(output_path)


def main() -> None:
    """Run the workbook-generation pipeline."""
    if not RAW_SALES_PATH.exists():
        raise FileNotFoundError(
            f"Required raw sales file was not found: {RAW_SALES_PATH}"
        )

    if not RAW_STORES_PATH.exists():
        raise FileNotFoundError(
            f"Required stores file was not found: {RAW_STORES_PATH}"
        )

    daily, store_summary, item_summary = aggregate_sales(
        RAW_SALES_PATH
    )

    stores = load_stores(RAW_STORES_PATH)

    create_workbook(
        daily=daily,
        store_summary=store_summary,
        item_summary=item_summary,
        stores=stores,
        output_path=OUTPUT_PATH,
    )

    print("Spreadsheet analysis workbook created successfully.")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Daily records: {len(daily):,}")
    print(f"Store records: {len(store_summary):,}")
    print(f"Item records: {len(item_summary):,}")


if __name__ == "__main__":
    main()
