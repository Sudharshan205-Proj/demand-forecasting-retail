"""Tests for Phase 12 model evaluation and tuning."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.evaluate_and_tune_models import (
    ModelConfiguration,
    create_cv_folds,
    mape,
    naive_forecast,
    rmse,
    seasonal_naive_forecast,
    select_configurations,
    validate_splits,
)


def test_rmse_is_zero_for_perfect_predictions() -> None:
    actual = pd.Series([1.0, 2.0, 3.0])
    predicted = np.array([1.0, 2.0, 3.0])

    assert rmse(actual, predicted) == 0.0


def test_mape_excludes_zero_actual_values() -> None:
    actual = pd.Series([0.0, 100.0])
    predicted = np.array([50.0, 110.0])

    assert mape(actual, predicted) == pytest.approx(10.0)


def test_mape_returns_nan_for_all_zero_actuals() -> None:
    actual = pd.Series([0.0, 0.0])
    predicted = np.array([1.0, 2.0])

    assert np.isnan(mape(actual, predicted))


def test_naive_forecast_repeats_last_value() -> None:
    history = pd.Series([10.0, 20.0, 30.0])

    forecast = naive_forecast(history, 3)

    assert forecast.tolist() == [30.0, 30.0, 30.0]


def test_seasonal_naive_repeats_pattern() -> None:
    history = pd.Series([1.0, 2.0, 3.0, 4.0])

    forecast = seasonal_naive_forecast(
        history,
        horizon=6,
        season_length=2,
    )

    assert forecast.tolist() == [
        3.0,
        4.0,
        3.0,
        4.0,
        3.0,
        4.0,
    ]


def test_seasonal_naive_rejects_insufficient_history() -> None:
    history = pd.Series([1.0, 2.0])

    with pytest.raises(ValueError):
        seasonal_naive_forecast(
            history,
            horizon=3,
            season_length=7,
        )


def test_create_cv_folds_preserves_temporal_order() -> None:
    index = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    series = pd.Series(
        np.arange(100, dtype=float),
        index=index,
    )

    folds = create_cv_folds(
        series,
        horizon=10,
        folds=3,
    )

    assert len(folds) == 3

    for history, actual in folds:
        assert history.index.max() < actual.index.min()


def test_create_cv_folds_is_expanding() -> None:
    index = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    series = pd.Series(
        np.arange(100, dtype=float),
        index=index,
    )

    folds = create_cv_folds(
        series,
        horizon=10,
        folds=3,
    )

    assert len(folds[0][0]) < len(folds[1][0])
    assert len(folds[1][0]) < len(folds[2][0])


def test_validate_splits_accepts_chronological_data() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "split": [
                "train",
                "validation",
                "test",
            ],
        }
    )

    validate_splits(data)


def test_validate_splits_rejects_temporal_leakage() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-03",
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "split": [
                "train",
                "validation",
                "test",
            ],
        }
    )

    with pytest.raises(ValueError):
        validate_splits(data)


def test_select_configurations_chooses_lowest_cv_rmse() -> None:
    summary = pd.DataFrame(
        {
            "store_id": [1, 1, 1, 2],
            "model": [
                "naive",
                "seasonal_naive",
                "arima",
                "naive",
            ],
            "configuration": [
                "last observed value",
                "season_length=7",
                "order=(1, 1, 1)",
                "last observed value",
            ],
            "cv_folds": [3, 3, 3, 3],
            "mean_rmse": [100.0, 50.0, 75.0, 20.0],
            "mean_mape_percent": [20.0, 10.0, 15.0, 5.0],
            "median_rmse": [100.0, 50.0, 75.0, 20.0],
            "median_mape_percent": [20.0, 10.0, 15.0, 5.0],
        }
    )

    selected = select_configurations(summary)

    store_one = selected[selected["store_id"] == 1].iloc[0]

    assert store_one["model"] == "seasonal_naive"
    assert store_one["configuration"] == "season_length=7"


def test_model_configuration_records_model_and_configuration() -> None:
    configuration = ModelConfiguration(
        model="arima",
        configuration="order=(1, 1, 1)",
        order=(1, 1, 1),
    )

    assert configuration.model == "arima"
    assert configuration.order == (1, 1, 1)
