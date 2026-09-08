"""Load validated analysis artifacts for the Streamlit application."""

from pathlib import Path

import pandas as pd

from app.config import REQUIRED_ANALYSIS_FILES


def validate_required_files() -> None:
    """Raise FileNotFoundError when an application input is missing."""
    missing = [path for path in REQUIRED_ANALYSIS_FILES if not path.exists()]

    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(
            "Required application artifacts are missing:\n"
            f"{missing_text}"
        )


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV artifact and validate that it contains data."""
    if not path.exists():
        raise FileNotFoundError(f"Required artifact does not exist: {path}")

    frame = pd.read_csv(path)

    if frame.empty:
        raise ValueError(f"Required artifact is empty: {path}")

    return frame


def load_application_data() -> dict[str, pd.DataFrame]:
    """Load all application datasets."""
    validate_required_files()

    from app.config import (
        FORECAST_CONFIGURATIONS_FILE,
        FORECAST_INSIGHTS_FILE,
        FORECAST_RESULTS_FILE,
        INVENTORY_DEMAND_FILE,
        INVENTORY_SCENARIOS_FILE,
        INVENTORY_VARIABILITY_FILE,
    )

    return {
        "demand": load_csv(INVENTORY_DEMAND_FILE),
        "variability": load_csv(INVENTORY_VARIABILITY_FILE),
        "scenarios": load_csv(INVENTORY_SCENARIOS_FILE),
        "insights": load_csv(FORECAST_INSIGHTS_FILE),
        "forecast_results": load_csv(FORECAST_RESULTS_FILE),
        "forecast_configurations": load_csv(FORECAST_CONFIGURATIONS_FILE),
    }