"""Validate and clean the retail sales dataset.

The raw sales CSV is intentionally processed in chunks because it contains
millions of records. The raw file is never modified.

The script produces:
- a cleaned sales CSV,
- a row-level quality summary,
- a cleaning summary,
- and a validation report.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

SALES_PATH = RAW_DATA_DIR / "sales.csv"
STORES_PATH = RAW_DATA_DIR / "stores.csv"

CLEAN_SALES_PATH = PROCESSED_DATA_DIR / "sales_clean.csv"
QUALITY_REPORT_PATH = PROCESSED_DATA_DIR / "data_quality_report.csv"
CLEANING_SUMMARY_PATH = PROCESSED_DATA_DIR / "cleaning_summary.csv"

CHUNK_SIZE = 250_000

REQUIRED_COLUMNS = [
    "date",
    "item_id",
    "quantity",
    "price_base",
    "sum_total",
    "store_id",
]


def validate_required_columns(columns: list[str]) -> None:
    """Raise an error when required sales columns are missing."""
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


def load_store_ids(path: Path) -> set[str]:
    """Load valid store identifiers from the stores lookup."""
    stores = pd.read_csv(
        path,
        usecols=["store_id"],
        dtype={"store_id": "string"},
    )

    return set(
        stores["store_id"]
        .dropna()
        .astype(str)
        .str.strip()
    )


def initialise_quality_metrics() -> dict[str, int | float]:
    """Create counters used by the quality report."""
    return {
        "rows_read": 0,
        "rows_written": 0,
        "missing_required_rows": 0,
        "duplicate_rows": 0,
        "invalid_date_rows": 0,
        "negative_quantity_rows": 0,
        "negative_price_rows": 0,
        "negative_revenue_rows": 0,
        "unknown_store_rows": 0,
        "revenue_mismatch_rows": 0,
        "potential_outlier_quantity_rows": 0,
    }


def update_quality_metrics(
    metrics: dict[str, int | float],
    chunk: pd.DataFrame,
    valid_store_ids: set[str],
) -> pd.DataFrame:
    """Validate a chunk and return the rows that pass cleaning rules."""
    metrics["rows_read"] += len(chunk)

    missing_required = chunk[REQUIRED_COLUMNS].isna().any(axis=1)
    metrics["missing_required_rows"] += int(missing_required.sum())

    duplicate_mask = chunk.duplicated(keep="first")
    metrics["duplicate_rows"] += int(duplicate_mask.sum())

    chunk["date"] = pd.to_datetime(
        chunk["date"],
        errors="coerce",
    )

    invalid_dates = chunk["date"].isna()
    metrics["invalid_date_rows"] += int(invalid_dates.sum())

    chunk["item_id"] = chunk["item_id"].astype("string").str.strip()
    chunk["store_id"] = chunk["store_id"].astype("string").str.strip()

    chunk["quantity"] = pd.to_numeric(
        chunk["quantity"],
        errors="coerce",
    )

    chunk["price_base"] = pd.to_numeric(
        chunk["price_base"],
        errors="coerce",
    )

    chunk["sum_total"] = pd.to_numeric(
        chunk["sum_total"],
        errors="coerce",
    )

    negative_quantity = chunk["quantity"] < 0
    negative_price = chunk["price_base"] < 0
    negative_revenue = chunk["sum_total"] < 0

    metrics["negative_quantity_rows"] += int(
        negative_quantity.fillna(False).sum()
    )
    metrics["negative_price_rows"] += int(
        negative_price.fillna(False).sum()
    )
    metrics["negative_revenue_rows"] += int(
        negative_revenue.fillna(False).sum()
    )

    unknown_store = (
        ~chunk["store_id"].isin(valid_store_ids)
        & chunk["store_id"].notna()
    )
    metrics["unknown_store_rows"] += int(unknown_store.sum())

    expected_revenue = chunk["quantity"] * chunk["price_base"]

    revenue_mismatch = (
        expected_revenue.notna()
        & chunk["sum_total"].notna()
        & ~expected_revenue.sub(chunk["sum_total"]).abs().le(0.01)
    )

    metrics["revenue_mismatch_rows"] += int(
        revenue_mismatch.sum()
    )

    quantity_outlier = chunk["quantity"] > chunk["quantity"].quantile(0.99)
    metrics["potential_outlier_quantity_rows"] += int(
        quantity_outlier.fillna(False).sum()
    )

    invalid_numeric = (
        chunk["quantity"].isna()
        | chunk["price_base"].isna()
        | chunk["sum_total"].isna()
    )

    invalid_row = (
        missing_required
        | duplicate_mask
        | invalid_dates
        | negative_quantity
        | negative_price
        | negative_revenue
        | unknown_store
        | invalid_numeric
    )

    cleaned = chunk.loc[~invalid_row, REQUIRED_COLUMNS].copy()

    return cleaned


def write_quality_report(
    metrics: dict[str, int | float],
    output_path: Path,
) -> None:
    """Write the quality metrics as a CSV report."""
    rows = [
        {
            "metric": metric,
            "value": value,
        }
        for metric, value in metrics.items()
    ]

    pd.DataFrame(rows).to_csv(
        output_path,
        index=False,
    )


def write_cleaning_summary(
    metrics: dict[str, int | float],
    output_path: Path,
) -> None:
    """Write a human-readable cleaning action summary."""
    rows_removed = (
        int(metrics["missing_required_rows"])
        + int(metrics["duplicate_rows"])
        + int(metrics["invalid_date_rows"])
        + int(metrics["negative_quantity_rows"])
        + int(metrics["negative_price_rows"])
        + int(metrics["negative_revenue_rows"])
        + int(metrics["unknown_store_rows"])
    )

    summary = pd.DataFrame(
        [
            {
                "action": "Rows read",
                "count": metrics["rows_read"],
                "reason": "All raw sales records inspected.",
            },
            {
                "action": "Rows written",
                "count": metrics["rows_written"],
                "reason": "Records passing documented cleaning rules.",
            },
            {
                "action": "Rows removed by quality rules",
                "count": rows_removed,
                "reason": "Records failing one or more validity checks.",
            },
            {
                "action": "Potential quantity outliers",
                "count": metrics["potential_outlier_quantity_rows"],
                "reason": "Reported for investigation; not removed automatically.",
            },
            {
                "action": "Revenue mismatches",
                "count": metrics["revenue_mismatch_rows"],
                "reason": "Reported because discounts/rounding may explain differences.",
            },
        ]
    )

    summary.to_csv(
        output_path,
        index=False,
    )


def clean_sales() -> dict[str, int | float]:
    """Clean the sales dataset and return quality metrics."""
    if not SALES_PATH.exists():
        raise FileNotFoundError(
            f"Sales file not found: {SALES_PATH}"
        )

    if not STORES_PATH.exists():
        raise FileNotFoundError(
            f"Stores file not found: {STORES_PATH}"
        )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    valid_store_ids = load_store_ids(STORES_PATH)
    metrics = initialise_quality_metrics()

    first_chunk = True

    for chunk in pd.read_csv(
        SALES_PATH,
        chunksize=CHUNK_SIZE,
    ):
        validate_required_columns(chunk.columns.tolist())

        cleaned = update_quality_metrics(
            metrics,
            chunk,
            valid_store_ids,
        )

        cleaned.to_csv(
            CLEAN_SALES_PATH,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )

        metrics["rows_written"] += len(cleaned)
        first_chunk = False

    write_quality_report(
        metrics,
        QUALITY_REPORT_PATH,
    )

    write_cleaning_summary(
        metrics,
        CLEANING_SUMMARY_PATH,
    )

    return metrics


def main() -> None:
    """Run the Phase 5 sales cleaning pipeline."""
    print("Validating and cleaning sales data...")

    metrics = clean_sales()

    print("Sales cleaning completed successfully.")
    print(f"Rows read: {metrics['rows_read']:,}")
    print(f"Rows written: {metrics['rows_written']:,}")
    print(f"Quality report: {QUALITY_REPORT_PATH}")
    print(f"Cleaning summary: {CLEANING_SUMMARY_PATH}")
    print(f"Clean dataset: {CLEAN_SALES_PATH}")


if __name__ == "__main__":
    main()
