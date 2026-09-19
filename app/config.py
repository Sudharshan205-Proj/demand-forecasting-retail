"""Application configuration.

The application reads compact analytical artifacts. Locally those are the
ones the analysis pipeline writes to ``data/analysis/``, which is excluded
from Git. A deployed instance has no pipeline output, so a small frozen
snapshot is committed under ``deploy/artifacts/`` and used as a fallback.

Resolution order for the artifact directory:

1. the ``APP_ANALYSIS_DIR`` environment variable, when set;
2. ``data/analysis/``, when it holds every required artifact;
3. ``deploy/artifacts/``, the committed deployment bundle.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
DEPLOY_ARTIFACTS_DIR = PROJECT_ROOT / "deploy" / "artifacts"

ANALYSIS_DIR_ENV_VAR = "APP_ANALYSIS_DIR"

#: Logical name -> file name for every artifact the application loads.
ARTIFACT_FILES = {
    "demand": "inventory_demand_summary.csv",
    "variability": "inventory_variability_summary.csv",
    "scenarios": "inventory_scenarios.csv",
    "forecast_results": "forecasting_model_results.csv",
    "forecast_configurations": "forecasting_model_configurations.csv",
    "selected_configurations": "selected_model_configurations.csv",
    "tuned_validation": "tuned_validation_results.csv",
}

REQUIRED_ARTIFACTS = tuple(ARTIFACT_FILES.values())


def _holds_every_artifact(directory: Path) -> bool:
    """Return True when ``directory`` contains every required artifact."""
    return all((directory / name).is_file() for name in REQUIRED_ARTIFACTS)


def resolve_analysis_dir() -> Path:
    """Return the directory the application should read its artifacts from."""
    override = os.environ.get(ANALYSIS_DIR_ENV_VAR)
    if override:
        return Path(override)

    if _holds_every_artifact(ANALYSIS_DIR):
        return ANALYSIS_DIR

    if _holds_every_artifact(DEPLOY_ARTIFACTS_DIR):
        return DEPLOY_ARTIFACTS_DIR

    # Neither location is complete: return the local path so the error
    # message names the directory the pipeline is expected to write.
    return ANALYSIS_DIR


def artifact_paths() -> dict[str, Path]:
    """Return the resolved path of every application artifact."""
    directory = resolve_analysis_dir()

    return {
        key: directory / filename for key, filename in ARTIFACT_FILES.items()
    }


def required_analysis_files() -> tuple[Path, ...]:
    """Return the resolved paths the application requires."""
    return tuple(artifact_paths().values())
