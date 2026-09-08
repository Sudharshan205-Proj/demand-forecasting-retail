"""Train and evaluate classical retail demand forecasting models.

Phase 11 models:
- Naive baseline
- Seasonal-naive baseline
- ARIMA

The forecasting target is physical retail quantity.

The test period remains isolated from model selection. Models are
developed and compared using the training and validation periods.
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

FINDINGS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "forecasting_findings.txt"
)

TARGET = "quantity"

TRAIN_END = pd.Timestamp("2024-02-10")
VALIDATION_END = pd.Timestamp("2024-06-03")
TEST_END = pd.Timestamp("2024-09-26")

SEASONAL_PERIOD = 7
ARIMA_ORDER = (1, 1, 1)

REQUIRED_COLUMNS = [
    "date",
    "quantity",
    "split",
]


def validate_input_columns(columns: list[str]) -> None:
    """Validate the required forecasting input columns."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_daily_store_demand() -> pd.DataFrame:
    """Load and aggregate physical demand by date and store."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Forecasting input dataset not found: {INPUT_PATH}"
        )

    columns = pd.read_csv(INPUT_PATH, nrows=0).columns.tolist()
    validate_input_columns(columns)

    frame = pd.read_csv(
        INPUT_PATH,
        usecols=["date", "store_id", "quantity", "split"],
        parse_dates=["date"],
    )

    daily = (
        frame.groupby(["date", "store_id"], as_index=False)["quantity"]
        .sum()
        .sort_values(["store_id", "date"])
        .reset_index(drop=True)
    )

    return daily


def _to_regular_daily_series(series: pd.Series) -> pd.Series:
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
        series = (
            group.set_index("date")["quantity"]
            .sort_index()
        )

        if series.empty:
            raise ValueError(
                f"No observations found for store_id={store_id!r}"
            )

        yield store_id, _to_regular_daily_series(series)


def naive_forecast(
    history: pd.Series,
    horizon: int,
) -> np.ndarray:
    """Forecast every future point using the latest observation."""
    if history.empty:
        raise ValueError("Cannot create a naive forecast from empty history.")

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


def rmse(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> float:
    """Calculate root mean squared error."""
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    return float(
        np.sqrt(np.mean((actual_array - predicted_array) ** 2))
    )


def mape(
    actual: pd.Series | np.ndarray,
    predicted: pd.Series | np.ndarray,
) -> float:
    """Calculate MAPE while excluding zero-actual observations."""
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

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
    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and forecast lengths do not match."
        )

    return {
        "rmse": rmse(actual, predicted),
        "mape_percent": mape(actual, predicted),
    }


def run_models_for_store(
    series: pd.Series,
    store_id: int | str,
) -> tuple[list[dict], list[dict]]:
    """Run all Phase 11 models for one store."""
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

    results = []

    for model_name, fit_forecast in model_fitters.items():
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
                "validation_start": validation.index.min().date().isoformat(),
                "validation_end": validation.index.max().date().isoformat(),
                "forecast_horizon": horizon,
                "rmse": metrics["rmse"],
                "mape_percent": metrics["mape_percent"],
            }
        )

    configurations = [
        {
            "model": "naive",
            "store_id": store_id,
            "configuration": "last observed value",
        },
        {
            "model": "seasonal_naive",
            "store_id": store_id,
            "configuration": f"season_length={SEASONAL_PERIOD}",
        },
        {
            "model": "arima",
            "store_id": store_id,
            "configuration": (
                f"order={ARIMA_ORDER}; "
                "enforce_stationarity=False; "
                "enforce_invertibility=False"
            ),
        },
    ]

    return results, configurations


def create_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize validation performance across stores."""
    return (
        results.groupby("model", as_index=False)
        .agg(
            stores_evaluated=("store_id", "nunique"),
            mean_rmse=("rmse", "mean"),
            median_rmse=("rmse", "median"),
            mean_mape_percent=("mape_percent", "mean"),
            median_mape_percent=("mape_percent", "median"),
        )
        .sort_values("mean_rmse")
        .reset_index(drop=True)
    )


def write_findings(
    results: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    """Write a human-readable model findings report."""
    best_model = (
        summary.iloc[0]["model"]
        if not summary.empty
        else "not determined"
    )

    lines = [
        "Phase 11 — Forecasting Model Findings",
        "",
        "Models evaluated:",
        "- Naive baseline",
        "- Seasonal-naive baseline",
        "- ARIMA",
        "",
        "Forecasting target: physical retail quantity",
        "Validation period:",
        f"{TRAIN_END.date()} to {VALIDATION_END.date()}",
        "",
        f"Best model by mean validation RMSE: {best_model}",
        "",
        "MAPE excludes validation observations where actual quantity is zero.",
        "The test period is intentionally not used for model selection.",
        "",
        "Important limitation:",
        "ARIMA is evaluated on daily store-level demand rather than every",
        "item-store series because the dataset contains substantial gaps",
        "and thousands of sparse item-store series.",
        "",
    ]

    FINDINGS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Execute Phase 11 forecasting experiments."""
    print("Running Phase 11 forecasting models...")

    daily = load_daily_store_demand()

    all_results = []
    all_configurations = []

    for store_id, series in iter_store_series(daily):
        try:
            results, configurations = run_models_for_store(
                series,
                store_id,
            )
        except ValueError as error:
            print(f"  skipping store_id={store_id!r}: {error}")
            continue

        all_results.extend(results)
        all_configurations.extend(configurations)

    if not all_results:
        raise RuntimeError(
            "No forecasting results were produced for any store."
        )

    results_frame = pd.DataFrame(all_results)
    configurations_frame = pd.DataFrame(all_configurations)

    summary = create_summary(results_frame)

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

    write_findings(
        results_frame,
        summary,
    )

    print("Forecasting models completed successfully.")
    print(f"Results: {RESULTS_PATH}")
    print(f"Configurations: {CONFIG_PATH}")
    print(f"Summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
