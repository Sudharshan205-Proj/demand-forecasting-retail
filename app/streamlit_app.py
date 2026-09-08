"""Streamlit application for retail demand forecasting and inventory insights."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.data_loader import load_application_data
from app.formatting import format_number, format_percent
from app.logging_config import get_logger

logger = get_logger()


st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def get_data() -> dict:
    """Load and cache application data."""
    return load_application_data()


def find_column(frame, candidates: list[str]) -> str | None:
    """Find the first matching column from a list of candidates."""
    normalized = {column.lower(): column for column in frame.columns}

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    return None


def main() -> None:
    """Render the application."""
    st.title("Retail Demand Forecasting & Inventory Insights")
    st.caption(
        "Decision-support application built from the validated project outputs."
    )

    try:
        data = get_data()
    except (FileNotFoundError, ValueError) as exc:
        logger.exception("Application data could not be loaded.")
        st.error("The application could not load its required analysis artifacts.")
        st.code(str(exc))
        st.stop()

    demand = data["demand"].copy()
    variability = data["variability"].copy()
    scenarios = data["scenarios"].copy()
    forecast_results = data["forecast_results"].copy()
    configurations = data["forecast_configurations"].copy()

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
            "The analysis artifacts do not contain the expected store identifier.")
        st.stop()

    stores = sorted(
        {
            int(value)
            for value in demand[demand_store_column].dropna().unique()
        }
    )

    if not stores:
        st.error("No stores were found in the analysis data.")
        st.stop()

    selected_store = st.sidebar.selectbox(
        "Store",
        stores,
        format_func=lambda value: f"Store {value}",
    )

    store_demand = demand[
        demand[demand_store_column] == selected_store
    ].copy()

    store_variability = variability[
        variability[variability_store_column] == selected_store
    ].copy()

    store_scenarios = scenarios[
        scenarios[scenario_store_column] == selected_store
    ].copy()

    st.sidebar.markdown("### Scenario controls")

    lead_time_column = find_column(
        store_scenarios,
        ["lead_time_days", "lead_time"],
    )
    service_level_column = find_column(
        store_scenarios,
        ["service_level"],
    )

    if lead_time_column:
        lead_times = sorted(
            store_scenarios[lead_time_column].dropna().unique().tolist()
        )
        selected_lead_time = st.sidebar.selectbox(
            "Lead time (days)",
            lead_times,
            index=lead_times.index(14) if 14 in lead_times else 0,
        )
        store_scenarios = store_scenarios[
            store_scenarios[lead_time_column] == selected_lead_time
        ]

    if service_level_column:
        service_levels = sorted(
            store_scenarios[service_level_column].dropna().unique().tolist()
        )
        selected_service_level = st.sidebar.selectbox(
            "Service level",
            service_levels,
            index=(
                service_levels.index(0.95)
                if 0.95 in service_levels
                else service_levels.index(95)
                if 95 in service_levels
                else 0
            ),
        )

        if selected_service_level <= 1:
            store_scenarios = store_scenarios[
                store_scenarios[service_level_column] == selected_service_level
            ]
        else:
            store_scenarios = store_scenarios[
                store_scenarios[service_level_column] == selected_service_level
            ]

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
        average_demand = float(store_demand[demand_value_column].iloc[0])
        metric_columns[0].metric(
            "Average Daily Demand",
            format_number(average_demand),
        )
    else:
        metric_columns[0].metric("Average Daily Demand", "N/A")

    if cv_column and not store_variability.empty:
        cv_value = float(store_variability[cv_column].iloc[0])

        if cv_value <= 1:
            cv_display = format_percent(cv_value * 100)
        else:
            cv_display = format_percent(cv_value)

        metric_columns[1].metric(
            "Demand Variability (CV)",
            cv_display,
        )
    else:
        metric_columns[1].metric("Demand Variability (CV)", "N/A")

    metric_columns[2].metric(
        "Forecasting Status",
        "Validated" if selected_store in [1, 2, 3] else "Descriptive",
    )

    st.subheader("Inventory Scenario")

    reorder_column = find_column(
        store_scenarios,
        ["reorder_point", "reorder_point_quantity"],
    )

    if reorder_column and not store_scenarios.empty:
        reorder_point = float(store_scenarios[reorder_column].iloc[0])
        st.metric(
            "Scenario Reorder Point",
            format_number(reorder_point),
        )

    st.dataframe(
        store_scenarios,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Forecast Model Evaluation")

    result_store_column = find_column(
        forecast_results,
        ["store_id"],
    )

    if result_store_column:
        store_results = forecast_results[
            forecast_results[result_store_column] == selected_store
        ].copy()

        st.dataframe(
            store_results,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Selected Model Configuration")

    configuration_store_column = find_column(
        configurations,
        ["store_id"],
    )

    if configuration_store_column:
        store_configurations = configurations[
            configurations[configuration_store_column] == selected_store
        ].copy()

        st.dataframe(
            store_configurations,
            use_container_width=True,
            hide_index=True,
        )

    if selected_store == 4:
        st.warning(
            "Store 4 is presented descriptively because the project did not "
            "establish a validated tuned forecasting configuration for this "
            "shorter series."
        )

    st.info(
        "Inventory values are scenario-based analytical estimates. "
        "They should not be treated as operational requirements without "
        "validated business inputs such as actual lead times and service-level "
        "policies."
    )

    st.caption(
        "Python remains the primary forecasting implementation. "
        "The application presents validated project outputs and does not "
        "retrain forecasting models during normal use."
    )


if __name__ == "__main__":
    main()