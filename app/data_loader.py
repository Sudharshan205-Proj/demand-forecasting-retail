"""Load validated analysis artifacts for the Streamlit application."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import (
    ANALYSIS_DIR,
    DEPLOY_ARTIFACTS_DIR,
    artifact_paths,
    required_analysis_files,
    resolve_analysis_dir,
)


def missing_artifacts() -> list[Path]:
    """Return the required artifact paths that do not exist."""
    return [path for path in required_analysis_files() if not path.is_file()]


def validate_required_files() -> None:
    """Raise FileNotFoundError when an application input is missing."""
    missing = missing_artifacts()

    if not missing:
        return

    missing_text = "\n".join(str(path) for path in missing)
    raise FileNotFoundError(
        "Required application artifacts are missing:\n"
        f"{missing_text}\n"
        "The application reads the analysis pipeline output in "
        f"{ANALYSIS_DIR} or the committed deployment bundle in "
        f"{DEPLOY_ARTIFACTS_DIR}; neither currently holds every artifact."
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
    """Load every application dataset from the resolved artifact directory."""
    validate_required_files()

    return {
        key: load_csv(path)
        for key, path in artifact_paths().items()
    }


__all__ = [
    "load_application_data",
    "load_csv",
    "missing_artifacts",
    "resolve_analysis_dir",
    "validate_required_files",
]
