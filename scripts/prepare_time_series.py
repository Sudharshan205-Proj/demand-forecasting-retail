"""Prepare integrated retail data for time-series forecasting.

The script converts transaction-level integrated retail data into a
date-item-store forecasting grain while preserving chronological order.

It does not create lag features or train forecasting models.

Design notes
------------
- The integrated source is read once, in chunks, and re-aggregated to the
  forecasting grain. Source row, quantity and date statistics are accumulated
  during the same chunked pass so the source file never has to be read a second
  time.
- Missing observations are preserved as missing. The prepared dataset keeps
  only observed date-item-store records and never fills a gap with zero demand.
- The chronological train/validation/test partitions are computed from unique
  dates only, so no future observation can enter an earlier partition.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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

KEY_COLUMNS = ["date", "item_id", "store_id"]

REQUIRED_COLUMNS = {
    "date",
    "item_id",
    "quantity",
    "store_id",
}

TRAIN_FRACTION = 0.70
VALIDATION_FRACTION = 0.85

SPLIT_ORDER = ["train", "validation", "test"]


def validate_columns(columns: list[str]) -> None:
    """Validate the required time-series input columns."""
    missing = REQUIRED_COLUMNS.difference(columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )


def aggregate_daily(
    input_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Aggregate integrated sales to date-item-store grain.

    The integrated source is streamed in chunks and reduced to one row per
    date-item-store key. Source verification statistics are accumulated inside
    the same pass so the source is never loaded as a whole.

    Returns
    -------
    tuple
        ``(prepared, source_stats)`` where ``prepared`` is the aggregated
        forecasting frame and ``source_stats`` records the source row count,
        source quantity, source date range and within-chunk duplicate count.
    """
    header = pd.read_csv(input_path, nrows=0)

    validate_columns(header.columns.tolist())

    parts: list[pd.DataFrame] = []

    source_rows = 0
    source_quantity = 0.0
    within_chunk_duplicate_keys = 0
    source_date_min: pd.Timestamp | None = None
    source_date_max: pd.Timestamp | None = None

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

        source_rows += len(chunk)
        source_quantity += float(chunk["quantity"].sum())

        within_chunk_duplicate_keys += int(
            chunk.duplicated(subset=KEY_COLUMNS).sum()
        )

        chunk_min = chunk["date"].min()
        chunk_max = chunk["date"].max()

        source_date_min = (
            chunk_min
            if source_date_min is None
            else min(source_date_min, chunk_min)
        )

        source_date_max = (
            chunk_max
            if source_date_max is None
            else max(source_date_max, chunk_max)
        )

        grouped = (
            chunk.groupby(
                KEY_COLUMNS,
                as_index=False,
            )
            .agg(quantity=("quantity", "sum"))
        )

        parts.append(grouped)

    result = (
        pd.concat(parts, ignore_index=True)
        .groupby(
            KEY_COLUMNS,
            as_index=False,
        )
        .agg(quantity=("quantity", "sum"))
        .sort_values(
            ["item_id", "store_id", "date"],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )

    source_stats: dict[str, Any] = {
        "rows": source_rows,
        "quantity": source_quantity,
        "date_min": source_date_min,
        "date_max": source_date_max,
        "within_chunk_duplicate_keys": within_chunk_duplicate_keys,
    }

    return result, source_stats


def validate_unique_keys(
    data: pd.DataFrame,
) -> int:
    """Return the number of duplicate date-item-store keys.

    The aggregation already guarantees a unique key, so this validates the
    aggregation contract rather than the raw source.
    """
    return int(
        data.duplicated(
            KEY_COLUMNS
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
    """Calculate chronological train/validation boundaries.

    The boundaries are derived from unique chronological dates only. The
    clamping guarantees that each of the three partitions holds at least one
    date, which keeps the documented three-date minimum valid.
    """
    unique_dates = (
        pd.Series(dates)
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    count = len(unique_dates)

    if count < 3:
        raise ValueError(
            "At least three unique dates are required "
            "for chronological splitting."
        )

    train_index = int(
        np.floor(count * TRAIN_FRACTION)
    ) - 1

    validation_index = int(
        np.floor(count * VALIDATION_FRACTION)
    ) - 1

    train_index = min(train_index, count - 3)
    validation_index = min(validation_index, count - 2)

    train_index = max(train_index, 0)
    validation_index = max(
        validation_index,
        train_index + 1,
    )

    train_end = unique_dates.iloc[train_index]
    validation_end = unique_dates.iloc[validation_index]

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
    summary = (
        data.groupby("split", as_index=False)
        .agg(
            rows=("quantity", "size"),
            quantity=("quantity", "sum"),
            date_min=("date", "min"),
            date_max=("date", "max"),
        )
    )

    summary["split"] = pd.Categorical(
        summary["split"],
        categories=SPLIT_ORDER,
        ordered=True,
    )

    return (
        summary.sort_values("split")
        .reset_index(drop=True)
    )


def _partition_date_ranges(
    data: pd.DataFrame,
) -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
    """Return the observed date range of each chronological partition."""
    ranges: dict[str, tuple[pd.Timestamp, pd.Timestamp]] = {}

    for split in SPLIT_ORDER:
        subset = data.loc[data["split"] == split, "date"]

        if subset.empty:
            continue

        ranges[split] = (subset.min(), subset.max())

    return ranges


def calculate_quality_report(
    prepared: pd.DataFrame,
    source_stats: dict[str, Any],
    gap_summary: pd.DataFrame,
    duplicate_keys: int,
    source_unchanged: bool,
) -> pd.DataFrame:
    """Create machine-readable preparation-quality checks."""
    prepared_quantity = float(prepared["quantity"].sum())
    source_quantity = float(source_stats["quantity"])

    prepared_date_min = prepared["date"].min()
    prepared_date_max = prepared["date"].max()
    span_days = int(
        (prepared_date_max - prepared_date_min).days
    )

    chronological_by_series = all(
        group["date"].is_monotonic_increasing
        for _, group in prepared.groupby(
            ["item_id", "store_id"],
            sort=False,
        )
    )

    partition_ranges = _partition_date_ranges(prepared)

    partitions_present = set(partition_ranges) == set(
        SPLIT_ORDER
    )

    partitions_ordered = bool(
        partitions_present
        and partition_ranges["train"][1]
        < partition_ranges["validation"][0]
        and partition_ranges["validation"][1]
        < partition_ranges["test"][0]
    )

    split_quantity = float(
        prepared.groupby("split")["quantity"].sum().sum()
    )

    split_rows = int(
        prepared.groupby("split")["quantity"].size().sum()
    )

    quantity_complete = bool(
        prepared["quantity"].notna().all()
        and np.isfinite(prepared["quantity"]).all()
    )

    if gap_summary.empty:
        maximum_gap = 0
        maximum_missing_intermediate_days = 0
    else:
        maximum_gap = int(
            gap_summary["maximum_gap_days"].max()
        )
        maximum_missing_intermediate_days = int(
            gap_summary["missing_intermediate_days"].max()
        )

    source_date_min = source_stats["date_min"]
    source_date_max = source_stats["date_max"]

    dates_within_source_range = bool(
        source_date_min is not None
        and source_date_max is not None
        and prepared_date_min >= source_date_min
        and prepared_date_max <= source_date_max
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
            "prepared_rows_do_not_exceed_source_rows",
            len(prepared) <= int(source_stats["rows"]),
            len(prepared),
            int(source_stats["rows"]),
        ),
        (
            "within_chunk_duplicate_source_keys",
            int(
                source_stats["within_chunk_duplicate_keys"]
            )
            == 0,
            int(source_stats["within_chunk_duplicate_keys"]),
            0,
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
            "quantity_numeric_and_complete",
            quantity_complete,
            quantity_complete,
            True,
        ),
        (
            "prepared_dates_within_source_range",
            dates_within_source_range,
            dates_within_source_range,
            True,
        ),
        (
            "all_partitions_present",
            partitions_present,
            partitions_present,
            True,
        ),
        (
            "partitions_chronological_without_overlap",
            partitions_ordered,
            partitions_ordered,
            True,
        ),
        (
            "split_quantity_reconciles_with_prepared",
            np.isclose(
                split_quantity,
                prepared_quantity,
                rtol=1e-10,
                atol=1e-6,
            ),
            split_quantity,
            prepared_quantity,
        ),
        (
            "split_rows_reconcile_with_prepared",
            split_rows == len(prepared),
            split_rows,
            len(prepared),
        ),
        (
            "maximum_gap_within_observed_span",
            maximum_gap <= span_days,
            maximum_gap,
            span_days,
        ),
        (
            "missing_intermediate_days_within_span",
            maximum_missing_intermediate_days <= span_days,
            maximum_missing_intermediate_days,
            span_days,
        ),
        (
            "source_file_not_modified",
            source_unchanged,
            source_unchanged,
            True,
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


def _format_quantity(value: float) -> str:
    """Format a demand quantity without floating-point artefacts."""
    return f"{value:.3f}"


def write_findings(
    prepared: pd.DataFrame,
    source_stats: dict[str, Any],
    gap_summary: pd.DataFrame,
    split_summary: pd.DataFrame,
    quality_report: pd.DataFrame,
) -> None:
    """Write a concise preparation findings report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if gap_summary.empty:
        series_count = 0
        series_with_gaps = 0
        total_missing_intermediate_days = 0
        maximum_gap = 0
    else:
        series_count = len(gap_summary)
        series_with_gaps = int(
            (
                gap_summary["missing_intermediate_days"] > 0
            ).sum()
        )
        total_missing_intermediate_days = int(
            gap_summary["missing_intermediate_days"].sum()
        )
        maximum_gap = int(
            gap_summary["maximum_gap_days"].max()
        )

    prepared_quantity = float(prepared["quantity"].sum())
    source_quantity = float(source_stats["quantity"])

    lines = [
        "Phase 9 — Time-Series Preparation",
        "",
        f"Prepared rows: {len(prepared):,}",
        f"Unique items: {prepared['item_id'].nunique():,}",
        f"Unique stores: {prepared['store_id'].nunique():,}",
        (
            "Date range: "
            f"{prepared['date'].min().date()} to "
            f"{prepared['date'].max().date()}"
        ),
        (
            "Total quantity: "
            f"{_format_quantity(prepared_quantity)}"
        ),
        "",
        "Source reconciliation:",
        f"- source rows: {int(source_stats['rows']):,}",
        f"- prepared rows: {len(prepared):,}",
        (
            "- rows reduced by aggregation: "
            f"{int(source_stats['rows']) - len(prepared):,}"
        ),
        (
            "- within-chunk duplicate source keys: "
            f"{int(source_stats['within_chunk_duplicate_keys']):,}"
        ),
        (
            "- source quantity: "
            f"{_format_quantity(source_quantity)}"
        ),
        (
            "- prepared quantity: "
            f"{_format_quantity(prepared_quantity)}"
        ),
        (
            "- quantities reconcile: "
            f"{bool(np.isclose(source_quantity, prepared_quantity, rtol=1e-10, atol=1e-6))}"
        ),
        "",
        "Series and gaps:",
        f"- item-store series: {series_count:,}",
        f"- series with gaps: {series_with_gaps:,}",
        (
            "- total missing intermediate days: "
            f"{total_missing_intermediate_days:,}"
        ),
        f"- maximum observed gap (days): {maximum_gap:,}",
        "",
        "Chronological split summary:",
    ]

    for row in split_summary.itertuples(index=False):
        lines.append(
            f"- {row.split}: "
            f"rows={row.rows:,}, "
            f"quantity={_format_quantity(float(row.quantity))}, "
            f"date_min={row.date_min.date()}, "
            f"date_max={row.date_max.date()}"
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

    source_before = INPUT_PATH.stat()

    prepared, source_stats = aggregate_daily(INPUT_PATH)

    duplicate_keys = validate_unique_keys(prepared)

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

    source_after = INPUT_PATH.stat()

    source_unchanged = (
        source_before.st_size == source_after.st_size
        and source_before.st_mtime_ns == source_after.st_mtime_ns
    )

    quality_report = calculate_quality_report(
        prepared,
        source_stats,
        gap_summary,
        duplicate_keys,
        source_unchanged,
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
            ["source_rows", int(source_stats["rows"])],
            ["unique_items", prepared["item_id"].nunique()],
            ["unique_stores", prepared["store_id"].nunique()],
            ["date_min", prepared["date"].min().date()],
            ["date_max", prepared["date"].max().date()],
            [
                "total_quantity",
                _format_quantity(
                    float(prepared["quantity"].sum())
                ),
            ],
            ["item_store_series", len(gap_summary)],
            [
                "series_with_gaps",
                int(
                    (
                        gap_summary[
                            "missing_intermediate_days"
                        ]
                        > 0
                    ).sum()
                ),
            ],
            [
                "missing_intermediate_days",
                int(
                    gap_summary[
                        "missing_intermediate_days"
                    ].sum()
                ),
            ],
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
        source_stats,
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
