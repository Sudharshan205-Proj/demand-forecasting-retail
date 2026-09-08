"""Tests for Phase 11 forecasting models."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.forecasting_models import (
    ARIMA_ORDER,
    SEASONAL_PERIOD,
    evaluate_forecast,
    mape,
    naive_forecast,
    rmse,
    seasonal_naive_forecast,
)


def test_naive_forecast_uses_last_observation():
    history = pd.Series([10.0, 20.0, 30.0])

    result = naive_forecast(history, 4)

    assert result.tolist() == [30.0, 30.0, 30.0, 30.0]


def test_naive_forecast_rejects_empty_history():
    with pytest.raises(ValueError):
        naive_forecast(pd.Series(dtype=float), 3)


def test_seasonal_naive_forecast_repeats_pattern():
    history = pd.Series(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    )

    result = seasonal_naive_forecast(
        history,
        10,
        season_length=7,
    )

    assert result.tolist() == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        1.0,
        2.0,
        3.0,
    ]


def test_seasonal_naive_requires_enough_history():
    history = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        seasonal_naive_forecast(
            history,
            2,
            season_length=SEASONAL_PERIOD,
        )


def test_rmse_is_zero_for_perfect_predictions():
    actual = np.array([1.0, 2.0, 3.0])
    predicted = np.array([1.0, 2.0, 3.0])

    assert rmse(actual, predicted) == 0.0


def test_rmse_calculates_expected_value():
    actual = np.array([1.0, 2.0])
    predicted = np.array([2.0, 4.0])

    assert rmse(actual, predicted) == pytest.approx(
        np.sqrt(2.5)
    )


def test_mape_excludes_zero_actual_values():
    actual = np.array([0.0, 100.0])
    predicted = np.array([50.0, 110.0])

    assert mape(actual, predicted) == pytest.approx(10.0)


def test_mape_returns_nan_when_all_actual_values_are_zero():
    actual = np.array([0.0, 0.0])
    predicted = np.array([1.0, 2.0])

    assert np.isnan(mape(actual, predicted))


def test_evaluation_requires_equal_lengths():
    actual = pd.Series([1.0, 2.0])
    predicted = np.array([1.0])

    with pytest.raises(ValueError):
        evaluate_forecast(actual, predicted)


def test_evaluation_returns_required_metrics():
    actual = pd.Series([10.0, 20.0])
    predicted = np.array([10.0, 20.0])

    result = evaluate_forecast(actual, predicted)

    assert set(result) == {"rmse", "mape_percent"}
    assert result["rmse"] == 0.0
    assert result["mape_percent"] == 0.0


def test_arima_configuration_is_explicit():
    assert ARIMA_ORDER == (1, 1, 1)
