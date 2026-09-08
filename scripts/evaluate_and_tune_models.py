"""Evaluate and tune the Phase 12 retail demand forecasting models.

The implementation performs time-aware cross-validation using only the
training period, tunes Seasonal Naive and ARIMA configurations, evaluates
the selected configurations on the untouched validation period, and writes
reproducible evaluation artifacts.

The final test period is intentionally excluded from model selection and
tuning.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.linalg import LinAlgError
from statsmodels.tools.sm_exceptions import MissingDataError
from statsmodels.tsa.arima.model import ARIMA

# Exceptions that a CV-fold evaluation can legitimately raise: bad/insufficient
# input data (ValueError, raised explicitly throughout this module and by
# statsmodels for malformed input), NaNs reaching the ARIMA fitter
# (MissingDataError), and numerically singular/ill-conditioned ARIMA fits
# (LinAlgError). Anything outside this set is a bug, not an expected fold
# failure, and should propagate instead of being recorded as "failed".
EXPECTED_EVALUATION_ERRORS = (ValueError, MissingDataError, LinAlgError)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "feature_engineered_daily.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"

RESULTS_PATH = OUTPUT_DIR / "model_tuning_results.csv"
SUMMARY_PATH = OUTPUT_DIR / "model_tuning_summary.csv"
SELECTED_PATH = OUTPUT_DIR / "selected_model_configurations.csv"
VALIDATION_PATH = OUTPUT_DIR / "tuned_validation_results.csv"
ERROR_PATH = OUTPUT_DIR / "model_error_analysis.csv"
FINDINGS_PATH = OUTPUT_DIR / "model_evaluation_findings.txt"

TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "validation"
TEST_SPLIT = "test"

CV_FOLDS = 3
CV_HORIZON = 28

SEASONAL_PERIODS = (7, 14, 28)
ARIMA_ORDERS = (
    (0, 1, 1),
    (1, 1, 0),
    (1, 1, 1),
    (2, 1, 1),
)


@dataclass(frozen=True)
class ModelConfiguration:
    """Represent one forecasting configuration."""

    model: str
    configuration: str
    season_length: int | None = None
    order: tuple[int, int, int] | None = None


def rmse(actual: pd.Series, predicted: np.ndarray) -> float:
    """Calculate root mean squared error."""
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)

    if len(actual_values) != len(predicted_values):
        raise ValueError(
            "Actual and predicted values must have equal lengths.")

    return float(
        np.sqrt(np.mean((actual_values - predicted_values) ** 2))
    )


def mape(actual: pd.Series, predicted: np.ndarray) -> float:
    """Calculate MAPE while excluding zero-actual observations."""
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)

    if len(actual_values) != len(predicted_values):
        raise ValueError(
            "Actual and predicted values must have equal lengths.")

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


def load_daily_store_demand() -> pd.DataFrame:
    """Load the large feature dataset in chunks and aggregate by date/store."""
    required_columns = ["date", "store_id", "quantity", "split"]

    daily_parts: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=required_columns,
        parse_dates=["date"],
        chunksize=250_000,
    ):
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

    return combined


def validate_splits(data: pd.DataFrame) -> None:
    """Validate chronological split ordering."""
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

    # Reindex onto a complete daily calendar so every model sees a regularly
    # spaced index with an explicit frequency -- ARIMA's out-of-sample
    # forecasting requires this, and it's what silences the "no frequency
    # information" warnings. It also means lag/seasonal windows correspond
    # to actual calendar days rather than "nth observed row", which matters
    # because Phase 9 preserves missing dates instead of zero-filling them.
    # At this store-aggregate grain, an absent date means no quantity was
    # recorded for that store that day, so zero-filling here is correct.
    full_index = pd.date_range(
        series.index.min(),
        series.index.max(),
        freq="D",
    )

    series = series.reindex(full_index, fill_value=0.0)
    series.index.freq = "D"

    return series


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

    pattern = history.iloc[-season_length:].to_numpy(dtype=float)

    repetitions = int(np.ceil(horizon / season_length))

    return np.tile(pattern, repetitions)[:horizon]


def naive_forecast(
    history: pd.Series,
    horizon: int,
) -> np.ndarray:
    """Forecast using the last observed value."""
    if history.empty:
        raise ValueError("History cannot be empty.")

    return np.repeat(float(history.iloc[-1]), horizon)


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


def create_cv_folds(
    series: pd.Series,
    horizon: int = CV_HORIZON,
    folds: int = CV_FOLDS,
) -> list[tuple[pd.Series, pd.Series]]:
    """Create expanding-window time-series CV folds."""
    if len(series) <= horizon * folds:
        raise ValueError(
            "Series is too short for the requested cross-validation setup."
        )

    initial_train_size = len(series) - horizon * folds

    results: list[tuple[pd.Series, pd.Series]] = []

    for fold_number in range(folds):
        train_end = initial_train_size + fold_number * horizon
        validation_end = train_end + horizon

        history = series.iloc[:train_end]
        actual = series.iloc[train_end:validation_end]

        results.append((history, actual))

    return results


def evaluate_forecast(
    actual: pd.Series,
    predicted: np.ndarray,
) -> tuple[float, float]:
    """Return RMSE and MAPE for a forecast."""
    return rmse(actual, predicted), mape(actual, predicted)


def evaluate_configuration(
    history: pd.Series,
    actual: pd.Series,
    configuration: ModelConfiguration,
) -> tuple[float, float]:
    """Evaluate one configuration on one CV fold."""
    horizon = len(actual)

    if configuration.model == "naive":
        predicted = naive_forecast(history, horizon)

    elif configuration.model == "seasonal_naive":
        if configuration.season_length is None:
            raise ValueError("Seasonal Naive requires season_length.")

        predicted = seasonal_naive_forecast(
            history,
            horizon,
            configuration.season_length,
        )

    elif configuration.model == "arima":
        if configuration.order is None:
            raise ValueError("ARIMA requires an order.")

        predicted = arima_forecast(
            history,
            horizon,
            configuration.order,
        )

    else:
        raise ValueError(
            f"Unsupported model: {configuration.model}"
        )

    return evaluate_forecast(actual, predicted)


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

    return configurations


def run_cross_validation(
    data: pd.DataFrame,
    configurations: list[ModelConfiguration],
) -> pd.DataFrame:
    """Run time-series CV for every store and candidate configuration."""
    records: list[dict[str, object]] = []

    stores = sorted(data["store_id"].astype(int).unique())

    for store_id in stores:
        try:
            train_series = get_store_series(
                data,
                store_id,
                TRAIN_SPLIT,
            )

            folds = create_cv_folds(train_series)
        except EXPECTED_EVALUATION_ERRORS as exc:
            print(
                f"  skipping store_id={store_id!r}: "
                f"{type(exc).__name__}: {exc}"
            )
            continue

        for configuration in configurations:
            for fold_number, (history, actual) in enumerate(
                folds,
                start=1,
            ):
                try:
                    fold_rmse, fold_mape = evaluate_configuration(
                        history,
                        actual,
                        configuration,
                    )

                    records.append(
                        {
                            "store_id": store_id,
                            "model": configuration.model,
                            "configuration": configuration.configuration,
                            "cv_fold": fold_number,
                            "horizon": len(actual),
                            "rmse": fold_rmse,
                            "mape_percent": fold_mape,
                            "status": "success",
                        }
                    )

                except EXPECTED_EVALUATION_ERRORS as exc:
                    records.append(
                        {
                            "store_id": store_id,
                            "model": configuration.model,
                            "configuration": configuration.configuration,
                            "cv_fold": fold_number,
                            "horizon": len(actual),
                            "rmse": np.nan,
                            "mape_percent": np.nan,
                            "status": f"failed: {type(exc).__name__}",
                        }
                    )

    return pd.DataFrame(records)


def summarize_cv_results(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize cross-validation results by store/configuration."""
    successful = results[results["status"] == "success"].copy()

    if successful.empty:
        raise RuntimeError("No successful cross-validation results.")

    summary = (
        successful.groupby(
            ["store_id", "model", "configuration"],
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


def evaluate_selected_on_validation(
    data: pd.DataFrame,
    selected: pd.DataFrame,
) -> pd.DataFrame:
    """Evaluate selected configurations on the untouched validation period."""
    records: list[dict[str, object]] = []

    for row in selected.itertuples(index=False):
        store_id = int(row.store_id)

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

        model = str(row.model)
        configuration = str(row.configuration)

        if model == "naive":
            predicted = naive_forecast(
                train_series,
                len(validation_series),
            )

        elif model == "seasonal_naive":
            season_length = int(configuration.split("=")[1])

            predicted = seasonal_naive_forecast(
                train_series,
                len(validation_series),
                season_length,
            )

        elif model == "arima":
            order_text = configuration.split("order=")[1].split(";")[0]
            order = tuple(
                int(value.strip())
                for value in order_text.strip("()").split(",")
            )

            predicted = arima_forecast(
                train_series,
                len(validation_series),
                order,
            )

        else:
            raise ValueError(f"Unsupported selected model: {model}")

        validation_rmse, validation_mape = evaluate_forecast(
            validation_series,
            predicted,
        )

        records.append(
            {
                "store_id": store_id,
                "model": model,
                "configuration": configuration,
                "validation_start": validation_series.index.min().date(),
                "validation_end": validation_series.index.max().date(),
                "forecast_horizon": len(validation_series),
                "rmse": validation_rmse,
                "mape_percent": validation_mape,
            }
        )

    return pd.DataFrame(records)


def create_error_analysis(
    data: pd.DataFrame,
    validation_results: pd.DataFrame,
) -> pd.DataFrame:
    """Create store-level validation error summaries."""
    rows: list[dict[str, object]] = []

    for row in validation_results.itertuples(index=False):
        validation_series = get_store_series(
            data,
            int(row.store_id),
            VALIDATION_SPLIT,
        )

        train_series = get_store_series(
            data,
            int(row.store_id),
            TRAIN_SPLIT,
        )

        if row.model == "naive":
            predicted = naive_forecast(
                train_series,
                len(validation_series),
            )

        elif row.model == "seasonal_naive":
            season_length = int(
                str(row.configuration).split("=")[1]
            )
            predicted = seasonal_naive_forecast(
                train_series,
                len(validation_series),
                season_length,
            )

        elif row.model == "arima":
            order_text = (
                str(row.configuration)
                .split("order=")[1]
                .split(";")[0]
            )
            order = tuple(
                int(value.strip())
                for value in order_text.strip("()").split(",")
            )

            predicted = arima_forecast(
                train_series,
                len(validation_series),
                order,
            )

        else:
            raise ValueError(f"Unsupported model: {row.model}")

        actual = validation_series.to_numpy(dtype=float)
        errors = actual - predicted

        midpoint = len(errors) // 2

        segments = {
            "first_half": slice(0, midpoint),
            "second_half": slice(midpoint, None),
        }

        for segment_name, segment in segments.items():
            segment_errors = errors[segment]

            rows.append(
                {
                    "store_id": int(row.store_id),
                    "model": row.model,
                    "configuration": row.configuration,
                    "validation_segment": segment_name,
                    "mean_error": float(np.mean(segment_errors)),
                    "mean_absolute_error": float(
                        np.mean(np.abs(segment_errors))
                    ),
                    "rmse": float(
                        np.sqrt(np.mean(segment_errors ** 2))
                    ),
                }
            )

    return pd.DataFrame(rows)


def write_findings(
    cv_summary: pd.DataFrame,
    selected: pd.DataFrame,
    validation_results: pd.DataFrame,
) -> None:
    """Write a concise reproducibility and findings report."""
    overall = (
        validation_results.groupby("model", as_index=False)
        .agg(
            stores=("store_id", "nunique"),
            mean_rmse=("rmse", "mean"),
            mean_mape_percent=("mape_percent", "mean"),
        )
        .sort_values("mean_rmse")
    )

    lines = [
        "Phase 12 — Model Evaluation & Tuning",
        "",
        "Tuning uses only the training period.",
        "The test period is not used for model selection or tuning.",
        f"Cross-validation folds: {CV_FOLDS}",
        f"Cross-validation horizon: {CV_HORIZON} days",
        "",
        "Selected configurations by store:",
        selected[
            [
                "store_id",
                "model",
                "configuration",
                "mean_rmse",
                "mean_mape_percent",
            ]
        ].to_string(index=False),
        "",
        "Validation performance of selected configurations:",
        overall.to_string(index=False),
        "",
        "Interpretation:",
        "RMSE is the primary configuration-selection metric.",
        "MAPE is reported as a complementary percentage-based metric.",
        "MAPE excludes observations where actual demand equals zero.",
        "Validation results should not be interpreted as final test performance.",
    ]

    FINDINGS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run Phase 12 model evaluation and tuning."""
    print("Running Phase 12 model evaluation and tuning...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_daily_store_demand()

    validate_splits(data)

    configurations = build_configurations()

    cv_results = run_cross_validation(
        data,
        configurations,
    )

    cv_summary = summarize_cv_results(cv_results)

    selected = select_configurations(cv_summary)

    validation_results = evaluate_selected_on_validation(
        data,
        selected,
    )

    error_analysis = create_error_analysis(
        data,
        validation_results,
    )

    cv_results.to_csv(
        RESULTS_PATH,
        index=False,
    )

    cv_summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    selected.to_csv(
        SELECTED_PATH,
        index=False,
    )

    validation_results.to_csv(
        VALIDATION_PATH,
        index=False,
    )

    error_analysis.to_csv(
        ERROR_PATH,
        index=False,
    )

    write_findings(
        cv_summary,
        selected,
        validation_results,
    )

    print("Model evaluation and tuning completed successfully.")
    print(f"CV results: {RESULTS_PATH}")
    print(f"CV summary: {SUMMARY_PATH}")
    print(f"Selected models: {SELECTED_PATH}")
    print(f"Validation results: {VALIDATION_PATH}")
    print(f"Error analysis: {ERROR_PATH}")


if __name__ == "__main__":
    main()
