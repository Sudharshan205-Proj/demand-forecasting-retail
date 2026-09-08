"""
Create Phase 15 stakeholder-facing visualizations.

The visualizations use compact analytical outputs produced by earlier
project phases. The script does not retrain forecasting models and does
not use the test period for model selection or tuning.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "data" / "analysis"
OUTPUT_DIR = ANALYSIS_DIR / "visualizations"


def require_file(path: Path) -> None:
    """Raise an explicit error when an expected input file is missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required input file is missing: {path}")


def save_figure(
    figure: plt.Figure,
    filename: str,
    *,
    width: float = 9,
    height: float = 5,
) -> None:
    """Save and close a visualization consistently."""
    path = OUTPUT_DIR / filename
    figure.set_size_inches(width, height)
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def create_store_demand_chart(demand: pd.DataFrame) -> None:
    """Create a comparison of average daily demand by store."""
    ordered = demand.sort_values("mean_daily_demand", ascending=True)

    figure, axis = plt.subplots()
    axis.barh(
        ordered["store_id"].astype(str),
        ordered["mean_daily_demand"],
    )

    axis.set_title("Average Daily Physical Demand by Store")
    axis.set_xlabel("Mean Daily Demand")
    axis.set_ylabel("Store")

    save_figure(
        figure,
        "store_average_daily_demand.png",
    )


def create_variability_chart(variability: pd.DataFrame) -> None:
    """Create a comparison of relative demand variability."""
    ordered = variability.sort_values(
        "coefficient_of_variation",
        ascending=True,
    )

    figure, axis = plt.subplots()
    axis.barh(
        ordered["store_id"].astype(str),
        ordered["coefficient_of_variation"],
    )

    axis.set_title("Relative Demand Variability by Store")
    axis.set_xlabel("Coefficient of Variation")
    axis.set_ylabel("Store")

    save_figure(
        figure,
        "store_demand_variability.png",
    )


def create_inventory_scenario_chart(scenarios: pd.DataFrame) -> None:
    """Create reorder-point scenarios by lead time for each store."""
    baseline = scenarios[
        scenarios["service_level"].eq(0.95)
    ].copy()

    figure, axis = plt.subplots()

    for store_id, group in baseline.groupby("store_id"):
        group = group.sort_values("lead_time_days")

        axis.plot(
            group["lead_time_days"],
            group["reorder_point"],
            marker="o",
            label=f"Store {store_id}",
        )

    axis.set_title(
        "Scenario Reorder Points at 95% Service Level"
    )
    axis.set_xlabel("Assumed Lead Time (Days)")
    axis.set_ylabel("Reorder Point")
    axis.legend(title="Store")

    save_figure(
        figure,
        "reorder_point_by_lead_time.png",
        width=10,
        height=6,
    )


def create_forecast_evidence_chart(insights: pd.DataFrame) -> None:
    """Create a simple chart showing validated forecast evidence."""
    validation = insights[
        insights["insight_type"].eq("lowest_validation_rmse")
    ].copy()

    if validation.empty:
        return

    figure, axis = plt.subplots()

    axis.bar(
        validation["store_id"].astype(str),
        validation["value"],
    )

    axis.set_title(
        "Lowest Validation RMSE Among Validated Stores"
    )
    axis.set_xlabel("Store")
    axis.set_ylabel("Validation RMSE")

    save_figure(
        figure,
        "lowest_validation_rmse.png",
    )


def validate_inputs(
    demand: pd.DataFrame,
    variability: pd.DataFrame,
    scenarios: pd.DataFrame,
) -> None:
    """Validate the minimum analytical inputs."""
    required_demand = {
        "store_id",
        "mean_daily_demand",
        "coefficient_of_variation",
    }

    required_variability = {
        "store_id",
        "coefficient_of_variation",
    }

    required_scenarios = {
        "store_id",
        "lead_time_days",
        "service_level",
        "reorder_point",
    }

    if not required_demand.issubset(demand.columns):
        raise ValueError("Demand summary is missing required columns.")

    if not required_variability.issubset(variability.columns):
        raise ValueError(
            "Variability summary is missing required columns."
        )

    if not required_scenarios.issubset(scenarios.columns):
        raise ValueError(
            "Inventory scenarios are missing required columns."
        )

    if demand.empty:
        raise ValueError("Demand summary is empty.")

    if variability.empty:
        raise ValueError("Variability summary is empty.")

    if scenarios.empty:
        raise ValueError("Inventory scenarios are empty.")

    if (demand["mean_daily_demand"] < 0).any():
        raise ValueError("Mean demand cannot be negative.")

    if (variability["coefficient_of_variation"] < 0).any():
        raise ValueError("Coefficient of variation cannot be negative.")

    if (scenarios["reorder_point"] < 0).any():
        raise ValueError("Reorder points cannot be negative.")


def main() -> None:
    """Run the Phase 15 visualization workflow."""
    print("Creating Phase 15 visualizations...")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    demand_path = ANALYSIS_DIR / "inventory_demand_summary.csv"
    variability_path = (
        ANALYSIS_DIR / "inventory_variability_summary.csv"
    )
    scenarios_path = ANALYSIS_DIR / "inventory_scenarios.csv"
    insights_path = (
        ANALYSIS_DIR / "forecast_inventory_insights.csv"
    )

    for path in (
        demand_path,
        variability_path,
        scenarios_path,
        insights_path,
    ):
        require_file(path)

    demand = pd.read_csv(demand_path)
    variability = pd.read_csv(variability_path)
    scenarios = pd.read_csv(scenarios_path)
    insights = pd.read_csv(insights_path)

    validate_inputs(
        demand,
        variability,
        scenarios,
    )

    create_store_demand_chart(demand)
    create_variability_chart(variability)
    create_inventory_scenario_chart(scenarios)
    create_forecast_evidence_chart(insights)

    print("Phase 15 visualizations completed successfully.")
    print(f"Visualization directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()