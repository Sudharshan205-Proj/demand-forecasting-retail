"""Prepare integrated retail data for time-series forecasting.

The script converts transaction-level integrated retail data into a
date-item-store forecasting grain while preserving chronological order.

It does not create lag features or train forecasting models.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "integrated_retail_data.csv"
)

OUTPUT_DATASET = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "time_series_daily.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"

CHUNK_SIZE = 250_000

REQUIRED_COLUMNS = {
    "date",
    "item_id",
    "quantity",
    "store_id",
}


def validate_columns(columns: list[str]) -> None:
    """Validate the required time-series input columns."""
    missing = REQUIRED_COLUMNS.difference(columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )


def aggregate_daily(
    input_path: Path,
) -> pd.DataFrame:
    """Aggregate integrated sales to date-item-store grain."""
    header = pd.read_csv(input_path, nrows=0)

    validate_columns(header.columns.tolist())

    parts: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        input_path,
        usecols=["date", "item_id", "quantity", "store_id"],
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        chunk["date"] = pd.to_datetime(
            chunk["date"],
            errors="coerce",
        )

        chunk["quantity"] = pd.to_numeric(
            chunk["quantity"],
            errors="coerce",
        )

        if chunk["date"].isna().any():
            raise ValueError("Invalid dates detected.")

        if chunk["quantity"].isna().any():
            raise ValueError("Invalid quantity values detected.")

        grouped = (
            chunk.groupby(
                ["date", "item_id", "store_id"],
                as_index=False,
            )
            .agg(quantity=("quantity", "sum"))
        )

        parts.append(grouped)

    result = (
        pd.concat(parts, ignore_index=True)
        .groupby(
            ["date", "item_id", "store_id"],
            as_index=False,
        )
        .agg(quantity=("quantity", "sum"))
        .sort_values(
            ["item_id", "store_id", "date"]
        )
        .reset_index(drop=True)
    )

    return result


def validate_unique_keys(
    data: pd.DataFrame,
) -> int:
    """Return the number of duplicate date-item-store keys."""
    return int(
        data.duplicated(
            ["date", "item_id", "store_id"]
        ).sum()
    )


def calculate_gap_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate observed temporal gaps by item-store series."""
    records: list[dict[str, object]] = []

    for (item_id, store_id), group in data.groupby(
        ["item_id", "store_id"],
        sort=False,
    ):
        dates = (
            group["date"]
            .drop_duplicates()
            .sort_values()
        )

        if len(dates) < 2:
            maximum_gap = 0
            gap_days = 0
        else:
            differences = dates.diff().dt.days.dropna()

            maximum_gap = int(differences.max())
            gap_days = int(
                (differences - 1)
                .clip(lower=0)
                .sum()
            )

        records.append(
            {
                "item_id": item_id,
                "store_id": store_id,
                "observed_dates": len(dates),
                "date_min": dates.min(),
                "date_max": dates.max(),
                "maximum_gap_days": maximum_gap,
                "missing_intermediate_days": gap_days,
            }
        )

    return pd.DataFrame(records)


def calculate_split_boundaries(
    dates: pd.Series,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Calculate chronological train/validation boundaries."""
    unique_dates = (
        pd.Series(dates)
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    if len(unique_dates) < 3:
        raise ValueError(
            "At least three unique dates are required "
            "for chronological splitting."
        )

    train_index = int(np.floor(len(unique_dates) * 0.70)) - 1
    validation_index = (
        int(np.floor(len(unique_dates) * 0.85)) - 1
    )

    train_end = unique_dates.iloc[
        max(train_index, 0)
    ]

    validation_end = unique_dates.iloc[
        max(validation_index, 1)
    ]

    if validation_end <= train_end:
        raise ValueError(
            "Invalid chronological split boundaries."
        )

    return train_end, validation_end


def assign_split(
    data: pd.DataFrame,
    train_end: pd.Timestamp,
    validation_end: pd.Timestamp,
) -> pd.DataFrame:
    """Assign observations to chronological partitions."""
    result = data.copy()

    result["split"] = np.select(
        [
            result["date"] <= train_end,
            result["date"] <= validation_end,
        ],
        [
            "train",
            "validation",
        ],
        default="test",
    )

    return result


def calculate_split_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize observations by chronological split."""
    return (
        data.groupby("split", as_index=False)
        .agg(
            rows=("quantity", "size"),
            quantity=("quantity", "sum"),
            date_min=("date", "min"),
            date_max=("date", "max"),
        )
        .sort_values(
            "date_min"
        )
        .reset_index(drop=True)
    )


def calculate_quality_report(
    source_path: Path,
    prepared: pd.DataFrame,
    duplicate_keys: int,
    gap_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Create machine-readable preparation-quality checks."""
    source = pd.read_csv(
        source_path,
        usecols=["date", "quantity"],
    )

    source["date"] = pd.to_datetime(
        source["date"],
        errors="coerce",
    )

    source["quantity"] = pd.to_numeric(
        source["quantity"],
        errors="coerce",
    )

    source_quantity = float(
        source["quantity"].sum()
    )

    prepared_quantity = float(
        prepared["quantity"].sum()
    )

    chronological_by_series = all(
        group["date"].is_monotonic_increasing
        for _, group in prepared.groupby(
            ["item_id", "store_id"],
            sort=False,
        )
    )

    maximum_gap = (
        int(gap_summary["maximum_gap_days"].max())
        if not gap_summary.empty
        else 0
    )

    total_missing_intermediate_days = (
        int(
            gap_summary[
                "missing_intermediate_days"
            ].sum()
        )
        if not gap_summary.empty
        else 0
    )

    checks = [
        (
            "source_quantity_equals_prepared_quantity",
            np.isclose(
                source_quantity,
                prepared_quantity,
                rtol=1e-10,
                atol=1e-6,
            ),
            source_quantity,
            prepared_quantity,
        ),
        (
            "duplicate_date_item_store_keys",
            duplicate_keys == 0,
            duplicate_keys,
            0,
        ),
        (
            "chronological_within_item_store_series",
            chronological_by_series,
            chronological_by_series,
            True,
        ),
        (
            "prepared_rows_positive",
            len(prepared) > 0,
            len(prepared),
            ">0",
        ),
        (
            "maximum_observed_gap_days",
            maximum_gap >= 0,
            maximum_gap,
            ">=0",
        ),
        (
            "missing_intermediate_days",
            total_missing_intermediate_days >= 0,
            total_missing_intermediate_days,
            ">=0",
        ),
    ]

    return pd.DataFrame(
        checks,
        columns=[
            "check",
            "passed",
            "actual",
            "expected",
        ],
    )


def write_findings(
    prepared: pd.DataFrame,
    gap_summary: pd.DataFrame,
    split_summary: pd.DataFrame,
    quality_report: pd.DataFrame,
) -> None:
    """Write a concise preparation findings report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "Phase 9 — Time-Series Preparation",
        "",
        f"Prepared rows: {len(prepared)}",
        f"Unique items: {prepared['item_id'].nunique()}",
        f"Unique stores: {prepared['store_id'].nunique()}",
        f"Date minimum: {prepared['date'].min().date()}",
        f"Date maximum: {prepared['date'].max().date()}",
        f"Total quantity: {prepared['quantity'].sum()}",
        "",
        "Chronological split summary:",
    ]

    for row in split_summary.itertuples(index=False):
        lines.append(
            f"- {row.split}: "
            f"rows={row.rows}, "
            f"quantity={row.quantity}, "
            f"date_min={row.date_min.date()}, "
            f"date_max={row.date_max.date()}"
        )

    if not gap_summary.empty:
        lines.extend(
            [
                "",
                "Gap summary:",
                f"- item-store series: {len(gap_summary)}",
                (f"- series with gaps: "
                f"{(gap_summary['missing_intermediate_days'] > 0).sum()}"),
                (f"- total missing intermediate days: "
                f"{gap_summary['missing_intermediate_days'].sum()}"),
            ]
        )

    lines.extend(
        [
            "",
            "Quality checks:",
        ]
    )

    for row in quality_report.itertuples(index=False):
        lines.append(
            f"- {row.check}: "
            f"{'PASS' if row.passed else 'FAIL'}"
        )

    (OUTPUT_DIR / "time_series_findings.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run the time-series preparation workflow."""
    print("Preparing retail data for time-series forecasting...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    prepared = aggregate_daily(INPUT_PATH)

    duplicate_keys = validate_unique_keys(prepared)

    if duplicate_keys != 0:
        raise ValueError(
            f"Duplicate date-item-store keys detected: "
            f"{duplicate_keys}"
        )

    gap_summary = calculate_gap_summary(prepared)

    train_end, validation_end = calculate_split_boundaries(
        prepared["date"]
    )

    prepared = assign_split(
        prepared,
        train_end,
        validation_end,
    )

    split_summary = calculate_split_summary(prepared)

    quality_report = calculate_quality_report(
        INPUT_PATH,
        prepared,
        duplicate_keys,
        gap_summary,
    )

    if not bool(quality_report["passed"].all()):
        failed = quality_report.loc[
            ~quality_report["passed"],
            "check",
        ].tolist()

        raise ValueError(
            f"Time-series quality checks failed: {failed}"
        )

    prepared.to_csv(
        OUTPUT_DATASET,
        index=False,
    )

    gap_summary.to_csv(
        OUTPUT_DIR / "time_series_gap_summary.csv",
        index=False,
    )

    split_summary.to_csv(
        OUTPUT_DIR / "time_series_split_summary.csv",
        index=False,
    )

    quality_report.to_csv(
        OUTPUT_DIR / "time_series_quality_report.csv",
        index=False,
    )

    summary = pd.DataFrame(
        [
            ["prepared_rows", len(prepared)],
            ["unique_items", prepared["item_id"].nunique()],
            ["unique_stores", prepared["store_id"].nunique()],
            ["date_min", prepared["date"].min().date()],
            ["date_max", prepared["date"].max().date()],
            ["total_quantity", prepared["quantity"].sum()],
            ["train_end", train_end.date()],
            ["validation_end", validation_end.date()],
        ],
        columns=["metric", "value"],
    )

    summary.to_csv(
        OUTPUT_DIR / "time_series_summary.csv",
        index=False,
    )

    write_findings(
        prepared,
        gap_summary,
        split_summary,
        quality_report,
    )

    print(
        "Time-series preparation completed successfully."
    )
    print(f"Prepared dataset: {OUTPUT_DATASET}")
    print(
        f"Summary: "
        f"{OUTPUT_DIR / 'time_series_summary.csv'}"
    )
    print(
        f"Quality report: "
        f"{OUTPUT_DIR / 'time_series_quality_report.csv'}"
    )


if __name__ == "__main__":
    main()