"""Tests for Phase 13 forecasting and inventory insights."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.forecasting_inventory_insights import (
    SERVICE_LEVELS,
    calculate_inventory_scenarios,
    validate_training_demand,
)


def test_validate_training_demand_accepts_valid_data() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),
            "store_id": [1, 1],
            "quantity": [100.0, 120.0],
        }
    )

    validate_training_demand(data)


def test_validate_training_demand_rejects_missing_quantity() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),
            "store_id": [1, 1],
            "quantity": [100.0, np.nan],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_rejects_negative_quantity() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),
            "store_id": [1, 1],
            "quantity": [100.0, -1.0],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_rejects_duplicate_store_date() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01"]
            ),
            "store_id": [1, 1],
            "quantity": [100.0, 120.0],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_service_levels_have_expected_values() -> None:
    assert set(SERVICE_LEVELS) == {0.90, 0.95, 0.99}


def test_inventory_scenarios_calculate_reorder_point() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
        }
    )

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    scenario = scenarios[
        (scenarios["lead_time_days"] == 7)
        & (scenarios["service_level"] == 0.95)
    ].iloc[0]

    expected_lead_time_demand = 700.0

    expected_safety_stock = (
        SERVICE_LEVELS[0.95]
        * 10.0
        * np.sqrt(7)
    )

    expected_reorder_point = (
        expected_lead_time_demand
        + expected_safety_stock
    )

    assert scenario["expected_lead_time_demand"] == pytest.approx(
        expected_lead_time_demand
    )

    assert scenario["safety_stock"] == pytest.approx(
        expected_safety_stock
    )

    assert scenario["reorder_point"] == pytest.approx(
        expected_reorder_point
    )


def test_inventory_scenarios_include_all_lead_time_scenarios() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
        }
    )

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    assert sorted(
        scenarios["lead_time_days"].unique()
    ) == [7, 14, 28]


def test_longer_lead_time_increases_expected_demand() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
        }
    )

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    expected = (
        scenarios[
            scenarios["service_level"] == 0.95
        ]
        .sort_values("lead_time_days")
        ["expected_lead_time_demand"]
        .tolist()
    )

    assert expected == [700.0, 1400.0, 2800.0]


def test_higher_service_level_increases_safety_stock() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
        }
    )

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    values = (
        scenarios[
            scenarios["lead_time_days"] == 7
        ]
        .sort_values("service_level")
        ["safety_stock"]
        .tolist()
    )

    assert values[0] < values[1] < values[2]


def test_store_without_selected_model_is_descriptive_only() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [4],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
        }
    )

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    assert (
        scenarios.iloc[0]["model"]
        == "descriptive_only"
    )
