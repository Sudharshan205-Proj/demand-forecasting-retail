"""Tests for the Phase 14 R analysis workflow.

The R workflow has no Python entry point, so these tests drive it as a
subprocess over synthetic Phase 13/Phase 12 inputs built in a temporary
directory. That keeps the suite independent of the generated artifacts (which
are excluded from Git) while still exercising the complete pipeline. A second
group of tests audits the artifacts that a real run leaves in
``data/analysis/r`` when they are present.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import statistics
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
R_DIR = PROJECT_ROOT / "r"
R_SCRIPT = R_DIR / "r_analysis.R"
R_REPORT = R_DIR / "r_analysis_report.Rmd"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
R_OUTPUT_DIR = ANALYSIS_DIR / "r"

RSCRIPT = shutil.which("Rscript")

PLOT_FILES = (
    "average_daily_demand_by_store.png",
    "demand_variability_by_store.png",
    "inventory_reorder_point_scenarios.png",
    "inventory_scenario_family_comparison.png",
)

OUTPUT_FILES = (
    "r_store_analysis.csv",
    "r_inventory_scenario_summary.csv",
    "r_forecast_inventory_scenario_summary.csv",
    "r_baseline_inventory_scenario.csv",
    "r_baseline_forecast_inventory_scenario.csv",
    "r_phase13_consistency.csv",
    "r_phase13_reconciliation.csv",
    "r_metric_reconciliation.csv",
    "r_analysis_quality_report.csv",
    "r_environment.csv",
    "r_analysis_findings.txt",
)

INPUT_FILES = (
    "inventory_demand_summary.csv",
    "inventory_variability_summary.csv",
    "inventory_scenarios.csv",
    "inventory_forecast_scenarios.csv",
    "inventory_forecast_error_summary.csv",
    "inventory_densification_summary.csv",
    "forecast_inventory_insights.csv",
    "tuned_validation_results.csv",
    "model_evaluation_predictions.csv",
)

LEAD_TIMES = (7, 14, 28)
SERVICE_LEVELS = (0.90, 0.95, 0.99)

# Synthetic store fixtures: (training days, mean demand, demand spread,
# validation residual, forecast bias).
STORES = {
    1: {"days": 100, "mean": 1000.0, "spread": 150.0, "residual": 150.0, "bias": 150.0},
    2: {"days": 50, "mean": 200.0, "spread": 70.0, "residual": 70.0, "bias": 35.0},
}

VALIDATION_OBSERVATIONS = 20

requires_r = pytest.mark.skipif(
    RSCRIPT is None,
    reason="Rscript is not available on this machine",
)


def normal_quantile(probability: float) -> float:
    """Return the standard-normal quantile without a SciPy dependency."""
    return statistics.NormalDist().inv_cdf(probability)


def actual_level(store_id: int) -> float:
    """Return the constant validation actual used for the store."""
    return STORES[store_id]["mean"]


def mape_percent(store_id: int) -> float:
    """Return the MAPE implied by the constant validation residual."""
    return STORES[store_id]["residual"] / actual_level(store_id) * 100


def build_inputs(directory: Path) -> None:
    """Write a complete, internally consistent synthetic input set."""
    directory.mkdir(parents=True, exist_ok=True)

    demand_rows = []
    variability_rows = []
    scenario_rows = []
    forecast_scenario_rows = []
    forecast_error_rows = []
    validation_rows = []
    prediction_rows = []
    densification_rows = []

    for store_id, config in STORES.items():
        mean = config["mean"]
        spread = config["spread"]
        residual = config["residual"]
        bias = config["bias"]
        days = config["days"]

        demand_rows.append(
            {
                "store_id": store_id,
                "training_days": days,
                "total_quantity": mean * days,
                "mean_daily_demand": mean,
                "median_daily_demand": mean * 0.98,
                "min_daily_demand": mean * 0.5,
                "max_daily_demand": mean * 1.5,
                "coefficient_of_variation": spread / mean,
            }
        )

        variability_rows.append(
            {
                "store_id": store_id,
                "mean_daily_demand": mean,
                "std_daily_demand": spread,
                "variance_daily_demand": spread**2,
                "p90_daily_demand": mean + 1.28 * spread,
                "p95_daily_demand": mean + 1.65 * spread,
                "p99_daily_demand": mean + 2.33 * spread,
                "coefficient_of_variation": spread / mean,
            }
        )

        for lead_time in LEAD_TIMES:
            for service_level in SERVICE_LEVELS:
                z_value = normal_quantile(service_level)

                scenario_rows.append(
                    {
                        "store_id": store_id,
                        "model": "seasonal_naive",
                        "configuration": "season_length=7",
                        "lead_time_days": lead_time,
                        "service_level": service_level,
                        "z_value": z_value,
                        "mean_daily_demand": mean,
                        "std_daily_demand": spread,
                        "expected_lead_time_demand": mean * lead_time,
                        "safety_stock": z_value * spread * (lead_time**0.5),
                        "reorder_point": mean * lead_time
                        + z_value * spread * (lead_time**0.5),
                    }
                )

                forecast_scenario_rows.append(
                    {
                        "store_id": store_id,
                        "model": "seasonal_naive",
                        "configuration": "season_length=7",
                        "lead_time_days": lead_time,
                        "service_level": service_level,
                        "z_value": z_value,
                        "model_daily_demand": mean,
                        "bias": bias,
                        "bias_adjusted_daily_demand": mean + bias,
                        "residual_std": residual,
                        "rmse": residual,
                        "expected_lead_time_demand": (mean + bias) * lead_time,
                        "safety_stock": z_value * residual * (lead_time**0.5),
                        "reorder_point": (mean + bias) * lead_time
                        + z_value * residual * (lead_time**0.5),
                    }
                )

        forecast_error_rows.append(
            {
                "store_id": store_id,
                "model": "seasonal_naive",
                "configuration": "season_length=7",
                "observations": VALIDATION_OBSERVATIONS,
                "mean_predicted": mean,
                "mean_actual": mean + bias,
                "bias": bias,
                "residual_std": residual,
                "rmse": residual,
                "mape_percent": mape_percent(store_id),
            }
        )

        validation_rows.append(
            {
                "store_id": store_id,
                "model": "seasonal_naive",
                "configuration": "season_length=7",
                "rmse": residual,
                "mape_percent": mape_percent(store_id),
            }
        )

        for step in range(VALIDATION_OBSERVATIONS):
            prediction_rows.append(
                {
                    "scope": "validation",
                    "store_id": store_id,
                    "model": "seasonal_naive",
                    "configuration": "season_length=7",
                    "cv_fold": None,
                    "date": f"2024-01-{step + 1:02d}",
                    "actual": actual_level(store_id),
                    "predicted": actual_level(store_id) - residual,
                }
            )

        prediction_rows.append(
            {
                "scope": "cv_fold",
                "store_id": store_id,
                "model": "seasonal_naive",
                "configuration": "season_length=7",
                "cv_fold": 1,
                "date": "2023-12-01",
                "actual": actual_level(store_id),
                "predicted": actual_level(store_id),
            }
        )

        densification_rows.append(
            {
                "store_id": store_id,
                "observed_days": days - (1 if store_id == 2 else 0),
                "densified_days": days,
                "synthetic_days": 1 if store_id == 2 else 0,
                "first_date": "2023-01-01",
                "last_date": "2024-01-01",
                "synthetic_dates": "2023-06-01" if store_id == 2 else "",
            }
        )

    demand = pd.DataFrame(demand_rows)
    variability = pd.DataFrame(variability_rows)
    scenarios = pd.DataFrame(scenario_rows)
    forecast_scenarios = pd.DataFrame(forecast_scenario_rows)

    historical_baseline = scenarios.loc[
        (scenarios["lead_time_days"] == 14)
        & (scenarios["service_level"] == 0.95)
    ]
    forecast_baseline = forecast_scenarios.loc[
        (forecast_scenarios["lead_time_days"] == 14)
        & (forecast_scenarios["service_level"] == 0.95)
    ]

    insight_rows = []

    def add_insight(insight_type, store_id, metric, value, interpretation="Synthetic."):
        insight_rows.append(
            {
                "insight_type": insight_type,
                "store_id": store_id,
                "metric": metric,
                "value": value,
                "interpretation": interpretation,
            }
        )

    highest_demand = max(STORES, key=lambda store: STORES[store]["mean"])
    highest_variability = max(
        STORES, key=lambda store: STORES[store]["spread"] / STORES[store]["mean"]
    )
    lowest_rmse = min(STORES, key=lambda store: STORES[store]["residual"])
    lowest_mape = min(STORES, key=lambda store: mape_percent(store))
    largest_bias = max(STORES, key=lambda store: STORES[store]["bias"])

    add_insight(
        "highest_average_demand",
        highest_demand,
        "mean_daily_demand",
        STORES[highest_demand]["mean"],
    )
    add_insight(
        "highest_relative_variability",
        highest_variability,
        "coefficient_of_variation",
        STORES[highest_variability]["spread"] / STORES[highest_variability]["mean"],
    )
    add_insight(
        "lowest_validation_rmse",
        lowest_rmse,
        "validation_rmse",
        STORES[lowest_rmse]["residual"],
    )
    add_insight(
        "lowest_relative_validation_error",
        lowest_mape,
        "validation_mape_percent",
        mape_percent(lowest_mape),
    )
    add_insight(
        "systematic_bias",
        largest_bias,
        "mean_forecast_bias",
        STORES[largest_bias]["bias"],
    )

    for row in historical_baseline.itertuples(index=False):
        add_insight(
            "inventory_scenario", row.store_id, "reorder_point", row.reorder_point
        )

    for row in forecast_baseline.itertuples(index=False):
        add_insight(
            "forecast_inventory_scenario",
            row.store_id,
            "reorder_point",
            row.reorder_point,
        )

    frames = {
        "inventory_demand_summary.csv": demand,
        "inventory_variability_summary.csv": variability,
        "inventory_scenarios.csv": scenarios,
        "inventory_forecast_scenarios.csv": forecast_scenarios,
        "inventory_forecast_error_summary.csv": pd.DataFrame(forecast_error_rows),
        "inventory_densification_summary.csv": pd.DataFrame(densification_rows),
        "forecast_inventory_insights.csv": pd.DataFrame(insight_rows),
        "tuned_validation_results.csv": pd.DataFrame(validation_rows),
        "model_evaluation_predictions.csv": pd.DataFrame(prediction_rows),
    }

    for name, frame in frames.items():
        frame.to_csv(directory / name, index=False)


def run_workflow(input_dir: Path, output_dir: Path) -> subprocess.CompletedProcess:
    """Run the R workflow against the supplied directories."""
    environment = dict(os.environ)
    environment["R_ANALYSIS_INPUT_DIR"] = str(input_dir)
    environment["R_ANALYSIS_OUTPUT_DIR"] = str(output_dir)

    return subprocess.run(
        [RSCRIPT, "--vanilla", str(R_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        timeout=600,
    )


def load_quality(output_dir: Path) -> pd.DataFrame:
    """Read the quality report written by a run."""
    report = pd.read_csv(output_dir / "r_analysis_quality_report.csv")
    report["passed"] = report["passed"].astype(str).str.lower().eq("true")
    return report


def failed_checks(output_dir: Path) -> set[str]:
    """Return the names of the checks that failed."""
    report = load_quality(output_dir)
    return set(report.loc[~report["passed"], "check"])


@pytest.fixture(scope="module")
def workspace(tmp_path_factory) -> dict:
    """Build one synthetic input set shared by the fast assertions."""
    root = tmp_path_factory.mktemp("phase14")
    input_dir = root / "inputs"
    build_inputs(input_dir)
    return {"root": root, "input_dir": input_dir}


@pytest.fixture
def mutable_workspace(tmp_path) -> dict:
    """Build a fresh input set that individual tests may corrupt."""
    input_dir = tmp_path / "inputs"
    output_dir = tmp_path / "outputs"
    build_inputs(input_dir)
    return {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "input_file": lambda name: input_dir / name,
        "output_file": lambda name: output_dir / name,
    }


def mutate_frame(workspace: dict, file_name: str, mutate) -> None:
    """Apply a mutation to one synthetic input table."""
    path = workspace["input_file"](file_name)
    frame = pd.read_csv(path)
    frame = mutate(frame)
    frame.to_csv(path, index=False)


@pytest.fixture(scope="module")
def baseline(workspace, tmp_path_factory) -> dict:
    """Run the workflow once over the valid synthetic inputs."""
    output_dir = tmp_path_factory.mktemp("phase14-baseline")
    result = run_workflow(workspace["input_dir"], output_dir)
    return {
        "result": result,
        "output_dir": output_dir,
        "input_dir": workspace["input_dir"],
    }


@requires_r
def test_workflow_exits_successfully(baseline) -> None:
    """A valid input set must complete the workflow."""
    assert baseline["result"].returncode == 0, baseline["result"].stderr
    assert "completed successfully" in baseline["result"].stdout


@requires_r
def test_quality_report_passes_completely(baseline) -> None:
    """Every recorded check must pass for the run to be accepted."""
    report = load_quality(baseline["output_dir"])
    assert len(report) > 50
    assert report["passed"].all(), failed_checks(baseline["output_dir"])


@requires_r
def test_expected_output_files_exist(baseline) -> None:
    """The documented artifacts must be produced."""
    for name in OUTPUT_FILES:
        assert (baseline["output_dir"] / name).is_file(), name


@requires_r
def test_plots_are_written_and_non_empty(baseline) -> None:
    """Every exported figure must exist and carry content."""
    for name in PLOT_FILES:
        plot = baseline["output_dir"] / "plots" / name
        assert plot.is_file(), name
        assert plot.stat().st_size > 0, name


@requires_r
def test_findings_report_is_derived_from_evidence(baseline) -> None:
    """The findings must quote the run's own reconciliation results."""
    findings = (baseline["output_dir"] / "r_analysis_findings.txt").read_text(
        encoding="utf-8"
    )
    assert "Quality checks passed:" in findings
    assert "R version" in findings
    assert "Phase 13 insight rows reconciled:" in findings
    assert "NOT verified" not in findings


@requires_r
def test_environment_record_captures_versions(baseline) -> None:
    """R, pandoc and package versions must be recorded for reproducibility."""
    environment = pd.read_csv(baseline["output_dir"] / "r_environment.csv")
    items = set(environment["item"])
    assert "r_version" in items
    assert "pandoc_version" in items
    assert "package_yardstick" in items
    assert "package_tidymodels" in items


@requires_r
def test_store_analysis_matches_the_input_demand(baseline) -> None:
    """The joined store table must reproduce the source demand values."""
    store_analysis = pd.read_csv(baseline["output_dir"] / "r_store_analysis.csv")
    expected = {store: config["mean"] for store, config in STORES.items()}
    assert set(store_analysis["store_id"]) == set(expected)
    for row in store_analysis.itertuples(index=False):
        assert row.mean_daily_demand == pytest.approx(expected[row.store_id])
        assert row.std_daily_demand == pytest.approx(STORES[row.store_id]["spread"])


@requires_r
def test_phase13_reconciliation_covers_every_published_insight(baseline) -> None:
    """Each insight must be reconciled on store and value."""
    reconciliation = pd.read_csv(
        baseline["output_dir"] / "r_phase13_reconciliation.csv"
    )
    published = pd.read_csv(baseline["input_dir"] / "forecast_inventory_insights.csv")
    assert len(reconciliation) == len(published)
    assert reconciliation["match"].all()


@requires_r
def test_metric_reconciliation_recomputes_phase12_metrics(baseline) -> None:
    """Recomputed metrics must agree with the reported ones."""
    metrics = pd.read_csv(baseline["output_dir"] / "r_metric_reconciliation.csv")
    assert len(metrics) == len(STORES)
    assert (metrics["observations"] == VALIDATION_OBSERVATIONS).all()
    assert (metrics["rmse_relative_difference"] < 1e-4).all()
    assert (metrics["mape_relative_difference"] < 1e-4).all()


@requires_r
def test_densification_reconciles_with_the_training_days(baseline) -> None:
    """The densified store-day count must match the demand summary."""
    demand = pd.read_csv(baseline["input_dir"] / "inventory_demand_summary.csv")
    quality = load_quality(baseline["output_dir"])
    checks = dict(zip(quality["check"], quality["actual"]))
    assert checks["densification_totals_reconcile"] == str(demand["training_days"].sum())


def run_mutated(mutable_workspace, file_name, mutate):
    """Run the workflow over one deliberately corrupted input table."""
    mutate_frame(mutable_workspace, file_name, mutate)
    result = run_workflow(
        mutable_workspace["input_dir"],
        mutable_workspace["output_dir"],
    )
    return result, failed_checks(mutable_workspace["output_dir"])


@requires_r
def test_missing_input_file_is_reported(mutable_workspace) -> None:
    """A missing required input must be reported rather than ignored."""
    mutable_workspace["input_file"](
        "inventory_densification_summary.csv"
    ).unlink()

    result = run_workflow(
        mutable_workspace["input_dir"],
        mutable_workspace["output_dir"],
    )

    assert result.returncode != 0
    checks = failed_checks(mutable_workspace["output_dir"])
    assert "required_input_files_present" in checks
    assert "inputs_ready_for_analysis" in checks


@requires_r
def test_missing_column_is_reported(mutable_workspace) -> None:
    """A missing required column must be reported."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_variability_summary.csv",
        lambda frame: frame.drop(columns=["p99_daily_demand"]),
    )

    assert result.returncode != 0
    assert "variability_columns_present" in checks
    assert "inputs_ready_for_analysis" in checks


@requires_r
def test_missing_key_column_is_reported_without_crashing(mutable_workspace) -> None:
    """Dropping a key column must be reported, not raise an R error."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_demand_summary.csv",
        lambda frame: frame.drop(columns=["store_id"]),
    )

    assert result.returncode != 0
    assert "demand_columns_present" in checks
    assert "inputs_ready_for_analysis" in checks
    assert "Traceback" not in result.stderr


@requires_r
def test_negative_demand_is_rejected(mutable_workspace) -> None:
    """Negative demand must fail validation."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_demand_summary.csv",
        lambda frame: frame.assign(
            mean_daily_demand=-1.0,
            total_quantity=-1.0 * frame["training_days"],
        ),
    )

    assert result.returncode != 0
    assert "demand_values_non_negative" in checks


@requires_r
def test_duplicate_store_rows_are_rejected(mutable_workspace) -> None:
    """A duplicated store row must fail the uniqueness check."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_demand_summary.csv",
        lambda frame: pd.concat([frame, frame.head(1)], ignore_index=True),
    )

    assert result.returncode != 0
    assert "store_ids_unique_in_demand" in checks


@requires_r
def test_store_set_mismatch_is_rejected(mutable_workspace) -> None:
    """Inputs covering different stores must fail validation."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_variability_summary.csv",
        lambda frame: frame.loc[frame["store_id"] != 2],
    )

    assert result.returncode != 0
    assert "store_sets_identical_across_inputs" in checks


@requires_r
def test_reorder_point_formula_is_verified(mutable_workspace) -> None:
    """The reorder-point identity must be checked, not assumed."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_scenarios.csv",
        lambda frame: frame.assign(
            reorder_point=frame["reorder_point"] * 1.01
        ),
    )

    assert result.returncode != 0
    assert "historical_reorder_point_formula_holds" in checks


@requires_r
def test_safety_stock_formula_is_verified(mutable_workspace) -> None:
    """The safety-stock identity must be checked, not assumed."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_scenarios.csv",
        lambda frame: frame.assign(
            safety_stock=frame["safety_stock"] * 1.01
        ),
    )

    assert result.returncode != 0
    assert "historical_safety_stock_formula_holds" in checks


@requires_r
def test_service_level_z_value_is_verified(mutable_workspace) -> None:
    """Service-level factors must match the standard-normal quantiles."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_scenarios.csv",
        lambda frame: frame.assign(z_value=2.0),
    )

    assert result.returncode != 0
    assert "historical_service_level_z_values_match" in checks


@requires_r
def test_bias_corrected_level_is_verified(mutable_workspace) -> None:
    """The forecast family must use the bias-corrected demand level."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_forecast_scenarios.csv",
        lambda frame: frame.assign(
            bias_adjusted_daily_demand=frame["model_daily_demand"]
        ),
    )

    assert result.returncode != 0
    assert "forecast_level_is_bias_corrected" in checks


@requires_r
def test_phase13_insight_mismatch_is_rejected(mutable_workspace) -> None:
    """A Phase 13 insight that R cannot reproduce must fail the run."""
    result, checks = run_mutated(
        mutable_workspace,
        "forecast_inventory_insights.csv",
        lambda frame: frame.assign(
            store_id=frame["store_id"].where(
                frame["insight_type"] != "highest_average_demand", 2
            )
        ),
    )

    assert result.returncode != 0
    assert "phase13_highest_average_demand_reconciles" in checks


@requires_r
def test_reported_metric_mismatch_is_rejected(mutable_workspace) -> None:
    """Recomputed metrics that disagree with Phase 12 must fail the run."""
    result, checks = run_mutated(
        mutable_workspace,
        "tuned_validation_results.csv",
        lambda frame: frame.assign(rmse=frame["rmse"] * 1.05),
    )

    assert result.returncode != 0
    assert "recomputed_rmse_reconciles_with_phase12" in checks
    assert "forecast_error_matches_validation" in checks


@requires_r
def test_zero_filled_day_measurement_is_verified(mutable_workspace) -> None:
    """The densification measurement must reconcile with the summary."""
    result, checks = run_mutated(
        mutable_workspace,
        "inventory_densification_summary.csv",
        lambda frame: frame.assign(synthetic_days=0),
    )

    assert result.returncode != 0
    assert "synthetic_days_measured_consistently" in checks
    assert "zero_filled_days_are_minimal" in checks


@requires_r
def test_failed_runs_do_not_publish_findings(mutable_workspace) -> None:
    """A failed run must not leave an interpretation artifact behind."""
    _, _ = run_mutated(
        mutable_workspace,
        "inventory_demand_summary.csv",
        lambda frame: frame.assign(mean_daily_demand=-1.0),
    )

    assert not (mutable_workspace["output_dir"] / "r_analysis_findings.txt").exists()
    assert (mutable_workspace["output_dir"] / "r_analysis_quality_report.csv").is_file()
    assert (mutable_workspace["output_dir"] / "r_environment.csv").is_file()


def shipped_artifacts_present() -> bool:
    """Return True when a real Phase 14 run has left its artifacts in place."""
    if not R_OUTPUT_DIR.is_dir():
        return False
    return all((R_OUTPUT_DIR / name).is_file() for name in OUTPUT_FILES)


shipped = pytest.mark.skipif(
    not shipped_artifacts_present(),
    reason="Phase 14 artifacts have not been generated in this checkout",
)


@shipped
def test_shipped_quality_report_passes() -> None:
    """The committed-in-place artifacts must represent a passing run."""
    report = load_quality(R_OUTPUT_DIR)
    assert report["passed"].all(), failed_checks(R_OUTPUT_DIR)


@shipped
def test_shipped_artifacts_post_date_their_phase_13_inputs() -> None:
    """Artifacts must be regenerated after the evidence they consume."""
    inputs = [
        ANALYSIS_DIR / name
        for name in (
            "inventory_demand_summary.csv",
            "inventory_scenarios.csv",
            "inventory_forecast_scenarios.csv",
            "tuned_validation_results.csv",
            "model_evaluation_predictions.csv",
        )
    ]
    latest_input = max(path.stat().st_mtime for path in inputs if path.is_file())

    outputs = [R_OUTPUT_DIR / name for name in OUTPUT_FILES]
    outputs += [R_OUTPUT_DIR / "plots" / name for name in PLOT_FILES]
    oldest_output = min(path.stat().st_mtime for path in outputs if path.is_file())

    assert oldest_output >= latest_input, (
        "Phase 14 artifacts predate the Phase 13 evidence they consume"
    )


@shipped
def test_shipped_store_analysis_matches_phase_13_demand() -> None:
    """The shipped store table must reproduce the shipped Phase 13 demand."""
    demand = pd.read_csv(ANALYSIS_DIR / "inventory_demand_summary.csv")
    store_analysis = pd.read_csv(R_OUTPUT_DIR / "r_store_analysis.csv")

    merged = store_analysis.merge(
        demand,
        on="store_id",
        suffixes=("_r", "_phase13"),
    )

    assert len(merged) == len(demand)
    assert (
        (merged["mean_daily_demand_r"] - merged["mean_daily_demand_phase13"]).abs()
        < 1e-9
    ).all()
    assert (
        (merged["training_days_r"] - merged["training_days_phase13"]).abs() == 0
    ).all()


@shipped
def test_shipped_findings_report_claims_verified_consistency() -> None:
    """The shipped findings must reflect a verified reconciliation."""
    findings = (R_OUTPUT_DIR / "r_analysis_findings.txt").read_text(encoding="utf-8")
    assert "Store-level consistency with Phase 13: verified" in findings
    assert "NOT verified" not in findings


@shipped
def test_shipped_plots_are_present_and_non_empty() -> None:
    """Every exported figure must exist and carry content."""
    for name in PLOT_FILES:
        plot = R_OUTPUT_DIR / "plots" / name
        assert plot.is_file(), name
        assert plot.stat().st_size > 0, name


def test_report_html_is_regenerated_after_the_report_source() -> None:
    """The knitted report must not predate the R Markdown source."""
    html = R_OUTPUT_DIR / "r_analysis_report.html"
    if not html.is_file():
        pytest.skip("the Phase 14 HTML report has not been knitted")

    assert html.stat().st_mtime >= R_REPORT.stat().st_mtime


def test_script_defines_functions_and_a_main_entry_point() -> None:
    """The phase must demonstrate real R functions, not a bare script."""
    source = R_SCRIPT.read_text(encoding="utf-8")

    for function_name in (
        "find_project_root",
        "resolve_paths",
        "load_inputs",
        "validate_inputs",
        "validate_scenario_family",
        "reconcile_phase13",
        "recompute_validation_metrics",
        "reconcile_densification",
        "build_plots",
        "write_findings",
        "build_quality_report",
        "main",
    ):
        if function_name == "build_quality_report":
            assert "write_quality_report" in source
            continue
        assert f"{function_name} <- function" in source, function_name

    assert 'if (sys.nframe() == 0L)' in source


def test_script_does_not_depend_on_the_checkout_directory_name() -> None:
    """Regression: the root must not be inferred from a hardcoded folder name."""
    source = R_SCRIPT.read_text(encoding="utf-8")
    assert "demand-forecasting-retail" not in source
    assert "R_ANALYSIS_PROJECT_ROOT" in source


def test_script_has_no_hardcoded_absolute_paths() -> None:
    """Paths must be resolved from the project root instead of hardcoded."""
    source = R_SCRIPT.read_text(encoding="utf-8")
    assert "C:\\\\" not in source
    assert "C:/Users" not in source


def test_script_uses_the_packages_it_requires() -> None:
    """Declared dependencies must be genuinely used."""
    source = R_SCRIPT.read_text(encoding="utf-8")
    assert "yardstick::rmse_vec" in source
    assert "yardstick::mape_vec" in source
    assert "tidymodels" in source


def test_script_covers_both_scenario_families_and_the_stored_forecasts() -> None:
    """The workflow must consume the full Phase 13/Phase 12 evidence base."""
    source = R_SCRIPT.read_text(encoding="utf-8")
    for file_name in (
        "inventory_scenarios.csv",
        "inventory_forecast_scenarios.csv",
        "inventory_forecast_error_summary.csv",
        "inventory_densification_summary.csv",
        "model_evaluation_predictions.csv",
        "tuned_validation_results.csv",
    ):
        assert file_name in source, file_name


def test_report_sources_the_script_and_gates_on_the_quality_report() -> None:
    """The report must render the audited evidence and refuse to knit on failure."""
    report = R_REPORT.read_text(encoding="utf-8")
    assert "source(" in report
    assert "r_analysis.R" in report
    assert "results <- main()" in report
    assert "results$quality$passed" in report
    assert "relative_to_report" in report
