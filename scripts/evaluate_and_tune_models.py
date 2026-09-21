"""Evaluate and tune the Phase 12 retail demand forecasting models.

Time-aware cross-validation runs on the training period only, and the
selected configurations are then evaluated on the untouched validation
period; the test period never takes part in model selection or tuning.
Every store is tuned -- the fold design adapts to the history a store
actually has, so short series are not silently dropped -- and
configurations are passed as typed objects rather than parsed back from a
string into an order or a season length. The feature-based candidate
consumes the Phase 10 lag, rolling and calendar features at the same
store-day grain as the classical models. Fold and validation predictions
are stored so every reported metric can be recomputed, and a
machine-readable quality report gates the run on input reconciliation,
split boundaries, fold structure, leakage controls, the selection rule and
metric reproduction. The evaluation artifacts are written under
``data/analysis/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.linalg import LinAlgError
from sklearn.ensemble import HistGradientBoostingRegressor
from statsmodels.tools.sm_exceptions import MissingDataError
from statsmodels.tsa.arima.model import ARIMA

# A fold can legitimately fail on bad input (ValueError), NaNs reaching the
# ARIMA fitter (MissingDataError), or a singular fit (LinAlgError); anything
# else is a bug and should propagate instead of being recorded as "failed".
EXPECTED_EVALUATION_ERRORS = (ValueError, MissingDataError, LinAlgError)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "feature_engineered_daily.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"

RESULTS_PATH = OUTPUT_DIR / "model_tuning_results.csv"
SUMMARY_PATH = OUTPUT_DIR / "model_tuning_summary.csv"
SELECTED_PATH = OUTPUT_DIR / "selected_model_configurations.csv"
VALIDATION_PATH = OUTPUT_DIR / "tuned_validation_results.csv"
ERROR_PATH = OUTPUT_DIR / "model_error_analysis.csv"
PREDICTIONS_PATH = OUTPUT_DIR / "model_evaluation_predictions.csv"
QUALITY_PATH = OUTPUT_DIR / "model_evaluation_quality_report.csv"
FINDINGS_PATH = OUTPUT_DIR / "model_evaluation_findings.txt"

TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "validation"
TEST_SPLIT = "test"

REQUIRED_COLUMNS = ["date", "store_id", "quantity", "split"]

# The Phase 2/9 dataset contract: four physical stores.
EXPECTED_STORES = 4

# Chronological contract established by Phase 9 and verified in Phase 11.
TRAIN_END = pd.Timestamp("2024-02-10")
VALIDATION_END = pd.Timestamp("2024-06-03")
TEST_START = pd.Timestamp("2024-06-04")
TEST_END = pd.Timestamp("2024-09-26")

CV_FOLDS = 3
CV_HORIZON = 28

# A fold must fit the longest seasonal window (28 days), so the shortest
# tunable series still has a usable initial training sample.
MIN_TRAIN_OBSERVATIONS = 28

SEASONAL_PERIODS = (7, 14, 28)
ARIMA_ORDERS = (
    (0, 1, 1),
    (1, 1, 0),
    (1, 1, 1),
    (2, 1, 1),
)

FEATURE_MODEL = "feature_gbm"
FEATURE_MODEL_DESCRIPTION = (
    "HistGradientBoostingRegressor(learning_rate=0.1, max_iter=200, "
    "max_depth=3, min_samples_leaf=5, l2_regularization=1.0, "
    "early_stopping=False, random_state=0)"
)

CALENDAR_FEATURES = (
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month",
    "quarter",
    "year",
    "is_weekend",
)

HISTORICAL_FEATURES = (
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_std_7",
    "rolling_mean_28",
    "rolling_std_28",
    "series_age_days",
)

FEATURE_COLUMNS = CALENDAR_FEATURES + HISTORICAL_FEATURES

QUALITY_COLUMNS = ["check", "passed", "actual", "expected"]


@dataclass(frozen=True)
class ModelConfiguration:
    """Represent one forecasting configuration."""

    model: str
    configuration: str
    season_length: int | None = None
    order: tuple[int, int, int] | None = None


def configuration_key(
    configuration: ModelConfiguration,
) -> tuple[str, str]:
    """Return the stable identity of a configuration."""
    return (configuration.model, configuration.configuration)


def configuration_fields(
    configuration: ModelConfiguration,
) -> dict[str, object]:
    """Return the explicit, non-parsed parameter columns for an artifact."""
    return {
        "season_length": (
            configuration.season_length
            if configuration.season_length is not None
            else ""
        ),
        "order": str(configuration.order) if configuration.order is not None else "",
    }


# --- Metrics -----------------------------------------------------------


def _as_float_arrays(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Coerce actual and predicted values to matching float arrays."""
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)

    if actual_values.shape != predicted_values.shape:
        raise ValueError(
            "Actual and predicted values must have equal lengths."
        )

    if actual_values.size == 0:
        raise ValueError("Cannot evaluate an empty forecast.")

    return actual_values, predicted_values


def rmse(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> float:
    """Calculate root mean squared error."""
    actual_values, predicted_values = _as_float_arrays(actual, predicted)

    return float(
        np.sqrt(np.mean((actual_values - predicted_values) ** 2))
    )


def mape(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> float:
    """Calculate MAPE while excluding zero-actual observations."""
    actual_values, predicted_values = _as_float_arrays(actual, predicted)

    mask = actual_values != 0

    if not mask.any():
        return float("nan")

    return float(
        np.mean(
            np.abs(
                (actual_values[mask] - predicted_values[mask])
                / actual_values[mask]
            )
        )
        * 100
    )


def evaluate_forecast(
    actual: pd.Series,
    predicted: np.ndarray,
) -> tuple[float, float]:
    """Return RMSE and MAPE for a forecast."""
    return rmse(actual, predicted), mape(actual, predicted)


# --- Loading and splits ------------------------------------------------


def load_daily_store_demand() -> tuple[pd.DataFrame, dict[str, float]]:
    """Aggregate the feature dataset by date/store and reconcile the source.

    The 888 MB matrix is read in chunks; the raw row count and total
    quantity are accumulated during the same pass so the aggregation can
    be reconciled against the source without a second read.
    """
    daily_parts: list[pd.DataFrame] = []

    source_rows = 0
    source_quantity = 0.0

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=REQUIRED_COLUMNS,
        parse_dates=["date"],
        chunksize=250_000,
    ):
        source_rows += int(len(chunk))
        source_quantity += float(chunk["quantity"].sum())

        grouped = (
            chunk.groupby(
                ["date", "store_id", "split"],
                as_index=False,
                observed=True,
            )["quantity"]
            .sum()
        )
        daily_parts.append(grouped)

    combined = pd.concat(daily_parts, ignore_index=True)

    combined = (
        combined.groupby(
            ["date", "store_id", "split"],
            as_index=False,
            observed=True,
        )["quantity"]
        .sum()
        .sort_values(["store_id", "date"])
        .reset_index(drop=True)
    )

    source_facts = {
        "rows": source_rows,
        "quantity": source_quantity,
    }

    return combined, source_facts


def validate_splits(data: pd.DataFrame) -> None:
    """Validate chronological split ordering and key uniqueness."""
    split_dates = data.groupby("split")["date"].agg(["min", "max"])

    required = {TRAIN_SPLIT, VALIDATION_SPLIT, TEST_SPLIT}

    if not required.issubset(set(split_dates.index)):
        raise ValueError("Expected train, validation, and test splits.")

    if not (
        split_dates.loc[TRAIN_SPLIT, "max"]
        < split_dates.loc[VALIDATION_SPLIT, "min"]
        <= split_dates.loc[VALIDATION_SPLIT, "max"]
        < split_dates.loc[TEST_SPLIT, "min"]
    ):
        raise ValueError("Chronological split ordering is invalid.")

    duplicates = int(data.duplicated(["date", "store_id"]).sum())

    if duplicates:
        raise ValueError(
            f"Duplicate store/date observations after aggregation: {duplicates}"
        )


def get_store_series(
    data: pd.DataFrame,
    store_id: int,
    split: str,
) -> pd.Series:
    """Return one store's regular, gap-free chronological demand series."""
    subset = data[
        (data["store_id"] == store_id)
        & (data["split"] == split)
    ].sort_values("date")

    if subset.empty:
        raise ValueError(
            f"No observations found for store {store_id}, split {split}."
        )

    series = subset.set_index("date")["quantity"].astype(float)

    if series.index.duplicated().any():
        raise ValueError(
            f"Duplicate dates found for store {store_id}, split {split}."
        )

    # Reindex onto a complete daily calendar: ARIMA needs an explicit
    # frequency to forecast out of sample, and lag/seasonal windows should
    # follow calendar days rather than "nth observed row". Phase 9 leaves
    # missing dates unfilled, but at this store aggregate an absent date
    # means no quantity was recorded that day, so zero-filling is correct.
    full_index = pd.date_range(
        series.index.min(),
        series.index.max(),
        freq="D",
    )

    series = series.reindex(full_index, fill_value=0.0)
    series.index.freq = "D"

    return series


# --- Forecast primitives -----------------------------------------------


def naive_forecast(
    history: pd.Series,
    horizon: int,
) -> np.ndarray:
    """Forecast using the last observed value."""
    if history.empty:
        raise ValueError("History cannot be empty.")

    if horizon < 1:
        raise ValueError("Forecast horizon must be at least one step.")

    return np.repeat(float(history.iloc[-1]), horizon)


def seasonal_naive_forecast(
    history: pd.Series,
    horizon: int,
    season_length: int,
) -> np.ndarray:
    """Forecast by repeating the most recent seasonal pattern."""
    if len(history) < season_length:
        raise ValueError(
            "History must contain at least one complete seasonal cycle."
        )

    if horizon < 1:
        raise ValueError("Forecast horizon must be at least one step.")

    pattern = history.iloc[-season_length:].to_numpy(dtype=float)

    repetitions = int(np.ceil(horizon / season_length))

    return np.tile(pattern, repetitions)[:horizon]


def arima_forecast(
    history: pd.Series,
    horizon: int,
    order: tuple[int, int, int],
) -> np.ndarray:
    """Fit ARIMA and forecast the requested horizon."""
    model = ARIMA(
        history,
        order=order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    fitted = model.fit()

    forecast = fitted.forecast(steps=horizon)

    return np.asarray(forecast, dtype=float)


def build_feature_frame(series: pd.Series) -> pd.DataFrame:
    """Build the store-day feature frame, mirroring the Phase 10 families.

    The Phase 10 matrix defines these features at the item-store grain.
    Phase 11-13 forecast daily store-level demand, so the same feature
    families are recomputed on the densified store-day series: lags use the
    previous observations, rollings use the shifted series (excluding the
    current day), and the calendar features come from the date itself. Every
    feature therefore uses only information available before the day it
    describes.
    """
    values = series.astype(float)

    frame = pd.DataFrame(index=series.index)
    frame["quantity"] = values

    for lag in (1, 7, 14, 28):
        frame[f"lag_{lag}"] = values.shift(lag)

    previous = values.shift(1)
    frame["rolling_mean_7"] = previous.rolling(7, min_periods=1).mean()
    frame["rolling_std_7"] = previous.rolling(7, min_periods=2).std()
    frame["rolling_mean_28"] = previous.rolling(28, min_periods=1).mean()
    frame["rolling_std_28"] = previous.rolling(28, min_periods=2).std()

    index = frame.index
    frame["day_of_week"] = index.dayofweek
    frame["day_of_month"] = index.day
    frame["week_of_year"] = index.isocalendar().week.astype("int16")
    frame["month"] = index.month
    frame["quarter"] = index.quarter
    frame["year"] = index.year
    frame["is_weekend"] = (index.dayofweek >= 5).astype("int8")
    frame["series_age_days"] = (index - index.min()).days

    return frame


def build_feature_model() -> HistGradientBoostingRegressor:
    """Create the deterministic feature-based learner."""
    return HistGradientBoostingRegressor(
        loss="squared_error",
        learning_rate=0.1,
        max_iter=200,
        max_depth=3,
        min_samples_leaf=5,
        l2_regularization=1.0,
        early_stopping=False,
        random_state=0,
    )


def feature_forecast(
    history: pd.Series,
    horizon: int,
) -> np.ndarray:
    """Recursively forecast with the store-day feature model.

    The model is fitted on the history's feature frame and then applied one
    step at a time. Each step rebuilds the feature frame on the history
    extended with the predictions made so far, so the lag and rolling
    features always describe demand that was available before the day being
    forecast -- the same relationship the training frame encodes.
    """
    if history.empty:
        raise ValueError("History cannot be empty.")

    if horizon < 1:
        raise ValueError("Forecast horizon must be at least one step.")

    frame = build_feature_frame(history)

    model = build_feature_model()
    model.fit(
        frame.loc[:, list(FEATURE_COLUMNS)],
        frame["quantity"].to_numpy(dtype=float),
    )

    working = history.astype(float)

    predictions: list[float] = []

    for _ in range(horizon):
        next_date = working.index[-1] + pd.Timedelta(days=1)

        extended = pd.concat(
            [
                working,
                pd.Series(
                    [np.nan],
                    index=pd.DatetimeIndex([next_date]),
                    name=working.name,
                ),
            ]
        )

        features = build_feature_frame(extended).iloc[[-1]].loc[
            :, list(FEATURE_COLUMNS)
        ]

        predicted = float(model.predict(features)[0])
        predictions.append(predicted)

        working = pd.concat(
            [
                working,
                pd.Series(
                    [predicted],
                    index=pd.DatetimeIndex([next_date]),
                    name=working.name,
                ),
            ]
        )

    return np.asarray(predictions, dtype=float)


def forecast_configuration(
    history: pd.Series,
    horizon: int,
    configuration: ModelConfiguration,
) -> np.ndarray:
    """Dispatch a typed configuration to its forecast function."""
    if configuration.model == "naive":
        return naive_forecast(history, horizon)

    if configuration.model == "seasonal_naive":
        if configuration.season_length is None:
            raise ValueError("Seasonal Naive requires season_length.")

        return seasonal_naive_forecast(
            history,
            horizon,
            configuration.season_length,
        )

    if configuration.model == "arima":
        if configuration.order is None:
            raise ValueError("ARIMA requires an order.")

        return arima_forecast(history, horizon, configuration.order)

    if configuration.model == FEATURE_MODEL:
        return feature_forecast(history, horizon)

    raise ValueError(f"Unsupported model: {configuration.model}")


# --- Cross-validation --------------------------------------------------


def create_cv_folds(
    series: pd.Series,
    horizon: int = CV_HORIZON,
    folds: int = CV_FOLDS,
    min_train: int = MIN_TRAIN_OBSERVATIONS,
) -> list[tuple[pd.Series, pd.Series]]:
    """Create expanding-window time-series CV folds.

    The requested fold count is used when the series can afford it.
    Shorter series -- notably store 4, which first appears mid-way through
    the training period -- use the largest fold count their history
    supports while keeping the forecast horizon fixed and preserving a
    minimum initial training sample. A series that cannot support a single
    fold raises rather than being silently dropped.
    """
    if horizon < 1:
        raise ValueError("Cross-validation horizon must be positive.")

    if min_train < 1:
        raise ValueError("Minimum training size must be positive.")

    if folds < 1:
        raise ValueError("Fold count must be positive.")

    affordable = (len(series) - min_train) // horizon

    if affordable < 1:
        raise ValueError(
            "Series is too short for the requested cross-validation setup: "
            f"{len(series)} observations cannot support a {horizon}-day "
            f"fold with {min_train} initial training observations."
        )

    fold_count = min(folds, affordable)

    initial_train_size = len(series) - horizon * fold_count

    results: list[tuple[pd.Series, pd.Series]] = []

    for fold_number in range(fold_count):
        train_end = initial_train_size + fold_number * horizon
        validation_end = train_end + horizon

        history = series.iloc[:train_end]
        actual = series.iloc[train_end:validation_end]

        results.append((history, actual))

    return results


def evaluate_configuration(
    history: pd.Series,
    actual: pd.Series,
    configuration: ModelConfiguration,
) -> tuple[float, float, np.ndarray]:
    """Evaluate one configuration on one fold and return its forecast."""
    horizon = len(actual)

    predicted = forecast_configuration(history, horizon, configuration)

    fold_rmse, fold_mape = evaluate_forecast(actual, predicted)

    return fold_rmse, fold_mape, predicted


def build_configurations() -> list[ModelConfiguration]:
    """Build the candidate model configuration list."""
    configurations = [
        ModelConfiguration(
            model="naive",
            configuration="last observed value",
        )
    ]

    configurations.extend(
        ModelConfiguration(
            model="seasonal_naive",
            configuration=f"season_length={period}",
            season_length=period,
        )
        for period in SEASONAL_PERIODS
    )

    configurations.extend(
        ModelConfiguration(
            model="arima",
            configuration=(
                f"order={order}; "
                "enforce_stationarity=False; "
                "enforce_invertibility=False"
            ),
            order=order,
        )
        for order in ARIMA_ORDERS
    )

    configurations.append(
        ModelConfiguration(
            model=FEATURE_MODEL,
            configuration=FEATURE_MODEL_DESCRIPTION,
        )
    )

    return configurations


def run_cross_validation(
    data: pd.DataFrame,
    configurations: list[ModelConfiguration],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run time-series CV for every store and candidate configuration.

    Returns the per-fold results, the explicitly recorded skipped stores
    and the per-fold predictions.
    """
    records: list[dict[str, object]] = []
    skipped_records: list[dict[str, object]] = []
    prediction_records: list[dict[str, object]] = []

    stores = [int(store) for store in sorted(data["store_id"].unique())]

    for store_id in stores:
        try:
            train_series = get_store_series(
                data,
                store_id,
                TRAIN_SPLIT,
            )

            folds = create_cv_folds(train_series)
        except EXPECTED_EVALUATION_ERRORS as exc:
            skipped_records.append(
                {
                    "store_id": store_id,
                    "training_observations": int(
                        (
                            (data["store_id"] == store_id)
                            & (data["split"] == TRAIN_SPLIT)
                        ).sum()
                    ),
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        for configuration in configurations:
            for fold_number, (history, actual) in enumerate(
                folds,
                start=1,
            ):
                fields = configuration_fields(configuration)

                try:
                    fold_rmse, fold_mape, predicted = evaluate_configuration(
                        history,
                        actual,
                        configuration,
                    )
                except EXPECTED_EVALUATION_ERRORS as exc:
                    records.append(
                        {
                            "store_id": store_id,
                            "model": configuration.model,
                            "configuration": configuration.configuration,
                            **fields,
                            "cv_fold": fold_number,
                            "fold_train_start": history.index.min().date(),
                            "fold_train_end": history.index.max().date(),
                            "fold_test_start": actual.index.min().date(),
                            "fold_test_end": actual.index.max().date(),
                            "horizon": len(actual),
                            "rmse": np.nan,
                            "mape_percent": np.nan,
                            "status": f"failed: {type(exc).__name__}",
                        }
                    )
                    continue

                records.append(
                    {
                        "store_id": store_id,
                        "model": configuration.model,
                        "configuration": configuration.configuration,
                        **fields,
                        "cv_fold": fold_number,
                        "fold_train_start": history.index.min().date(),
                        "fold_train_end": history.index.max().date(),
                        "fold_test_start": actual.index.min().date(),
                        "fold_test_end": actual.index.max().date(),
                        "horizon": len(actual),
                        "rmse": fold_rmse,
                        "mape_percent": fold_mape,
                        "status": "success",
                    }
                )

                prediction_records.extend(
                    {
                        "scope": "cv_fold",
                        "store_id": store_id,
                        "model": configuration.model,
                        "configuration": configuration.configuration,
                        "cv_fold": fold_number,
                        "date": date,
                        "actual": float(observed),
                        "predicted": float(predicted_value),
                    }
                    for date, observed, predicted_value in zip(
                        actual.index,
                        actual.to_numpy(dtype=float),
                        predicted,
                    )
                )

    return (
        pd.DataFrame(records),
        pd.DataFrame(
            skipped_records,
            columns=["store_id", "training_observations", "reason"],
        ),
        pd.DataFrame(prediction_records),
    )


def summarize_cv_results(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize cross-validation results by store/configuration."""
    successful = results[results["status"] == "success"].copy()

    if successful.empty:
        raise RuntimeError("No successful cross-validation results.")

    summary = (
        successful.groupby(
            [
                "store_id",
                "model",
                "configuration",
                "season_length",
                "order",
            ],
            as_index=False,
        )
        .agg(
            cv_folds=("cv_fold", "count"),
            mean_rmse=("rmse", "mean"),
            mean_mape_percent=("mape_percent", "mean"),
            median_rmse=("rmse", "median"),
            median_mape_percent=("mape_percent", "median"),
        )
        .sort_values(
            ["store_id", "mean_rmse", "mean_mape_percent"]
        )
        .reset_index(drop=True)
    )

    return summary


def select_configurations(summary: pd.DataFrame) -> pd.DataFrame:
    """Select the lowest-CV-RMSE configuration for every store."""
    selected = (
        summary.sort_values(
            [
                "store_id",
                "mean_rmse",
                "mean_mape_percent",
            ]
        )
        .groupby("store_id", as_index=False)
        .first()
    )

    selected["selection_basis"] = (
        "lowest mean CV RMSE; mean CV MAPE used as secondary tie-break"
    )

    return selected


def _resolve_configuration(
    row: pd.Series,
    registry: dict[tuple[str, str], ModelConfiguration],
) -> ModelConfiguration:
    """Look a configuration up by identity. No string is ever parsed."""
    key = (str(row["model"]), str(row["configuration"]))

    if key not in registry:
        raise ValueError(f"Unresolved configuration: {key}")

    return registry[key]


def evaluate_selected_on_validation(
    data: pd.DataFrame,
    selected: pd.DataFrame,
    registry: dict[tuple[str, str], ModelConfiguration],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate selected configurations on the untouched validation period."""
    records: list[dict[str, object]] = []
    prediction_records: list[dict[str, object]] = []

    for row in selected.to_dict("records"):
        store_id = int(row["store_id"])

        configuration = _resolve_configuration(row, registry)

        train_series = get_store_series(
            data,
            store_id,
            TRAIN_SPLIT,
        )

        validation_series = get_store_series(
            data,
            store_id,
            VALIDATION_SPLIT,
        )

        predicted = forecast_configuration(
            train_series,
            len(validation_series),
            configuration,
        )

        validation_rmse, validation_mape = evaluate_forecast(
            validation_series,
            predicted,
        )

        fields = configuration_fields(configuration)

        records.append(
            {
                "store_id": store_id,
                "model": configuration.model,
                "configuration": configuration.configuration,
                **fields,
                "validation_start": validation_series.index.min().date(),
                "validation_end": validation_series.index.max().date(),
                "forecast_horizon": len(validation_series),
                "rmse": validation_rmse,
                "mape_percent": validation_mape,
            }
        )

        prediction_records.extend(
            {
                "scope": "validation",
                "store_id": store_id,
                "model": configuration.model,
                "configuration": configuration.configuration,
                "cv_fold": "",
                "date": date,
                "actual": float(observed),
                "predicted": float(predicted_value),
            }
            for date, observed, predicted_value in zip(
                validation_series.index,
                validation_series.to_numpy(dtype=float),
                predicted,
            )
        )

    return pd.DataFrame(records), pd.DataFrame(prediction_records)


def create_error_analysis(
    validation_predictions: pd.DataFrame,
) -> pd.DataFrame:
    """Create store-level validation error summaries from stored forecasts."""
    rows: list[dict[str, object]] = []

    if validation_predictions.empty:
        return pd.DataFrame(rows)

    for (store_id, model, configuration), group in (
        validation_predictions.sort_values("date").groupby(
            ["store_id", "model", "configuration"],
            sort=True,
        )
    ):
        errors = (
            group["actual"].to_numpy(dtype=float)
            - group["predicted"].to_numpy(dtype=float)
        )

        midpoint = len(errors) // 2

        segments = {
            "first_half": slice(0, midpoint),
            "second_half": slice(midpoint, None),
        }

        for segment_name, segment in segments.items():
            segment_errors = errors[segment]

            rows.append(
                {
                    "store_id": int(store_id),
                    "model": model,
                    "configuration": configuration,
                    "validation_segment": segment_name,
                    "mean_error": float(np.mean(segment_errors)),
                    "mean_absolute_error": float(
                        np.mean(np.abs(segment_errors))
                    ),
                    "rmse": float(np.sqrt(np.mean(segment_errors ** 2))),
                }
            )

    return pd.DataFrame(rows)


# --- Quality report ----------------------------------------------------


def _arrays_agree(
    first: pd.Series | np.ndarray,
    second: pd.Series | np.ndarray,
) -> bool:
    """Return True when two numeric arrays match element-wise."""
    first_values = np.asarray(first, dtype=float)
    second_values = np.asarray(second, dtype=float)

    if first_values.shape != second_values.shape:
        return False

    return bool(
        np.allclose(
            first_values,
            second_values,
            rtol=1e-9,
            atol=1e-9,
        )
    )


def _format_quantity(value: float) -> str:
    """Format a demand quantity without floating-point artefacts."""
    return f"{value:.3f}"


def _stored_predictions(
    predictions: pd.DataFrame,
    *,
    scope: str,
    store_id: int,
    model: str,
    configuration: str,
    cv_fold: int | None = None,
) -> pd.DataFrame:
    """Select stored predictions for one evaluation group."""
    subset = predictions[
        (predictions["scope"] == scope)
        & (predictions["store_id"] == store_id)
        & (predictions["model"] == model)
        & (predictions["configuration"] == configuration)
    ]

    if cv_fold is not None:
        subset = subset[subset["cv_fold"] == cv_fold]

    return subset.sort_values("date")


def create_quality_report(
    data: pd.DataFrame,
    source_facts: dict[str, float],
    configurations: list[ModelConfiguration],
    cv_results: pd.DataFrame,
    skipped: pd.DataFrame,
    cv_summary: pd.DataFrame,
    selected: pd.DataFrame,
    validation_results: pd.DataFrame,
    error_analysis: pd.DataFrame,
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    """Create machine-readable evaluation-quality checks."""
    rows = int(len(data))
    required_present = sum(
        column in data.columns for column in REQUIRED_COLUMNS
    )
    target_missing = int(data["quantity"].isna().sum())
    duplicate_days = int(data.duplicated(["date", "store_id"]).sum())

    source_quantity = float(source_facts["quantity"])
    daily_quantity = float(data["quantity"].sum())
    quantity_reconciled = bool(
        np.isclose(source_quantity, daily_quantity, rtol=1e-10, atol=1e-6)
    )

    source_rows = int(source_facts["rows"])
    rows_reconciled = source_rows >= rows and source_rows > 0

    store_ids = [int(store) for store in sorted(data["store_id"].unique())]
    store_count = len(store_ids)

    split_dates = data.groupby("split")["date"].agg(["min", "max"])

    boundaries_ok = bool(
        split_dates.loc[TRAIN_SPLIT, "max"] == TRAIN_END
        and split_dates.loc[VALIDATION_SPLIT, "min"]
        == TRAIN_END + pd.Timedelta(days=1)
        and split_dates.loc[VALIDATION_SPLIT, "max"] == VALIDATION_END
        and split_dates.loc[TEST_SPLIT, "min"] == TEST_START
        and split_dates.loc[TEST_SPLIT, "max"] == TEST_END
    )

    contiguous = bool(
        split_dates.loc[VALIDATION_SPLIT, "min"]
        == split_dates.loc[TRAIN_SPLIT, "max"] + pd.Timedelta(days=1)
        and split_dates.loc[TEST_SPLIT, "min"]
        == split_dates.loc[VALIDATION_SPLIT, "max"] + pd.Timedelta(days=1)
    )

    tuned_stores = sorted(int(store) for store in cv_results["store_id"].unique())
    store_coverage_ok = tuned_stores == store_ids

    train_series_by_store = {
        store_id: get_store_series(data, store_id, TRAIN_SPLIT)
        for store_id in store_ids
    }

    expected_rows = 0
    fold_checks_ok = True
    fold_rule_ok = True
    fold_horizon_ok = True
    fold_chronology_ok = True
    fold_expanding_ok = True
    minimum_training_ok = True

    for store_id in tuned_stores:
        train_series = train_series_by_store[store_id]
        folds = create_cv_folds(train_series)

        affordable = (len(train_series) - MIN_TRAIN_OBSERVATIONS) // CV_HORIZON
        expected_fold_count = min(CV_FOLDS, affordable)
        expected_rows += len(configurations) * expected_fold_count

        store_rows = cv_results[cv_results["store_id"] == store_id]

        if store_rows["cv_fold"].nunique() != expected_fold_count:
            fold_rule_ok = False

        if sorted(store_rows["horizon"].unique().tolist()) != [CV_HORIZON]:
            fold_horizon_ok = False

        previous_train_end = None
        previous_test_end = None

        for history, actual in folds:
            if len(history) < MIN_TRAIN_OBSERVATIONS:
                minimum_training_ok = False

            if history.index.max() >= actual.index.min():
                fold_chronology_ok = False

            if (
                previous_test_end is not None
                and actual.index.min() <= previous_test_end
            ):
                fold_chronology_ok = False

            if (
                previous_train_end is not None
                and len(history) <= previous_train_end
            ):
                fold_expanding_ok = False

            previous_train_end = len(history)
            previous_test_end = actual.index.max()

    if expected_rows != len(cv_results):
        fold_checks_ok = False

    if sorted(int(s) for s in skipped["store_id"].tolist()):
        # Any skipped store means the coverage contract was not met.
        store_coverage_ok = False

    cv_metrics_ok = True

    for row in cv_results.itertuples(index=False):
        group = _stored_predictions(
            predictions,
            scope="cv_fold",
            store_id=int(row.store_id),
            model=row.model,
            configuration=row.configuration,
            cv_fold=int(row.cv_fold),
        )

        if row.status != "success":
            # A recorded failure is honest, not a metric mismatch.
            continue

        if len(group) != int(row.horizon):
            cv_metrics_ok = False
            continue

        recomputed_rmse = rmse(
            group["actual"].to_numpy(dtype=float),
            group["predicted"].to_numpy(dtype=float),
        )
        recomputed_mape = mape(
            group["actual"].to_numpy(dtype=float),
            group["predicted"].to_numpy(dtype=float),
        )

        if not (
            np.isclose(recomputed_rmse, float(row.rmse), rtol=1e-9, atol=1e-9)
            and np.isclose(
                recomputed_mape,
                float(row.mape_percent),
                rtol=1e-9,
                atol=1e-9,
            )
        ):
            cv_metrics_ok = False

    summary_ok = True

    for row in cv_summary.itertuples(index=False):
        group = cv_results[
            (cv_results["store_id"] == row.store_id)
            & (cv_results["model"] == row.model)
            & (cv_results["configuration"] == row.configuration)
            & (cv_results["status"] == "success")
        ]

        if not (
            int(row.cv_folds) == len(group)
            and np.isclose(
                row.mean_rmse, group["rmse"].mean(), rtol=1e-9, atol=1e-9
            )
            and np.isclose(
                row.median_rmse,
                group["rmse"].median(),
                rtol=1e-9,
                atol=1e-9,
            )
        ):
            summary_ok = False

    selection_ok = True

    for store_id in store_ids:
        store_summary = cv_summary[cv_summary["store_id"] == store_id]

        if store_summary.empty:
            selection_ok = False
            continue

        ordered = store_summary.sort_values(
            ["mean_rmse", "mean_mape_percent"]
        )

        best = ordered.iloc[0]
        chosen = selected[selected["store_id"] == store_id].iloc[0]

        if not (
            chosen["model"] == best["model"]
            and chosen["configuration"] == best["configuration"]
            and np.isclose(
                chosen["mean_rmse"], best["mean_rmse"], rtol=1e-9, atol=1e-9
            )
        ):
            selection_ok = False

    registry_keys = {configuration_key(c) for c in configurations}
    resolution_ok = all(
        (str(row["model"]), str(row["configuration"])) in registry_keys
        for row in selected.to_dict("records")
    )

    feature_frame = build_feature_frame(train_series_by_store[store_ids[0]])

    feature_columns_present = sum(
        column in feature_frame.columns for column in FEATURE_COLUMNS
    )

    feature_values = train_series_by_store[store_ids[0]].to_numpy(dtype=float)

    lag_1_expected = np.concatenate([[np.nan], feature_values[:-1]])
    lag_1_ok = bool(
        np.allclose(
            feature_frame["lag_1"].to_numpy(dtype=float),
            lag_1_expected,
            rtol=1e-9,
            atol=1e-9,
            equal_nan=True,
        )
    )

    rolling_7_expected = np.full(len(feature_values), np.nan)
    for position in range(len(feature_values)):
        start = max(0, position - 7)
        window = feature_values[start:position]
        if len(window) > 0:
            rolling_7_expected[position] = float(np.mean(window))

    rolling_ok = bool(
        np.allclose(
            feature_frame["rolling_mean_7"].to_numpy(dtype=float),
            rolling_7_expected,
            rtol=1e-9,
            atol=1e-9,
            equal_nan=True,
        )
    )

    target_preserved = bool(
        np.allclose(
            feature_frame["quantity"].to_numpy(dtype=float),
            feature_values,
            rtol=1e-9,
            atol=1e-9,
        )
    )

    determinism_history, determinism_actual = create_cv_folds(
        train_series_by_store[store_ids[0]]
    )[0]

    determinism_ok = _arrays_agree(
        feature_forecast(determinism_history, len(determinism_actual)),
        feature_forecast(determinism_history, len(determinism_actual)),
    )

    validation_predictions = predictions[predictions["scope"] == "validation"]

    expected_validation_rows = 0

    for row in validation_results.itertuples(index=False):
        expected_validation_rows += int(row.forecast_horizon)

    validation_complete = bool(
        len(validation_predictions) == expected_validation_rows
        and len(validation_results) == store_count
    )

    validation_missing = int(
        validation_predictions[["actual", "predicted"]].isna().sum().sum()
    )

    validation_metrics_ok = True

    for row in validation_results.itertuples(index=False):
        group = _stored_predictions(
            predictions,
            scope="validation",
            store_id=int(row.store_id),
            model=row.model,
            configuration=row.configuration,
        )

        if len(group) != int(row.forecast_horizon):
            validation_metrics_ok = False
            continue

        actual_values = group["actual"].to_numpy(dtype=float)
        predicted_values = group["predicted"].to_numpy(dtype=float)

        if not (
            np.isclose(
                rmse(actual_values, predicted_values),
                float(row.rmse),
                rtol=1e-9,
                atol=1e-9,
            )
            and np.isclose(
                mape(actual_values, predicted_values),
                float(row.mape_percent),
                rtol=1e-9,
                atol=1e-9,
            )
        ):
            validation_metrics_ok = False

    error_ok = True

    for row in error_analysis.itertuples(index=False):
        group = _stored_predictions(
            predictions,
            scope="validation",
            store_id=int(row.store_id),
            model=row.model,
            configuration=row.configuration,
        )

        if group.empty:
            error_ok = False
            continue

        errors = (
            group["actual"].to_numpy(dtype=float)
            - group["predicted"].to_numpy(dtype=float)
        )

        midpoint = len(errors) // 2
        segment = (
            errors[:midpoint]
            if row.validation_segment == "first_half"
            else errors[midpoint:]
        )

        if not (
            np.isclose(
                row.mean_error,
                float(np.mean(segment)),
                rtol=1e-9,
                atol=1e-9,
            )
            and np.isclose(
                row.mean_absolute_error,
                float(np.mean(np.abs(segment))),
                rtol=1e-9,
                atol=1e-9,
            )
            and np.isclose(
                row.rmse,
                float(np.sqrt(np.mean(segment ** 2))),
                rtol=1e-9,
                atol=1e-9,
            )
        ):
            error_ok = False

    prediction_dates = predictions["date"].max()
    test_period_clean = bool(
        not pd.isna(prediction_dates)
        and pd.Timestamp(prediction_dates) < TEST_START
        and int((predictions["date"] >= TEST_START).sum()) == 0
    )

    test_rows = int((data["split"] == TEST_SPLIT).sum())

    checks = [
        ("input_rows_positive", rows > 0, rows, ">0"),
        (
            "input_required_columns_present",
            required_present == len(REQUIRED_COLUMNS),
            required_present,
            len(REQUIRED_COLUMNS),
        ),
        ("input_target_complete", target_missing == 0, target_missing, 0),
        ("store_day_keys_unique", duplicate_days == 0, duplicate_days, 0),
        (
            "source_rows_reconciled",
            rows_reconciled,
            rows,
            source_rows,
        ),
        (
            "source_quantity_reconciled",
            quantity_reconciled,
            _format_quantity(source_quantity),
            _format_quantity(daily_quantity),
        ),
        (
            "store_count_preserved",
            store_count == EXPECTED_STORES,
            store_count,
            EXPECTED_STORES,
        ),
        ("split_boundaries_exact", boundaries_ok, boundaries_ok, True),
        ("split_partitions_contiguous", contiguous, contiguous, True),
        (
            "store_coverage_complete",
            store_coverage_ok,
            len(tuned_stores),
            store_count,
        ),
        (
            "configuration_coverage_complete",
            fold_checks_ok,
            len(cv_results),
            expected_rows,
        ),
        ("fold_horizon_fixed", fold_horizon_ok, fold_horizon_ok, True),
        (
            "fold_count_rule_applied",
            fold_rule_ok,
            fold_rule_ok,
            True,
        ),
        (
            "fold_windows_chronological",
            fold_chronology_ok,
            fold_chronology_ok,
            True,
        ),
        (
            "fold_windows_expanding",
            fold_expanding_ok,
            fold_expanding_ok,
            True,
        ),
        (
            "fold_minimum_training_respected",
            minimum_training_ok,
            minimum_training_ok,
            True,
        ),
        (
            "cv_metrics_reproduced_from_predictions",
            cv_metrics_ok,
            cv_metrics_ok,
            True,
        ),
        (
            "cv_summary_reconciles_with_results",
            summary_ok,
            summary_ok,
            True,
        ),
        ("selection_rule_verified", selection_ok, selection_ok, True),
        (
            "selected_configurations_resolve",
            resolution_ok,
            resolution_ok,
            True,
        ),
        (
            "feature_columns_complete",
            feature_columns_present == len(FEATURE_COLUMNS),
            feature_columns_present,
            len(FEATURE_COLUMNS),
        ),
        (
            "feature_lag_matches_previous_observation",
            lag_1_ok,
            lag_1_ok,
            True,
        ),
        (
            "feature_rolling_excludes_current",
            rolling_ok,
            rolling_ok,
            True,
        ),
        (
            "feature_target_preserved",
            target_preserved,
            target_preserved,
            True,
        ),
        (
            "feature_forecast_deterministic",
            determinism_ok,
            determinism_ok,
            True,
        ),
        (
            "predictions_avoid_test_period",
            test_period_clean,
            test_period_clean,
            True,
        ),
        (
            "validation_predictions_complete",
            validation_complete and validation_missing == 0,
            len(validation_predictions),
            expected_validation_rows,
        ),
        (
            "validation_metrics_reproduced_from_predictions",
            validation_metrics_ok,
            validation_metrics_ok,
            True,
        ),
        (
            "error_analysis_reconciles_with_predictions",
            error_ok,
            error_ok,
            True,
        ),
        ("test_partition_present_but_unused", test_rows > 0, test_rows, ">0"),
    ]

    return pd.DataFrame(checks, columns=QUALITY_COLUMNS)


# --- Findings ----------------------------------------------------------


PHASE11_PREDICTIONS_PATH = OUTPUT_DIR / "forecasting_predictions.csv"


def reconcile_with_phase11(
    validation_results: pd.DataFrame,
    validation_predictions: pd.DataFrame,
) -> tuple[int, int, float]:
    """Compare Phase 12 classical forecasts against Phase 11's.

    Phase 11 published per-store naive, seasonal-naive (7) and ARIMA(1,1,1)
    forecasts. Where a Phase 12 selected configuration uses the same model
    and the same parameters, the validation forecasts must match exactly.
    Returns (compared, matched, maximum absolute difference).
    """
    if not PHASE11_PREDICTIONS_PATH.exists():
        return 0, 0, 0.0

    phase11 = pd.read_csv(
        PHASE11_PREDICTIONS_PATH,
        parse_dates=["date"],
    )

    compared = 0
    matched = 0
    maximum_difference = 0.0

    for row in validation_results.to_dict("records"):
        model = str(row["model"])

        if model == "seasonal_naive" and int(row["season_length"]) != 7:
            continue

        if model == "arima" and str(row["order"]) != str((1, 1, 1)):
            continue

        if model not in {"naive", "seasonal_naive", "arima"}:
            continue

        observed_frame = _stored_predictions(
            validation_predictions,
            scope="validation",
            store_id=int(row["store_id"]),
            model=model,
            configuration=str(row["configuration"]),
        )

        reference = phase11[
            (phase11["store_id"] == int(row["store_id"]))
            & (phase11["model"] == model)
        ].sort_values("date")

        if reference.empty or len(reference) != len(observed_frame):
            continue

        observed = observed_frame["predicted"].to_numpy(dtype=float)
        expected = reference["predicted"].to_numpy(dtype=float)

        compared += 1
        difference = float(np.max(np.abs(observed - expected)))
        maximum_difference = max(maximum_difference, difference)

        if np.allclose(observed, expected, rtol=1e-9, atol=1e-6):
            matched += 1

    return compared, matched, maximum_difference


def write_findings(
    source_facts: dict[str, float],
    configurations: list[ModelConfiguration],
    skipped: pd.DataFrame,
    selected: pd.DataFrame,
    validation_results: pd.DataFrame,
    validation_predictions: pd.DataFrame,
    quality_report: pd.DataFrame,
) -> None:
    """Write a concise reproducibility and findings report."""
    failed_checks = quality_report.loc[
        ~quality_report["passed"].astype(bool),
        "check",
    ].tolist()

    overall = (
        validation_results.groupby("model", as_index=False)
        .agg(
            stores=("store_id", "nunique"),
            mean_rmse=("rmse", "mean"),
            mean_mape_percent=("mape_percent", "mean"),
        )
        .sort_values("mean_rmse")
    )

    compared, matched, maximum_difference = reconcile_with_phase11(
        validation_results,
        validation_predictions,
    )

    store_ids = sorted(int(store) for store in selected["store_id"].unique())

    lines = [
        "Phase 12 — Model Evaluation & Tuning",
        "",
        "Input reconciliation (Phase 10 feature-engineered dataset):",
        f"- source rows: {int(source_facts['rows']):,}",
        (
            "- source quantity: "
            f"{_format_quantity(float(source_facts['quantity']))}"
        ),
        f"- stores: {len(store_ids)}",
        "",
        "Cross-validation design:",
        f"- folds requested per store: {CV_FOLDS}",
        f"- forecast horizon: {CV_HORIZON} days",
        (
            "- minimum initial training sample: "
            f"{MIN_TRAIN_OBSERVATIONS} observations"
        ),
        (
            "- fold rule: the requested fold count is used when the store's "
            "history can afford it, otherwise the largest affordable count "
            "is used so every store is tuned"
        ),
        f"- candidate configurations: {len(configurations)}",
        "",
        "Store coverage:",
        f"- stores tuned: {', '.join(str(store) for store in store_ids)}",
        (
            "- stores skipped: "
            + (
                ", ".join(str(int(s)) for s in skipped["store_id"].tolist())
                if not skipped.empty
                else "none"
            )
        ),
        "",
        "Selected configurations by store (training-period CV):",
        selected[
            [
                "store_id",
                "model",
                "configuration",
                "cv_folds",
                "mean_rmse",
                "mean_mape_percent",
            ]
        ].to_string(index=False),
        "",
        "Validation performance of selected configurations:",
        overall.to_string(index=False),
        "",
        "Feature-based candidate:",
        f"- model: {FEATURE_MODEL} ({FEATURE_MODEL_DESCRIPTION})",
        (
            "- features: "
            f"{len(FEATURE_COLUMNS)} store-day lag, rolling and calendar "
            "features mirroring the Phase 10 families"
        ),
        (
            "- selected by: "
            + (
                ", ".join(
                    str(int(row["store_id"]))
                    for row in selected.to_dict("records")
                    if row["model"] == FEATURE_MODEL
                )
                or "no store"
            )
        ),
        "",
        "Phase 11 reconciliation:",
        (
            f"- {matched}/{compared} selected classical configurations "
            "reproduce the Phase 11 validation forecasts exactly "
            f"(maximum absolute difference {maximum_difference:.6g})"
            if compared
            else "- no selected configuration matches a Phase 11 model"
        ),
        "",
        "Interpretation:",
        "RMSE is the primary configuration-selection metric.",
        "MAPE is reported as a complementary percentage-based metric.",
        "MAPE excludes observations where actual demand equals zero.",
        "Tuning uses only the training period.",
        "The test period is not used for model selection or tuning.",
        "Validation results should not be interpreted as final test "
        "performance.",
        "",
        "Quality checks: "
        + (
            f"all {len(quality_report)} passed"
            if not failed_checks
            else f"{len(failed_checks)} failed"
        ),
    ]

    if failed_checks:
        lines.extend(f"- failed: {check}" for check in failed_checks)

    FINDINGS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run Phase 12 model evaluation and tuning."""
    print("Running Phase 12 model evaluation and tuning...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data, source_facts = load_daily_store_demand()

    validate_splits(data)

    configurations = build_configurations()

    registry = {
        configuration_key(configuration): configuration
        for configuration in configurations
    }

    cv_results, skipped, cv_predictions = run_cross_validation(
        data,
        configurations,
    )

    if cv_results.empty:
        raise RuntimeError("No cross-validation results were produced.")

    cv_summary = summarize_cv_results(cv_results)

    selected = select_configurations(cv_summary)

    validation_results, validation_predictions = (
        evaluate_selected_on_validation(data, selected, registry)
    )

    error_analysis = create_error_analysis(validation_predictions)

    predictions = pd.concat(
        [cv_predictions, validation_predictions],
        ignore_index=True,
    )

    quality_report = create_quality_report(
        data,
        source_facts,
        configurations,
        cv_results,
        skipped,
        cv_summary,
        selected,
        validation_results,
        error_analysis,
        predictions,
    )

    if not bool(quality_report["passed"].all()):
        failed = quality_report.loc[
            ~quality_report["passed"],
            "check",
        ].tolist()

        raise RuntimeError(
            "One or more evaluation-quality checks failed: "
            f"{failed}"
        )

    cv_results.to_csv(RESULTS_PATH, index=False)
    cv_summary.to_csv(SUMMARY_PATH, index=False)
    selected.to_csv(SELECTED_PATH, index=False)
    validation_results.to_csv(VALIDATION_PATH, index=False)
    error_analysis.to_csv(ERROR_PATH, index=False)
    predictions.to_csv(
        PREDICTIONS_PATH,
        index=False,
        float_format="%.12g",
        date_format="%Y-%m-%d",
    )
    quality_report.to_csv(QUALITY_PATH, index=False)

    write_findings(
        source_facts,
        configurations,
        skipped,
        selected,
        validation_results,
        validation_predictions,
        quality_report,
    )

    print("Model evaluation and tuning completed successfully.")
    print(f"CV results: {RESULTS_PATH}")
    print(f"CV summary: {SUMMARY_PATH}")
    print(f"Selected models: {SELECTED_PATH}")
    print(f"Validation results: {VALIDATION_PATH}")
    print(f"Error analysis: {ERROR_PATH}")
    print(f"Predictions: {PREDICTIONS_PATH}")
    print(f"Quality report: {QUALITY_PATH}")


if __name__ == "__main__":
    main()
