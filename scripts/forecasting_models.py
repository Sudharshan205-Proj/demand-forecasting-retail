"""Train and evaluate classical retail demand forecasting models.

Phase 11 models: naive, seasonal-naive and ARIMA, forecasting physical
retail quantity. Models are developed and compared on the training and
validation periods, and the test period stays isolated from model
selection. The Phase 10 feature-engineered input is reconciled at the
store-day grain (rows, keys, total quantity) before any model is fitted,
and every store series is densified onto a complete daily calendar, with
the densification measured rather than assumed. Naive and seasonal-naive
forecasts are checked against their documented definitions, ARIMA's order
is recorded explicitly, and RMSE and MAPE are recomputed from the stored
predictions. No observation at or after ``TEST_START`` is used for
training, validation or model selection.
"""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.arima.model import ARIMA
except ImportError as exc:
    raise ImportError(
        "statsmodels is required for Phase 11 ARIMA forecasting. "
        "Install it with: pip install statsmodels"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "feature_engineered_daily.csv"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_model_results.csv"
)

CONFIG_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_model_configurations.csv"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_summary.csv"
)

PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_predictions.csv"
)

QUALITY_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_quality_report.csv"
)

FINDINGS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_findings.txt"
)

TARGET = "quantity"

TRAIN_END = pd.Timestamp("2024-02-10")
VALIDATION_END = pd.Timestamp("2024-06-03")
TEST_START = pd.Timestamp("2024-06-04")
TEST_END = pd.Timestamp("2024-09-26")

SEASONAL_PERIOD = 7
ARIMA_ORDER = (1, 1, 1)

MODELS = ("naive", "seasonal_naive", "arima")

REQUIRED_COLUMNS = [
    "date",
    "store_id",
    "quantity",
    "split",
]

QUALITY_COLUMNS = ["check", "passed", "actual", "expected"]


def validate_input_columns(columns: list[str]) -> None:
    """Validate the required forecasting input columns."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_feature_matrix() -> pd.DataFrame:
    """Load the key, target and split columns of the Phase 10 matrix.

    Only the four columns the forecasting workflow needs are read, so
    the 7.4 million-row source is not materialised in full.
    """
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Forecasting input dataset not found: {INPUT_PATH}"
        )

    columns = pd.read_csv(INPUT_PATH, nrows=0).columns.tolist()
    validate_input_columns(columns)

    frame = pd.read_csv(
        INPUT_PATH,
        usecols=REQUIRED_COLUMNS,
        parse_dates=["date"],
    )

    frame = frame.sort_values(
        ["store_id", "date"],
        kind="mergesort",
    ).reset_index(drop=True)

    return frame


def summarize_input(source: pd.DataFrame) -> dict[str, object]:
    """Record the reconciliation facts of the forecasting input."""
    return {
        "rows": len(source),
        "quantity_total": float(source[TARGET].sum()),
        "date_min": source["date"].min(),
        "date_max": source["date"].max(),
        "stores": int(source["store_id"].nunique()),
        "split_rows": {
            str(split): int(count)
            for split, count in source["split"]
            .value_counts()
            .items()
        },
    }


def aggregate_daily_demand(source: pd.DataFrame) -> pd.DataFrame:
    """Aggregate physical demand to the store-day forecasting grain."""
    daily = (
        source.groupby(["date", "store_id"], as_index=False)[TARGET]
        .sum()
        .sort_values(["store_id", "date"], kind="mergesort")
        .reset_index(drop=True)
    )

    return daily


def to_regular_daily_series(
    series: pd.Series,
    store_id: int | str,
) -> pd.Series:
    """Reindex a store's series onto a complete, gap-free daily calendar.

    Phase 9 intentionally preserves missing dates rather than assuming
    zero demand at the item-store grain. Once aggregated to the store
    level for forecasting, an absent date means no quantity was recorded
    for that store on that day, so zero-filling is the correct
    interpretation here. This also gives every model an explicit,
    regularly spaced frequency, which ARIMA's out-of-sample forecasting
    requires -- an irregular index causes
    ``ValueError: No supported index is available`` at forecast time.
    """
    if series.empty:
        raise ValueError(
            f"No observations found for store_id={store_id!r}"
        )

    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError(
            "Forecasting series must be indexed by date."
        )

    if not series.index.is_monotonic_increasing:
        raise ValueError(
            f"Series for store_id={store_id!r} is not chronological."
        )

    full_index = pd.date_range(
        series.index.min(),
        series.index.max(),
        freq="D",
    )

    regular = series.reindex(full_index, fill_value=0.0)
    regular.index.freq = "D"

    return regular


def iter_store_series(
    daily: pd.DataFrame,
) -> Iterator[tuple[int | str, pd.Series]]:
    """Yield each store's regular, gap-free chronological demand series.

    Groups the full frame once instead of re-filtering it per store, so
    this scans the dataset in O(rows) rather than O(stores x rows).
    """
    for store_id, group in daily.groupby("store_id", sort=True):
        series = group.set_index("date")[TARGET].sort_index()

        yield store_id, to_regular_daily_series(series, store_id)


def naive_forecast(
    history: pd.Series,
    horizon: int,
) -> np.ndarray:
    """Forecast every future point using the latest observation."""
    if history.empty:
        raise ValueError("Cannot create a naive forecast from empty history.")

    if horizon < 1:
        raise ValueError("Forecast horizon must be at least one step.")

    return np.repeat(float(history.iloc[-1]), horizon)


def seasonal_naive_forecast(
    history: pd.Series,
    horizon: int,
    season_length: int = SEASONAL_PERIOD,
) -> np.ndarray:
    """Repeat the most recent seasonal pattern."""
    if len(history) < season_length:
        raise ValueError(
            "Insufficient history for seasonal-naive forecasting."
        )

    if horizon < 1:
        raise ValueError("Forecast horizon must be at least one step.")

    recent = history.iloc[-season_length:].to_numpy(dtype=float)

    repeats = int(np.ceil(horizon / season_length))

    return np.tile(recent, repeats)[:horizon]


def fit_arima_forecast(
    history: pd.Series,
    horizon: int,
    order: tuple[int, int, int] = ARIMA_ORDER,
) -> np.ndarray:
    """Fit ARIMA and forecast the requested horizon."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        model = ARIMA(
            history,
            order=order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )

        fitted = model.fit()

        forecast = fitted.forecast(steps=horizon)

    return np.asarray(forecast, dtype=float)


def _as_float_arrays(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Coerce actual and predicted values to matching float arrays."""
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if actual_array.shape != predicted_array.shape:
        raise ValueError(
            "Actual and forecast lengths do not match."
        )

    if actual_array.size == 0:
        raise ValueError(
            "Cannot evaluate an empty forecast."
        )

    return actual_array, predicted_array


def rmse(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> float:
    """Calculate root mean squared error."""
    actual_array, predicted_array = _as_float_arrays(actual, predicted)

    return float(
        np.sqrt(np.mean((actual_array - predicted_array) ** 2))
    )


def mape(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> float:
    """Calculate MAPE while excluding zero-actual observations."""
    actual_array, predicted_array = _as_float_arrays(actual, predicted)

    mask = actual_array != 0

    if not np.any(mask):
        return float("nan")

    return float(
        np.mean(
            np.abs(
                (actual_array[mask] - predicted_array[mask])
                / actual_array[mask]
            )
        )
        * 100
    )


def evaluate_forecast(
    actual: pd.Series,
    predicted: np.ndarray,
) -> dict[str, float]:
    """Return RMSE and MAPE for a forecast."""
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if actual_array.shape != predicted_array.shape:
        raise ValueError(
            "Actual and forecast lengths do not match."
        )

    return {
        "rmse": rmse(actual_array, predicted_array),
        "mape_percent": mape(actual_array, predicted_array),
    }


def _model_configuration(model: str) -> str:
    """Return the documented configuration string for a model."""
    if model == "naive":
        return "last observed value"

    if model == "seasonal_naive":
        return f"season_length={SEASONAL_PERIOD}"

    return (
        f"order={ARIMA_ORDER}; "
        "enforce_stationarity=False; "
        "enforce_invertibility=False"
    )


def run_models_for_store(
    series: pd.Series,
    store_id: int | str,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Run all Phase 11 models for one store.

    Returns the per-model metric rows, the reproducibility
    configurations and the store-day predictions.
    """
    train = series.loc[:TRAIN_END]
    validation = series.loc[
        (series.index > TRAIN_END)
        & (series.index <= VALIDATION_END)
    ]

    if train.empty:
        raise ValueError(
            f"Store {store_id!r} has no training observations."
        )

    if validation.empty:
        raise ValueError(
            f"Store {store_id!r} has no validation observations."
        )

    horizon = len(validation)

    model_fitters = {
        "naive": lambda: naive_forecast(train, horizon),
        "seasonal_naive": lambda: seasonal_naive_forecast(
            train,
            horizon,
            SEASONAL_PERIOD,
        ),
        "arima": lambda: fit_arima_forecast(
            train,
            horizon,
            ARIMA_ORDER,
        ),
    }

    training_start = train.index.min().date().isoformat()
    training_end = train.index.max().date().isoformat()
    validation_start = validation.index.min().date().isoformat()
    validation_end = validation.index.max().date().isoformat()

    results: list[dict] = []
    configurations: list[dict] = []
    predictions: list[dict] = []

    for model_name, fit_forecast in model_fitters.items():
        configurations.append(
            {
                "model": model_name,
                "store_id": store_id,
                "training_start": training_start,
                "training_end": training_end,
                "validation_start": validation_start,
                "validation_end": validation_end,
                "forecast_horizon": horizon,
                "configuration": _model_configuration(model_name),
            }
        )

        try:
            prediction = fit_forecast()
        except Exception as error:  # noqa: BLE001 - isolate per-store failures
            print(
                f"  skipping {model_name} for store_id={store_id!r}: "
                f"{error}"
            )
            continue

        metrics = evaluate_forecast(
            validation,
            prediction,
        )

        results.append(
            {
                "store_id": store_id,
                "model": model_name,
                "validation_start": validation_start,
                "validation_end": validation_end,
                "forecast_horizon": horizon,
                "rmse": metrics["rmse"],
                "mape_percent": metrics["mape_percent"],
            }
        )

        predictions.extend(
            {
                "store_id": store_id,
                "model": model_name,
                "date": date,
                "actual": float(actual),
                "predicted": float(predicted),
            }
            for date, actual, predicted in zip(
                validation.index,
                validation.to_numpy(dtype=float),
                prediction,
            )
        )

    return results, configurations, predictions


def create_summary(
    results: pd.DataFrame,
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize validation performance across stores.

    The mean and median are computed across stores; the pooled metrics
    are computed across every store-day validation observation, so they
    weight larger stores more heavily. Both are reported because they
    answer different questions.
    """
    summary = (
        results.groupby("model", as_index=False)
        .agg(
            stores_evaluated=("store_id", "nunique"),
            mean_rmse=("rmse", "mean"),
            median_rmse=("rmse", "median"),
            mean_mape_percent=("mape_percent", "mean"),
            median_mape_percent=("mape_percent", "median"),
        )
    )

    pooled_records = [
        {
            "model": model,
            "pooled_observations": len(group),
            "pooled_rmse": rmse(
                group["actual"].to_numpy(dtype=float),
                group["predicted"].to_numpy(dtype=float),
            ),
            "pooled_mape_percent": mape(
                group["actual"].to_numpy(dtype=float),
                group["predicted"].to_numpy(dtype=float),
            ),
        }
        for model, group in predictions.groupby("model", sort=True)
    ]

    pooled = pd.DataFrame(pooled_records)

    summary = summary.merge(pooled, on="model", how="left")

    return (
        summary.sort_values("mean_rmse")
        .reset_index(drop=True)
    )


def _arrays_agree(
    first: pd.Series | np.ndarray,
    second: pd.Series | np.ndarray,
) -> bool:
    """Return True when two numeric arrays match element-wise.

    A shape difference is a mismatch rather than an error, so a quality
    check reports a failed comparison instead of raising when a forecast
    length is wrong.
    """
    first_array = np.asarray(first, dtype=float)
    second_array = np.asarray(second, dtype=float)

    if first_array.shape != second_array.shape:
        return False

    return bool(
        np.allclose(
            first_array,
            second_array,
            rtol=1e-9,
            atol=1e-9,
        )
    )


def _format_quantity(value: float) -> str:
    """Format a demand quantity without floating-point artefacts."""
    return f"{value:.3f}"


def create_quality_report(
    source: pd.DataFrame,
    daily: pd.DataFrame,
    series_by_store: dict[int | str, pd.Series],
    results: pd.DataFrame,
    configurations: pd.DataFrame,
    predictions: pd.DataFrame,
    summary: pd.DataFrame,
) -> pd.DataFrame:
    """Create machine-readable forecasting quality checks.

    The report covers the quality framework's four validation areas:
    input validation, temporal validation, model validation and metric
    validation, plus the reproducibility and leakage contract.
    """
    rows = len(source)

    required_present = sum(
        column in source.columns for column in REQUIRED_COLUMNS
    )

    target_missing = int(source[TARGET].isna().sum())

    dates_parsed = bool(
        pd.api.types.is_datetime64_any_dtype(source["date"])
    )

    duplicate_days = int(
        daily.duplicated(["date", "store_id"]).sum()
    )

    source_quantity = float(source[TARGET].sum())
    daily_quantity = float(daily[TARGET].sum())

    demand_reconciled = bool(
        np.isclose(
            source_quantity,
            daily_quantity,
            rtol=1e-10,
            atol=1e-6,
        )
    )

    series_regular = all(
        isinstance(series.index, pd.DatetimeIndex)
        and series.index.freqstr == "D"
        and len(series)
        == (series.index.max() - series.index.min()).days + 1
        for series in series_by_store.values()
    )

    series_chronological = all(
        series.index.is_monotonic_increasing
        for series in series_by_store.values()
    )

    source_stores = int(source["store_id"].nunique())
    stores_preserved = len(series_by_store) == source_stores

    training_ends = (
        configurations.loc[
            configurations["model"] == "naive",
            "training_end",
        ]
        .drop_duplicates()
        .tolist()
    )
    training_end_ok = training_ends == [TRAIN_END.date().isoformat()]

    expected_validation_start = (TRAIN_END + pd.Timedelta(days=1)).date()
    expected_validation_end = VALIDATION_END.date()

    validation_windows = {
        (
            series.loc[
                (series.index > TRAIN_END)
                & (series.index <= VALIDATION_END)
            ].index.min(),
            series.loc[
                (series.index > TRAIN_END)
                & (series.index <= VALIDATION_END)
            ].index.max(),
        )
        for series in series_by_store.values()
    }

    validation_window_ok = validation_windows == {
        (
            pd.Timestamp(expected_validation_start),
            pd.Timestamp(expected_validation_end),
        )
    }

    horizons = sorted(results["forecast_horizon"].unique().tolist())

    first_series = next(iter(series_by_store.values()))
    expected_horizon = len(
        first_series.loc[
            (first_series.index > TRAIN_END)
            & (first_series.index <= VALIDATION_END)
        ]
    )
    horizon_ok = horizons == [expected_horizon]

    test_rows = int((source["split"] == "test").sum())
    max_prediction_date = predictions["date"].max()
    test_isolated = bool(
        max_prediction_date < TEST_START
        and all(
            pd.Timestamp(end) <= TRAIN_END
            for end in configurations["training_end"].unique()
        )
    )

    evaluated_pairs = int(
        results.groupby(["store_id", "model"]).ngroups
    )
    expected_pairs = source_stores * len(MODELS)
    models_complete = evaluated_pairs == expected_pairs

    naive_ok = True
    seasonal_naive_ok = True

    for store_id, series in series_by_store.items():
        train = series.loc[:TRAIN_END]
        horizon = len(series.loc[
            (series.index > TRAIN_END)
            & (series.index <= VALIDATION_END)
        ])

        naive_predictions = predictions.loc[
            (predictions["store_id"] == store_id)
            & (predictions["model"] == "naive"),
            "predicted",
        ].to_numpy(dtype=float)

        naive_expected = np.repeat(float(train.iloc[-1]), horizon)

        if not _arrays_agree(naive_predictions, naive_expected):
            naive_ok = False

        expected_seasonal = seasonal_naive_forecast(
            train,
            horizon,
            SEASONAL_PERIOD,
        )
        seasonal_predictions = predictions.loc[
            (predictions["store_id"] == store_id)
            & (predictions["model"] == "seasonal_naive"),
            "predicted",
        ].to_numpy(dtype=float)

        if not _arrays_agree(
            seasonal_predictions,
            expected_seasonal,
        ):
            seasonal_naive_ok = False

    arima_configurations = configurations.loc[
        configurations["model"] == "arima",
        "configuration",
    ]
    arima_ok = bool(
        len(arima_configurations) == source_stores
        and arima_configurations.str.contains(
            r"order=\(1, 1, 1\)",
            regex=True,
        ).all()
    )

    expected_prediction_rows = expected_pairs * expected_horizon
    prediction_rows_ok = len(predictions) == expected_prediction_rows

    prediction_values_missing = int(
        predictions[["actual", "predicted"]].isna().sum().sum()
    )

    rmse_ok = True
    mape_ok = True
    mape_finite = True

    for _, result in results.iterrows():
        group = predictions.loc[
            (predictions["store_id"] == result["store_id"])
            & (predictions["model"] == result["model"])
        ]

        actual_values = group["actual"].to_numpy(dtype=float)
        predicted_values = group["predicted"].to_numpy(dtype=float)

        if not np.isclose(
            rmse(actual_values, predicted_values),
            float(result["rmse"]),
            rtol=1e-9,
            atol=1e-9,
        ):
            rmse_ok = False

        recomputed_mape = mape(actual_values, predicted_values)

        if np.isclose(
            recomputed_mape,
            float(result["mape_percent"]),
            rtol=1e-9,
            atol=1e-9,
        ):
            if np.any(actual_values != 0) and not np.isfinite(
                recomputed_mape
            ):
                mape_finite = False
        else:
            mape_ok = False

    summary_ok = True

    for _, row in summary.iterrows():
        model_results = results.loc[results["model"] == row["model"]]

        if not (
            np.isclose(
                row["mean_rmse"],
                model_results["rmse"].mean(),
                rtol=1e-9,
                atol=1e-9,
            )
            and np.isclose(
                row["pooled_rmse"],
                rmse(
                    predictions.loc[
                        predictions["model"] == row["model"], "actual"
                    ].to_numpy(dtype=float),
                    predictions.loc[
                        predictions["model"] == row["model"], "predicted"
                    ].to_numpy(dtype=float),
                ),
                rtol=1e-9,
                atol=1e-9,
            )
        ):
            summary_ok = False

    checks = [
        (
            "input_rows_positive",
            rows > 0,
            rows,
            ">0",
        ),
        (
            "input_required_columns_present",
            required_present == len(REQUIRED_COLUMNS),
            required_present,
            len(REQUIRED_COLUMNS),
        ),
        (
            "input_target_complete",
            target_missing == 0,
            target_missing,
            0,
        ),
        (
            "input_dates_parsed",
            dates_parsed,
            dates_parsed,
            True,
        ),
        (
            "store_day_keys_unique",
            duplicate_days == 0,
            duplicate_days,
            0,
        ),
        (
            "store_day_demand_reconciled",
            demand_reconciled,
            _format_quantity(source_quantity),
            _format_quantity(daily_quantity),
        ),
        (
            "store_series_regular_daily",
            series_regular,
            series_regular,
            True,
        ),
        (
            "store_series_chronological",
            series_chronological,
            series_chronological,
            True,
        ),
        (
            "store_count_preserved",
            stores_preserved,
            len(series_by_store),
            source_stores,
        ),
        (
            "training_window_ends_at_train_end",
            training_end_ok,
            training_ends[0] if training_ends else "missing",
            TRAIN_END.date().isoformat(),
        ),
        (
            "validation_window_matches_contract",
            validation_window_ok,
            len(validation_windows),
            1,
        ),
        (
            "validation_horizon_consistent",
            horizon_ok,
            horizons[0] if horizons else 0,
            expected_horizon,
        ),
        (
            "test_period_excluded_from_evaluation",
            test_isolated,
            max_prediction_date.date().isoformat()
            if pd.notna(max_prediction_date)
            else "missing",
            f"< {TEST_START.date().isoformat()}",
        ),
        (
            "models_evaluated_per_store",
            models_complete,
            evaluated_pairs,
            expected_pairs,
        ),
        (
            "naive_matches_last_observation",
            naive_ok,
            naive_ok,
            True,
        ),
        (
            "seasonal_naive_matches_weekly_pattern",
            seasonal_naive_ok,
            seasonal_naive_ok,
            True,
        ),
        (
            "arima_configuration_explicit",
            arima_ok,
            arima_ok,
            True,
        ),
        (
            "prediction_rows_match_horizons",
            prediction_rows_ok,
            len(predictions),
            expected_prediction_rows,
        ),
        (
            "predictions_have_no_missing_values",
            prediction_values_missing == 0,
            prediction_values_missing,
            0,
        ),
        (
            "rmse_reproduced_from_predictions",
            rmse_ok,
            rmse_ok,
            True,
        ),
        (
            "mape_reproduced_from_predictions",
            mape_ok,
            mape_ok,
            True,
        ),
        (
            "mape_finite_for_nonzero_actuals",
            mape_finite,
            mape_finite,
            True,
        ),
        (
            "summary_reconciles_with_results",
            summary_ok,
            summary_ok,
            True,
        ),
        (
            "test_partition_present_but_unused",
            test_rows > 0,
            test_rows,
            ">0",
        ),
    ]

    return pd.DataFrame(checks, columns=QUALITY_COLUMNS)


def write_findings(
    input_summary: dict[str, object],
    daily: pd.DataFrame,
    series_by_store: dict[int | str, pd.Series],
    summary: pd.DataFrame,
    results: pd.DataFrame,
    quality_report: pd.DataFrame,
) -> None:
    """Write a human-readable model findings report."""
    failed_checks = quality_report.loc[
        ~quality_report["passed"].astype(bool),
        "check",
    ].tolist()

    best_mean = (
        summary.iloc[0]["model"] if not summary.empty else "not determined"
    )

    best_pooled = (
        summary.sort_values("pooled_rmse").iloc[0]["model"]
        if not summary.empty
        else "not determined"
    )

    validation_start = (TRAIN_END + pd.Timedelta(days=1)).date()

    zero_filled = int(
        sum(len(series) for series in series_by_store.values())
        - len(daily)
    )

    lines = [
        "Phase 11 — Forecasting Model Findings",
        "",
        "Forecasting target: physical retail quantity",
        "",
        "Input reconciliation (Phase 10 feature-engineered dataset):",
        f"- rows: {int(input_summary['rows']):,}",
        f"- unique stores: {int(input_summary['stores']):,}",
        (
            "- date range: "
            f"{pd.Timestamp(input_summary['date_min']).date()} to "
            f"{pd.Timestamp(input_summary['date_max']).date()}"
        ),
        (
            "- total quantity: "
            f"{_format_quantity(float(input_summary['quantity_total']))}"
        ),
        "- split rows: "
        + "; ".join(
            f"{split}={count:,}"
            for split, count in sorted(
                dict(input_summary["split_rows"]).items()
            )
        ),
        "",
        "Modelling inputs:",
        (
            "- grain: daily store-level demand "
            f"({daily['date'].nunique():,} dates x "
            f"{daily['store_id'].nunique()} stores)"
        ),
        f"- observed store-days: {len(daily):,}",
        f"- zero-filled store-days: {zero_filled:,}",
        f"- training end: {TRAIN_END.date()}",
        (
            "- validation period: "
            f"{validation_start} to {VALIDATION_END.date()}"
        ),
        (
            "- test period (excluded from selection): "
            f"{TEST_START.date()} to {TEST_END.date()}"
        ),
        "",
        "Models evaluated:",
    ]

    for model in MODELS:
        lines.append(f"- {model}: {_model_configuration(model)}")

    lines.extend(
        [
            "",
            "Validation results (per store):",
            (
                f"{'store':>5}  {'model':<15} {'rmse':>14} "
                f"{'mape_percent':>14}"
            ),
        ]
    )

    for row in results.sort_values(["store_id", "model"]).itertuples(
        index=False
    ):
        lines.append(
            f"{row.store_id!s:>5}  {row.model:<15} "
            f"{row.rmse:>14.4f} {row.mape_percent:>14.4f}"
        )

    lines.extend(
        [
            "",
            "Summary (across stores):",
            (
                f"{'model':<15} {'stores':>6} {'mean_rmse':>14} "
                f"{'median_rmse':>14} {'pooled_rmse':>14} "
                f"{'pooled_mape%':>14}"
            ),
        ]
    )

    for row in summary.itertuples(index=False):
        lines.append(
            f"{row.model:<15} {row.stores_evaluated:>6} "
            f"{row.mean_rmse:>14.4f} {row.median_rmse:>14.4f} "
            f"{row.pooled_rmse:>14.4f} {row.pooled_mape_percent:>14.4f}"
        )

    lines.extend(
        [
            "",
            f"Best model by mean validation RMSE: {best_mean}",
            f"Best model by pooled validation RMSE: {best_pooled}",
            "",
            ("MAPE excludes validation observations where actual quantity "
            "is zero."),
            "The test period is intentionally not used for model selection.",
            "",
            "Quality checks: "
            + (
                f"all {len(quality_report)} passed"
                if not failed_checks
                else f"{len(failed_checks)} failed"
            ),
        ]
    )

    if failed_checks:
        lines.extend(
            [f"- failed: {check}" for check in failed_checks]
        )

    lines.extend(
        [
            "",
            "Important limitation:",
            "ARIMA and the baselines are evaluated on daily store-level",
            "demand rather than every item-store series because the",
            "dataset contains substantial gaps and thousands of sparse",
            "item-store series.",
            "",
            "Scope note:",
            "The Phase 10 engineered lag, rolling and calendar features are",
            "not used as predictors by this phase; the classical models",
            "consume the demand target only.",
            "",
        ]
    )

    FINDINGS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Execute Phase 11 forecasting experiments."""
    print("Running Phase 11 forecasting models...")

    source = load_feature_matrix()
    daily = aggregate_daily_demand(source)

    series_by_store = dict(iter_store_series(daily))

    all_results: list[dict] = []
    all_configurations: list[dict] = []
    all_predictions: list[dict] = []

    for store_id, series in series_by_store.items():
        try:
            results, configurations, predictions = run_models_for_store(
                series,
                store_id,
            )
        except ValueError as error:
            print(f"  skipping store_id={store_id!r}: {error}")
            continue

        all_results.extend(results)
        all_configurations.extend(configurations)
        all_predictions.extend(predictions)

    if not all_results:
        raise RuntimeError(
            "No forecasting results were produced for any store."
        )

    results_frame = pd.DataFrame(all_results)
    configurations_frame = pd.DataFrame(all_configurations)
    predictions_frame = pd.DataFrame(all_predictions)

    summary = create_summary(results_frame, predictions_frame)

    quality_report = create_quality_report(
        source,
        daily,
        series_by_store,
        results_frame,
        configurations_frame,
        predictions_frame,
        summary,
    )

    if not bool(quality_report["passed"].all()):
        failed = quality_report.loc[
            ~quality_report["passed"],
            "check",
        ].tolist()

        raise RuntimeError(
            "One or more forecasting quality checks failed: "
            f"{failed}"
        )

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    results_frame.to_csv(
        RESULTS_PATH,
        index=False,
        float_format="%.12g",
    )

    configurations_frame.to_csv(
        CONFIG_PATH,
        index=False,
    )

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
        float_format="%.12g",
    )

    predictions_frame.to_csv(
        PREDICTIONS_PATH,
        index=False,
        float_format="%.12g",
        date_format="%Y-%m-%d",
    )

    quality_report.to_csv(QUALITY_PATH, index=False)

    write_findings(
        summarize_input(source),
        daily,
        series_by_store,
        summary,
        results_frame,
        quality_report,
    )

    print("Forecasting models completed successfully.")
    print(f"Results: {RESULTS_PATH}")
    print(f"Configurations: {CONFIG_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Predictions: {PREDICTIONS_PATH}")
    print(f"Quality report: {QUALITY_PATH}")


if __name__ == "__main__":
    main()
