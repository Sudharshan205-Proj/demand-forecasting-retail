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

Design notes
------------
- Lag and rolling windows operate over previous *observed records*. Because
  Phase 9 identified substantial intermediate-date gaps, `lag_7` is the
  seventh previous observed record rather than necessarily the observation
  exactly seven calendar days earlier. This is a documented limitation.
- The feature matrix is reconciled against the Phase 9 input: rows, keys,
  target and split labels are compared, and the quantity total is reconciled.
- A per-feature completeness artifact records the missing-value structure of
  the lag and rolling features at each series start.
- Dates are parsed with an explicit ISO format so the calendar features are
  built deterministically: an invalid or ambiguous date raises rather than
  being inferred element by element.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
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
FEATURE_SUMMARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "feature_engineering_feature_summary.csv"
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

CALENDAR_FEATURES = [
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month",
    "quarter",
    "year",
    "is_weekend",
]

HISTORICAL_FEATURES = [
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

FEATURE_COLUMNS = CALENDAR_FEATURES + HISTORICAL_FEATURES

SPLIT_ORDER = ["train", "validation", "test"]


def validate_input_columns(columns: list[str]) -> None:
    """Validate the minimum input schema."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add calendar features derived only from the observation date.

    The date is parsed with an explicit ISO format. This keeps calendar
    derivation deterministic and makes an invalid date raise immediately
    instead of silently falling back to per-element inference.
    """
    frame = frame.copy()

    frame["date"] = pd.to_datetime(
        frame["date"],
        errors="raise",
        format="%Y-%m-%d",
    )

    frame["day_of_week"] = frame["date"].dt.dayofweek
    frame["day_of_month"] = frame["date"].dt.day
    frame["week_of_year"] = frame["date"].dt.isocalendar().week.astype("int16")
    frame["month"] = frame["date"].dt.month
    frame["quarter"] = frame["date"].dt.quarter
    frame["year"] = frame["date"].dt.year
    frame["is_weekend"] = frame["day_of_week"].isin([5, 6]).astype("int8")

    return frame


def _rolling_statistic(
    series: pd.Series,
    item_ids: pd.Series,
    store_ids: pd.Series,
    window: int,
    min_periods: int,
    method: str,
) -> pd.Series:
    """Compute a grouped rolling statistic over prior observations.

    Uses pandas' compiled grouped-rolling implementation rather than a
    Python-level ``transform`` lambda; both produce identical values, but
    the compiled path is roughly an order of magnitude faster on the full
    dataset. The result is returned in the original row order.
    """
    grouped = series.groupby(
        [item_ids, store_ids],
        sort=False,
        observed=True,
    ).rolling(window=window, min_periods=min_periods)

    result = getattr(grouped, method)()
    result.index = result.index.droplevel([0, 1])

    return result.sort_index()


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

    item_ids = frame["item_id"]
    store_ids = frame["store_id"]

    frame["rolling_mean_7"] = _rolling_statistic(
        previous_quantity, item_ids, store_ids, 7, 1, "mean"
    )
    frame["rolling_std_7"] = _rolling_statistic(
        previous_quantity, item_ids, store_ids, 7, 2, "std"
    )
    frame["rolling_mean_28"] = _rolling_statistic(
        previous_quantity, item_ids, store_ids, 28, 1, "mean"
    )
    frame["rolling_std_28"] = _rolling_statistic(
        previous_quantity, item_ids, store_ids, 28, 2, "std"
    )

    first_dates = grouped["date"].transform("min")
    frame["series_age_days"] = (
        frame["date"] - first_dates
    ).dt.days.astype("int32")

    return frame


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create the complete leakage-safe feature matrix.

    The frame is copied once for the calendar features and once for the
    historical features; the historical step also performs the final
    chronological ordering, so no further re-sort is required.
    """
    validate_input_columns(frame.columns.tolist())

    prepared = add_calendar_features(frame)
    prepared = add_series_features(prepared)

    return prepared


def _align_to_keys(frame: pd.DataFrame) -> pd.DataFrame:
    """Order the key, target and split columns by the canonical key."""
    view = frame.loc[:, KEY_COLUMNS + [TARGET_COLUMN, "split"]]

    return (
        view.sort_values(KEY_COLUMNS, kind="mergesort")
        .reset_index(drop=True)
    )


def create_quality_report(
    frame: pd.DataFrame,
    source: pd.DataFrame,
) -> pd.DataFrame:
    """Create machine-readable quality checks.

    The report reconciles the engineered frame against the Phase 9 source
    (rows, keys, target and split labels) and verifies the leakage contract
    of the historical features. The quantity reconciliation renders its
    figures without floating-point artefacts, after the comparisons that
    decide pass/fail have already been evaluated numerically.
    """
    aligned = _align_to_keys(frame)
    source_aligned = _align_to_keys(source)

    rows = len(frame)
    source_rows = len(source)

    rows_match = rows == source_rows

    keys_match = bool(
        rows_match
        and (aligned["date"] == source_aligned["date"]).all()
        and (aligned["item_id"] == source_aligned["item_id"]).all()
        and (aligned["store_id"] == source_aligned["store_id"]).all()
    )

    target_preserved = bool(
        keys_match
        and np.allclose(
            source_aligned[TARGET_COLUMN].to_numpy(dtype=float),
            aligned[TARGET_COLUMN].to_numpy(dtype=float),
            rtol=1e-9,
            atol=1e-9,
            equal_nan=True,
        )
    )

    split_preserved = bool(
        keys_match
        and (source_aligned["split"] == aligned["split"]).all()
    )

    quantity_reconciled = bool(
        np.isclose(
            float(source[TARGET_COLUMN].sum()),
            float(frame[TARGET_COLUMN].sum()),
            rtol=1e-10,
            atol=1e-6,
        )
    )

    duplicate_count = int(frame.duplicated(KEY_COLUMNS).sum())

    chronological = all(
        group["date"].is_monotonic_increasing
        for _, group in frame.groupby(
            ["item_id", "store_id"],
            sort=False,
            observed=True,
        )
    )

    target_missing = int(frame[TARGET_COLUMN].isna().sum())

    calendar_present = sum(
        column in frame.columns for column in CALENDAR_FEATURES
    )

    historical_present = sum(
        column in frame.columns for column in HISTORICAL_FEATURES
    )

    series_group = frame.groupby(
        ["item_id", "store_id"],
        sort=False,
        observed=True,
    )

    first_observation = (
        series_group["date"].transform("min") == frame["date"]
    )

    if (
        "lag_1" in frame.columns
        and "rolling_mean_7" in frame.columns
    ):
        first_observation_has_no_history = bool(
            frame.loc[
                first_observation,
                ["lag_1", "rolling_mean_7"],
            ]
            .isna()
            .all()
            .all()
        )
    else:
        first_observation_has_no_history = False

    expected_lag_1 = series_group[TARGET_COLUMN].shift(1)

    lag_1_matches = bool(
        np.allclose(
            frame["lag_1"].to_numpy(dtype=float),
            expected_lag_1.to_numpy(dtype=float),
            rtol=1e-9,
            atol=1e-9,
            equal_nan=True,
        )
    )

    expected_rolling = _rolling_statistic(
        expected_lag_1,
        frame["item_id"],
        frame["store_id"],
        7,
        1,
        "mean",
    )

    rolling_excludes_current = bool(
        np.allclose(
            frame["rolling_mean_7"].to_numpy(dtype=float),
            expected_rolling.to_numpy(dtype=float),
            rtol=1e-9,
            atol=1e-9,
            equal_nan=True,
        )
    )

    checks = [
        (
            "duplicate_date_item_store_keys",
            duplicate_count == 0,
            duplicate_count,
            0,
        ),
        (
            "chronological_within_item_store_series",
            chronological,
            chronological,
            True,
        ),
        (
            "rows_positive",
            rows > 0,
            rows,
            ">0",
        ),
        (
            "target_quantity_missing",
            target_missing == 0,
            target_missing,
            0,
        ),
        (
            "input_output_rows_match",
            rows_match,
            rows,
            source_rows,
        ),
        (
            "input_output_keys_match",
            keys_match,
            keys_match,
            True,
        ),
        (
            "target_preserved_vs_input",
            target_preserved,
            target_preserved,
            True,
        ),
        (
            "split_preserved_vs_input",
            split_preserved,
            split_preserved,
            True,
        ),
        (
            "quantity_total_reconciled",
            quantity_reconciled,
            _format_quantity(float(source[TARGET_COLUMN].sum())),
            _format_quantity(float(frame[TARGET_COLUMN].sum())),
        ),
        (
            "calendar_features_present",
            calendar_present == len(CALENDAR_FEATURES),
            calendar_present,
            len(CALENDAR_FEATURES),
        ),
        (
            "historical_features_present",
            historical_present == len(HISTORICAL_FEATURES),
            historical_present,
            len(HISTORICAL_FEATURES),
        ),
        (
            "first_observation_has_no_history",
            first_observation_has_no_history,
            first_observation_has_no_history,
            True,
        ),
        (
            "lag_1_matches_previous_observation",
            lag_1_matches,
            lag_1_matches,
            True,
        ),
        (
            "rolling_excludes_current_target",
            rolling_excludes_current,
            rolling_excludes_current,
            True,
        ),
    ]

    return pd.DataFrame(
        checks,
        columns=["check", "passed", "actual", "expected"],
    )


def create_feature_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Record the completeness of every engineered feature."""
    total = len(frame)

    records: list[dict[str, object]] = []

    for column in FEATURE_COLUMNS:
        non_null = int(frame[column].notna().sum())
        missing = total - non_null

        records.append(
            {
                "feature": column,
                "feature_group": (
                    "calendar"
                    if column in CALENDAR_FEATURES
                    else "historical"
                ),
                "dtype": str(frame[column].dtype),
                "non_null": non_null,
                "missing": missing,
                "missing_share": (
                    round(missing / total, 6) if total else 0.0
                ),
            }
        )

    return pd.DataFrame(records)


def create_summary(
    frame: pd.DataFrame,
    source: pd.DataFrame,
) -> pd.DataFrame:
    """Create a compact feature-engineering summary."""
    split_counts = (
        frame["split"]
        .value_counts()
        .to_dict()
    )

    return pd.DataFrame(
        [
            {"metric": "rows", "value": len(frame)},
            {"metric": "source_rows", "value": len(source)},
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
                "value": len(FEATURE_COLUMNS),
            },
            {"metric": "target", "value": TARGET_COLUMN},
            {
                "metric": "train_rows",
                "value": int(split_counts.get("train", 0)),
            },
            {
                "metric": "validation_rows",
                "value": int(split_counts.get("validation", 0)),
            },
            {
                "metric": "test_rows",
                "value": int(split_counts.get("test", 0)),
            },
        ]
    )


def create_split_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize the preserved chronological partitions."""
    summary = (
        frame.groupby("split", dropna=False)
        .agg(
            rows=("quantity", "size"),
            quantity=("quantity", "sum"),
            date_min=("date", "min"),
            date_max=("date", "max"),
        )
        .reset_index()
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


def _format_quantity(value: float) -> str:
    """Format a demand quantity without floating-point artefacts."""
    return f"{value:.3f}"


def write_findings(
    frame: pd.DataFrame,
    source: pd.DataFrame,
    quality_report: pd.DataFrame,
    feature_summary: pd.DataFrame,
    split_summary: pd.DataFrame,
) -> None:
    """Write a human-readable feature-engineering findings report."""
    failed_checks = quality_report.loc[
        ~quality_report["passed"].astype(bool),
        "check",
    ].tolist()

    source_quantity = float(source[TARGET_COLUMN].sum())
    prepared_quantity = float(frame[TARGET_COLUMN].sum())

    lines = [
        "Phase 10 — Feature Engineering Findings",
        "",
        f"Rows: {len(frame):,}",
        f"Source rows: {len(source):,}",
        f"Unique items: {frame['item_id'].nunique():,}",
        f"Unique stores: {frame['store_id'].nunique():,}",
        (
            "Date range: "
            f"{frame['date'].min().date()} to "
            f"{frame['date'].max().date()}"
        ),
        f"Target: {TARGET_COLUMN}",
        f"Feature count: {len(FEATURE_COLUMNS)}",
        "",
        "Source reconciliation:",
        (
            "- input and output rows match: "
            f"{len(frame) == len(source)}"
        ),
        (
            "- target preserved: "
            f"{np.allclose(source_quantity, prepared_quantity, rtol=1e-10, atol=1e-6, equal_nan=True)}"
        ),
        (
            "- split labels preserved: "
            f"{set(frame['split']) == set(source['split'])}"
        ),
        (
            "- source quantity: "
            f"{_format_quantity(source_quantity)}"
        ),
        (
            "- prepared quantity: "
            f"{_format_quantity(prepared_quantity)}"
        ),
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
            "Leakage contract:",
            "- historical features use prior observations only",
            (
                "- the first observation of every series has no "
                "history (lag_1 and rolling_mean_7 are missing)"
            ),
            "- lag_1 equals the previous observed quantity",
            "- rolling_mean_7 excludes the current observation",
            "",
            "Feature completeness (missing share):",
        ]
    )

    for row in feature_summary.itertuples(index=False):
        if row.feature_group == "calendar":
            continue

        lines.append(
            f"- {row.feature}: missing={row.missing:,} "
            f"({row.missing_share * 100:.2f}%)"
        )

    lines.append(
        "- calendar features: missing=0 (derived from the date)"
    )

    lines.extend(
        [
            "",
            "Important limitation:",
            "Lag and rolling windows operate over previous observed "
            "records.",
            "They are not guaranteed to represent exact calendar-day "
            "windows",
            "because Phase 9 identified substantial intermediate-date "
            "gaps.",
            "",
        ]
    )

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

    source = pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
    )

    prepared = prepare_features(source)

    quality_report = create_quality_report(prepared, source)

    if not bool(quality_report["passed"].all()):
        failed = quality_report.loc[
            ~quality_report["passed"],
            "check",
        ].tolist()

        raise RuntimeError(
            "One or more feature-engineering quality checks failed: "
            f"{failed}"
        )

    prepared.to_csv(
        OUTPUT_PATH,
        index=False,
        float_format="%.12g",
    )

    quality_report.to_csv(QUALITY_PATH, index=False)

    feature_summary = create_feature_summary(prepared)
    feature_summary.to_csv(FEATURE_SUMMARY_PATH, index=False)

    summary = create_summary(prepared, source)
    summary.to_csv(SUMMARY_PATH, index=False)

    split_summary = create_split_summary(prepared)
    split_summary.to_csv(SPLIT_PATH, index=False)

    write_findings(
        prepared,
        source,
        quality_report,
        feature_summary,
        split_summary,
    )

    print("Feature engineering completed successfully.")
    print(f"Prepared dataset: {OUTPUT_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Quality report: {QUALITY_PATH}")
    print(f"Feature summary: {FEATURE_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
