"""Streamlit application for retail demand forecasting and inventory insights.

The module is import-safe: every Streamlit call happens inside ``main()``, so
the pure helpers below can be exercised by the test suite without a running
Streamlit runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app.data_loader import load_application_data, resolve_analysis_dir
from app.formatting import format_number, format_ratio_as_percent
from app.logging_config import get_logger

logger = get_logger()

PAGE_TITLE = "Retail Demand Forecasting"
PAGE_ICON = "📊"

SCENARIO_ASSUMPTION_NOTE = (
    "Inventory values are scenario-based analytical estimates. They should "
    "not be treated as operational requirements without validated business "
    "inputs such as actual lead times and service-level policies."
)

NON_RETRAINING_NOTE = (
    "Python remains the primary forecasting implementation. The application "
    "presents validated project outputs and does not retrain forecasting "
    "models during normal use."
)


def find_column(frame, candidates: list[str]) -> str | None:
    """Find the first matching column from a list of candidates."""
    normalized = {column.lower(): column for column in frame.columns}

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    return None


def store_ids(frame, store_column: str) -> list[int]:
    """Return the sorted store identifiers present in a frame."""
    values = frame[store_column].dropna().unique()

    return sorted({int(value) for value in values})


def selected_model_evidence(
    selected: pd.DataFrame,
    tuned: pd.DataFrame,
    store_id: int,
) -> dict | None:
    """Return the Phase 12 selected-model evidence for one store.

    Every field is read from the artifacts, so no store is treated
    differently by identifier.
    """
    selected_column = find_column(selected, ["store_id"])
    tuned_column = find_column(tuned, ["store_id"])

    if selected_column is None:
        return None

    selected_rows = selected[selected[selected_column] == store_id]

    if selected_rows.empty:
        return None

    row = selected_rows.iloc[0]
    tuned_row = None

    if tuned_column is not None:
        tuned_rows = tuned[tuned[tuned_column] == store_id]
        if not tuned_rows.empty:
            tuned_row = tuned_rows.iloc[0]

    def value(frame_row, column, default=None):
        if frame_row is None:
            return default
        return frame_row[column] if column in frame_row.index else default

    folds = value(row, "cv_folds")

    return {
        "store_id": int(store_id),
        "model": str(value(row, "model", "unknown")),
        "configuration": str(value(row, "configuration", "")),
        "cv_folds": int(folds) if folds is not None else None,
        "selection_basis": str(value(row, "selection_basis", "")),
        "mean_cv_rmse": value(row, "mean_rmse"),
        "mean_cv_mape": value(row, "mean_mape_percent"),
        "validation_rmse": value(tuned_row, "rmse"),
        "validation_mape": value(tuned_row, "mape_percent"),
    }


def evidence_label(evidence: dict) -> str:
    """Return a short, accurate description of a store's model evidence."""
    folds = evidence.get("cv_folds")

    if folds is None:
        return "Validated"

    return f"Validated ({folds}-fold CV)"


def evidence_caveat(
    evidence: dict,
    training_days: int | None = None,
) -> str | None:
    """Return a caveat when a store's selection rests on a single fold."""
    folds = evidence.get("cv_folds")

    if folds is None or folds > 1:
        return None

    history = (
        f" Its history is the shortest of the stores ({training_days} "
        "training days)."
        if training_days
        else ""
    )

    return (
        f"Store {evidence['store_id']} has a validated tuned configuration "
        f"({evidence['model']}, {evidence['configuration']}), selected on a "
        "single cross-validation fold because its shorter history supports "
        f"only one.{history} Its validation result therefore rests on weaker "
        "evidence than stores tuned across three folds and should not be "
        "read as equally well evidenced. It is a validated configuration, "
        "not a descriptive-only result."
    )


def filter_scenarios(
    scenarios: pd.DataFrame,
    lead_time_column: str,
    service_level_column: str,
    lead_time,
    service_level,
) -> pd.DataFrame:
    """Filter scenarios to one lead time and one service level."""
    filtered = scenarios

    if lead_time is not None:
        filtered = filtered[filtered[lead_time_column] == lead_time]

    if service_level is not None:
        filtered = filtered[filtered[service_level_column] == service_level]

    return filtered


def training_days_for(
    demand: pd.DataFrame,
    demand_column: str,
    store_id: int,
) -> int | None:
    """Return the training-day count recorded for one store."""
    rows = demand[demand[demand_column] == store_id]

    if rows.empty or "training_days" not in rows.columns:
        return None

    return int(rows.iloc[0]["training_days"])


def main() -> None:
    """Render the application."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
    )

    st.title("Retail Demand Forecasting & Inventory Insights")
    st.caption(
        "Decision-support application built from the validated project outputs."
    )

    @st.cache_data
    def load_data() -> dict:
        """Load and cache application data."""
        return load_application_data()

    try:
        data = load_data()
    except (FileNotFoundError, ValueError) as exc:
        logger.exception("Application data could not be loaded.")
        st.error(
            "The application could not load its required analysis artifacts."
        )
        st.code(str(exc))
        st.stop()

    demand = data["demand"]
    variability = data["variability"]
    scenarios = data["scenarios"]
    forecast_results = data["forecast_results"]
    configurations = data["forecast_configurations"]
    selected = data["selected_configurations"]
    tuned = data["tuned_validation"]

    demand_store_column = find_column(demand, ["store_id"])
    variability_store_column = find_column(variability, ["store_id"])
    scenario_store_column = find_column(scenarios, ["store_id"])

    if not all(
        (
            demand_store_column,
            variability_store_column,
            scenario_store_column,
        )
    ):
        st.error(
            "The analysis artifacts do not contain the expected store identifier."
        )
        st.stop()

    stores = store_ids(demand, demand_store_column)

    if not stores:
        st.error("No stores were found in the analysis data.")
        st.stop()

    selected_store = st.sidebar.selectbox(
        "Store",
        stores,
        format_func=lambda value: f"Store {value}",
    )

    store_demand = demand[demand[demand_store_column] == selected_store]
    store_variability = variability[
        variability[variability_store_column] == selected_store
    ]
    store_scenarios = scenarios[
        scenarios[scenario_store_column] == selected_store
    ]

    st.sidebar.markdown("### Scenario controls")

    lead_time_column = find_column(
        store_scenarios,
        ["lead_time_days", "lead_time"],
    )
    service_level_column = find_column(
        store_scenarios,
        ["service_level"],
    )

    selected_lead_time = None
    selected_service_level = None

    if lead_time_column:
        lead_times = sorted(
            store_scenarios[lead_time_column].dropna().unique().tolist()
        )
        selected_lead_time = st.sidebar.selectbox(
            "Lead time (days)",
            lead_times,
            index=lead_times.index(14) if 14 in lead_times else 0,
        )

    if service_level_column:
        service_levels = sorted(
            store_scenarios[service_level_column].dropna().unique().tolist()
        )
        selected_service_level = st.sidebar.selectbox(
            "Service level",
            service_levels,
            index=(
                service_levels.index(0.95) if 0.95 in service_levels else 0
            ),
            format_func=lambda value: format_ratio_as_percent(value),
        )

    if lead_time_column and service_level_column:
        store_scenarios = filter_scenarios(
            store_scenarios,
            lead_time_column,
            service_level_column,
            selected_lead_time,
            selected_service_level,
        )

    evidence = selected_model_evidence(selected, tuned, selected_store)
    training_days = training_days_for(
        demand,
        demand_store_column,
        selected_store,
    )

    st.subheader(f"Store {selected_store} — Demand Overview")

    demand_value_column = find_column(
        store_demand,
        ["mean_daily_demand", "average_daily_demand"],
    )
    cv_column = find_column(
        store_variability,
        ["coefficient_of_variation", "cv"],
    )

    metric_columns = st.columns(3)

    if demand_value_column and not store_demand.empty:
        metric_columns[0].metric(
            "Average Daily Demand",
            format_number(float(store_demand[demand_value_column].iloc[0])),
        )
    else:
        metric_columns[0].metric("Average Daily Demand", "N/A")

    if cv_column and not store_variability.empty:
        metric_columns[1].metric(
            "Demand Variability (CV)",
            format_ratio_as_percent(
                float(store_variability[cv_column].iloc[0])
            ),
        )
    else:
        metric_columns[1].metric("Demand Variability (CV)", "N/A")

    if evidence:
        metric_columns[2].metric(
            "Forecast Evidence",
            evidence_label(evidence),
        )
    else:
        metric_columns[2].metric("Forecast Evidence", "Not available")

    if training_days:
        st.caption(
            f"Training history: {training_days:,} observed days."
        )

    st.subheader("Inventory Scenario")

    reorder_column = find_column(
        store_scenarios,
        ["reorder_point", "reorder_point_quantity"],
    )

    if reorder_column and not store_scenarios.empty:
        st.metric(
            "Scenario Reorder Point",
            format_number(float(store_scenarios[reorder_column].iloc[0])),
        )

    st.dataframe(
        store_scenarios,
        width="stretch",
        hide_index=True,
    )

    st.subheader("Selected Model (Phase 12)")

    if evidence:
        evidence_columns = st.columns(3)
        evidence_columns[0].metric("Selected model", evidence["model"])
        evidence_columns[1].metric(
            "Cross-validation folds",
            evidence["cv_folds"] if evidence["cv_folds"] is not None else "N/A",
        )
        evidence_columns[2].metric(
            "Validation RMSE",
            format_number(evidence["validation_rmse"]),
        )

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "store_id": evidence["store_id"],
                        "model": evidence["model"],
                        "configuration": evidence["configuration"],
                        "cv_folds": evidence["cv_folds"],
                        "mean_cv_rmse": evidence["mean_cv_rmse"],
                        "mean_cv_mape_percent": evidence["mean_cv_mape"],
                        "validation_rmse": evidence["validation_rmse"],
                        "validation_mape_percent": evidence["validation_mape"],
                    }
                ]
            ),
            width="stretch",
            hide_index=True,
        )

        if evidence["selection_basis"]:
            st.caption(f"Selection basis: {evidence['selection_basis']}")

        caveat = evidence_caveat(evidence, training_days)
        if caveat:
            st.warning(caveat)
    else:
        st.info(
            "No selected Phase 12 configuration is recorded for this store."
        )

    st.subheader("Forecast Model Comparison (Phase 11)")

    result_store_column = find_column(forecast_results, ["store_id"])

    if result_store_column:
        st.dataframe(
            forecast_results[
                forecast_results[result_store_column] == selected_store
            ],
            width="stretch",
            hide_index=True,
        )

    configuration_store_column = find_column(configurations, ["store_id"])

    if configuration_store_column:
        with st.expander("Model configurations (Phase 11)"):
            st.dataframe(
                configurations[
                    configurations[configuration_store_column] == selected_store
                ],
                width="stretch",
                hide_index=True,
            )

    st.info(SCENARIO_ASSUMPTION_NOTE)
    st.caption(NON_RETRAINING_NOTE)

    with st.expander("Data source"):
        st.code(str(resolve_analysis_dir()))
        st.caption(
            "Artifacts are read from the analysis pipeline output when it is "
            "present, otherwise from the committed deployment bundle."
        )


if __name__ == "__main__":
    main()

