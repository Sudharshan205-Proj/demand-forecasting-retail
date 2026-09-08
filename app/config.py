"""Application configuration."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

INVENTORY_DEMAND_FILE = ANALYSIS_DIR / "inventory_demand_summary.csv"
INVENTORY_VARIABILITY_FILE = ANALYSIS_DIR / "inventory_variability_summary.csv"
INVENTORY_SCENARIOS_FILE = ANALYSIS_DIR / "inventory_scenarios.csv"
FORECAST_INSIGHTS_FILE = ANALYSIS_DIR / "forecast_inventory_insights.csv"
FORECAST_RESULTS_FILE = ANALYSIS_DIR / "forecasting_model_results.csv"
FORECAST_CONFIGURATIONS_FILE = (
    ANALYSIS_DIR / "forecasting_model_configurations.csv"
)
FORECAST_SUMMARY_FILE = ANALYSIS_DIR / "forecasting_summary.csv"


REQUIRED_ANALYSIS_FILES = (
    INVENTORY_DEMAND_FILE,
    INVENTORY_VARIABILITY_FILE,
    INVENTORY_SCENARIOS_FILE,
    FORECAST_INSIGHTS_FILE,
    FORECAST_RESULTS_FILE,
    FORECAST_CONFIGURATIONS_FILE,
)