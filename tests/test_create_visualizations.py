"""Tests for the Phase 15 visualization workflow."""

import pandas as pd
import pytest

from scripts.create_visualizations import (
    validate_inputs,
)


def valid_inputs():
    """Return minimal valid analytical inputs."""
    demand = pd.DataFrame(
        {
            "store_id": [1, 2],
            "mean_daily_demand": [100.0, 80.0],
            "coefficient_of_variation": [0.1, 0.2],
        }
    )

    variability = pd.DataFrame(
        {
            "store_id": [1, 2],
            "coefficient_of_variation": [0.1, 0.2],
        }
    )

    scenarios = pd.DataFrame(
        {
            "store_id": [1, 1],
            "lead_time_days": [7, 14],
            "service_level": [0.95, 0.95],
            "reorder_point": [800.0, 1600.0],
        }
    )

    return demand, variability, scenarios


def test_valid_inputs_are_accepted():
    """Valid analytical inputs should pass validation."""
    demand, variability, scenarios = valid_inputs()

    validate_inputs(
        demand,
        variability,
        scenarios,
    )


def test_missing_demand_column_is_rejected():
    """Missing demand fields should fail validation."""
    demand, variability, scenarios = valid_inputs()

    demand = demand.drop(columns=["mean_daily_demand"])

    with pytest.raises(ValueError):
        validate_inputs(
            demand,
            variability,
            scenarios,
        )


def test_empty_demand_is_rejected():
    """An empty demand dataset should fail validation."""
    demand, variability, scenarios = valid_inputs()

    demand = demand.iloc[0:0]

    with pytest.raises(ValueError):
        validate_inputs(
            demand,
            variability,
            scenarios,
        )


def test_negative_mean_demand_is_rejected():
    """Negative demand should fail validation."""
    demand, variability, scenarios = valid_inputs()

    demand.loc[0, "mean_daily_demand"] = -1

    with pytest.raises(ValueError):
        validate_inputs(
            demand,
            variability,
            scenarios,
        )


def test_negative_variability_is_rejected():
    """Negative variability should fail validation."""
    demand, variability, scenarios = valid_inputs()

    variability.loc[0, "coefficient_of_variation"] = -1

    with pytest.raises(ValueError):
        validate_inputs(
            demand,
            variability,
            scenarios,
        )


def test_negative_reorder_point_is_rejected():
    """Negative reorder points should fail validation."""
    demand, variability, scenarios = valid_inputs()

    scenarios.loc[0, "reorder_point"] = -1

    with pytest.raises(ValueError):
        validate_inputs(
            demand,
            variability,
            scenarios,
        )


def test_store_ids_are_present():
    """Store identifiers must be available in the analytical inputs."""
    demand, variability, scenarios = valid_inputs()

    assert demand["store_id"].notna().all()
    assert variability["store_id"].notna().all()
    assert scenarios["store_id"].notna().all()


def test_lead_time_is_positive():
    """Inventory scenarios must use positive lead times."""
    _, _, scenarios = valid_inputs()

    assert (scenarios["lead_time_days"] > 0).all()


def test_service_level_is_valid():
    """Service levels must be valid probability values."""
    _, _, scenarios = valid_inputs()

    assert scenarios["service_level"].between(0, 1).all()


def test_reorder_points_are_non_negative():
    """Reorder points must be non-negative."""
    _, _, scenarios = valid_inputs()

    assert (scenarios["reorder_point"] >= 0).all()
