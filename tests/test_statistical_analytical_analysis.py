"""Tests for Phase 8 statistical and analytical analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.statistical_analytical_analysis import (
    calculate_autocorrelation,
    calculate_correlations,
    calculate_price_analysis,
    calculate_promotion_analysis,
    calculate_summary,
    calculate_trend,
    safe_cv,
    validate_columns,
)


def test_required_columns_are_defined() -> None:
    """The integrated dataset must contain the required analysis fields."""
    columns = {
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    }

    validate_columns(list(columns))


def test_missing_required_column_fails() -> None:
    """Missing required fields must stop analysis."""
    with pytest.raises(ValueError):
        validate_columns(
            [
                "date",
                "item_id",
                "quantity",
                "price_base",
                "store_id",
            ]
        )


def test_safe_cv_returns_expected_value() -> None:
    """Coefficient of variation should be standard deviation divided by mean."""
    series = pd.Series([10.0, 20.0, 30.0])

    expected = series.std(ddof=1) / series.mean()

    assert safe_cv(series) == pytest.approx(expected)


def test_safe_cv_handles_zero_mean() -> None:
    """Zero-mean data should not cause division by zero."""
    series = pd.Series([0.0, 0.0, 0.0])

    assert np.isnan(safe_cv(series))


def test_summary_contains_expected_metrics() -> None:
    """Summary statistics should contain the main demand measures."""
    daily = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "quantity": [10.0, 20.0, 30.0],
            "revenue": [100.0, 200.0, 300.0],
            "records": [1, 1, 1],
            "average_price": [10.0, 10.0, 10.0],
        }
    )

    store = pd.DataFrame(
        {
            "store_id": [1, 2],
            "quantity": [30.0, 30.0],
            "revenue": [300.0, 300.0],
            "records": [2, 2],
        }
    )

    result = calculate_summary(daily, store)

    metrics = set(result["metric"])

    assert "daily_quantity_mean" in metrics
    assert "daily_quantity_std" in metrics
    assert "daily_quantity_cv" in metrics
    assert "store_count" in metrics


def test_correlation_identifies_relationship() -> None:
    """A constructed linear relationship should produce high correlation."""
    relationships = pd.DataFrame(
        {
            "quantity": [1, 2, 3, 4, 5],
            "price_base": [2, 4, 6, 8, 10],
        }
    )

    result = calculate_correlations(relationships)

    assert len(result) == 1
    assert result.iloc[0]["pearson_r"] == pytest.approx(1.0)


def test_price_analysis_returns_regression_statistics() -> None:
    """Price analysis should return correlation and regression statistics."""
    relationships = pd.DataFrame(
        {
            "quantity": [10, 20, 30, 40, 50],
            "price_base": [1, 2, 3, 4, 5],
        }
    )

    result = calculate_price_analysis(relationships)

    assert len(result) == 1
    assert "pearson_r" in result.columns
    assert "p_value" in result.columns
    assert "slope" in result.columns
    assert "r_squared" in result.columns


def test_promotion_analysis_groups_records() -> None:
    """Promotion analysis should separate promotional and non-promotional rows."""
    relationships = pd.DataFrame(
        {
            "quantity": [10, 20, 30, 40],
            "promo_discount_rate": [0.0, 0.0, 0.1, 0.2],
        }
    )

    result = calculate_promotion_analysis(relationships)

    assert len(result) == 2
    assert set(result["promotion_group"]) == {
        "promotion_discount_present",
        "no_promotion_discount",
    }


def test_autocorrelation_returns_requested_lags() -> None:
    """Autocorrelation output should contain one row per requested lag."""
    daily = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=20),
            "quantity": np.arange(20, dtype=float),
        }
    )

    result = calculate_autocorrelation(daily, max_lag=5)

    assert len(result) == 5
    assert result["lag_days"].tolist() == [1, 2, 3, 4, 5]


def test_trend_detects_positive_trend() -> None:
    """A constructed increasing series should have a positive slope."""
    daily = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "quantity": np.arange(10, dtype=float),
        }
    )

    result = calculate_trend(daily)

    assert len(result) == 1
    assert result.iloc[0]["slope_per_day"] > 0
    assert result.iloc[0]["r_squared"] == pytest.approx(1.0)
