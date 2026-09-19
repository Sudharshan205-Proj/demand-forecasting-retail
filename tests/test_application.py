"""Tests for the Phase 16 Streamlit application."""

from __future__ import annotations

import math
import re
from pathlib import Path

import pandas as pd
import pytest

import app.config as config
from app.data_loader import (
    load_application_data,
    load_csv,
    missing_artifacts,
    validate_required_files,
)
from app.formatting import (
    format_number,
    format_percent,
    format_ratio_as_percent,
)
from app import streamlit_app

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "data" / "analysis"
BUNDLE_DIR = ROOT / "deploy" / "artifacts"
APP_SOURCE = ROOT / "app"

pipeline_available = pytest.mark.skipif(
    not all(
        (PIPELINE_DIR / name).is_file() for name in config.REQUIRED_ARTIFACTS
    ),
    reason="the analysis pipeline output is not present in this checkout",
)


def write_artifacts(directory: Path) -> dict[str, pd.DataFrame]:
    """Write a minimal, internally consistent artifact set."""
    directory.mkdir(parents=True, exist_ok=True)

    frames = {
        "inventory_demand_summary.csv": pd.DataFrame(
            {
                "store_id": [1, 2],
                "training_days": [500, 60],
                "mean_daily_demand": [100.0, 80.0],
                "coefficient_of_variation": [0.2, 0.3],
            }
        ),
        "inventory_variability_summary.csv": pd.DataFrame(
            {
                "store_id": [1, 2],
                "coefficient_of_variation": [0.2, 0.3],
            }
        ),
        "inventory_scenarios.csv": pd.DataFrame(
            {
                "store_id": [1, 1, 1, 1],
                "lead_time_days": [7, 7, 14, 14],
                "service_level": [0.9, 0.95, 0.9, 0.95],
                "reorder_point": [800.0, 850.0, 1600.0, 1700.0],
            }
        ),
        "forecasting_model_results.csv": pd.DataFrame(
            {
                "store_id": [1, 2],
                "model": ["seasonal_naive", "seasonal_naive"],
                "rmse": [10.0, 12.0],
            }
        ),
        "forecasting_model_configurations.csv": pd.DataFrame(
            {
                "store_id": [1, 2],
                "model": ["seasonal_naive", "seasonal_naive"],
                "configuration": ["season_length=7", "season_length=7"],
            }
        ),
        "selected_model_configurations.csv": pd.DataFrame(
            {
                "store_id": [1, 2],
                "model": ["feature_gbm", "seasonal_naive"],
                "configuration": ["synthetic", "season_length=7"],
                "cv_folds": [3, 1],
                "mean_rmse": [5.0, 9.0],
                "mean_mape_percent": [4.0, 8.0],
                "selection_basis": ["lowest mean CV RMSE", "lowest mean CV RMSE"],
            }
        ),
        "tuned_validation_results.csv": pd.DataFrame(
            {
                "store_id": [1, 2],
                "rmse": [6.0, 11.0],
                "mape_percent": [5.0, 9.0],
            }
        ),
    }

    for name, frame in frames.items():
        frame.to_csv(directory / name, index=False)

    return frames


@pytest.fixture
def artifacts(tmp_path: Path) -> Path:
    """A temporary directory holding a complete artifact set."""
    directory = tmp_path / "artifacts"
    write_artifacts(directory)
    return directory


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------


def test_format_number_basic():
    assert format_number(1234.5) == "1,234.50"


def test_format_number_integer():
    assert format_number(7) == "7.00"


def test_format_number_handles_missing_values():
    assert format_number(None) == "N/A"
    assert format_number(float("nan")) == "N/A"
    assert format_number(float("inf")) == "N/A"
    assert format_number(float("-inf")) == "N/A"


def test_format_percent_basic():
    assert format_percent(95.5) == "95.50%"


def test_format_percent_handles_missing_values():
    assert format_percent(None) == "N/A"
    assert format_percent(float("nan")) == "N/A"
    assert format_percent(math.inf) == "N/A"


def test_format_ratio_as_percent_scales_a_ratio():
    assert format_ratio_as_percent(0.3801) == "38.01%"


def test_format_ratio_as_percent_passes_through_a_percentage():
    assert format_ratio_as_percent(38.01) == "38.01%"


def test_format_ratio_as_percent_handles_missing_values():
    assert format_ratio_as_percent(None) == "N/A"
    assert format_ratio_as_percent(float("nan")) == "N/A"


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def test_load_csv_reads_a_file(tmp_path: Path):
    path = tmp_path / "example.csv"
    pd.DataFrame({"store_id": [1, 2], "value": [10.0, 20.0]}).to_csv(
        path, index=False
    )

    frame = load_csv(path)

    assert len(frame) == 2
    assert list(frame.columns) == ["store_id", "value"]


def test_load_csv_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "missing.csv")


def test_load_csv_empty_file(tmp_path: Path):
    path = tmp_path / "empty.csv"
    pd.DataFrame(columns=["store_id"]).to_csv(path, index=False)

    with pytest.raises(ValueError):
        load_csv(path)


def test_load_application_data_uses_the_override(
    artifacts: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv(config.ANALYSIS_DIR_ENV_VAR, str(artifacts))

    data = load_application_data()

    assert sorted(data) == sorted(config.ARTIFACT_FILES)
    assert len(data["scenarios"]) == 4


def test_missing_artifacts_names_every_gap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv(config.ANALYSIS_DIR_ENV_VAR, str(empty))

    missing = missing_artifacts()

    assert len(missing) == len(config.REQUIRED_ARTIFACTS)

    with pytest.raises(FileNotFoundError) as error:
        validate_required_files()

    message = str(error.value)
    assert "inventory_scenarios.csv" in message
    assert str(config.DEPLOY_ARTIFACTS_DIR) in message


# --------------------------------------------------------------------------
# Artifact resolution
# --------------------------------------------------------------------------


def test_resolution_honours_the_environment_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    override = tmp_path / "elsewhere"
    monkeypatch.setenv(config.ANALYSIS_DIR_ENV_VAR, str(override))

    assert config.resolve_analysis_dir() == override


def test_resolution_falls_back_to_the_deployment_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.delenv(config.ANALYSIS_DIR_ENV_VAR, raising=False)
    monkeypatch.setattr(config, "ANALYSIS_DIR", tmp_path / "absent")

    assert config.resolve_analysis_dir() == config.DEPLOY_ARTIFACTS_DIR


def test_resolution_returns_the_local_path_when_nothing_is_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.delenv(config.ANALYSIS_DIR_ENV_VAR, raising=False)
    monkeypatch.setattr(config, "ANALYSIS_DIR", tmp_path / "absent")
    monkeypatch.setattr(config, "DEPLOY_ARTIFACTS_DIR", tmp_path / "also-absent")

    assert config.resolve_analysis_dir() == tmp_path / "absent"


@pipeline_available
def test_resolution_prefers_the_pipeline_output(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv(config.ANALYSIS_DIR_ENV_VAR, raising=False)

    assert config.resolve_analysis_dir() == PIPELINE_DIR


# --------------------------------------------------------------------------
# Deployment bundle
# --------------------------------------------------------------------------


def test_deployment_bundle_is_complete():
    for name in config.REQUIRED_ARTIFACTS:
        path = BUNDLE_DIR / name
        assert path.is_file(), f"{name} is missing from the deployment bundle"
        assert path.stat().st_size > 0


def test_deployment_bundle_holds_nothing_unexpected():
    present = sorted(p.name for p in BUNDLE_DIR.glob("*.csv"))

    assert present == sorted(config.REQUIRED_ARTIFACTS)


@pipeline_available
def test_deployment_bundle_matches_the_pipeline_output():
    """A deployed instance must not silently differ from the local one."""
    for name in config.REQUIRED_ARTIFACTS:
        bundled = pd.read_csv(BUNDLE_DIR / name)
        produced = pd.read_csv(PIPELINE_DIR / name)

        try:
            pd.testing.assert_frame_equal(bundled, produced)
        except AssertionError as error:  # pragma: no cover - failure detail
            raise AssertionError(
                f"deploy/artifacts/{name} has drifted from "
                f"data/analysis/{name}: {error}"
            ) from error


# --------------------------------------------------------------------------
# Model evidence derivation
# --------------------------------------------------------------------------


@pytest.fixture
def evidence_frames(artifacts: Path) -> dict:
    """Load the synthetic artifact set that the evidence tests use."""
    return {
        key: pd.read_csv(artifacts / name)
        for key, name in config.ARTIFACT_FILES.items()
    }


def test_store_ids_are_sorted_integers(evidence_frames: dict):
    demand = pd.DataFrame({"store_id": [3, 1, 2, 1]})

    assert streamlit_app.store_ids(demand, "store_id") == [1, 2, 3]


def test_find_column_is_case_insensitive_and_reports_missing():
    frame = pd.DataFrame({"Store_Id": [1], "Value": [2.0]})

    assert streamlit_app.find_column(frame, ["store_id"]) == "Store_Id"
    assert streamlit_app.find_column(frame, ["absent"]) is None


def test_single_fold_store_is_derived_from_the_data(evidence_frames: dict):
    evidence = streamlit_app.selected_model_evidence(
        evidence_frames["selected_configurations"],
        evidence_frames["tuned_validation"],
        2,
    )

    assert evidence["model"] == "seasonal_naive"
    assert evidence["configuration"] == "season_length=7"
    assert evidence["cv_folds"] == 1
    assert evidence["validation_rmse"] == pytest.approx(11.0)


def test_evidence_matches_every_store_row(evidence_frames: dict):
    """No store may be special-cased: each value comes from its own row."""
    selected = evidence_frames["selected_configurations"]
    tuned = evidence_frames["tuned_validation"]

    for row in selected.itertuples():
        evidence = streamlit_app.selected_model_evidence(
            selected, tuned, int(row.store_id)
        )

        assert evidence["model"] == row.model
        assert evidence["cv_folds"] == int(row.cv_folds)
        assert evidence["store_id"] == int(row.store_id)


def test_unknown_store_has_no_evidence(evidence_frames: dict):
    assert (
        streamlit_app.selected_model_evidence(
            evidence_frames["selected_configurations"],
            evidence_frames["tuned_validation"],
            99,
        )
        is None
    )


def test_evidence_label_reports_the_fold_count(evidence_frames: dict):
    multi = streamlit_app.selected_model_evidence(
        evidence_frames["selected_configurations"],
        evidence_frames["tuned_validation"],
        1,
    )
    single = streamlit_app.selected_model_evidence(
        evidence_frames["selected_configurations"],
        evidence_frames["tuned_validation"],
        2,
    )

    assert streamlit_app.evidence_label(multi) == "Validated (3-fold CV)"
    assert streamlit_app.evidence_label(single) == "Validated (1-fold CV)"
    assert streamlit_app.evidence_label({}) == "Validated"


def test_caveat_applies_only_to_a_single_fold(evidence_frames: dict):
    selected = evidence_frames["selected_configurations"]
    tuned = evidence_frames["tuned_validation"]

    single = streamlit_app.selected_model_evidence(selected, tuned, 2)
    multi = streamlit_app.selected_model_evidence(selected, tuned, 1)

    assert streamlit_app.evidence_caveat(multi, 500) is None

    caveat = streamlit_app.evidence_caveat(single, 60)

    assert caveat is not None
    assert "validated tuned configuration" in caveat
    assert "60 training days" in caveat


def test_caveat_does_not_deny_a_configuration_exists(
    evidence_frames: dict,
):
    evidence = streamlit_app.selected_model_evidence(
        evidence_frames["selected_configurations"],
        evidence_frames["tuned_validation"],
        2,
    )

    caveat = streamlit_app.evidence_caveat(evidence, 60)

    assert caveat is not None
    assert "did not establish" not in caveat
    assert "descriptive-only result" in caveat


def test_training_days_are_read_from_the_demand_summary(
    evidence_frames: dict,
):
    demand = evidence_frames["demand"]

    assert streamlit_app.training_days_for(demand, "store_id", 2) == 60
    assert streamlit_app.training_days_for(demand, "store_id", 99) is None


# --------------------------------------------------------------------------
# Scenario filtering
# --------------------------------------------------------------------------


def test_filter_scenarios_selects_one_lead_time_and_level():
    scenarios = pd.DataFrame(
        {
            "lead_time_days": [7, 7, 14, 14],
            "service_level": [0.9, 0.95, 0.9, 0.95],
            "reorder_point": [1.0, 2.0, 3.0, 4.0],
        }
    )

    filtered = streamlit_app.filter_scenarios(
        scenarios, "lead_time_days", "service_level", 14, 0.95
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["reorder_point"] == pytest.approx(4.0)


def test_filter_scenarios_keeps_everything_when_no_filter_is_given():
    scenarios = pd.DataFrame(
        {
            "lead_time_days": [7, 14],
            "service_level": [0.9, 0.95],
        }
    )

    assert len(
        streamlit_app.filter_scenarios(
            scenarios, "lead_time_days", "service_level", None, None
        )
    ) == 2


# --------------------------------------------------------------------------
# Source hygiene and startup
# ---------------------------------------------------------------------------

SECRET_PATTERNS = (
    "password=",
    "api_key",
    "apikey",
    "secret=",
    "access_token",
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
)


def test_application_source_contains_no_secrets():
    for path in sorted(APP_SOURCE.glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()

        for pattern in SECRET_PATTERNS:
            assert pattern.lower() not in text, f"{path.name} contains {pattern}"


def test_application_uses_project_relative_paths():
    text = (APP_SOURCE / "config.py").read_text(encoding="utf-8")

    assert "__file__" in text
    assert "Users" not in text


def test_module_imports_without_a_streamlit_runtime():
    """Importing the app must not run any Streamlit command."""
    assert callable(streamlit_app.main)
    assert not hasattr(streamlit_app, "set_page_config")
    assert callable(streamlit_app.selected_model_evidence)


def test_no_streamlit_calls_run_at_module_scope():
    """Every ``st.`` call must sit inside a function body."""
    import ast

    source = (APP_SOURCE / "streamlit_app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    offenders = []

    for node in tree.body:
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            continue

        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue

            function = child.func
            if (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "st"
            ):
                offenders.append(function.attr)

    assert not offenders, f"Streamlit calls at module scope: {offenders}"


def test_streamlit_app_serves_headless():
    """The application starts and answers its health endpoint."""
    import socket
    import subprocess
    import sys
    import time
    import urllib.request

    pytest.importorskip("streamlit")

    # Ask the OS for a free port so a developer's running app cannot collide
    # with the smoke test.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/streamlit_app.py",
            "--server.headless",
            "true",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            str(port),
        ],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        health = f"http://127.0.0.1:{port}/_stcore/health"
        deadline = time.time() + 60
        status = None
        body = ""

        while time.time() < deadline:
            if process.poll() is not None:
                break
            try:
                with urllib.request.urlopen(health, timeout=3) as response:
                    status = response.status
                    body = response.read().decode("utf-8", "replace")
                if status == 200 and "ok" in body:
                    break
            except Exception:
                pass
            time.sleep(1)

        assert process.poll() is None, (
            "the application exited before answering: "
            + (process.stdout.read() if process.stdout else "")
        )
        assert status == 200
        assert "ok" in body

        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/", timeout=10
        ) as response:
            assert response.status == 200
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:  # pragma: no cover - cleanup
            process.kill()

