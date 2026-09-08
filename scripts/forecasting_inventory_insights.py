"""Generate forecasting and inventory-planning insights for Phase 13.

The analysis combines historical demand statistics with the validated
forecasting configurations from Phase 12.

Inventory calculations are scenario-based because the dataset does not
contain verified supplier lead times, service-level requirements, holding
costs, or ordering costs.

The Phase 12 test period is not used for model selection. This script uses
historical training-period demand for inventory variability calculations and
Phase 12 validation results only as model-performance evidence.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "feature_engineered_daily.csv"
SELECTED_MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "selected_model_configurations.csv"
)
VALIDATION_RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "tuned_validation_results.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"

DEMAND_SUMMARY_PATH = OUTPUT_DIR / "inventory_demand_summary.csv"
VARIABILITY_PATH = OUTPUT_DIR / "inventory_variability_summary.csv"
SCENARIOS_PATH = OUTPUT_DIR / "inventory_scenarios.csv"
INSIGHTS_PATH = OUTPUT_DIR / "forecast_inventory_insights.csv"
FINDINGS_PATH = OUTPUT_DIR / "forecasting_inventory_findings.txt"

TRAIN_SPLIT = "train"

LEAD_TIME_SCENARIOS = (7, 14, 28)

SERVICE_LEVELS = {
    0.90: 1.2815515655446004,
    0.95: 1.6448536269514722,
    0.99: 2.3263478740408408,
}


def load_training_demand() -> pd.DataFrame:
    """Load and aggregate historical training demand by store/date."""
    required_columns = [
        "date",
        "store_id",
        "quantity",
        "split",
    ]

    parts: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=required_columns,
        parse_dates=["date"],
        chunksize=250_000,
    ):
        train_chunk = chunk[chunk["split"] == TRAIN_SPLIT]

        if train_chunk.empty:
            continue

        grouped = (
            train_chunk.groupby(
                ["date", "store_id"],
                as_index=False,
                observed=True,
            )["quantity"]
            .sum()
        )

        parts.append(grouped)

    if not parts:
        raise RuntimeError("No training demand observations were found.")

    combined = pd.concat(parts, ignore_index=True)

    combined = (
        combined.groupby(
            ["date", "store_id"],
            as_index=False,
            observed=True,
        )["quantity"]
        .sum()
        .sort_values(["store_id", "date"])
        .reset_index(drop=True)
    )

    return combined


def validate_training_demand(data: pd.DataFrame) -> None:
    """Validate the aggregated training demand."""
    required_columns = {
        "date",
        "store_id",
        "quantity",
    }

    missing = required_columns - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("Training demand is empty.")

    if data["quantity"].isna().any():
        raise ValueError("Training demand contains missing quantities.")

    if (data["quantity"] < 0).any():
        raise ValueError("Training demand contains negative quantities.")

    if data.duplicated(["date", "store_id"]).any():
        raise ValueError(
            "Duplicate date/store observations exist after aggregation."
        )


def calculate_demand_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate store-level historical demand summaries."""
    summary = (
        data.groupby("store_id", as_index=False)
        .agg(
            training_days=("date", "nunique"),
            total_quantity=("quantity", "sum"),
            mean_daily_demand=("quantity", "mean"),
            median_daily_demand=("quantity", "median"),
            min_daily_demand=("quantity", "min"),
            max_daily_demand=("quantity", "max"),
        )
    )

    summary["coefficient_of_variation"] = (
        data.groupby("store_id")["quantity"].std(ddof=1).to_numpy()
        / summary["mean_daily_demand"].replace(0, np.nan)
    )

    return summary


def calculate_variability_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate store-level demand variability."""
    summary = (
        data.groupby("store_id", as_index=False)
        .agg(
            mean_daily_demand=("quantity", "mean"),
            std_daily_demand=("quantity", "std"),
            variance_daily_demand=("quantity", "var"),
            p90_daily_demand=(
                "quantity",
                lambda values: float(np.percentile(values, 90)),
            ),
            p95_daily_demand=(
                "quantity",
                lambda values: float(np.percentile(values, 95)),
            ),
            p99_daily_demand=(
                "quantity",
                lambda values: float(np.percentile(values, 99)),
            ),
        )
    )

    summary["coefficient_of_variation"] = (
        summary["std_daily_demand"]
        / summary["mean_daily_demand"].replace(0, np.nan)
    )

    return summary


def load_phase12_model_evidence() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load selected models and their validation evidence."""
    selected = pd.read_csv(SELECTED_MODEL_PATH)
    validation = pd.read_csv(VALIDATION_RESULTS_PATH)

    required_selected = {
        "store_id",
        "model",
        "configuration",
    }

    required_validation = {
        "store_id",
        "model",
        "configuration",
        "rmse",
        "mape_percent",
    }

    if not required_selected.issubset(selected.columns):
        raise ValueError("Selected-model file has missing required columns.")

    if not required_validation.issubset(validation.columns):
        raise ValueError("Validation-results file has missing required columns.")

    return selected, validation


def calculate_inventory_scenarios(
    variability: pd.DataFrame,
    selected_models: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate scenario-based safety stock and reorder points."""
    rows: list[dict[str, object]] = []

    for demand in variability.itertuples(index=False):
        store_id = int(demand.store_id)

        selected_match = selected_models[
            selected_models["store_id"] == store_id
        ]

        if selected_match.empty:
            model_name = "descriptive_only"
            configuration = "no validated Phase 12 model"
        else:
            model_name = str(selected_match.iloc[0]["model"])
            configuration = str(
                selected_match.iloc[0]["configuration"]
            )

        mean_demand = float(demand.mean_daily_demand)
        std_demand = float(demand.std_daily_demand)

        for lead_time in LEAD_TIME_SCENARIOS:
            expected_lead_time_demand = mean_demand * lead_time

            for service_level, z_value in SERVICE_LEVELS.items():
                safety_stock = (
                    z_value
                    * std_demand
                    * np.sqrt(lead_time)
                )

                reorder_point = (
                    expected_lead_time_demand
                    + safety_stock
                )

                rows.append(
                    {
                        "store_id": store_id,
                        "model": model_name,
                        "configuration": configuration,
                        "lead_time_days": lead_time,
                        "service_level": service_level,
                        "z_value": z_value,
                        "mean_daily_demand": mean_demand,
                        "std_daily_demand": std_demand,
                        "expected_lead_time_demand": (
                            expected_lead_time_demand
                        ),
                        "safety_stock": safety_stock,
                        "reorder_point": reorder_point,
                    }
                )

    return pd.DataFrame(rows)


def create_insights(
    demand_summary: pd.DataFrame,
    variability: pd.DataFrame,
    scenarios: pd.DataFrame,
    validation: pd.DataFrame,
) -> pd.DataFrame:
    """Create structured business-facing insights."""
    rows: list[dict[str, object]] = []

    highest_demand = demand_summary.loc[
        demand_summary["mean_daily_demand"].idxmax()
    ]

    highest_variability = variability.loc[
        variability["coefficient_of_variation"].idxmax()
    ]

    best_validation_store = validation.loc[
        validation["rmse"].idxmin()
    ]

    rows.extend(
        [
            {
                "insight_type": "highest_average_demand",
                "store_id": int(highest_demand["store_id"]),
                "metric": "mean_daily_demand",
                "value": float(
                    highest_demand["mean_daily_demand"]
                ),
                "interpretation": (
                    "This store has the highest observed average "
                    "daily physical demand during training."
                ),
            },
            {
                "insight_type": "highest_relative_variability",
                "store_id": int(highest_variability["store_id"]),
                "metric": "coefficient_of_variation",
                "value": float(
                    highest_variability["coefficient_of_variation"]
                ),
                "interpretation": (
                    "This store has the highest relative demand "
                    "variability during training."
                ),
            },
            {
                "insight_type": "lowest_validation_rmse",
                "store_id": int(best_validation_store["store_id"]),
                "metric": "validation_rmse",
                "value": float(best_validation_store["rmse"]),
                "interpretation": (
                    "This store had the lowest validation RMSE among "
                    "stores with a validated Phase 12 model."
                ),
            },
        ]
    )

    scenario_95_14 = scenarios[
        (scenarios["service_level"] == 0.95)
        & (scenarios["lead_time_days"] == 14)
    ]

    for row in scenario_95_14.itertuples(index=False):
        rows.append(
            {
                "insight_type": "inventory_scenario",
                "store_id": int(row.store_id),
                "metric": "reorder_point",
                "value": float(row.reorder_point),
                "interpretation": (
                    "Scenario reorder point assuming a 14-day lead "
                    "time and 95% service level. This is a planning "
                    "scenario, not a verified operational requirement."
                ),
            }
        )

    return pd.DataFrame(rows)


def write_findings(
    demand_summary: pd.DataFrame,
    variability: pd.DataFrame,
    scenarios: pd.DataFrame,
    validation: pd.DataFrame,
) -> None:
    """Write a concise textual interpretation."""
    highest_demand = demand_summary.loc[
        demand_summary["mean_daily_demand"].idxmax()
    ]

    highest_variability = variability.loc[
        variability["coefficient_of_variation"].idxmax()
    ]

    lines = [
        "Phase 13 — Forecasting & Inventory Insights",
        "",
        "Historical demand statistics are calculated from the training period.",
        "Phase 12 validation metrics are used as forecasting evidence.",
        "",
        (
            f"Highest average daily demand store: "
            f"{int(highest_demand['store_id'])}"
        ),
        (
            f"Mean daily demand: "
            f"{highest_demand['mean_daily_demand']:.3f}"
        ),
        "",
        (
            f"Highest relative variability store: "
            f"{int(highest_variability['store_id'])}"
        ),
        (
            f"Coefficient of variation: "
            f"{highest_variability['coefficient_of_variation']:.6f}"
        ),
        "",
        "Inventory scenario assumptions:",
        "- Lead times: 7, 14, and 28 days",
        "- Service levels: 90%, 95%, and 99%",
        "- Safety stock uses normal-demand variability approximation",
        "- Reorder point = expected lead-time demand + safety stock",
        "",
        "Important limitations:",
        "- Supplier lead times are not available in the dataset.",
        "- Actual service-level targets are not available.",
        "- Holding costs and ordering costs are not available.",
        "- Therefore inventory quantities are scenario estimates.",
        "- Store 4 has no Phase 12 tuned forecasting configuration.",
        "- Inventory scenarios must be calibrated with operational data before deployment.",
    ]

    FINDINGS_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run Phase 13 forecasting and inventory insights."""
    print("Running Phase 13 forecasting and inventory insights...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    training_demand = load_training_demand()

    validate_training_demand(training_demand)

    demand_summary = calculate_demand_summary(
        training_demand
    )

    variability = calculate_variability_summary(
        training_demand
    )

    selected_models, validation = load_phase12_model_evidence()

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    insights = create_insights(
        demand_summary,
        variability,
        scenarios,
        validation,
    )

    demand_summary.to_csv(
        DEMAND_SUMMARY_PATH,
        index=False,
    )

    variability.to_csv(
        VARIABILITY_PATH,
        index=False,
    )

    scenarios.to_csv(
        SCENARIOS_PATH,
        index=False,
    )

    insights.to_csv(
        INSIGHTS_PATH,
        index=False,
    )

    write_findings(
        demand_summary,
        variability,
        scenarios,
        validation,
    )

    print("Forecasting and inventory insights completed successfully.")
    print(f"Demand summary: {DEMAND_SUMMARY_PATH}")
    print(f"Variability summary: {VARIABILITY_PATH}")
    print(f"Inventory scenarios: {SCENARIOS_PATH}")
    print(f"Insights: {INSIGHTS_PATH}")
    print(f"Findings: {FINDINGS_PATH}")


if __name__ == "__main__":
    main()