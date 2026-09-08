"""Tests for Phase 10 feature engineering."""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.feature_engineering import (
    KEY_COLUMNS,
    add_calendar_features,
    add_series_features,
    create_quality_report,
    prepare_features,
    validate_input_columns,
)


def make_sample_frame() -> pd.DataFrame:
    """Create a small deterministic retail time-series frame."""
    dates = pd.date_range("2024-01-01", periods=35, freq="D")

    return pd.DataFrame(
        {
            "date": dates,
            "item_id": ["item_1"] * 35,
            "store_id": [1] * 35,
            "quantity": list(range(1, 36)),
            "price_base": [10.0] * 35,
            "markdown_record_count": [0] * 35,
            "markdown_quantity": [0.0] * 35,
            "markdown_discount": [0.0] * 35,
            "discount_record_count": [0] * 35,
            "promo_discount_rate": [0.0] * 35,
            "price_change_count": [0] * 35,
            "split": ["train"] * 20
            + ["validation"] * 10
            + ["test"] * 5,
        }
    )


def test_required_columns_are_validated():
    frame = make_sample_frame()

    validate_input_columns(frame.columns.tolist())


def test_missing_column_fails_validation():
    frame = make_sample_frame().drop(columns=["quantity"])

    with pytest.raises(ValueError):
        validate_input_columns(frame.columns.tolist())


def test_calendar_features_are_created():
    result = add_calendar_features(make_sample_frame())

    expected = {
        "day_of_week",
        "day_of_month",
        "week_of_year",
        "month",
        "quarter",
        "year",
        "is_weekend",
    }

    assert expected.issubset(result.columns)


def test_calendar_values_are_correct():
    result = add_calendar_features(make_sample_frame())

    assert result.loc[0, "day_of_week"] == 0
    assert result.loc[0, "day_of_month"] == 1
    assert result.loc[0, "month"] == 1
    assert result.loc[0, "quarter"] == 1
    assert result.loc[0, "is_weekend"] == 0


def test_lag_features_use_previous_observations():
    result = add_series_features(make_sample_frame())

    assert pd.isna(result.loc[0, "lag_1"])
    assert result.loc[1, "lag_1"] == 1
    assert result.loc[7, "lag_7"] == 1
    assert result.loc[14, "lag_14"] == 1
    assert result.loc[28, "lag_28"] == 1


def test_rolling_features_exclude_current_target():
    result = add_series_features(make_sample_frame())

    assert pd.isna(result.loc[0, "rolling_mean_7"])
    assert result.loc[1, "rolling_mean_7"] == 1
    assert result.loc[7, "rolling_mean_7"] == 4


def test_series_age_starts_at_zero():
    result = add_series_features(make_sample_frame())

    assert result.loc[0, "series_age_days"] == 0
    assert result.loc[10, "series_age_days"] == 10


def test_feature_engineered_keys_are_unique():
    result = prepare_features(make_sample_frame())

    assert result.duplicated(KEY_COLUMNS).sum() == 0


def test_feature_engineering_preserves_target():
    source = make_sample_frame()
    result = prepare_features(source)

    pd.testing.assert_series_equal(
        result["quantity"].reset_index(drop=True),
        source["quantity"].reset_index(drop=True),
        check_names=False,
    )


def test_quality_report_passes_for_valid_data():
    result = prepare_features(make_sample_frame())
    report = create_quality_report(result)

    assert bool(report["passed"].all())
