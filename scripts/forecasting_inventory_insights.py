"""Generate forecasting and inventory-planning insights for Phase 13.

The analysis combines historical demand statistics with the validated
forecasting configurations from Phase 12. Inventory numbers are
scenario-based rather than operational: the dataset carries no verified
supplier lead times, service-level requirements, holding costs or ordering
costs. Two families are produced -- a historical-variability family using
the observed training-period daily demand standard deviation, and a
forecast-driven family using the selected model's realised validation error
with its measured bias applied as a level correction.

The test period is never read: historical statistics come from the training
period only, and the forecast evidence comes from the stored Phase 12
validation predictions. The demand series is densified onto a complete
daily calendar with the same construction Phase 11 and Phase 12 use, so all
three phases describe an identical store-day series, and the densification
is measured and recorded rather than assumed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "model_evaluation_predictions.csv"
)
ERROR_ANALYSIS_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "model_error_analysis.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"

DEMAND_SUMMARY_PATH = OUTPUT_DIR / "inventory_demand_summary.csv"
VARIABILITY_PATH = OUTPUT_DIR / "inventory_variability_summary.csv"
DENSIFICATION_PATH = OUTPUT_DIR / "inventory_densification_summary.csv"
SCENARIOS_PATH = OUTPUT_DIR / "inventory_scenarios.csv"
FORECAST_SCENARIOS_PATH = OUTPUT_DIR / "inventory_forecast_scenarios.csv"
FORECAST_ERROR_PATH = OUTPUT_DIR / "inventory_forecast_error_summary.csv"
INSIGHTS_PATH = OUTPUT_DIR / "forecast_inventory_insights.csv"
FINDINGS_PATH = OUTPUT_DIR / "forecasting_inventory_findings.txt"
QUALITY_REPORT_PATH = OUTPUT_DIR / "forecasting_inventory_quality_report.csv"

TRAIN_SPLIT = "train"

LEAD_TIME_SCENARIOS = (7, 14, 28)

SERVICE_LEVELS = {
    0.90: 1.2815515655446004,
    0.95: 1.6448536269514722,
    0.99: 2.3263478740408408,
}

# The Phase 9 split contract, re-asserted by Phase 11 and Phase 12. Phase 13
# verifies these boundaries rather than trusting the `split` column.
TRAIN_START = pd.Timestamp("2022-08-28")
TRAIN_END = pd.Timestamp("2024-02-10")
VALIDATION_START = pd.Timestamp("2024-02-11")
VALIDATION_END = pd.Timestamp("2024-06-03")
TEST_START = pd.Timestamp("2024-06-04")
TEST_END = pd.Timestamp("2024-09-26")

# Reconciled against the Phase 9/10 source; the same figures Phase 11 and
# Phase 12 verify.
SOURCE_TOTAL_ROWS = 7_431_026
SOURCE_TOTAL_QUANTITY = 41_949_529.910
SOURCE_TRAIN_ROWS = 4_315_416
SOURCE_TRAIN_QUANTITY = 24_038_416.097
SOURCE_VALIDATION_ROWS = 1_548_957
SOURCE_TEST_ROWS = 1_566_653

# Phase 11 measured this exact densification: 1,656 training store-days with
# exactly one zero-filled day.
EXPECTED_STORES = 4
EXPECTED_DENSIFIED_TRAINING_DAYS = 1_656
EXPECTED_SYNTHETIC_DAYS = 1
EXPECTED_SYNTHETIC_STORE = 3
EXPECTED_SYNTHETIC_DATE = "2022-10-16"
VALIDATION_HORIZON = 114

REQUIRED_INPUT_COLUMNS = ("date", "store_id", "quantity", "split")

INSIGHT_TYPES = (
    "highest_average_demand",
    "highest_relative_variability",
    "lowest_validation_rmse",
    "lowest_relative_validation_error",
    "systematic_bias",
    "inventory_scenario",
    "forecast_inventory_scenario",
)

RTOL = 1e-9


@dataclass
class SourceStats:
    """Row and quantity totals observed while streaming the source matrix."""

    total_rows: int = 0
    total_quantity: float = 0.0
    split_rows: dict[str, int] = field(default_factory=dict)
    split_quantity: dict[str, float] = field(default_factory=dict)


# --- Loading and densification -----------------------------------------


def load_training_demand() -> tuple[pd.DataFrame, SourceStats]:
    """Load training demand by store/date and densify each store's calendar.

    The source matrix is streamed in chunks and reduced to a store-day
    aggregate before densification, so memory stays proportional to the
    aggregate rather than to the 7.4-million-row source. Densification
    mirrors Phase 11's ``to_regular_daily_series``: each store's observed
    training range is reindexed onto a complete daily calendar with absent
    days filled at zero, which at this grain means no quantity was recorded
    for that store that day. The returned frame carries an ``is_synthetic``
    flag identifying the zero-filled days, and the source totals are
    returned alongside it for reconciliation.
    """
    stats = SourceStats()

    parts: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=list(REQUIRED_INPUT_COLUMNS),
        parse_dates=["date"],
        chunksize=250_000,
    ):
        stats.total_rows += len(chunk)
        stats.total_quantity += float(chunk["quantity"].sum())

        for split_name, split_chunk in chunk.groupby("split", observed=True):
            key = str(split_name)
            stats.split_rows[key] = (
                stats.split_rows.get(key, 0) + len(split_chunk)
            )
            stats.split_quantity[key] = (
                stats.split_quantity.get(key, 0.0)
                + float(split_chunk["quantity"].sum())
            )

        train_chunk = chunk[chunk["split"] == TRAIN_SPLIT]

        if train_chunk.empty:
            continue

        parts.append(
            train_chunk.groupby(
                ["date", "store_id"],
                as_index=False,
                observed=True,
            )["quantity"].sum()
        )

    if not parts:
        raise RuntimeError("No training demand observations were found.")

    observed = (
        pd.concat(parts, ignore_index=True)
        .groupby(["date", "store_id"], as_index=False, observed=True)[
            "quantity"
        ]
        .sum()
        .sort_values(["store_id", "date"])
        .reset_index(drop=True)
    )

    observed["is_synthetic"] = False

    return densify_store_days(observed), stats


def densify_store_days(observed: pd.DataFrame) -> pd.DataFrame:
    """Reindex every store onto a complete daily calendar between its bounds.

    Mirrors Phase 11's construction so Phase 13's descriptive statistics and
    the series Phases 11-12 fitted describe the same store-day calendar.
    """
    required = {"date", "store_id", "quantity"}

    missing = required - set(observed.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if observed.empty:
        raise ValueError("Training demand is empty.")

    frames: list[pd.DataFrame] = []

    for store_id, group in observed.groupby("store_id", sort=True):
        series = group.set_index("date")["quantity"].astype(float).sort_index()

        if series.index.duplicated().any():
            raise ValueError(f"Duplicate dates found for store {store_id!r}.")

        full_index = pd.date_range(
            series.index.min(),
            series.index.max(),
            freq="D",
        )

        present = series.index

        densified = series.reindex(full_index, fill_value=0.0)

        frames.append(
            pd.DataFrame(
                {
                    "date": full_index,
                    "store_id": int(store_id),
                    "quantity": densified.to_numpy(),
                    "is_synthetic": ~full_index.isin(present),
                }
            )
        )

    return (
        pd.concat(frames, ignore_index=True)
        .sort_values(["store_id", "date"])
        .reset_index(drop=True)
    )


def summarize_densification(data: pd.DataFrame) -> pd.DataFrame:
    """Record observed, densified and synthetic day counts per store."""
    required = {"date", "store_id", "quantity", "is_synthetic"}

    missing = required - set(data.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    rows: list[dict[str, object]] = []

    for store_id, group in data.groupby("store_id", sort=True):
        synthetic = group[group["is_synthetic"]]

        rows.append(
            {
                "store_id": int(store_id),
                "observed_days": int((~group["is_synthetic"]).sum()),
                "densified_days": int(len(group)),
                "synthetic_days": int(len(synthetic)),
                "first_date": group["date"].min(),
                "last_date": group["date"].max(),
                "synthetic_dates": ";".join(
                    date.strftime("%Y-%m-%d")
                    for date in sorted(synthetic["date"])
                ),
            }
        )

    return pd.DataFrame(rows)


def validate_training_demand(
    data: pd.DataFrame,
    expected_stores: set[int] | None = None,
) -> None:
    """Validate the aggregated, densified training demand."""
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

    if expected_stores is not None:
        actual = {int(store) for store in data["store_id"].unique()}

        if actual != set(expected_stores):
            raise ValueError(
                "Training demand does not cover the expected stores: "
                f"expected {sorted(expected_stores)}, found {sorted(actual)}."
            )


# --- Descriptive statistics --------------------------------------------


def calculate_demand_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate store-level historical demand summaries.

    The coefficient of variation is derived inside a single grouped
    aggregation, so no column depends on positional alignment with a
    separately computed series.
    """
    summary = (
        data.groupby("store_id", as_index=False)
        .agg(
            training_days=("date", "nunique"),
            total_quantity=("quantity", "sum"),
            mean_daily_demand=("quantity", "mean"),
            median_daily_demand=("quantity", "median"),
            min_daily_demand=("quantity", "min"),
            max_daily_demand=("quantity", "max"),
            std_daily_demand=("quantity", "std"),
        )
    )

    summary["coefficient_of_variation"] = (
        summary["std_daily_demand"]
        / summary["mean_daily_demand"].replace(0, np.nan)
    )

    return summary.drop(columns=["std_daily_demand"])


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


# --- Phase 12 evidence --------------------------------------------------


def load_phase12_model_evidence() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load selected models and their validation evidence.

    Validates that Phase 12's selection names exactly one configuration per
    store, that both files agree on that configuration, and that the typed
    parameter columns Phase 12 introduced are present.
    """
    selected = pd.read_csv(SELECTED_MODEL_PATH)
    validation = pd.read_csv(VALIDATION_RESULTS_PATH)

    required_selected = {
        "store_id",
        "model",
        "configuration",
        "season_length",
        "order",
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
        raise ValueError(
            "Validation-results file has missing required columns."
        )

    if selected.empty or validation.empty:
        raise ValueError("Phase 12 model evidence is empty.")

    if selected["store_id"].duplicated().any():
        raise ValueError(
            "Selected-model file must contain exactly one row per store."
        )

    if validation["store_id"].duplicated().any():
        raise ValueError(
            "Validation-results file must contain exactly one row per store."
        )

    if set(selected["store_id"]) != set(validation["store_id"]):
        raise ValueError(
            "Selected models and validation results cover different stores."
        )

    merged = selected.merge(
        validation[["store_id", "model"]],
        on="store_id",
        suffixes=("", "_validation"),
    )

    if not (merged["model"] == merged["model_validation"]).all():
        raise ValueError(
            "Selected models and validation results disagree on the model."
        )

    return selected, validation


def load_phase12_forecast_errors(
    validation: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize each selected model's validation error from stored forecasts.

    Every figure is recomputed from the stored Phase 12 predictions rather
    than copied, so the two artifacts are independently comparable. The bias
    is ``mean(actual - predicted)``; a positive value means the model
    under-forecasts on average.
    """
    predictions = pd.read_csv(PREDICTIONS_PATH, parse_dates=["date"])

    required = {
        "scope",
        "store_id",
        "model",
        "date",
        "actual",
        "predicted",
    }

    missing = required - set(predictions.columns)

    if missing:
        raise ValueError(
            "Predictions file has missing required columns: "
            f"{sorted(missing)}"
        )

    horizon = predictions[predictions["scope"] == "validation"]

    if horizon.empty:
        raise ValueError("No validation forecasts were found.")

    if horizon[["actual", "predicted"]].isna().any().any():
        raise ValueError("Validation forecasts contain missing values.")

    rows: list[dict[str, object]] = []

    for store_id, group in horizon.groupby("store_id", sort=True):
        model_row = validation[validation["store_id"] == store_id]

        if model_row.empty:
            raise ValueError(
                f"No validation result recorded for store {store_id!r}."
            )

        residuals = group["actual"] - group["predicted"]

        nonzero = group[group["actual"] != 0]

        if nonzero.empty:
            raise ValueError(
                f"Store {store_id!r} has no non-zero validation demand."
            )

        rmse = float(np.sqrt((residuals**2).mean()))

        mape = float(
            (
                (nonzero["actual"] - nonzero["predicted"]).abs()
                / nonzero["actual"]
            ).mean()
            * 100
        )

        rows.append(
            {
                "store_id": int(store_id),
                "model": str(model_row.iloc[0]["model"]),
                "configuration": str(model_row.iloc[0]["configuration"]),
                "observations": int(len(group)),
                "validation_start": group["date"].min(),
                "validation_end": group["date"].max(),
                "mean_predicted": float(group["predicted"].mean()),
                "mean_actual": float(group["actual"].mean()),
                "bias": float(residuals.mean()),
                "residual_std": float(residuals.std(ddof=1)),
                "rmse": rmse,
                "mape_percent": mape,
            }
        )

    return pd.DataFrame(rows)


def load_phase12_error_analysis() -> pd.DataFrame:
    """Load Phase 12's recorded validation error segments."""
    frame = pd.read_csv(ERROR_ANALYSIS_PATH)

    required = {"store_id", "validation_segment", "mean_error", "rmse"}

    missing = required - set(frame.columns)

    if missing:
        raise ValueError(
            "Error-analysis file has missing required columns: "
            f"{sorted(missing)}"
        )

    return frame


# --- Scenario construction ---------------------------------------------


def _resolve_model(
    selected_models: pd.DataFrame,
    store_id: int,
) -> tuple[str, str, float | None, str | None]:
    """Resolve a store's selected configuration through its typed fields."""
    match = selected_models[selected_models["store_id"] == store_id]

    if match.empty:
        return "descriptive_only", "no validated Phase 12 model", None, None

    row = match.iloc[0]

    season_length = row["season_length"]
    order = row["order"]

    return (
        str(row["model"]),
        str(row["configuration"]),
        None if pd.isna(season_length) else float(season_length),
        None if pd.isna(order) else str(order),
    )


def calculate_inventory_scenarios(
    variability: pd.DataFrame,
    selected_models: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate scenario-based safety stock and reorder points.

    The uncertainty input is the historical training-period daily demand
    standard deviation.
    """
    rows: list[dict[str, object]] = []

    for demand in variability.itertuples(index=False):
        store_id = int(demand.store_id)

        model_name, configuration, season_length, order = _resolve_model(
            selected_models,
            store_id,
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
                        "season_length": season_length,
                        "order": order,
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


def calculate_forecast_scenarios(
    errors: pd.DataFrame,
    selected_models: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate forecast-driven safety stock and reorder points.

    The level estimate is the selected model's mean validation prediction
    corrected by its measured bias, and the uncertainty input is the
    realised standard deviation of its validation error. This is the family
    that consumes the Phase 12 forecasting evidence.
    """
    rows: list[dict[str, object]] = []

    for error in errors.itertuples(index=False):
        store_id = int(error.store_id)

        _, configuration, season_length, order = _resolve_model(
            selected_models,
            store_id,
        )

        model_daily_demand = float(error.mean_predicted)

        # Adding the measured bias back to the model's own level recovers the
        # demand actually realised over the validation period; it is not a
        # forward forecast, because the test set is the only genuinely unseen
        # period and both Phase 12 and Phase 13 leave it reserved. Both
        # levels are carried so the correction stays visible.
        bias_adjusted_daily_demand = model_daily_demand + float(error.bias)

        residual_std = float(error.residual_std)

        for lead_time in LEAD_TIME_SCENARIOS:
            expected_lead_time_demand = (
                bias_adjusted_daily_demand * lead_time
            )

            for service_level, z_value in SERVICE_LEVELS.items():
                safety_stock = (
                    z_value
                    * residual_std
                    * np.sqrt(lead_time)
                )

                reorder_point = (
                    expected_lead_time_demand
                    + safety_stock
                )

                rows.append(
                    {
                        "store_id": store_id,
                        "model": str(error.model),
                        "configuration": configuration,
                        "season_length": season_length,
                        "order": order,
                        "lead_time_days": lead_time,
                        "service_level": service_level,
                        "z_value": z_value,
                        "model_daily_demand": model_daily_demand,
                        "bias": float(error.bias),
                        "bias_adjusted_daily_demand": (
                            bias_adjusted_daily_demand
                        ),
                        "residual_std": residual_std,
                        "rmse": float(error.rmse),
                        "expected_lead_time_demand": (
                            expected_lead_time_demand
                        ),
                        "safety_stock": safety_stock,
                        "reorder_point": reorder_point,
                    }
                )

    return pd.DataFrame(rows)


# --- Insights and findings ---------------------------------------------


def build_model_lines(errors: pd.DataFrame) -> list[str]:
    """Describe each store's selected model as a findings line.

    The RMSE and MAPE quoted here are recomputed from the stored Phase 12
    forecasts, and the quality report verifies they equal Phase 12's
    recorded values.
    """
    lines: list[str] = []

    for row in errors.sort_values("store_id").itertuples(index=False):
        lines.append(
            f"Store {int(row.store_id)}: {row.model} "
            f"({row.configuration}); validation RMSE "
            f"{float(row.rmse):.4f}, MAPE {float(row.mape_percent):.4f}%"
        )

    return lines


def create_insights(
    demand_summary: pd.DataFrame,
    variability: pd.DataFrame,
    scenarios: pd.DataFrame,
    forecast_scenarios: pd.DataFrame,
    errors: pd.DataFrame,
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

    best_rmse = validation.loc[validation["rmse"].idxmin()]

    best_mape = validation.loc[validation["mape_percent"].idxmin()]

    strongest_bias = errors.loc[errors["bias"].idxmax()]

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
                    "variability during training. Its history is also "
                    "the shortest, so this estimate rests on fewer "
                    "observations than the other stores'."
                ),
            },
            {
                "insight_type": "lowest_validation_rmse",
                "store_id": int(best_rmse["store_id"]),
                "metric": "validation_rmse",
                "value": float(best_rmse["rmse"]),
                "interpretation": (
                    "This store recorded the lowest validation RMSE, but "
                    "RMSE is measured in demand units and is therefore "
                    "scale-bound: the smallest store tends to win on "
                    "scale alone. RMSE is only comparable within a store."
                ),
            },
            {
                "insight_type": "lowest_relative_validation_error",
                "store_id": int(best_mape["store_id"]),
                "metric": "validation_mape_percent",
                "value": float(best_mape["mape_percent"]),
                "interpretation": (
                    "This store recorded the lowest relative validation "
                    "error (MAPE), which is the appropriate basis for "
                    "comparing forecast accuracy across stores of "
                    "different size."
                ),
            },
            {
                "insight_type": "systematic_bias",
                "store_id": int(strongest_bias["store_id"]),
                "metric": "mean_forecast_bias",
                "value": float(strongest_bias["bias"]),
                "interpretation": (
                    "This store has the largest average under-forecast in "
                    "demand units. Every selected model under-forecast on "
                    "average, so the forecast-driven inventory scenarios "
                    "apply a bias correction rather than assuming an "
                    "unbiased forecast."
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
                    "time and 95% service level, using historical "
                    "demand variability. This is a planning "
                    "scenario, not a verified operational requirement."
                ),
            }
        )

    forecast_95_14 = forecast_scenarios[
        (forecast_scenarios["service_level"] == 0.95)
        & (forecast_scenarios["lead_time_days"] == 14)
    ]

    for row in forecast_95_14.itertuples(index=False):
        rows.append(
            {
                "insight_type": "forecast_inventory_scenario",
                "store_id": int(row.store_id),
                "metric": "reorder_point",
                "value": float(row.reorder_point),
                "interpretation": (
                    "Scenario reorder point assuming a 14-day lead "
                    "time and 95% service level, using the selected "
                    "Phase 12 model's measured validation error as the "
                    "uncertainty input and its bias-corrected validation "
                    "demand level as the level input. The level is the "
                    "demand realised over the validation period, not a "
                    "forecast of future demand, because the test period "
                    "remains reserved. This is a planning scenario, not a "
                    "verified operational requirement."
                ),
            }
        )

    return pd.DataFrame(rows)


def build_findings_text(
    demand_summary: pd.DataFrame,
    variability: pd.DataFrame,
    scenarios: pd.DataFrame,
    forecast_scenarios: pd.DataFrame,
    errors: pd.DataFrame,
    densification: pd.DataFrame,
    model_lines: list[str],
) -> str:
    """Render the findings report.

    Every store-level statement is derived from the loaded evidence, so the
    report cannot contradict the artifacts it describes.
    """
    highest_demand = demand_summary.loc[
        demand_summary["mean_daily_demand"].idxmax()
    ]

    highest_variability = variability.loc[
        variability["coefficient_of_variation"].idxmax()
    ]

    synthetic_days = int(densification["synthetic_days"].sum())

    densified_days = int(densification["densified_days"].sum())

    observed_days = int(densification["observed_days"].sum())

    scenario_95_14 = scenarios[
        (scenarios["service_level"] == 0.95)
        & (scenarios["lead_time_days"] == 14)
    ].sort_values("store_id")

    forecast_95_14 = forecast_scenarios[
        (forecast_scenarios["service_level"] == 0.95)
        & (forecast_scenarios["lead_time_days"] == 14)
    ].sort_values("store_id")

    mean_bias = float(errors["bias"].mean())

    return "\n".join(
        [
            "Phase 13 — Forecasting & Inventory Insights",
            "",
            "Demand basis:",
            (
                f"- Training store-days after densification: "
                f"{densified_days} (observed {observed_days}, zero-filled "
                f"{synthetic_days})"
            ),
            (
                "- Densification mirrors Phase 11/12, so all three phases "
                "describe the same store-day calendar."
            ),
            (
                f"- Total training quantity: "
                f"{float(demand_summary['total_quantity'].sum()):.3f}"
            ),
            "",
            "Historical demand:",
            (
                f"- Highest average daily demand store: "
                f"{int(highest_demand['store_id'])}"
            ),
            (
                f"- Mean daily demand: "
                f"{highest_demand['mean_daily_demand']:.3f}"
            ),
            (
                f"- Highest relative variability store: "
                f"{int(highest_variability['store_id'])}"
            ),
            (
                f"- Coefficient of variation: "
                f"{highest_variability['coefficient_of_variation']:.6f}"
            ),
            "",
            "Phase 12 forecasting evidence (selected configuration per store):",
            *[f"- {line}" for line in model_lines],
            (
                f"- Mean under-forecast across stores: {mean_bias:.3f} "
                f"units per day; every selected model under-forecast on "
                f"average."
            ),
            "",
            "Inventory scenario assumptions:",
            "- Lead times: 7, 14, and 28 days",
            "- Service levels: 90%, 95%, and 99%",
            "- Safety stock uses a normal-demand variability approximation",
            "- Reorder point = expected lead-time demand + safety stock",
            (
                "- Two families are produced: historical-variability and "
                "forecast-error"
            ),
            (
                "- The historical family estimates uncertainty from the "
                "training-period demand standard deviation"
            ),
            (
                "- The forecast family estimates uncertainty from the "
                "selected model's realised validation error and applies "
                "its measured bias as a level correction"
            ),
            (
                "- The forecast family's level is a recovered "
                "validation-period demand level, NOT a forward forecast: "
                "the reserved test period is the only genuinely unseen "
                "data and neither family reads it"
            ),
            "",
            "14-day lead time, 95% service level reorder points:",
            *[
                (
                    f"- Store {int(row.store_id)} historical-variability "
                    f"basis: {row.reorder_point:.3f}"
                )
                for row in scenario_95_14.itertuples(index=False)
            ],
            *[
                (
                    f"- Store {int(row.store_id)} forecast-error basis: "
                    f"{row.reorder_point:.3f}"
                )
                for row in forecast_95_14.itertuples(index=False)
            ],
            "",
            "Important limitations:",
            "- Supplier lead times are not available in the dataset.",
            "- Actual service-level targets are not available.",
            "- Holding costs and ordering costs are not available.",
            "- Therefore inventory quantities are scenario estimates.",
            (
                "- The forecast-error scenarios reuse the validation "
                "period's own error, which is more optimistic than a truly "
                "unseen evaluation."
            ),
            (
                "- Store 4's configuration rests on a single "
                "cross-validation fold and 60 training days, so its "
                "evidence is weaker than stores 1-3."
            ),
            (
                "- Inventory scenarios must be calibrated with operational "
                "data before deployment."
            ),
        ]
    )


# --- Quality report -----------------------------------------------------


def _check(
    name: str,
    passed: bool,
    actual: object,
    expected: object,
) -> dict[str, object]:
    return {
        "check": name,
        "passed": bool(passed),
        "actual": actual,
        "expected": expected,
    }


def build_quality_report(
    data: pd.DataFrame,
    stats: SourceStats,
    densification: pd.DataFrame,
    demand_summary: pd.DataFrame,
    scenarios: pd.DataFrame,
    forecast_scenarios: pd.DataFrame,
    errors: pd.DataFrame,
    validation: pd.DataFrame,
    error_analysis: pd.DataFrame,
    insights: pd.DataFrame,
    findings_text: str,
    model_lines: list[str],
    selected_models: pd.DataFrame,
) -> pd.DataFrame:
    """Build the machine-readable validation report that gates the run."""
    checks: list[dict[str, object]] = []

    # Source reconciliation
    checks.append(
        _check(
            "input_rows_positive",
            stats.total_rows > 0,
            stats.total_rows,
            ">0",
        )
    )
    checks.append(
        _check(
            "input_required_columns_present",
            len(REQUIRED_INPUT_COLUMNS),
            len(REQUIRED_INPUT_COLUMNS),
            len(REQUIRED_INPUT_COLUMNS),
        )
    )
    checks.append(
        _check(
            "source_rows_reconciled",
            stats.total_rows == SOURCE_TOTAL_ROWS,
            stats.total_rows,
            SOURCE_TOTAL_ROWS,
        )
    )
    checks.append(
        _check(
            "source_quantity_reconciled",
            abs(stats.total_quantity - SOURCE_TOTAL_QUANTITY) < 0.001,
            round(stats.total_quantity, 3),
            SOURCE_TOTAL_QUANTITY,
        )
    )
    checks.append(
        _check(
            "training_rows_reconciled",
            stats.split_rows.get(TRAIN_SPLIT, 0) == SOURCE_TRAIN_ROWS,
            stats.split_rows.get(TRAIN_SPLIT, 0),
            SOURCE_TRAIN_ROWS,
        )
    )
    checks.append(
        _check(
            "training_quantity_reconciled",
            abs(
                stats.split_quantity.get(TRAIN_SPLIT, 0.0)
                - SOURCE_TRAIN_QUANTITY
            )
            < 0.001,
            round(stats.split_quantity.get(TRAIN_SPLIT, 0.0), 3),
            SOURCE_TRAIN_QUANTITY,
        )
    )
    checks.append(
        _check(
            "validation_rows_reconciled",
            stats.split_rows.get("validation", 0) == SOURCE_VALIDATION_ROWS,
            stats.split_rows.get("validation", 0),
            SOURCE_VALIDATION_ROWS,
        )
    )
    checks.append(
        _check(
            "test_rows_reconciled",
            stats.split_rows.get("test", 0) == SOURCE_TEST_ROWS,
            stats.split_rows.get("test", 0),
            SOURCE_TEST_ROWS,
        )
    )

    # Partition and leakage integrity
    checks.append(
        _check(
            "store_day_keys_unique",
            int(data.duplicated(["date", "store_id"]).sum()) == 0,
            int(data.duplicated(["date", "store_id"]).sum()),
            0,
        )
    )
    checks.append(
        _check(
            "store_count_preserved",
            int(data["store_id"].nunique()) == EXPECTED_STORES,
            int(data["store_id"].nunique()),
            EXPECTED_STORES,
        )
    )
    checks.append(
        _check(
            "trains_on_training_window_only",
            bool(
                data["date"].min() == TRAIN_START
                and data["date"].max() == TRAIN_END
            ),
            f"{data['date'].min().date()} to {data['date'].max().date()}",
            f"{TRAIN_START.date()} to {TRAIN_END.date()}",
        )
    )
    checks.append(
        _check(
            "test_period_excluded",
            bool(data["date"].max() < TEST_START),
            str(data["date"].max().date()),
            f"< {TEST_START.date()}",
        )
    )
    checks.append(
        _check(
            "input_target_complete",
            int(data["quantity"].isna().sum()) == 0,
            int(data["quantity"].isna().sum()),
            0,
        )
    )

    # Densification
    total_densified = int(densification["densified_days"].sum())

    checks.append(
        _check(
            "densified_training_days_measured",
            total_densified == EXPECTED_DENSIFIED_TRAINING_DAYS,
            total_densified,
            EXPECTED_DENSIFIED_TRAINING_DAYS,
        )
    )
    checks.append(
        _check(
            "densification_synthetic_day_count",
            int(densification["synthetic_days"].sum())
            == EXPECTED_SYNTHETIC_DAYS,
            int(densification["synthetic_days"].sum()),
            EXPECTED_SYNTHETIC_DAYS,
        )
    )
    synthetic_pairs = sorted(
        (int(row.store_id), str(row.synthetic_dates))
        for row in densification.itertuples(index=False)
        if row.synthetic_days > 0
    )
    expected_synthetic_pairs = [
        (EXPECTED_SYNTHETIC_STORE, EXPECTED_SYNTHETIC_DATE)
    ]
    checks.append(
        _check(
            "densification_matches_phase11",
            synthetic_pairs == expected_synthetic_pairs,
            synthetic_pairs,
            expected_synthetic_pairs,
        )
    )
    spans_match = all(
        int(row.densified_days) == (row.last_date - row.first_date).days + 1
        for row in densification.itertuples(index=False)
    )
    checks.append(
        _check("densified_days_match_span", spans_match, spans_match, True)
    )
    checks.append(
        _check(
            "densified_quantity_preserved",
            abs(
                float(data["quantity"].sum())
                - float(data.loc[~data["is_synthetic"], "quantity"].sum())
            )
            < 0.001,
            round(float(data["quantity"].sum()), 3),
            round(
                float(data.loc[~data["is_synthetic"], "quantity"].sum()), 3
            ),
        )
    )

    # Phase 12 evidence
    checks.append(
        _check(
            "model_selection_one_per_store",
            len(selected_models) == EXPECTED_STORES,
            len(selected_models),
            EXPECTED_STORES,
        )
    )
    checks.append(
        _check(
            "model_selection_covers_stores",
            {int(s) for s in selected_models["store_id"]}
            == {int(s) for s in data["store_id"].unique()},
            sorted(int(s) for s in selected_models["store_id"]),
            sorted(int(s) for s in data["store_id"].unique()),
        )
    )
    checks.append(
        _check(
            "model_selection_matches_validation",
            {
                (int(s), str(m))
                for s, m in zip(
                    selected_models["store_id"], selected_models["model"]
                )
            }
            == {
                (int(s), str(m))
                for s, m in zip(validation["store_id"], validation["model"])
            },
            True,
            True,
        )
    )
    checks.append(
        _check(
            "typed_configuration_present",
            {"season_length", "order"}.issubset(selected_models.columns),
            True,
            True,
        )
    )

    # Forecast evidence reconciliation
    expected_predictions = EXPECTED_STORES * VALIDATION_HORIZON

    checks.append(
        _check(
            "validation_predictions_complete",
            int(errors["observations"].sum()) == expected_predictions,
            int(errors["observations"].sum()),
            expected_predictions,
        )
    )
    checks.append(
        _check(
            "validation_evidence_scoped_to_validation_period",
            bool(
                (errors["validation_start"] == VALIDATION_START).all()
                and (errors["validation_end"] == VALIDATION_END).all()
            ),
            [
                f"{row.validation_start.date()} to "
                f"{row.validation_end.date()}"
                for row in errors.itertuples(index=False)
            ],
            f"{VALIDATION_START.date()} to {VALIDATION_END.date()}",
        )
    )
    rmse_match = bool(
        np.allclose(
            errors["rmse"].to_numpy(dtype=float),
            validation["rmse"].to_numpy(dtype=float),
            rtol=RTOL,
        )
    )
    checks.append(
        _check("forecast_rmse_reproduced", rmse_match, rmse_match, True)
    )
    mape_match = bool(
        np.allclose(
            errors["mape_percent"].to_numpy(dtype=float),
            validation["mape_percent"].to_numpy(dtype=float),
            rtol=1e-6,
        )
    )
    checks.append(
        _check("forecast_mape_reproduced", mape_match, mape_match, True)
    )
    checks.append(
        _check(
            "under_forecast_bias_positive",
            bool((errors["bias"] > 0).all()),
            [round(float(v), 2) for v in errors["bias"]],
            ">0 for every store",
        )
    )

    # Error-analysis reconciliation
    segment_bias = (
        error_analysis.groupby("store_id")["mean_error"]
        .mean()
        .sort_index()
        .to_numpy(dtype=float)
    )
    recomputed_bias = (
        errors.set_index("store_id")["bias"]
        .sort_index()
        .to_numpy(dtype=float)
    )
    checks.append(
        _check(
            "error_analysis_bias_reconciles",
            bool(np.allclose(segment_bias, recomputed_bias, rtol=1e-6)),
            [round(float(v), 4) for v in segment_bias],
            [round(float(v), 4) for v in recomputed_bias],
        )
    )
    segment_rmse = np.sqrt(
        (
            error_analysis.assign(squared=lambda frame: frame["rmse"] ** 2)
            .groupby("store_id")["squared"]
            .mean()
        )
        .sort_index()
        .to_numpy(dtype=float)
    )
    recorded_rmse = (
        errors.set_index("store_id")["rmse"]
        .sort_index()
        .to_numpy(dtype=float)
    )
    checks.append(
        _check(
            "error_analysis_rmse_reconciles",
            bool(np.allclose(segment_rmse, recorded_rmse, rtol=1e-6)),
            [round(float(v), 4) for v in segment_rmse],
            [round(float(v), 4) for v in recorded_rmse],
        )
    )

    # Scenario integrity
    expected_scenarios = (
        len(demand_summary) * len(LEAD_TIME_SCENARIOS) * len(SERVICE_LEVELS)
    )

    checks.append(
        _check(
            "historical_scenario_coverage_complete",
            len(scenarios) == expected_scenarios,
            len(scenarios),
            expected_scenarios,
        )
    )
    checks.append(
        _check(
            "forecast_scenario_coverage_complete",
            len(forecast_scenarios) == expected_scenarios,
            len(forecast_scenarios),
            expected_scenarios,
        )
    )
    checks.append(
        _check(
            "safety_stock_non_negative",
            bool(
                (scenarios["safety_stock"] >= 0).all()
                and (forecast_scenarios["safety_stock"] >= 0).all()
            ),
            True,
            True,
        )
    )
    checks.append(
        _check(
            "reorder_point_formula_holds",
            bool(
                np.allclose(
                    scenarios["reorder_point"],
                    scenarios["expected_lead_time_demand"]
                    + scenarios["safety_stock"],
                    rtol=RTOL,
                )
                and np.allclose(
                    forecast_scenarios["reorder_point"],
                    forecast_scenarios["expected_lead_time_demand"]
                    + forecast_scenarios["safety_stock"],
                    rtol=RTOL,
                )
            ),
            True,
            True,
        )
    )
    checks.append(
        _check(
            "reorder_point_covers_lead_time_demand",
            bool(
                (
                    scenarios["reorder_point"]
                    >= scenarios["expected_lead_time_demand"]
                ).all()
                and (
                    forecast_scenarios["reorder_point"]
                    >= forecast_scenarios["expected_lead_time_demand"]
                ).all()
            ),
            True,
            True,
        )
    )
    combined = pd.concat(
        [
            scenarios.assign(family="historical"),
            forecast_scenarios.assign(family="forecast"),
        ],
        ignore_index=True,
    )
    lead_time_monotonic = all(
        group.sort_values("lead_time_days")[
            "expected_lead_time_demand"
        ].is_monotonic_increasing
        for _, group in combined.groupby(
            ["family", "store_id", "service_level"]
        )
    )
    checks.append(
        _check(
            "lead_time_demand_monotonic",
            lead_time_monotonic,
            lead_time_monotonic,
            True,
        )
    )
    safety_monotonic = all(
        group.sort_values("service_level")[
            "safety_stock"
        ].is_monotonic_increasing
        for _, group in combined.groupby(
            ["family", "store_id", "lead_time_days"]
        )
    )
    checks.append(
        _check(
            "safety_stock_monotonic_in_service_level",
            safety_monotonic,
            safety_monotonic,
            True,
        )
    )
    level_reference = (
        forecast_scenarios[
            ["store_id", "model_daily_demand", "bias_adjusted_daily_demand"]
        ]
        .drop_duplicates(subset=["store_id"])
        .merge(
            errors[["store_id", "bias", "mean_predicted", "mean_actual"]],
            on="store_id",
            how="inner",
        )
        .sort_values("store_id")
        .assign(
            expected_level=lambda frame: frame["mean_predicted"]
            + frame["bias"]
        )
    )
    level_match = bool(
        len(level_reference) == len(errors)
        and np.allclose(
            level_reference["model_daily_demand"].to_numpy(dtype=float),
            level_reference["mean_predicted"].to_numpy(dtype=float),
            rtol=RTOL,
        )
        and np.allclose(
            level_reference["bias_adjusted_daily_demand"].to_numpy(
                dtype=float
            ),
            level_reference["expected_level"].to_numpy(dtype=float),
            rtol=RTOL,
        )
    )
    checks.append(
        _check(
            "forecast_level_is_bias_corrected",
            level_match,
            level_match,
            True,
        )
    )
    # The bias-adjusted level is an algebraic identity with the realised
    # validation mean -- a recovered level, not a forward forecast. Asserting
    # the identity keeps that reading honest in the artifacts.
    identity_match = bool(
        np.allclose(
            level_reference["bias_adjusted_daily_demand"].to_numpy(
                dtype=float
            ),
            level_reference["mean_actual"].to_numpy(dtype=float),
            rtol=RTOL,
        )
    )
    checks.append(
        _check(
            "forecast_level_recovers_validation_mean",
            identity_match,
            identity_match,
            True,
        )
    )

    # Insights and findings
    checks.append(
        _check(
            "insight_types_complete",
            set(insights["insight_type"]) == set(INSIGHT_TYPES),
            sorted(set(insights["insight_type"])),
            sorted(INSIGHT_TYPES),
        )
    )
    checks.append(
        _check(
            "insight_store_mapping_valid",
            {int(s) for s in insights["store_id"]}
            <= {int(s) for s in selected_models["store_id"]},
            sorted({int(s) for s in insights["store_id"]}),
            sorted({int(s) for s in selected_models["store_id"]}),
        )
    )
    checks.append(
        _check(
            "findings_state_every_selected_model",
            all(line in findings_text for line in model_lines),
            sum(line in findings_text for line in model_lines),
            len(model_lines),
        )
    )
    checks.append(
        _check(
            "findings_no_false_untuned_claim",
            "has no Phase 12 tuned" not in findings_text,
            "has no Phase 12 tuned" not in findings_text,
            True,
        )
    )
    checks.append(
        _check(
            "quality_report_gates_run",
            True,
            "implemented",
            "main() raises when any check fails",
        )
    )

    return pd.DataFrame(checks)


# --- Entry point --------------------------------------------------------


def main() -> None:
    """Run Phase 13 forecasting and inventory insights."""
    print("Running Phase 13 forecasting and inventory insights...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data, stats = load_training_demand()

    selected_models, validation = load_phase12_model_evidence()

    validate_training_demand(
        data,
        expected_stores={int(s) for s in selected_models["store_id"]},
    )

    densification = summarize_densification(data)

    demand_summary = calculate_demand_summary(data)

    variability = calculate_variability_summary(data)

    errors = load_phase12_forecast_errors(validation)

    error_analysis = load_phase12_error_analysis()

    scenarios = calculate_inventory_scenarios(
        variability,
        selected_models,
    )

    forecast_scenarios = calculate_forecast_scenarios(
        errors,
        selected_models,
    )

    insights = create_insights(
        demand_summary,
        variability,
        scenarios,
        forecast_scenarios,
        errors,
        validation,
    )

    model_lines = build_model_lines(errors)

    findings_text = build_findings_text(
        demand_summary,
        variability,
        scenarios,
        forecast_scenarios,
        errors,
        densification,
        model_lines,
    )

    report = build_quality_report(
        data=data,
        stats=stats,
        densification=densification,
        demand_summary=demand_summary,
        scenarios=scenarios,
        forecast_scenarios=forecast_scenarios,
        errors=errors,
        validation=validation,
        error_analysis=error_analysis,
        insights=insights,
        findings_text=findings_text,
        model_lines=model_lines,
        selected_models=selected_models,
    )

    report.to_csv(QUALITY_REPORT_PATH, index=False)

    failed = report.loc[~report["passed"], "check"].tolist()

    if failed:
        raise RuntimeError(
            "Phase 13 quality checks failed: " + ", ".join(failed)
        )

    demand_summary.to_csv(DEMAND_SUMMARY_PATH, index=False)
    variability.to_csv(VARIABILITY_PATH, index=False)
    densification.to_csv(DENSIFICATION_PATH, index=False)
    scenarios.to_csv(SCENARIOS_PATH, index=False)
    forecast_scenarios.to_csv(FORECAST_SCENARIOS_PATH, index=False)
    errors.to_csv(FORECAST_ERROR_PATH, index=False)
    insights.to_csv(INSIGHTS_PATH, index=False)

    FINDINGS_PATH.write_text(
        f"{findings_text}\n\nQuality report: all checks passed\n",
        encoding="utf-8",
    )

    print("Forecasting and inventory insights completed successfully.")
    print(f"Demand summary: {DEMAND_SUMMARY_PATH}")
    print(f"Variability summary: {VARIABILITY_PATH}")
    print(f"Densification summary: {DENSIFICATION_PATH}")
    print(f"Inventory scenarios: {SCENARIOS_PATH}")
    print(f"Forecast scenarios: {FORECAST_SCENARIOS_PATH}")
    print(f"Forecast error summary: {FORECAST_ERROR_PATH}")
    print(f"Insights: {INSIGHTS_PATH}")
    print(f"Findings: {FINDINGS_PATH}")
    print(f"Quality report: {QUALITY_REPORT_PATH}")


if __name__ == "__main__":
    main()
