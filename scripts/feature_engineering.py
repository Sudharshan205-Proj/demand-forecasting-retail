"""Create leakage-safe features for retail demand forecasting.

The script transforms the Phase 9 time-series dataset into a feature
dataset suitable for later forecasting and machine-learning phases.

Feature groups:
- Calendar features
- Historical demand lags
- Shifted rolling demand statistics
- Series age

The target is `quantity`.

Demand-derived features are calculated from prior observations only.
The current target is never included in its own lag or rolling feature.

The Phase 9 chronological split labels are preserved.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "time_series_daily.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / \
    "processed" / "feature_engineered_daily.csv"

SUMMARY_PATH = PROJECT_ROOT / "data" / \
    "analysis" / "feature_engineering_summary.csv"
QUALITY_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "feature_engineering_quality_report.csv"
)
SPLIT_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "feature_engineering_split_summary.csv"
)
FINDINGS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "feature_engineering_findings.txt"
)

KEY_COLUMNS = ["date", "item_id", "store_id"]
TARGET_COLUMN = "quantity"

REQUIRED_COLUMNS = [
    "date",
    "item_id",
    "store_id",
    "quantity",
    "split",
]


def validate_input_columns(columns: list[str]) -> None:
    """Validate the minimum input schema."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add calendar features derived only from the observation date."""
    frame = frame.copy()

    frame["date"] = pd.to_datetime(frame["date"], errors="raise")

    frame["day_of_week"] = frame["date"].dt.dayofweek
    frame["day_of_month"] = frame["date"].dt.day
    frame["week_of_year"] = frame["date"].dt.isocalendar().week.astype("int16")
    frame["month"] = frame["date"].dt.month
    frame["quarter"] = frame["date"].dt.quarter
    frame["year"] = frame["date"].dt.year
    frame["is_weekend"] = frame["day_of_week"].isin([5, 6]).astype("int8")

    return frame


def add_series_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add historical demand and series-age features."""
    frame = frame.copy()

    frame = frame.sort_values(
        KEY_COLUMNS, kind="mergesort").reset_index(drop=True)

    grouped = frame.groupby(
        ["item_id", "store_id"],
        sort=False,
        observed=True,
    )

    for lag in (1, 7, 14, 28):
        frame[f"lag_{lag}"] = grouped[TARGET_COLUMN].shift(lag)

    previous_quantity = grouped[TARGET_COLUMN].shift(1)

    previous_grouped = previous_quantity.groupby(
        [frame["item_id"], frame["store_id"]],
        sort=False,
        observed=True,
    )

    frame["rolling_mean_7"] = previous_grouped.transform(
        lambda series: series.rolling(window=7, min_periods=1).mean()
    )

    frame["rolling_std_7"] = previous_grouped.transform(
        lambda series: series.rolling(window=7, min_periods=2).std()
    )

    frame["rolling_mean_28"] = previous_grouped.transform(
        lambda series: series.rolling(window=28, min_periods=1).mean()
    )

    frame["rolling_std_28"] = previous_grouped.transform(
        lambda series: series.rolling(window=28, min_periods=2).std()
    )

    first_dates = grouped["date"].transform("min")
    frame["series_age_days"] = (
        frame["date"] - first_dates
    ).dt.days.astype("int32")

    return frame


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create the complete leakage-safe feature matrix."""
    validate_input_columns(frame.columns.tolist())

    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")

    frame = add_calendar_features(frame)
    frame = add_series_features(frame)

    frame = frame.sort_values(KEY_COLUMNS, kind="mergesort")
    frame = frame.reset_index(drop=True)

    return frame


def create_quality_report(frame: pd.DataFrame) -> pd.DataFrame:
    """Create machine-readable quality checks."""
    duplicate_count = int(frame.duplicated(KEY_COLUMNS).sum())

    chronological = True

    for _, group in frame.groupby(
        ["item_id", "store_id"],
        sort=False,
        observed=True,
    ):
        if not group["date"].is_monotonic_increasing:
            chronological = False
            break

    feature_columns = [
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_28",
        "rolling_std_28",
        "series_age_days",
    ]

    report = pd.DataFrame(
        [
            {
                "check": "duplicate_date_item_store_keys",
                "passed": duplicate_count == 0,
                "actual": duplicate_count,
                "expected": 0,
            },
            {
                "check": "chronological_within_item_store_series",
                "passed": chronological,
                "actual": chronological,
                "expected": True,
            },
            {
                "check": "prepared_rows_positive",
                "passed": len(frame) > 0,
                "actual": len(frame),
                "expected": ">0",
            },
            {
                "check": "target_quantity_missing",
                "passed": int(frame[TARGET_COLUMN].isna().sum()) == 0,
                "actual": int(frame[TARGET_COLUMN].isna().sum()),
                "expected": 0,
            },
            {
                "check": "calendar_features_present",
                "passed": all(
                    column in frame.columns
                    for column in [
                        "day_of_week",
                        "day_of_month",
                        "week_of_year",
                        "month",
                        "quarter",
                        "year",
                        "is_weekend",
                    ]
                ),
                "actual": True,
                "expected": True,
            },
            {
                "check": "historical_features_present",
                "passed": all(
                    column in frame.columns for column in feature_columns
                ),
                "actual": True,
                "expected": True,
            },
        ]
    )

    return report


def create_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Create a compact feature-engineering summary."""
    feature_columns = [
        "day_of_week",
        "day_of_month",
        "week_of_year",
        "month",
        "quarter",
        "year",
        "is_weekend",
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_28",
        "rolling_std_28",
        "series_age_days",
    ]

    return pd.DataFrame(
        [
            {
                "metric": "rows",
                "value": len(frame),
            },
            {
                "metric": "unique_items",
                "value": frame["item_id"].nunique(),
            },
            {
                "metric": "unique_stores",
                "value": frame["store_id"].nunique(),
            },
            {
                "metric": "date_min",
                "value": frame["date"].min().date().isoformat(),
            },
            {
                "metric": "date_max",
                "value": frame["date"].max().date().isoformat(),
            },
            {
                "metric": "feature_count",
                "value": len(feature_columns),
            },
            {
                "metric": "target",
                "value": TARGET_COLUMN,
            },
        ]
    )


def create_split_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize the preserved chronological partitions."""
    return (
        frame.groupby("split", dropna=False)
        .agg(
            rows=("quantity", "size"),
            quantity=("quantity", "sum"),
            date_min=("date", "min"),
            date_max=("date", "max"),
        )
        .reset_index()
        .sort_values("date_min")
    )


def write_findings(
    frame: pd.DataFrame,
    quality_report: pd.DataFrame,
) -> None:
    """Write a human-readable feature-engineering findings report."""
    feature_columns = [
        "day_of_week",
        "day_of_month",
        "week_of_year",
        "month",
        "quarter",
        "year",
        "is_weekend",
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_28",
        "rolling_std_28",
        "series_age_days",
    ]

    failed_checks = quality_report.loc[
        ~quality_report["passed"].astype(bool),
        "check",
    ].tolist()

    lines = [
        "Phase 10 — Feature Engineering Findings",
        "",
        f"Prepared rows: {len(frame):,}",
        f"Unique items: {frame['item_id'].nunique():,}",
        f"Unique stores: {frame['store_id'].nunique():,}",
        f"Date range: {frame['date'].min().date()} to {frame['date'].max().date()}",
        f"Target: {TARGET_COLUMN}",
        f"Feature count: {len(feature_columns)}",
        "",
        "Demand-derived features use prior observations only.",
        "Current-day quantity is not included in rolling calculations.",
        "The Phase 9 chronological split labels are preserved.",
        "",
        "Important limitation:",
        "Lag and rolling windows operate over previous observed records.",
        "They are not guaranteed to represent exact calendar-day windows",
        "because Phase 9 identified substantial intermediate-date gaps.",
        "",
    ]

    if failed_checks:
        lines.extend(
            [
                "Failed quality checks:",
                *[f"- {check}" for check in failed_checks],
            ]
        )
    else:
        lines.append("All feature-engineering quality checks passed.")

    FINDINGS_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Run feature engineering and write all Phase 10 artifacts."""
    print("Creating forecasting features...")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_PATH}"
        )

    INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    columns = pd.read_csv(INPUT_PATH, nrows=0).columns.tolist()
    validate_input_columns(columns)

    frame = pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
    )

    prepared = prepare_features(frame)

    prepared.to_csv(
        OUTPUT_PATH,
        index=False,
        float_format="%.12g",
    )

    quality_report = create_quality_report(prepared)
    quality_report.to_csv(QUALITY_PATH, index=False)

    summary = create_summary(prepared)
    summary.to_csv(SUMMARY_PATH, index=False)

    split_summary = create_split_summary(prepared)
    split_summary.to_csv(SPLIT_PATH, index=False)

    write_findings(prepared, quality_report)

    if not bool(quality_report["passed"].all()):
        raise RuntimeError(
            "One or more feature-engineering quality checks failed."
        )

    print("Feature engineering completed successfully.")
    print(f"Prepared dataset: {OUTPUT_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Quality report: {QUALITY_PATH}")


if __name__ == "__main__":
    main()
