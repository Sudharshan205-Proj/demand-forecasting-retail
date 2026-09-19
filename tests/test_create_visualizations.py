"""Tests for the Phase 15 visualization and Tableau workflow."""

from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import pytest
from scipy import stats

from scripts.create_visualizations import (
    FIGURE_SOURCES,
    WorkflowError,
    run_workflow,
    validate_inputs,
    validate_leakage_guard,
)
from scripts.sync_tableau_workbook_schema import (
    read_source_schema,
    sync_workbook,
)

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "tableau" / "Retail_Demand_Forecasting.twb"
ANALYSIS_DIR = ROOT / "data" / "analysis"

SERVICE_LEVELS = (0.90, 0.95, 0.99)
LEAD_TIMES = (7, 14, 21)
BASELINE_LEVEL = 0.95
BASELINE_LEAD = 14

PUBLISHED_URL = (
    "https://public.tableau.com/views/Retail_Demand_Forecasting/"
    "RetailDemandForecastingInventoryPlanning"
)

STORE_PROFILE = {
    1: {"mean": 100.0, "cv": 0.20, "rmse": 10.0, "mape": 8.0},
    2: {"mean": 80.0, "cv": 0.10, "rmse": 12.0, "mape": 9.0},
}

def _demand_frame() -> pd.DataFrame:
    rows = []
    for store, profile in STORE_PROFILE.items():
        mean = profile["mean"]
        std = mean * profile["cv"]
        rows.append(
            {
                "store_id": store,
                "training_days": 500,
                "total_quantity": mean * 500,
                "mean_daily_demand": mean,
                "median_daily_demand": mean * 0.95,
                "min_daily_demand": max(mean - 4 * std, 0.0),
                "max_daily_demand": mean + 4 * std,
                "coefficient_of_variation": profile["cv"],
            }
        )
    return pd.DataFrame(rows)


def _variability_frame() -> pd.DataFrame:
    rows = []
    for store, profile in STORE_PROFILE.items():
        mean = profile["mean"]
        std = mean * profile["cv"]
        rows.append(
            {
                "store_id": store,
                "mean_daily_demand": mean,
                "std_daily_demand": std,
                "variance_daily_demand": std**2,
                "p90_daily_demand": mean + 1.2816 * std,
                "p95_daily_demand": mean + 1.6449 * std,
                "p99_daily_demand": mean + 2.3263 * std,
                "coefficient_of_variation": profile["cv"],
            }
        )
    return pd.DataFrame(rows)


def _scenarios_frame() -> pd.DataFrame:
    rows = []
    for store, profile in STORE_PROFILE.items():
        mean = profile["mean"]
        std = mean * profile["cv"]
        for lead in LEAD_TIMES:
            for level in SERVICE_LEVELS:
                z_value = float(stats.norm.ppf(level))
                expected = mean * lead
                safety = z_value * std * (lead**0.5)
                rows.append(
                    {
                        "store_id": store,
                        "model": "feature_gbm",
                        "configuration": "synthetic",
                        "season_length": None,
                        "order": None,
                        "lead_time_days": lead,
                        "service_level": level,
                        "z_value": z_value,
                        "mean_daily_demand": mean,
                        "std_daily_demand": std,
                        "expected_lead_time_demand": expected,
                        "safety_stock": safety,
                        "reorder_point": expected + safety,
                    }
                )
    return pd.DataFrame(rows)


def _validation_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "store_id": store,
                "model": "feature_gbm",
                "rmse": profile["rmse"],
                "mape_percent": profile["mape"],
            }
            for store, profile in STORE_PROFILE.items()
        ]
    )


def _insights_frame(scenarios: pd.DataFrame) -> pd.DataFrame:
    baseline = scenarios[
        scenarios["lead_time_days"].eq(BASELINE_LEAD)
        & scenarios["service_level"].eq(BASELINE_LEVEL)
    ]

    rows = [
        {
            "insight_type": "highest_average_demand",
            "store_id": 1,
            "metric": "mean_daily_demand",
            "value": 100.0,
            "interpretation": "synthetic",
        },
        {
            "insight_type": "highest_relative_variability",
            "store_id": 1,
            "metric": "coefficient_of_variation",
            "value": 0.20,
            "interpretation": "synthetic",
        },
        {
            "insight_type": "lowest_validation_rmse",
            "store_id": 1,
            "metric": "validation_rmse",
            "value": 10.0,
            "interpretation": "synthetic",
        },
        {
            "insight_type": "lowest_relative_validation_error",
            "store_id": 1,
            "metric": "validation_mape_percent",
            "value": 8.0,
            "interpretation": "synthetic",
        },
    ]

    for row in baseline.itertuples():
        rows.append(
            {
                "insight_type": "inventory_scenario",
                "store_id": row.store_id,
                "metric": "reorder_point",
                "value": row.reorder_point,
                "interpretation": "synthetic",
            }
        )

    return pd.DataFrame(rows)


def fixture_frames() -> dict[str, pd.DataFrame]:
    """Build a complete, internally consistent set of synthetic inputs."""
    scenarios = _scenarios_frame()

    return {
        "inventory_demand_summary.csv": _demand_frame(),
        "inventory_variability_summary.csv": _variability_frame(),
        "inventory_scenarios.csv": scenarios,
        "forecast_inventory_insights.csv": _insights_frame(scenarios),
        "tuned_validation_results.csv": _validation_frame(),
    }


def write_inputs(directory: Path) -> dict[str, pd.DataFrame]:
    """Write the synthetic inputs into ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    frames = fixture_frames()

    for name, frame in frames.items():
        frame.to_csv(directory / name, index=False)

    return frames


def workflow_env(input_dir: Path, output_dir: Path, report_dir: Path) -> dict:
    """Return the environment that redirects the workflow into a temp dir."""
    env = os.environ.copy()
    env["VISUALIZATION_PROJECT_ROOT"] = str(ROOT)
    env["VISUALIZATION_INPUT_DIR"] = str(input_dir)
    env["VISUALIZATION_OUTPUT_DIR"] = str(output_dir)
    env["VISUALIZATION_REPORT_DIR"] = str(report_dir)
    return env


SCRIPT = ROOT / "scripts" / "create_visualizations.py"


def run_script(env: dict, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the visualization workflow as a subprocess."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(cwd or ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def workspace(tmp_path: Path) -> dict:
    """A temporary input/output/report workspace with valid inputs."""
    input_dir = tmp_path / "input"
    frames = write_inputs(input_dir)

    return {
        "tmp": tmp_path,
        "input_dir": input_dir,
        "output_dir": tmp_path / "out",
        "report_dir": tmp_path / "report",
        "frames": frames,
    }


def sha256_of(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def mutate(workspace: dict, filename: str, change) -> None:
    """Apply a mutation to one synthetic input table."""
    path = workspace["input_dir"] / filename
    frame = pd.read_csv(path)
    frame = change(frame)
    frame.to_csv(path, index=False)


def failed_checks(checks) -> list:
    """Return the failing checks from a validation run."""
    return [check for check in checks if not check.passed]


# --------------------------------------------------------------------------
# End-to-end workflow
# --------------------------------------------------------------------------


def test_workflow_produces_every_artifact(workspace: dict) -> None:
    """A valid run writes four figures, a passing report and a manifest."""
    env = workflow_env(
        workspace["input_dir"],
        workspace["output_dir"],
        workspace["report_dir"],
    )

    result = run_script(env, cwd=workspace["tmp"])

    assert result.returncode == 0, result.stderr
    assert "completed successfully" in result.stdout

    for filename in FIGURE_SOURCES:
        figure = workspace["output_dir"] / filename
        assert figure.is_file(), f"{filename} was not written"
        assert figure.stat().st_size > 0

    report = pd.read_csv(
        workspace["report_dir"] / "visualization_quality_report.csv"
    )
    assert report["status"].eq("PASS").all()
    assert len(report) >= 50
    assert report["check"].is_unique


def test_manifest_matches_the_files_on_disk(workspace: dict) -> None:
    """The manifest digest and size must describe the written figures."""
    env = workflow_env(
        workspace["input_dir"],
        workspace["output_dir"],
        workspace["report_dir"],
    )
    run_script(env, cwd=workspace["tmp"])

    manifest = pd.read_csv(
        workspace["report_dir"] / "visualization_manifest.csv"
    )

    assert set(manifest["figure"]) == set(FIGURE_SOURCES)

    for row in manifest.itertuples():
        figure = workspace["output_dir"] / row.figure
        assert figure.stat().st_size == row.bytes
        assert sha256_of(figure) == row.sha256


def test_workflow_is_location_independent(workspace: dict) -> None:
    """The workflow runs from a directory that is not the project root."""
    deep = workspace["tmp"] / "a" / "b"
    deep.mkdir(parents=True)

    env = workflow_env(
        workspace["input_dir"],
        workspace["output_dir"],
        workspace["report_dir"],
    )

    result = run_script(env, cwd=deep)

    assert result.returncode == 0, result.stderr
    assert (workspace["report_dir"] / "visualization_manifest.csv").is_file()


def test_run_workflow_returns_the_collected_checks(workspace: dict) -> None:
    """The in-process workflow returns its checks and figures."""
    result = run_workflow(
        input_dir=workspace["input_dir"],
        output_dir=workspace["output_dir"],
        report_dir=workspace["report_dir"],
    )

    assert len(result["figures"]) == len(FIGURE_SOURCES)
    assert not failed_checks(result["checks"])


def test_validation_failure_withholds_the_figures(workspace: dict) -> None:
    """A failing gate must not draw any figure."""
    mutate(
        workspace,
        "inventory_scenarios.csv",
        lambda frame: frame.assign(
            reorder_point=frame["reorder_point"] * 2
        ),
    )

    with pytest.raises(WorkflowError):
        run_workflow(
            input_dir=workspace["input_dir"],
            output_dir=workspace["output_dir"],
            report_dir=workspace["report_dir"],
        )

    assert not list(workspace["output_dir"].glob("*.png"))

    report = pd.read_csv(
        workspace["report_dir"] / "visualization_quality_report.csv"
    )
    assert report["status"].eq("FAIL").any()


# --------------------------------------------------------------------------
# Validation units
# --------------------------------------------------------------------------


def test_valid_inputs_produce_no_failures(workspace: dict) -> None:
    """The synthetic fixture satisfies every check."""
    frames = workspace["frames"]

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
        frames["forecast_inventory_insights.csv"],
        frames["tuned_validation_results.csv"],
    )

    assert not failed_checks(checks)
    assert all(hasattr(check, "name") for check in checks)


def test_missing_demand_column_is_reported(workspace: dict) -> None:
    """A missing demand field fails validation with a useful detail."""
    frames = workspace["frames"]
    demand = frames["inventory_demand_summary.csv"].drop(
        columns=["mean_daily_demand"]
    )

    checks = validate_inputs(
        demand,
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
    )

    failures = failed_checks(checks)
    assert [check.name for check in failures] == ["demand_columns_present"]
    assert "mean_daily_demand" in failures[0].detail


def test_empty_demand_is_rejected(workspace: dict) -> None:
    """An empty demand dataset fails validation."""
    frames = workspace["frames"]

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"].iloc[0:0],
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
    )

    assert "demand_not_empty" in [check.name for check in failed_checks(checks)]


def test_negative_mean_demand_is_rejected(workspace: dict) -> None:
    """Negative demand fails validation."""
    frames = workspace["frames"]
    demand = frames["inventory_demand_summary.csv"].copy()
    demand.loc[0, "mean_daily_demand"] = -1.0

    checks = validate_inputs(
        demand,
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
    )

    assert "demand_mean_non_negative" in [
        check.name for check in failed_checks(checks)
    ]


def test_negative_variability_is_rejected(workspace: dict) -> None:
    """Negative variability fails validation."""
    frames = workspace["frames"]
    variability = frames["inventory_variability_summary.csv"].copy()
    variability.loc[0, "coefficient_of_variation"] = -1.0

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        variability,
        frames["inventory_scenarios.csv"],
    )

    assert "variability_cv_non_negative" in [
        check.name for check in failed_checks(checks)
    ]


def test_broken_variance_formula_is_rejected(workspace: dict) -> None:
    """Variance that is not std squared fails validation."""
    frames = workspace["frames"]
    variability = frames["inventory_variability_summary.csv"].copy()
    variability.loc[0, "variance_daily_demand"] = 1.0

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        variability,
        frames["inventory_scenarios.csv"],
    )

    assert "variability_variance_reconciles" in [
        check.name for check in failed_checks(checks)
    ]


def test_negative_reorder_point_is_rejected(workspace: dict) -> None:
    """Negative reorder points fail validation."""
    frames = workspace["frames"]
    scenarios = frames["inventory_scenarios.csv"].copy()
    scenarios.loc[0, "reorder_point"] = -1.0

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        frames["inventory_variability_summary.csv"],
        scenarios,
    )

    names = [check.name for check in failed_checks(checks)]
    assert "scenarios_reorder_point_non_negative" in names
    assert "scenarios_reorder_point_reconciles" in names


def test_invalid_service_level_is_rejected(workspace: dict) -> None:
    """A service level outside [0, 1] fails validation."""
    frames = workspace["frames"]
    scenarios = frames["inventory_scenarios.csv"].copy()
    scenarios.loc[0, "service_level"] = 1.5

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        frames["inventory_variability_summary.csv"],
        scenarios,
    )

    assert "scenarios_service_level_in_range" in [
        check.name for check in failed_checks(checks)
    ]


def test_mismatched_store_sets_are_rejected(workspace: dict) -> None:
    """A store missing from a detail input fails validation."""
    frames = workspace["frames"]
    variability = frames["inventory_variability_summary.csv"].iloc[0:1]

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        variability,
        frames["inventory_scenarios.csv"],
    )

    assert "variability_store_set_matches_demand" in [
        check.name for check in failed_checks(checks)
    ]


def test_duplicate_store_ids_are_rejected(workspace: dict) -> None:
    """Duplicate store ids in the demand summary fail validation."""
    frames = workspace["frames"]
    demand = pd.concat(
        [
            frames["inventory_demand_summary.csv"],
            frames["inventory_demand_summary.csv"].iloc[0:1],
        ],
        ignore_index=True,
    )

    checks = validate_inputs(
        demand,
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
    )

    assert "demand_store_ids_unique" in [
        check.name for check in failed_checks(checks)
    ]


def test_missing_insight_type_is_rejected(workspace: dict) -> None:
    """Dropping a required insight fails validation."""
    frames = workspace["frames"]
    insights = frames["forecast_inventory_insights.csv"]
    insights = insights[
        ~insights["insight_type"].eq("lowest_validation_rmse")
    ]

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
        insights,
        frames["tuned_validation_results.csv"],
    )

    names = [check.name for check in failed_checks(checks)]
    assert "insights_required_types_present" in names
    assert "insights_lowest_validation_rmse_reconciles" in names


def test_unreconciled_insight_is_rejected(workspace: dict) -> None:
    """An insight value that disagrees with its source fails validation."""
    frames = workspace["frames"]
    insights = frames["forecast_inventory_insights.csv"].copy()
    insights.loc[
        insights["insight_type"].eq("lowest_validation_rmse"), "value"
    ] = 999.0

    checks = validate_inputs(
        frames["inventory_demand_summary.csv"],
        frames["inventory_variability_summary.csv"],
        frames["inventory_scenarios.csv"],
        insights,
        frames["tuned_validation_results.csv"],
    )

    assert "insights_lowest_validation_rmse_reconciles" in [
        check.name for check in failed_checks(checks)
    ]


def test_leakage_guard_passes_for_the_fixture(workspace: dict) -> None:
    """The declared inputs carry no test-period artifact."""
    frames = workspace["frames"]
    guard = validate_leakage_guard(
        {
            "demand": frames["inventory_demand_summary.csv"],
            "insights": frames["forecast_inventory_insights.csv"],
        }
    )

    assert not failed_checks(guard)


def test_leakage_guard_rejects_test_metric_insights(workspace: dict) -> None:
    """A test-period metric in the insights fails the leakage guard."""
    frames = workspace["frames"]
    insights = frames["forecast_inventory_insights.csv"].copy()
    insights.loc[
        insights["insight_type"].eq("lowest_validation_rmse"), "metric"
    ] = "test_rmse"

    guard = validate_leakage_guard(
        {
            "demand": frames["inventory_demand_summary.csv"],
            "insights": insights,
        }
    )

    assert "leakage_insights_use_validation_not_test" in [
        check.name for check in failed_checks(guard)
    ]


# --------------------------------------------------------------------------
# Failure paths (subprocess)
# --------------------------------------------------------------------------


def _drop_column(workspace: dict, filename: str, column: str) -> None:
    mutate(workspace, filename, lambda frame: frame.drop(columns=[column]))


FAILURE_MUTATIONS = {
    "missing_input_file": lambda w: (
        w["input_dir"] / "inventory_scenarios.csv"
    ).unlink(),
    "missing_required_column": lambda w: _drop_column(
        w, "inventory_demand_summary.csv", "training_days"
    ),
    "empty_demand": lambda w: mutate(
        w, "inventory_demand_summary.csv", lambda frame: frame.iloc[0:0]
    ),
    "broken_scenario_formula": lambda w: mutate(
        w,
        "inventory_scenarios.csv",
        lambda frame: frame.assign(
            reorder_point=frame["reorder_point"] * 2
        ),
    ),
    "inconsistent_insight": lambda w: mutate(
        w,
        "forecast_inventory_insights.csv",
        lambda frame: frame.assign(
            value=frame["value"].where(
                ~frame["insight_type"].eq("lowest_validation_rmse"),
                999.0,
            )
        ),
    ),
    "invalid_service_level": lambda w: mutate(
        w,
        "inventory_scenarios.csv",
        lambda frame: frame.assign(service_level=1.5),
    ),
}


@pytest.mark.parametrize("scenario", sorted(FAILURE_MUTATIONS))
def test_workflow_fails_loudly(tmp_path: Path, scenario: str) -> None:
    """Each broken input exits non-zero without claiming success."""
    input_dir = tmp_path / scenario / "input"
    write_inputs(input_dir)

    workspace = {
        "input_dir": input_dir,
        "output_dir": tmp_path / scenario / "out",
        "report_dir": tmp_path / scenario / "report",
    }

    FAILURE_MUTATIONS[scenario](workspace)

    env = workflow_env(
        workspace["input_dir"],
        workspace["output_dir"],
        workspace["report_dir"],
    )
    result = run_script(env, cwd=tmp_path / scenario)

    assert result.returncode != 0
    assert "completed successfully" not in result.stdout
    assert "FAILED" in result.stderr
    assert not list(workspace["output_dir"].glob("*.png"))


# --------------------------------------------------------------------------
# Tableau workbook
# --------------------------------------------------------------------------


def datasources(root: ET.Element) -> dict[str, ET.Element]:
    """Map each workbook data source's CSV filename to its element."""
    found: dict[str, ET.Element] = {}

    for datasource in root.findall("datasources/datasource"):
        connection = datasource.find(
            "connection/named-connections/named-connection/connection"
        )
        if connection is not None and connection.get("filename"):
            found[connection.get("filename")] = datasource

    return found


def test_workbook_is_well_formed() -> None:
    """The workbook parses, and carries its worksheets and dashboard."""
    root = ET.parse(WORKBOOK).getroot()

    assert root.tag == "workbook"
    assert root.find("repository-location") is not None

    worksheets = [w.get("name") for w in root.findall("worksheets/worksheet")]
    dashboards = [d.get("name") for d in root.findall("dashboards/dashboard")]

    assert len(worksheets) == 5
    assert dashboards == [
        "Retail Demand Forecasting & Inventory Planning"
    ]


def test_workbook_schema_matches_its_current_sources() -> None:
    """Every cached schema block matches the CSV header order."""
    root = ET.parse(WORKBOOK).getroot()
    sources = datasources(root)

    assert sorted(sources) == [
        "inventory_scenarios.csv",
        "inventory_variability_summary.csv",
        "tuned_validation_results.csv",
    ]

    for filename, datasource in sources.items():
        headers = list(
            pd.read_csv(ANALYSIS_DIR / filename, nrows=1).columns
        )
        blocks = datasource.findall(".//columns")

        assert blocks, f"no cached schema for {filename}"

        for block in blocks:
            columns = block.findall("column")
            assert [c.get("name") for c in columns] == headers
            assert [int(c.get("ordinal")) for c in columns] == list(
                range(len(headers))
            )


def test_workbook_preserves_declared_datatypes() -> None:
    """The repair must not downgrade a declared date to text."""
    root = ET.parse(WORKBOOK).getroot()
    sources = datasources(root)

    blocks = sources["tuned_validation_results.csv"].findall(".//columns")
    declared = {
        c.get("name"): c.get("datatype")
        for block in blocks
        for c in block.findall("column")
    }

    assert declared["validation_start"] == "date"
    assert declared["validation_end"] == "date"


def copy_workbook_and_sources(tmp_path: Path) -> tuple[Path, Path]:
    """Copy the workbook and the CSVs it references into a temp dir."""
    import shutil

    workbook = tmp_path / "workbook.twb"
    shutil.copy(WORKBOOK, workbook)

    analysis = tmp_path / "analysis"
    analysis.mkdir()

    for filename in [
        "inventory_scenarios.csv",
        "inventory_variability_summary.csv",
        "tuned_validation_results.csv",
    ]:
        shutil.copy(ANALYSIS_DIR / filename, analysis / filename)

    return workbook, analysis


def test_schema_sync_is_idempotent(tmp_path: Path) -> None:
    """A reconciled workbook reports no further change."""
    workbook, analysis = copy_workbook_and_sources(tmp_path)

    first = sync_workbook(workbook, analysis)
    second = sync_workbook(workbook, analysis)

    assert first.changed is False
    assert second.changed is False


def test_schema_sync_detects_a_new_column(tmp_path: Path) -> None:
    """A new source column is added to every cached schema block."""
    workbook, analysis = copy_workbook_and_sources(tmp_path)

    source = analysis / "inventory_scenarios.csv"
    frame = pd.read_csv(source)
    frame["extra_metric"] = 1.0
    frame.to_csv(source, index=False)

    result = sync_workbook(workbook, analysis)
    assert result.changed is True

    root = ET.parse(workbook).getroot()
    blocks = datasources(root)["inventory_scenarios.csv"].findall(
        ".//columns"
    )

    assert blocks
    for block in blocks:
        columns = block.findall("column")
        assert columns[-1].get("name") == "extra_metric"
        assert [int(c.get("ordinal")) for c in columns] == list(
            range(len(columns))
        )

    assert sync_workbook(workbook, analysis).changed is False


def test_schema_sync_rejects_an_unknown_source(tmp_path: Path) -> None:
    """A workbook source with no matching CSV is reported, not ignored."""
    import shutil

    workbook = tmp_path / "workbook.twb"
    shutil.copy(WORKBOOK, workbook)

    with pytest.raises(FileNotFoundError):
        sync_workbook(workbook, tmp_path / "analysis")


def test_published_url_matches_the_workbook() -> None:
    """The recorded Tableau Public URL names this workbook and view."""
    import re

    root = ET.parse(WORKBOOK).getroot()
    repository = root.find("repository-location")
    dashboard = root.find("dashboards/dashboard")

    workbook_id = repository.get("id")
    view_slug = re.sub(r"[^A-Za-z0-9]", "", dashboard.get("name"))

    assert workbook_id == "Retail_Demand_Forecasting"
    assert view_slug == "RetailDemandForecastingInventoryPlanning"
    assert PUBLISHED_URL.startswith("https://public.tableau.com/views/")
    assert f"/views/{workbook_id}/" in PUBLISHED_URL
    assert PUBLISHED_URL.endswith(view_slug)
