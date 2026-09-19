"""Create Phase 15 stakeholder-facing visualizations.

The visualizations use compact analytical outputs produced by earlier
project phases. The workflow does not retrain forecasting models and does
not use the test period for model selection or tuning.

Design notes
------------
* The project root is discovered by walking up from the working directory
  looking for ``pyproject.toml``. It can be overridden, together with the
  input, output and report directories, through the environment variables
  ``VISUALIZATION_PROJECT_ROOT``, ``VISUALIZATION_INPUT_DIR``,
  ``VISUALIZATION_OUTPUT_DIR`` and ``VISUALIZATION_REPORT_DIR``. Those
  overrides let the automated tests run the complete workflow into a
  temporary directory.
* Every validation result is recorded in a machine-readable quality report
  (``visualization_quality_report.csv``) that gates the run: if any check
  fails, no "completed" message is printed, a non-zero exit code is
  returned and the figures are withheld.
* Every generated figure is recorded in ``visualization_manifest.csv`` with
  its byte size and SHA-256 digest so the artifacts can be re-verified.
"""

from __future__ import annotations

import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

INPUT_FILES = {
    "demand": "inventory_demand_summary.csv",
    "variability": "inventory_variability_summary.csv",
    "scenarios": "inventory_scenarios.csv",
    "insights": "forecast_inventory_insights.csv",
    "validation": "tuned_validation_results.csv",
}

REQUIRED_COLUMNS = {
    "demand": {
        "store_id",
        "training_days",
        "mean_daily_demand",
        "median_daily_demand",
        "min_daily_demand",
        "max_daily_demand",
        "coefficient_of_variation",
    },
    "variability": {
        "store_id",
        "mean_daily_demand",
        "std_daily_demand",
        "variance_daily_demand",
        "coefficient_of_variation",
    },
    "scenarios": {
        "store_id",
        "model",
        "lead_time_days",
        "service_level",
        "z_value",
        "mean_daily_demand",
        "std_daily_demand",
        "expected_lead_time_demand",
        "safety_stock",
        "reorder_point",
    },
    "insights": {
        "insight_type",
        "store_id",
        "metric",
        "value",
    },
    "validation": {
        "store_id",
        "model",
        "rmse",
        "mape_percent",
    },
}

REQUIRED_INSIGHT_TYPES = {
    "highest_average_demand",
    "highest_relative_variability",
    "lowest_validation_rmse",
    "lowest_relative_validation_error",
    "inventory_scenario",
}

BASELINE_SERVICE_LEVEL = 0.95
SCENARIO_SERVICE_LEVELS = (0.90, 0.95, 0.99)

FIGURE_SOURCES = {
    "store_average_daily_demand.png": "demand",
    "store_demand_variability.png": "variability",
    "reorder_point_by_lead_time.png": "scenarios",
    "lowest_validation_rmse.png": "insights",
}

TOLERANCE = 1e-6


class WorkflowError(RuntimeError):
    """Raised when the visualization workflow cannot complete."""


@dataclass(frozen=True)
class Check:
    """One machine-readable validation result."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Paths:
    """Resolved input, output and report directories."""

    root: Path
    input_dir: Path
    output_dir: Path
    report_dir: Path


def discover_project_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` looking for the project root marker."""
    current = (start or Path.cwd()).resolve()

    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate

    raise WorkflowError(
        "Could not locate the project root (no pyproject.toml found in any "
        "parent directory). Set VISUALIZATION_PROJECT_ROOT to override."
    )


def resolve_paths(
    *,
    root: Path | None = None,
    input_dir: Path | None = None,
    output_dir: Path | None = None,
    report_dir: Path | None = None,
) -> Paths:
    """Resolve the workflow directories from arguments and the environment."""
    env_root = os.environ.get("VISUALIZATION_PROJECT_ROOT")
    resolved_root = Path(root or env_root) if (root or env_root) else None
    if resolved_root is None:
        resolved_root = discover_project_root()

    env_input = os.environ.get("VISUALIZATION_INPUT_DIR")
    resolved_input = Path(
        input_dir or env_input or resolved_root / "data" / "analysis"
    )

    env_output = os.environ.get("VISUALIZATION_OUTPUT_DIR")
    resolved_output = Path(
        output_dir or env_output or resolved_input / "visualizations"
    )

    env_report = os.environ.get("VISUALIZATION_REPORT_DIR")
    # In the project the input and report directories are both
    # `data/analysis`; deriving the report directory from the input
    # directory keeps the tests from writing into the real project.
    resolved_report = Path(report_dir or env_report or resolved_input)

    return Paths(
        root=resolved_root,
        input_dir=resolved_input,
        output_dir=resolved_output,
        report_dir=resolved_report,
    )


def require_file(path: Path) -> None:
    """Raise an explicit error when an expected input file is missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required input file is missing: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Required input is not a file: {path}")


def load_inputs(input_dir: Path) -> dict[str, pd.DataFrame]:
    """Load every analytical input the workflow consumes."""
    frames: dict[str, pd.DataFrame] = {}

    for key, filename in INPUT_FILES.items():
        path = input_dir / filename
        require_file(path)
        frames[key] = pd.read_csv(path)

    return frames


def _check(name: str, condition: bool, detail: str) -> Check:
    return Check(name=name, passed=bool(condition), detail=detail)


def _columns_check(key: str, frame: pd.DataFrame) -> Check:
    missing = sorted(REQUIRED_COLUMNS[key] - set(frame.columns))
    return _check(
        f"{key}_columns_present",
        not missing,
        "all required columns present"
        if not missing
        else f"missing columns: {', '.join(missing)}",
    )


def _empty_check(key: str, frame: pd.DataFrame) -> Check:
    return _check(
        f"{key}_not_empty",
        not frame.empty,
        f"{len(frame)} row(s)",
    )


def validate_inputs(
    demand: pd.DataFrame,
    variability: pd.DataFrame,
    scenarios: pd.DataFrame,
    insights: pd.DataFrame | None = None,
    validation: pd.DataFrame | None = None,
) -> list[Check]:
    """Validate every analytical input and return the collected checks."""
    checks: list[Check] = []

    frames = {
        "demand": demand,
        "variability": variability,
        "scenarios": scenarios,
    }
    if insights is not None:
        frames["insights"] = insights
    if validation is not None:
        frames["validation"] = validation

    for key, frame in frames.items():
        checks.append(_columns_check(key, frame))
        checks.append(_empty_check(key, frame))

    if not all(check.passed for check in checks):
        # Column or emptiness failures make the numeric checks meaningless.
        return checks

    checks.extend(_validate_demand(demand))
    checks.extend(_validate_variability(variability))
    checks.extend(_validate_scenarios(scenarios, demand))

    if validation is not None and not validation.empty:
        checks.extend(_validate_validation(validation))

    if insights is not None and not insights.empty:
        checks.extend(
            _validate_insights(insights, demand, scenarios, validation)
        )

    checks.extend(_validate_store_sets(frames))
    return checks


def _validate_demand(demand: pd.DataFrame) -> list[Check]:
    """Validate the store-level demand summary."""
    return [
        _check(
            "demand_store_ids_not_null",
            demand["store_id"].notna().all(),
            "all store ids populated",
        ),
        _check(
            "demand_store_ids_unique",
            demand["store_id"].is_unique,
            f"{demand['store_id'].nunique()} unique store id(s)",
        ),
        _check(
            "demand_mean_non_negative",
            bool((demand["mean_daily_demand"] >= 0).all()),
            "mean daily demand is non-negative",
        ),
        _check(
            "demand_cv_non_negative",
            bool((demand["coefficient_of_variation"] >= 0).all()),
            "coefficient of variation is non-negative",
        ),
        _check(
            "demand_min_max_ordered",
            bool(
                (
                    demand["min_daily_demand"] <= demand["max_daily_demand"]
                ).all()
            ),
            "minimum daily demand never exceeds the maximum",
        ),
        _check(
            "demand_training_days_positive",
            bool((demand["training_days"] > 0).all()),
            "every store has at least one training day",
        ),
    ]


def _validate_variability(variability: pd.DataFrame) -> list[Check]:
    """Validate the store-level variability summary."""
    mean = variability["mean_daily_demand"]
    std = variability["std_daily_demand"]
    variance = variability["variance_daily_demand"]
    cv = variability["coefficient_of_variation"]

    denominator = mean.where(mean != 0)
    expected_cv = (std / denominator).fillna(0.0)

    checks = [
        _check(
            "variability_std_non_negative",
            bool((std >= 0).all()),
            "standard deviation is non-negative",
        ),
        _check(
            "variability_cv_non_negative",
            bool((cv >= 0).all()),
            "coefficient of variation is non-negative",
        ),
        _check(
            "variability_cv_reconciles",
            bool((cv - expected_cv).abs().le(TOLERANCE).all()),
            "coefficient of variation equals std / mean",
        ),
        _check(
            "variability_variance_reconciles",
            bool((variance - std.pow(2)).abs().le(TOLERANCE).all()),
            "variance equals the squared standard deviation",
        ),
    ]

    percentiles = {
        "p90_daily_demand",
        "p95_daily_demand",
        "p99_daily_demand",
    }
    if percentiles.issubset(variability.columns):
        ordered = (
            variability["p90_daily_demand"]
            <= variability["p95_daily_demand"]
        ) & (
            variability["p95_daily_demand"]
            <= variability["p99_daily_demand"]
        )
        checks.append(
            _check(
                "variability_percentiles_ordered",
                bool(ordered.all()),
                "p90 <= p95 <= p99 for every store",
            )
        )

    return checks


def _validate_scenarios(
    scenarios: pd.DataFrame,
    demand: pd.DataFrame,
) -> list[Check]:
    """Validate the reorder-point scenarios and their formulas."""
    z_value = scenarios["z_value"]
    service_level = scenarios["service_level"]
    lead_time = scenarios["lead_time_days"]
    mean = scenarios["mean_daily_demand"]
    std = scenarios["std_daily_demand"]
    expected = scenarios["expected_lead_time_demand"]
    safety = scenarios["safety_stock"]
    reorder = scenarios["reorder_point"]

    expected_z = pd.Series(
        stats.norm.ppf(service_level.to_numpy()),
        index=scenarios.index,
    )

    checks = [
        _check(
            "scenarios_store_ids_not_null",
            scenarios["store_id"].notna().all(),
            "all store ids populated",
        ),
        _check(
            "scenarios_lead_time_positive",
            bool((lead_time > 0).all()),
            "assumed lead times are positive",
        ),
        _check(
            "scenarios_service_level_in_range",
            bool(service_level.between(0.0, 1.0).all()),
            "service levels are valid probabilities",
        ),
        _check(
            "scenarios_service_level_coverage",
            set(service_level.round(6)) == set(SCENARIO_SERVICE_LEVELS),
            f"service levels {sorted(set(service_level.round(6)))}",
        ),
        _check(
            "scenarios_z_values_reconcile",
            bool((z_value - expected_z).abs().le(TOLERANCE).all()),
            "z values equal the standard-normal quantile of the service level",
        ),
        _check(
            "scenarios_expected_demand_reconciles",
            bool((expected - mean * lead_time).abs().le(TOLERANCE).all()),
            "expected lead-time demand equals mean demand x lead time",
        ),
        _check(
            "scenarios_safety_stock_reconciles",
            bool(
                (safety - z_value * std * lead_time.pow(0.5))
                .abs()
                .le(TOLERANCE)
                .all()
            ),
            "safety stock equals z x std x sqrt(lead time)",
        ),
        _check(
            "scenarios_reorder_point_reconciles",
            bool((reorder - (expected + safety)).abs().le(TOLERANCE).all()),
            "reorder point equals expected demand plus safety stock",
        ),
        _check(
            "scenarios_reorder_point_non_negative",
            bool((reorder >= 0).all()),
            "reorder points are non-negative",
        ),
    ]

    demand_means = demand.set_index("store_id")["mean_daily_demand"]
    scenario_means = scenarios.groupby("store_id")["mean_daily_demand"].first()
    aligned = scenario_means.reindex(demand_means.index)
    checks.append(
        _check(
            "scenarios_demand_level_reconciles",
            bool(((aligned - demand_means).abs() <= TOLERANCE).all()),
            "scenario demand levels match the Phase 13 demand summary",
        )
    )

    grid = scenarios.groupby("store_id")[
        ["lead_time_days", "service_level"]
    ].apply(lambda group: len(group.drop_duplicates()) == 9)
    checks.append(
        _check(
            "scenarios_grid_complete",
            bool(grid.all()),
            "every store covers 3 lead times x 3 service levels",
        )
    )

    baseline = scenarios[
        scenarios["service_level"].round(6).eq(BASELINE_SERVICE_LEVEL)
    ]
    by_service = (
        scenarios.sort_values("service_level")
        .groupby(["store_id", "lead_time_days"])["reorder_point"]
        .apply(lambda values: values.is_monotonic_increasing)
    )
    checks.append(
        _check(
            "scenarios_monotonic_in_service_level",
            bool(by_service.all()) and not baseline.empty,
            "reorder points rise with the assumed service level",
        )
    )

    by_lead = (
        scenarios.sort_values("lead_time_days")
        .groupby(["store_id", "service_level"])["reorder_point"]
        .apply(lambda values: values.is_monotonic_increasing)
    )
    checks.append(
        _check(
            "scenarios_monotonic_in_lead_time",
            bool(by_lead.all()),
            "reorder points rise with the assumed lead time",
        )
    )

    return checks


def _validate_validation(validation: pd.DataFrame) -> list[Check]:
    """Validate the stored Phase 12 validation results."""
    return [
        _check(
            "validation_rmse_positive",
            bool((validation["rmse"] > 0).all()),
            "validation RMSE is positive",
        ),
        _check(
            "validation_mape_non_negative",
            bool((validation["mape_percent"] >= 0).all()),
            "validation MAPE is non-negative",
        ),
        _check(
            "validation_one_row_per_store",
            validation["store_id"].is_unique,
            f"{validation['store_id'].nunique()} store(s) with a selected "
            "model",
        ),
    ]


def _validate_insights(
    insights: pd.DataFrame,
    demand: pd.DataFrame,
    scenarios: pd.DataFrame,
    validation: pd.DataFrame | None,
) -> list[Check]:
    """Validate and reconcile the Phase 13 forecast and inventory insights."""
    present = set(insights["insight_type"])
    missing = sorted(REQUIRED_INSIGHT_TYPES - present)

    checks = [
        _check(
            "insights_required_types_present",
            not missing,
            "all required insight types present"
            if not missing
            else f"missing insight types: {', '.join(missing)}",
        ),
        _check(
            "insights_values_non_negative",
            bool((insights["value"].dropna() >= 0).all()),
            "insight values are non-negative",
        ),
        _check(
            "insights_store_ids_valid",
            bool(insights["store_id"].isin(demand["store_id"]).all()),
            "insight store ids exist in the demand summary",
        ),
    ]

    checks.append(
        _reconcile_insight(
            insights,
            "highest_average_demand",
            demand["mean_daily_demand"].max(),
            "highest average daily demand matches the demand summary",
        )
    )
    checks.append(
        _reconcile_insight(
            insights,
            "highest_relative_variability",
            demand["coefficient_of_variation"].max(),
            "highest relative variability matches the demand summary",
        )
    )

    if validation is not None and not validation.empty:
        checks.append(
            _reconcile_insight(
                insights,
                "lowest_validation_rmse",
                validation["rmse"].min(),
                "lowest validation RMSE matches the Phase 12 tuned results",
            )
        )
        checks.append(
            _reconcile_insight(
                insights,
                "lowest_relative_validation_error",
                validation["mape_percent"].min(),
                "lowest relative validation error matches the Phase 12 "
                "results",
            )
        )

    scenario_rows = insights[
        insights["insight_type"].eq("inventory_scenario")
    ]
    if not scenario_rows.empty:
        baseline = scenarios[
            scenarios["lead_time_days"].eq(14)
            & scenarios["service_level"]
            .round(6)
            .eq(BASELINE_SERVICE_LEVEL)
        ].set_index("store_id")["reorder_point"]

        mismatched = [
            int(row.store_id)
            for row in scenario_rows.itertuples()
            if row.store_id not in baseline.index
            or abs(row.value - baseline.loc[row.store_id]) > TOLERANCE
        ]
        checks.append(
            _check(
                "insights_inventory_scenario_reconciles",
                not mismatched,
                "14-day / 95% scenario reorder points match the scenario "
                "table",
            )
        )

    return checks


def _reconcile_insight(
    insights: pd.DataFrame,
    insight_type: str,
    expected: float,
    detail: str,
) -> Check:
    """Check that one insight's value matches its recomputed source value."""
    rows = insights[insights["insight_type"].eq(insight_type)]

    if rows.empty:
        return _check(
            f"insights_{insight_type}_reconciles",
            False,
            f"required insight '{insight_type}' is missing",
        )

    difference = float((rows["value"] - expected).abs().max())
    return _check(
        f"insights_{insight_type}_reconciles",
        difference <= TOLERANCE,
        f"{detail} (max difference {difference:.3e})",
    )


def _validate_store_sets(frames: dict[str, pd.DataFrame]) -> list[Check]:
    """Check that every detail input covers exactly the demanded stores."""
    reference = set(frames["demand"]["store_id"])
    detail_sets = {
        "variability": set(frames["variability"]["store_id"]),
        "scenarios": set(frames["scenarios"]["store_id"]),
    }
    if "validation" in frames:
        detail_sets["validation"] = set(frames["validation"]["store_id"])

    return [
        _check(
            f"{key}_store_set_matches_demand",
            stores == reference,
            f"{len(stores)} store(s), identical to the demand summary",
        )
        for key, stores in detail_sets.items()
    ]


def validate_leakage_guard(frames: dict[str, pd.DataFrame]) -> list[Check]:
    """Confirm no test-period artifact reaches a visualization."""
    offending = [
        filename
        for filename in INPUT_FILES.values()
        if any(token in filename.lower() for token in ("test", "holdout"))
    ]

    checks = [
        _check(
            "leakage_no_test_artifacts",
            not offending,
            "no declared input is a test-period artifact"
            if not offending
            else f"test-period artifact(s) declared as inputs: {offending}",
        ),
        _check(
            "leakage_training_days_declared",
            "training_days" in frames["demand"].columns,
            "the demand summary declares its training window",
        ),
    ]

    rmse = frames["insights"][
        frames["insights"]["insight_type"].eq("lowest_validation_rmse")
    ]
    metric_ok = bool(
        not rmse.empty and rmse["metric"].eq("validation_rmse").all()
    )
    checks.append(
        _check(
            "leakage_insights_use_validation_not_test",
            metric_ok,
            "forecast-evidence insights are derived from validation, not "
            "test, data",
        )
    )

    return checks


def save_figure(
    figure: plt.Figure,
    path: Path,
    *,
    width: float = 9,
    height: float = 5,
) -> Path:
    """Save and close a visualization consistently."""
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.set_size_inches(width, height)
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return path


def create_store_demand_chart(demand: pd.DataFrame, output_dir: Path) -> Path:
    """Create a comparison of average daily demand by store."""
    ordered = demand.sort_values("mean_daily_demand", ascending=True)

    figure, axis = plt.subplots()
    bars = axis.barh(
        ordered["store_id"].astype(str),
        ordered["mean_daily_demand"],
        color="#3b6ea5",
    )

    axis.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
    axis.set_title("Average Daily Physical Demand by Store")
    axis.set_xlabel("Mean Daily Demand (demand units, training period)")
    axis.set_ylabel("Store")
    axis.margins(x=0.12)

    return save_figure(figure, output_dir / "store_average_daily_demand.png")


def create_variability_chart(
    variability: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Create a comparison of relative demand variability."""
    ordered = variability.sort_values(
        "coefficient_of_variation",
        ascending=True,
    )

    figure, axis = plt.subplots()
    bars = axis.barh(
        ordered["store_id"].astype(str),
        ordered["coefficient_of_variation"],
        color="#8a6d3b",
    )

    axis.bar_label(bars, fmt="%.4f", padding=3, fontsize=8)
    axis.set_title("Relative Demand Variability by Store")
    axis.set_xlabel(
        "Coefficient of Variation (std / mean, training period)"
    )
    axis.set_ylabel("Store")
    axis.margins(x=0.15)

    return save_figure(figure, output_dir / "store_demand_variability.png")


def create_inventory_scenario_chart(
    scenarios: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Create reorder-point scenarios by lead time for each store."""
    baseline = scenarios[
        scenarios["service_level"].round(6).eq(BASELINE_SERVICE_LEVEL)
    ]

    if baseline.empty:
        raise WorkflowError(
            "No inventory scenarios at the baseline 95% service level."
        )

    figure, axis = plt.subplots()

    for store_id, group in baseline.groupby("store_id"):
        group = group.sort_values("lead_time_days")

        axis.plot(
            group["lead_time_days"],
            group["reorder_point"],
            marker="o",
            label=f"Store {store_id}",
        )

    axis.set_title(
        "Scenario Reorder Points at an Assumed 95% Service Level"
    )
    axis.set_xlabel(
        "Assumed Lead Time (days) - a planning assumption, not a requirement"
    )
    axis.set_ylabel("Scenario Reorder Point (demand units)")
    axis.legend(title="Store")
    axis.grid(axis="y", linewidth=0.4, alpha=0.4)

    return save_figure(
        figure,
        output_dir / "reorder_point_by_lead_time.png",
        width=10,
        height=6,
    )


def create_forecast_evidence_chart(
    insights: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Create a chart of the lowest validation RMSE per store."""
    validation = insights[
        insights["insight_type"].eq("lowest_validation_rmse")
    ].copy()

    if validation.empty:
        raise WorkflowError(
            "The lowest_validation_rmse insight is missing, so the "
            "forecast-evidence chart cannot be drawn."
        )

    validation = validation.sort_values("value", ascending=False)

    figure, axis = plt.subplots()
    bars = axis.bar(
        validation["store_id"].astype(str),
        validation["value"],
        color="#4a7c59",
    )

    axis.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
    axis.set_title(
        "Lowest Validation RMSE Among Validated Models, by Store"
    )
    axis.set_xlabel("Store")
    axis.set_ylabel(
        "Validation RMSE (demand units - not comparable across stores)"
    )
    axis.margins(y=0.15)

    return save_figure(
        figure,
        output_dir / "lowest_validation_rmse.png",
    )


def sha256_of(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def figure_checks(
    output_dir: Path,
    sources: dict[str, int],
) -> list[Check]:
    """Confirm every expected figure was written as a non-empty file."""
    checks = []

    for filename, source in FIGURE_SOURCES.items():
        path = output_dir / filename
        exists = path.is_file()
        size = path.stat().st_size if exists else 0
        checks.append(
            _check(
                f"figure_{filename}_written",
                exists and size > 0,
                f"{size} byte(s); source rows: {sources.get(source, 0)}",
            )
        )

    return checks


def write_quality_report(checks: list[Check], report_dir: Path) -> Path:
    """Write the run-gating quality report."""
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "visualization_quality_report.csv"

    pd.DataFrame(
        [
            {
                "check": check.name,
                "status": "PASS" if check.passed else "FAIL",
                "detail": check.detail,
            }
            for check in checks
        ]
    ).to_csv(path, index=False)

    return path


def write_manifest(
    figures: list[Path],
    sources: dict[str, int],
    report_dir: Path,
) -> Path:
    """Write the manifest of generated figures."""
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "visualization_manifest.csv"

    rows = [
        {
            "figure": figure.name,
            "path": figure.as_posix(),
            "bytes": figure.stat().st_size,
            "sha256": sha256_of(figure),
            "source": FIGURE_SOURCES[figure.name],
            "source_rows": sources.get(FIGURE_SOURCES[figure.name], 0),
        }
        for figure in figures
    ]

    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def run_workflow(
    *,
    root: Path | None = None,
    input_dir: Path | None = None,
    output_dir: Path | None = None,
    report_dir: Path | None = None,
) -> dict[str, object]:
    """Run the Phase 15 visualization workflow and gate it on its checks."""
    paths = resolve_paths(
        root=root,
        input_dir=input_dir,
        output_dir=output_dir,
        report_dir=report_dir,
    )

    frames = load_inputs(paths.input_dir)
    sources = {key: len(frame) for key, frame in frames.items()}

    checks = validate_inputs(
        frames["demand"],
        frames["variability"],
        frames["scenarios"],
        frames["insights"],
        frames["validation"],
    )
    checks.extend(validate_leakage_guard(frames))

    write_quality_report(checks, paths.report_dir)

    failures = [check for check in checks if not check.passed]
    if failures:
        raise WorkflowError(
            f"Input validation failed ({len(failures)} of {len(checks)} "
            "checks); no figures were drawn."
        )

    paths.output_dir.mkdir(parents=True, exist_ok=True)

    figures = [
        create_store_demand_chart(frames["demand"], paths.output_dir),
        create_variability_chart(frames["variability"], paths.output_dir),
        create_inventory_scenario_chart(
            frames["scenarios"], paths.output_dir
        ),
        create_forecast_evidence_chart(
            frames["insights"], paths.output_dir
        ),
    ]

    checks.extend(figure_checks(paths.output_dir, sources))
    report_path = write_quality_report(checks, paths.report_dir)

    figure_failures = [check for check in checks if not check.passed]
    if figure_failures:
        raise WorkflowError(
            "Figure verification failed: "
            + "; ".join(check.name for check in figure_failures)
        )

    manifest_path = write_manifest(figures, sources, paths.report_dir)

    return {
        "paths": paths,
        "frames": frames,
        "checks": checks,
        "figures": figures,
        "report": report_path,
        "manifest": manifest_path,
    }


def main() -> int:
    """Run the Phase 15 visualization workflow as a script."""
    print("Creating Phase 15 visualizations...")

    try:
        result = run_workflow()
    except (WorkflowError, FileNotFoundError, ValueError) as error:
        print(f"Phase 15 visualizations FAILED: {error}", file=sys.stderr)
        return 1

    checks = result["checks"]
    passed = sum(1 for check in checks if check.passed)

    print(
        "Phase 15 visualizations completed successfully "
        f"({passed} of {len(checks)} checks)."
    )
    print(f"Visualization directory: {result['paths'].output_dir}")
    print(f"Quality report: {result['report']}")
    print(f"Manifest: {result['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

