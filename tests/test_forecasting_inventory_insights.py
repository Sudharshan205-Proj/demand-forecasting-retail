"""Tests for Phase 13 forecasting and inventory insights."""

from __future__ import annotations

import inspect
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import scripts.forecasting_inventory_insights as fi
from scripts.forecasting_inventory_insights import (
    SERVICE_LEVELS,
    build_findings_text,
    build_model_lines,
    calculate_demand_summary,
    calculate_forecast_scenarios,
    calculate_inventory_scenarios,
    calculate_variability_summary,
    create_insights,
    densify_store_days,
    summarize_densification,
    validate_training_demand,
)

# The fixture spans the real split boundaries so the phase's date contract
# holds without patching it.
FIXTURE_START = "2022-08-28"
FIXTURE_END = "2024-09-26"
DROPPED_DATE = pd.Timestamp("2022-10-16")
DROPPED_STORE = 3

# Per-store validation design. ``level`` is the model's constant prediction
# and ``error`` alternates around it, so residuals vary (giving a non-zero
# residual standard deviation) while the ordering of RMSE and MAPE disagree:
# store 2 has the lowest RMSE, store 1 the lowest MAPE.
VALIDATION_DESIGN = {
    1: {"level": 1000.0, "error": 10.0},
    2: {"level": 100.0, "error": 5.0},
    3: {"level": 500.0, "error": 20.0},
    4: {"level": 300.0, "error": 30.0},
}

FEATURE_CONFIGURATION = "HistGradientBoostingRegressor(recursive, 16 features)"

MODEL_DESIGN = {
    1: {"model": "feature_gbm", "configuration": FEATURE_CONFIGURATION,
        "season_length": np.nan, "order": np.nan},
    2: {"model": "feature_gbm", "configuration": FEATURE_CONFIGURATION,
        "season_length": np.nan, "order": np.nan},
    3: {"model": "feature_gbm", "configuration": FEATURE_CONFIGURATION,
        "season_length": np.nan, "order": np.nan},
    4: {"model": "seasonal_naive", "configuration": "season_length=7",
        "season_length": 7.0, "order": np.nan},
}


def build_source_frame() -> pd.DataFrame:
    """Build a deterministic store-day matrix covering the real partitions."""
    dates = pd.date_range(FIXTURE_START, FIXTURE_END, freq="D")

    records: list[dict[str, object]] = []

    for store_id in sorted(MODEL_DESIGN):
        for position, date in enumerate(dates):
            if date == DROPPED_DATE and store_id == DROPPED_STORE:
                continue

            if date <= fi.TRAIN_END:
                split = "train"
            elif date <= fi.VALIDATION_END:
                split = "validation"
            else:
                split = "test"

            records.append(
                {
                    "date": date,
                    "store_id": store_id,
                    "quantity": float(100 + position),
                    "split": split,
                }
            )

    return pd.DataFrame(records)


def build_prediction_frame() -> pd.DataFrame:
    """Build stored validation forecasts with a controlled error structure."""
    validation_dates = pd.date_range(
        fi.VALIDATION_START, fi.VALIDATION_END, freq="D"
    )

    records: list[dict[str, object]] = []

    for store_id, design in sorted(VALIDATION_DESIGN.items()):
        for position, date in enumerate(validation_dates):
            residual = (
                design["error"] * 0.5
                if position % 2 == 0
                else design["error"] * 1.5
            )

            records.append(
                {
                    "scope": "validation",
                    "store_id": store_id,
                    "model": MODEL_DESIGN[store_id]["model"],
                    "cv_fold": np.nan,
                    "date": date,
                    "actual": design["level"] + residual,
                    "predicted": design["level"],
                }
            )

    return pd.DataFrame(records)


def summarize_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    """Reproduce the RMSE/MAPE a stored prediction set implies."""
    horizon = predictions[predictions["scope"] == "validation"]

    rows: list[dict[str, object]] = []

    for store_id, group in horizon.groupby("store_id", sort=True):
        residuals = group["actual"] - group["predicted"]

        rows.append(
            {
                "store_id": int(store_id),
                "model": MODEL_DESIGN[store_id]["model"],
                "configuration": MODEL_DESIGN[store_id]["configuration"],
                "rmse": float(np.sqrt((residuals**2).mean())),
                "mape_percent": float(
                    (residuals.abs() / group["actual"]).mean() * 100
                ),
            }
        )

    return pd.DataFrame(rows)


def fixture_for(paths: dict[str, object]) -> dict[str, object]:
    """Write every Phase 13 input into a temporary workspace."""
    source = build_source_frame()
    predictions = build_prediction_frame()
    validation = summarize_predictions(predictions)

    selected = pd.DataFrame(
        [
            {
                "store_id": store_id,
                "model": design["model"],
                "configuration": design["configuration"],
                "season_length": design["season_length"],
                "order": design["order"],
            }
            for store_id, design in sorted(MODEL_DESIGN.items())
        ]
    )

    # Two equal halves per store, so the recorded segment means reproduce the
    # overall bias and RMSE exactly.
    error_rows: list[dict[str, object]] = []

    for row in validation.itertuples(index=False):
        for segment in ("first_half", "second_half"):
            error_rows.append(
                {
                    "store_id": int(row.store_id),
                    "model": row.model,
                    "configuration": row.configuration,
                    "validation_segment": segment,
                    "mean_error": float(row.rmse) / np.sqrt(1.25),
                    "mean_absolute_error": float(row.rmse) / np.sqrt(1.25),
                    "rmse": float(row.rmse),
                }
            )

    error_analysis = pd.DataFrame(error_rows)

    source.to_csv(paths["input"], index=False)
    selected.to_csv(paths["selected"], index=False)
    validation.to_csv(paths["validation"], index=False)
    predictions.to_csv(paths["predictions"], index=False)
    error_analysis.to_csv(paths["error_analysis"], index=False)

    train = source[source["split"] == "train"]

    return {
        "source": source,
        "predictions": predictions,
        "validation": validation,
        "selected": selected,
        "error_analysis": error_analysis,
        "source_total_rows": int(len(source)),
        "source_total_quantity": float(source["quantity"].sum()),
        "source_train_rows": int(len(train)),
        "source_train_quantity": float(train["quantity"].sum()),
        "source_validation_rows": int(
            (source["split"] == "validation").sum()
        ),
        "source_test_rows": int((source["split"] == "test").sum()),
    }


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Patch every path and reconciliation constant onto a fixture dataset."""
    paths = {
        "input": tmp_path / "feature_engineered_daily.csv",
        "selected": tmp_path / "selected.csv",
        "validation": tmp_path / "validation.csv",
        "predictions": tmp_path / "predictions.csv",
        "error_analysis": tmp_path / "error_analysis.csv",
    }

    fixture = fixture_for(paths)

    monkeypatch.setattr(fi, "INPUT_PATH", paths["input"])
    monkeypatch.setattr(fi, "SELECTED_MODEL_PATH", paths["selected"])
    monkeypatch.setattr(fi, "VALIDATION_RESULTS_PATH", paths["validation"])
    monkeypatch.setattr(fi, "PREDICTIONS_PATH", paths["predictions"])
    monkeypatch.setattr(fi, "ERROR_ANALYSIS_PATH", paths["error_analysis"])

    monkeypatch.setattr(fi, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fi, "DEMAND_SUMMARY_PATH", tmp_path / "demand.csv")
    monkeypatch.setattr(fi, "VARIABILITY_PATH", tmp_path / "variability.csv")
    monkeypatch.setattr(
        fi, "DENSIFICATION_PATH", tmp_path / "densification.csv"
    )
    monkeypatch.setattr(fi, "SCENARIOS_PATH", tmp_path / "scenarios.csv")
    monkeypatch.setattr(
        fi, "FORECAST_SCENARIOS_PATH", tmp_path / "forecast_scenarios.csv"
    )
    monkeypatch.setattr(
        fi, "FORECAST_ERROR_PATH", tmp_path / "forecast_error.csv"
    )
    monkeypatch.setattr(fi, "INSIGHTS_PATH", tmp_path / "insights.csv")
    monkeypatch.setattr(fi, "FINDINGS_PATH", tmp_path / "findings.txt")
    monkeypatch.setattr(
        fi, "QUALITY_REPORT_PATH", tmp_path / "quality_report.csv"
    )

    monkeypatch.setattr(fi, "SOURCE_TOTAL_ROWS", fixture["source_total_rows"])
    monkeypatch.setattr(
        fi, "SOURCE_TOTAL_QUANTITY", fixture["source_total_quantity"]
    )
    monkeypatch.setattr(fi, "SOURCE_TRAIN_ROWS", fixture["source_train_rows"])
    monkeypatch.setattr(
        fi, "SOURCE_TRAIN_QUANTITY", fixture["source_train_quantity"]
    )
    monkeypatch.setattr(
        fi, "SOURCE_VALIDATION_ROWS", fixture["source_validation_rows"]
    )
    monkeypatch.setattr(fi, "SOURCE_TEST_ROWS", fixture["source_test_rows"])

    densified_days = int(len(build_source_frame()) - 0)

    monkeypatch.setattr(
        fi,
        "EXPECTED_DENSIFIED_TRAINING_DAYS",
        int(
            sum(
                (len(pd.date_range(fi.TRAIN_START, fi.TRAIN_END, freq="D")))
                for _ in sorted(MODEL_DESIGN)
            )
        ),
    )

    return SimpleNamespace(
        paths=paths,
        output_dir=tmp_path,
        densified_days=densified_days,
        **fixture,
    )


def compute_bundle() -> dict[str, object]:
    """Run every computation main() performs, returning the frames."""
    data, stats = fi.load_training_demand()

    selected_models, validation = fi.load_phase12_model_evidence()

    validate_training_demand(
        data,
        expected_stores={int(s) for s in selected_models["store_id"]},
    )

    densification = summarize_densification(data)

    demand_summary = calculate_demand_summary(data)

    variability = calculate_variability_summary(data)

    errors = fi.load_phase12_forecast_errors(validation)

    error_analysis = fi.load_phase12_error_analysis()

    scenarios = calculate_inventory_scenarios(variability, selected_models)

    forecast_scenarios = calculate_forecast_scenarios(
        errors, selected_models
    )

    insights = create_insights(
        demand_summary,
        variability,
        scenarios,
        forecast_scenarios,
        errors,
        validation,
    )

    model_lines = build_model_lines(errors)

    findings_text = build_findings_text(
        demand_summary,
        variability,
        scenarios,
        forecast_scenarios,
        errors,
        densification,
        model_lines,
    )

    return {
        "data": data,
        "stats": stats,
        "densification": densification,
        "demand_summary": demand_summary,
        "variability": variability,
        "scenarios": scenarios,
        "forecast_scenarios": forecast_scenarios,
        "errors": errors,
        "validation": validation,
        "error_analysis": error_analysis,
        "insights": insights,
        "findings_text": findings_text,
        "model_lines": model_lines,
        "selected_models": selected_models,
    }


_REPORT_PARAMETERS = frozenset(
    inspect.signature(fi.build_quality_report).parameters
)


def report_for(bundle: dict[str, object], **overrides) -> pd.DataFrame:
    """Build the quality report for a bundle, with optional mutations."""
    merged = {**bundle, **overrides}

    kwargs = {key: value for key, value in merged.items()
              if key in _REPORT_PARAMETERS}

    return fi.build_quality_report(**kwargs)


def failed_checks(report: pd.DataFrame) -> set[str]:
    return set(report.loc[~report["passed"], "check"])


# --- Training-demand validation -----------------------------------------


def test_validate_training_demand_accepts_valid_data() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "store_id": [1, 1],
            "quantity": [100.0, 120.0],
        }
    )

    validate_training_demand(data)


def test_validate_training_demand_rejects_missing_quantity() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "store_id": [1, 1],
            "quantity": [100.0, np.nan],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_rejects_negative_quantity() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "store_id": [1, 1],
            "quantity": [100.0, -1.0],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_rejects_duplicate_store_date() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "store_id": [1, 1],
            "quantity": [100.0, 120.0],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_rejects_missing_columns() -> None:
    data = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"])})

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_rejects_empty_frame() -> None:
    data = pd.DataFrame(
        {"date": pd.to_datetime([]), "store_id": [], "quantity": []}
    )

    with pytest.raises(ValueError):
        validate_training_demand(data)


def test_validate_training_demand_checks_expected_stores() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "store_id": [1],
            "quantity": [100.0],
        }
    )

    with pytest.raises(ValueError):
        validate_training_demand(data, expected_stores={1, 2})

    validate_training_demand(data, expected_stores={1})


# --- Densification ------------------------------------------------------


def test_densify_store_days_fills_gap_with_zero() -> None:
    observed = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-04"]
            ),
            "store_id": [1, 1, 1],
            "quantity": [10.0, 20.0, 40.0],
        }
    )

    densified = densify_store_days(observed)

    assert len(densified) == 4
    assert densified["quantity"].tolist() == [10.0, 20.0, 0.0, 40.0]
    assert densified["is_synthetic"].tolist() == [False, False, True, False]


def test_densify_store_days_preserves_total_quantity() -> None:
    observed = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-05"]
            ),
            "store_id": [1, 1, 1],
            "quantity": [10.0, 20.0, 40.0],
        }
    )

    densified = densify_store_days(observed)

    assert densified["quantity"].sum() == pytest.approx(70.0)


def test_densify_store_days_uses_each_store_own_bounds() -> None:
    observed = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-03", "2024-01-10", "2024-01-12"]
            ),
            "store_id": [1, 1, 2, 2],
            "quantity": [1.0, 3.0, 10.0, 12.0],
        }
    )

    densified = densify_store_days(observed)

    store_one = densified[densified["store_id"] == 1]
    store_two = densified[densified["store_id"] == 2]

    assert len(store_one) == 3
    assert len(store_two) == 3
    assert store_one["date"].min() == pd.Timestamp("2024-01-01")
    assert store_two["date"].min() == pd.Timestamp("2024-01-10")


def test_densify_store_days_rejects_duplicate_dates() -> None:
    observed = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "store_id": [1, 1],
            "quantity": [1.0, 2.0],
        }
    )

    with pytest.raises(ValueError):
        densify_store_days(observed)


def test_densify_store_days_rejects_empty_frame() -> None:
    observed = pd.DataFrame(
        {"date": pd.to_datetime([]), "store_id": [], "quantity": []}
    )

    with pytest.raises(ValueError):
        densify_store_days(observed)


def test_summarize_densification_records_counts_and_dates() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03"]
            ),
            "store_id": [1, 1, 1],
            "quantity": [10.0, 0.0, 30.0],
            "is_synthetic": [False, True, False],
        }
    )

    summary = summarize_densification(data)

    assert int(summary.iloc[0]["observed_days"]) == 2
    assert int(summary.iloc[0]["densified_days"]) == 3
    assert int(summary.iloc[0]["synthetic_days"]) == 1
    assert summary.iloc[0]["synthetic_dates"] == "2024-01-02"


def test_summarize_densification_requires_flag() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "store_id": [1],
            "quantity": [10.0],
        }
    )

    with pytest.raises(ValueError):
        summarize_densification(data)


def test_workspace_densification_matches_phase11_expectation() -> None:
    """The fixture's single gap must land on the recorded Phase 11 day."""
    data, _ = fi.load_training_demand()

    summary = summarize_densification(data)

    gaps = summary[summary["synthetic_days"] > 0]

    assert len(gaps) == 1
    assert int(gaps.iloc[0]["store_id"]) == fi.EXPECTED_SYNTHETIC_STORE
    assert gaps.iloc[0]["synthetic_dates"] == fi.EXPECTED_SYNTHETIC_DATE


def test_load_training_demand_reconciles_source_totals(workspace) -> None:
    data, stats = fi.load_training_demand()

    assert stats.total_rows == workspace.source_total_rows
    assert stats.total_quantity == pytest.approx(
        workspace.source_total_quantity
    )
    assert stats.split_rows["train"] == workspace.source_train_rows
    assert stats.split_rows["validation"] == workspace.source_validation_rows
    assert stats.split_rows["test"] == workspace.source_test_rows


def test_load_training_demand_is_training_only(workspace) -> None:
    data, _ = fi.load_training_demand()

    assert data["date"].max() == fi.TRAIN_END
    assert data["date"].min() == fi.TRAIN_START
    assert not data.duplicated(["date", "store_id"]).any()


# --- Descriptive statistics ---------------------------------------------


def test_demand_summary_columns_and_values() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
            ),
            "store_id": [1, 1, 1, 1],
            "quantity": [10.0, 20.0, 30.0, 40.0],
            "is_synthetic": [False] * 4,
        }
    )

    summary = calculate_demand_summary(data)

    assert summary.columns.tolist() == [
        "store_id",
        "training_days",
        "total_quantity",
        "mean_daily_demand",
        "median_daily_demand",
        "min_daily_demand",
        "max_daily_demand",
        "coefficient_of_variation",
    ]

    row = summary.iloc[0]

    assert int(row["training_days"]) == 4
    assert row["total_quantity"] == pytest.approx(100.0)
    assert row["mean_daily_demand"] == pytest.approx(25.0)
    assert row["min_daily_demand"] == pytest.approx(10.0)
    assert row["max_daily_demand"] == pytest.approx(40.0)


def test_demand_summary_coefficient_of_variation_is_std_over_mean() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03"]
            ),
            "store_id": [1, 1, 1],
            "quantity": [10.0, 20.0, 30.0],
            "is_synthetic": [False] * 3,
        }
    )

    summary = calculate_demand_summary(data)

    expected = np.std([10.0, 20.0, 30.0], ddof=1) / 20.0

    assert summary.iloc[0]["coefficient_of_variation"] == pytest.approx(
        expected
    )


def test_demand_summary_counts_synthetic_day_but_keeps_zero_minimum() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03"]
            ),
            "store_id": [3, 3, 3],
            "quantity": [100.0, 0.0, 300.0],
            "is_synthetic": [False, True, False],
        }
    )

    summary = calculate_demand_summary(data)

    row = summary.iloc[0]

    assert int(row["training_days"]) == 3
    assert row["min_daily_demand"] == pytest.approx(0.0)
    assert row["total_quantity"] == pytest.approx(400.0)


def test_variability_summary_columns_and_ordering() -> None:
    data = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "store_id": [1] * 10,
            "quantity": [float(value) for value in range(1, 11)],
            "is_synthetic": [False] * 10,
        }
    )

    summary = calculate_variability_summary(data)

    assert summary.columns.tolist() == [
        "store_id",
        "mean_daily_demand",
        "std_daily_demand",
        "variance_daily_demand",
        "p90_daily_demand",
        "p95_daily_demand",
        "p99_daily_demand",
        "coefficient_of_variation",
    ]

    row = summary.iloc[0]

    assert row["p90_daily_demand"] <= row["p95_daily_demand"]
    assert row["p95_daily_demand"] <= row["p99_daily_demand"]
    assert row["variance_daily_demand"] == pytest.approx(
        row["std_daily_demand"] ** 2
    )
    assert row["coefficient_of_variation"] == pytest.approx(
        row["std_daily_demand"] / row["mean_daily_demand"]
    )


def test_variability_and_demand_summaries_agree_on_cv(workspace) -> None:
    data, _ = fi.load_training_demand()

    demand = calculate_demand_summary(data).set_index("store_id")
    variability = calculate_variability_summary(data).set_index("store_id")

    assert np.allclose(
        demand["coefficient_of_variation"].to_numpy(dtype=float),
        variability["coefficient_of_variation"].to_numpy(dtype=float),
    )


# --- Phase 12 model evidence --------------------------------------------


def test_model_evidence_one_row_per_store(workspace) -> None:
    selected, validation = fi.load_phase12_model_evidence()

    assert len(selected) == len(MODEL_DESIGN)
    assert not selected["store_id"].duplicated().any()
    assert set(selected["store_id"]) == set(validation["store_id"])


def test_model_evidence_requires_typed_configuration(
    workspace, monkeypatch, tmp_path
) -> None:
    selected = workspace.selected.drop(columns=["season_length"])

    path = tmp_path / "selected_no_season.csv"
    selected.to_csv(path, index=False)

    monkeypatch.setattr(fi, "SELECTED_MODEL_PATH", path)

    with pytest.raises(ValueError):
        fi.load_phase12_model_evidence()


def test_model_evidence_rejects_duplicate_store(
    workspace, monkeypatch, tmp_path
) -> None:
    selected = pd.concat(
        [workspace.selected, workspace.selected.iloc[[0]]],
        ignore_index=True,
    )

    path = tmp_path / "selected_duplicate.csv"
    selected.to_csv(path, index=False)

    monkeypatch.setattr(fi, "SELECTED_MODEL_PATH", path)

    with pytest.raises(ValueError):
        fi.load_phase12_model_evidence()


def test_model_evidence_rejects_model_disagreement(
    workspace, monkeypatch, tmp_path
) -> None:
    validation = workspace.validation.copy()
    validation.loc[validation["store_id"] == 1, "model"] = "naive"

    path = tmp_path / "validation_mismatch.csv"
    validation.to_csv(path, index=False)

    monkeypatch.setattr(fi, "VALIDATION_RESULTS_PATH", path)

    with pytest.raises(ValueError):
        fi.load_phase12_model_evidence()


def test_model_evidence_rejects_different_store_sets(
    workspace, monkeypatch, tmp_path
) -> None:
    validation = workspace.validation[workspace.validation["store_id"] != 4]

    path = tmp_path / "validation_missing_store.csv"
    validation.to_csv(path, index=False)

    monkeypatch.setattr(fi, "VALIDATION_RESULTS_PATH", path)

    with pytest.raises(ValueError):
        fi.load_phase12_model_evidence()


# --- Forecast errors ----------------------------------------------------


def test_forecast_errors_recompute_rmse_and_mape(workspace) -> None:
    _, validation = fi.load_phase12_model_evidence()

    errors = fi.load_phase12_forecast_errors(validation)

    merged = errors.merge(
        validation[["store_id", "rmse", "mape_percent"]], on="store_id"
    )

    assert np.allclose(merged["rmse_x"], merged["rmse_y"], rtol=1e-12)
    assert np.allclose(
        merged["mape_percent_x"], merged["mape_percent_y"], rtol=1e-12
    )


def test_forecast_errors_recover_bias_from_residuals(workspace) -> None:
    _, validation = fi.load_phase12_model_evidence()

    errors = fi.load_phase12_forecast_errors(validation).set_index("store_id")

    for store_id, design in VALIDATION_DESIGN.items():
        assert errors.loc[store_id, "bias"] == pytest.approx(design["error"])

    assert (errors["bias"] > 0).all()
    assert (errors["residual_std"] > 0).all()


def test_forecast_errors_cover_the_validation_window(workspace) -> None:
    _, validation = fi.load_phase12_model_evidence()

    errors = fi.load_phase12_forecast_errors(validation)

    assert (errors["observations"] == 114).all()
    assert (errors["validation_start"] == fi.VALIDATION_START).all()
    assert (errors["validation_end"] == fi.VALIDATION_END).all()


def test_forecast_errors_require_predictions(
    workspace, monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(fi, "PREDICTIONS_PATH", tmp_path / "missing.csv")

    _, validation = fi.load_phase12_model_evidence()

    with pytest.raises(FileNotFoundError):
        fi.load_phase12_forecast_errors(validation)


def test_forecast_errors_require_scope_column(
    workspace, monkeypatch, tmp_path
) -> None:
    predictions = workspace.predictions.drop(columns=["scope"])

    path = tmp_path / "predictions_no_scope.csv"
    predictions.to_csv(path, index=False)

    monkeypatch.setattr(fi, "PREDICTIONS_PATH", path)

    _, validation = fi.load_phase12_model_evidence()

    with pytest.raises(ValueError):
        fi.load_phase12_forecast_errors(validation)


def test_forecast_errors_reject_empty_validation_scope(
    workspace, monkeypatch, tmp_path
) -> None:
    predictions = workspace.predictions.assign(scope="cv_fold")

    path = tmp_path / "predictions_no_validation.csv"
    predictions.to_csv(path, index=False)

    monkeypatch.setattr(fi, "PREDICTIONS_PATH", path)

    _, validation = fi.load_phase12_model_evidence()

    with pytest.raises(ValueError):
        fi.load_phase12_forecast_errors(validation)


# --- Inventory scenarios ------------------------------------------------


def test_service_levels_have_expected_values() -> None:
    assert set(SERVICE_LEVELS) == {0.90, 0.95, 0.99}


def test_inventory_scenarios_calculate_reorder_point() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
            "season_length": [7.0],
            "order": [np.nan],
        }
    )

    scenarios = calculate_inventory_scenarios(variability, selected_models)

    scenario = scenarios[
        (scenarios["lead_time_days"] == 7)
        & (scenarios["service_level"] == 0.95)
    ].iloc[0]

    expected_lead_time_demand = 700.0

    expected_safety_stock = (
        SERVICE_LEVELS[0.95] * 10.0 * np.sqrt(7)
    )

    expected_reorder_point = (
        expected_lead_time_demand + expected_safety_stock
    )

    assert scenario["expected_lead_time_demand"] == pytest.approx(
        expected_lead_time_demand
    )

    assert scenario["safety_stock"] == pytest.approx(expected_safety_stock)

    assert scenario["reorder_point"] == pytest.approx(expected_reorder_point)


def test_inventory_scenarios_include_all_lead_time_scenarios() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
            "season_length": [7.0],
            "order": [np.nan],
        }
    )

    scenarios = calculate_inventory_scenarios(variability, selected_models)

    assert sorted(scenarios["lead_time_days"].unique()) == [7, 14, 28]
    assert sorted(scenarios["service_level"].unique()) == [0.90, 0.95, 0.99]
    assert len(scenarios) == 9


def test_longer_lead_time_increases_expected_demand() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
            "season_length": [7.0],
            "order": [np.nan],
        }
    )

    scenarios = calculate_inventory_scenarios(variability, selected_models)

    expected = (
        scenarios[scenarios["service_level"] == 0.95]
        .sort_values("lead_time_days")["expected_lead_time_demand"]
        .tolist()
    )

    assert expected == [700.0, 1400.0, 2800.0]


def test_higher_service_level_increases_safety_stock() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [1],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
            "season_length": [7.0],
            "order": [np.nan],
        }
    )

    scenarios = calculate_inventory_scenarios(variability, selected_models)

    values = (
        scenarios[scenarios["lead_time_days"] == 7]
        .sort_values("service_level")["safety_stock"]
        .tolist()
    )

    assert values[0] < values[1] < values[2]


def test_store_without_selected_model_is_descriptive_only() -> None:
    variability = pd.DataFrame(
        {
            "store_id": [4],
            "mean_daily_demand": [100.0],
            "std_daily_demand": [10.0],
            "coefficient_of_variation": [0.1],
        }
    )

    selected_models = pd.DataFrame(
        {
            "store_id": [1],
            "model": ["seasonal_naive"],
            "configuration": ["season_length=7"],
            "season_length": [7.0],
            "order": [np.nan],
        }
    )

    scenarios = calculate_inventory_scenarios(variability, selected_models)

    assert scenarios.iloc[0]["model"] == "descriptive_only"
    assert scenarios.iloc[0]["season_length"] is None or pd.isna(
        scenarios.iloc[0]["season_length"]
    )


def test_historical_scenarios_carry_typed_configuration(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["scenarios"]

    assert {"season_length", "order"}.issubset(scenarios.columns)

    store_four = scenarios[scenarios["store_id"] == 4].iloc[0]

    assert store_four["model"] == "seasonal_naive"
    assert float(store_four["season_length"]) == 7.0


# --- Forecast-driven scenarios ------------------------------------------


def test_forecast_scenarios_use_bias_adjusted_level(workspace) -> None:
    bundle = compute_bundle()

    errors = bundle["errors"].set_index("store_id")

    scenarios = bundle["forecast_scenarios"]

    for store_id, row in errors.iterrows():
        subset = scenarios[scenarios["store_id"] == store_id]

        assert np.allclose(
            subset["bias_adjusted_daily_demand"].to_numpy(dtype=float),
            float(row["mean_predicted"]) + float(row["bias"]),
        )

        assert np.allclose(
            subset["model_daily_demand"].to_numpy(dtype=float),
            float(row["mean_predicted"]),
        )


def test_forecast_scenarios_recover_validation_mean(workspace) -> None:
    """The bias-adjusted level is the realised validation mean by identity."""
    bundle = compute_bundle()

    errors = bundle["errors"].set_index("store_id")

    scenarios = bundle["forecast_scenarios"]

    for store_id, row in errors.iterrows():
        subset = scenarios[scenarios["store_id"] == store_id]

        assert np.allclose(
            subset["bias_adjusted_daily_demand"].to_numpy(dtype=float),
            float(row["mean_actual"]),
        )


def test_forecast_scenarios_use_realised_error_not_historical_spread(
    workspace,
) -> None:
    bundle = compute_bundle()

    errors = bundle["errors"].set_index("store_id")
    variability = bundle["variability"].set_index("store_id")

    scenarios = bundle["forecast_scenarios"]

    for store_id in errors.index:
        subset = scenarios[scenarios["store_id"] == store_id]

        assert np.allclose(
            subset["residual_std"].to_numpy(dtype=float),
            float(errors.loc[store_id, "residual_std"]),
        )

        assert not np.isclose(
            float(errors.loc[store_id, "residual_std"]),
            float(variability.loc[store_id, "std_daily_demand"]),
        )


def test_forecast_scenarios_safety_stock_uses_error_basis(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["forecast_scenarios"]

    scenario = scenarios[
        (scenarios["lead_time_days"] == 14)
        & (scenarios["service_level"] == 0.95)
    ].iloc[0]

    expected = (
        SERVICE_LEVELS[0.95]
        * scenario["residual_std"]
        * np.sqrt(14)
    )

    assert scenario["safety_stock"] == pytest.approx(expected)


def test_forecast_scenarios_cover_every_store_and_scenario(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["forecast_scenarios"]

    assert sorted(scenarios["store_id"].unique()) == sorted(MODEL_DESIGN)
    assert len(scenarios) == 36
    assert (scenarios["reorder_point"] >= 0).all()


def test_forecast_scenarios_reorder_point_formula(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["forecast_scenarios"]

    assert np.allclose(
        scenarios["reorder_point"],
        scenarios["expected_lead_time_demand"] + scenarios["safety_stock"],
        rtol=1e-9,
    )


# --- Insights and findings ----------------------------------------------


def test_build_model_lines_one_line_per_store(workspace) -> None:
    bundle = compute_bundle()

    lines = bundle["model_lines"]

    assert len(lines) == len(MODEL_DESIGN)

    for store_id in MODEL_DESIGN:
        assert any(line.startswith(f"Store {store_id}:") for line in lines)

    assert any("seasonal_naive" in line for line in lines)
    assert any("feature_gbm" in line for line in lines)


def test_insights_cover_every_insight_type(workspace) -> None:
    bundle = compute_bundle()

    insights = bundle["insights"]

    assert set(insights["insight_type"]) == set(fi.INSIGHT_TYPES)
    assert len(insights) == len(fi.INSIGHT_TYPES) + 6


def test_insights_distinguish_rmse_from_relative_error(workspace) -> None:
    """The cross-store comparison must not rest on scale-bound RMSE."""
    bundle = compute_bundle()

    insights = bundle["insights"].set_index("insight_type")

    rmse_insight = insights.loc["lowest_validation_rmse"]
    mape_insight = insights.loc["lowest_relative_validation_error"]

    assert "scale-bound" in rmse_insight["interpretation"]
    assert "MAPE" in mape_insight["interpretation"]

    # The fixture is designed so the two metrics point at different stores.
    assert rmse_insight["store_id"] != mape_insight["store_id"]


def test_insights_report_largest_under_forecast(workspace) -> None:
    bundle = compute_bundle()

    insights = bundle["insights"].set_index("insight_type")

    bias_insight = insights.loc["systematic_bias"]

    errors = bundle["errors"].set_index("store_id")

    assert bias_insight["store_id"] == int(errors["bias"].idxmax())
    assert bias_insight["value"] == pytest.approx(errors["bias"].max())


def test_findings_report_state_every_selected_model(workspace) -> None:
    bundle = compute_bundle()

    text = bundle["findings_text"]

    for line in bundle["model_lines"]:
        assert line in text


def test_findings_report_drops_the_false_untuned_claim(workspace) -> None:
    """The stale artifact asserted store 4 had no tuned Phase 12 model."""
    bundle = compute_bundle()

    text = bundle["findings_text"]

    assert "Store 4 has no Phase 12 tuned" not in text
    assert "has no Phase 12 tuned" not in text
    assert "Store 4: seasonal_naive" in text


def test_findings_report_records_the_demand_basis(workspace) -> None:
    bundle = compute_bundle()

    text = bundle["findings_text"]

    assert "Training store-days after densification" in text
    assert "zero-filled 1" in text
    assert "NOT a forward forecast" in text


def test_findings_report_lists_both_scenario_families(workspace) -> None:
    bundle = compute_bundle()

    text = bundle["findings_text"]

    assert "historical-variability basis" in text
    assert "forecast-error basis" in text


# --- Quality report -----------------------------------------------------


def test_quality_report_passes_for_the_fixture(workspace) -> None:
    bundle = compute_bundle()

    report = report_for(bundle)

    assert report["passed"].all()
    assert len(report) == 43


def test_quality_report_has_no_duplicate_checks(workspace) -> None:
    bundle = compute_bundle()

    report = report_for(bundle)

    assert not report["check"].duplicated().any()


def test_quality_report_flags_source_row_mismatch(workspace) -> None:
    bundle = compute_bundle()

    stats = fi.SourceStats(**vars(bundle["stats"]))
    stats.total_rows -= 1

    report = report_for(bundle, stats=stats)

    assert "source_rows_reconciled" in failed_checks(report)


def test_quality_report_flags_training_quantity_mismatch(workspace) -> None:
    bundle = compute_bundle()

    stats = fi.SourceStats(**vars(bundle["stats"]))
    stats.split_quantity["train"] -= 1.0

    report = report_for(bundle, stats=stats)

    assert "training_quantity_reconciled" in failed_checks(report)


def test_quality_report_flags_data_extending_into_the_test_period(
    workspace,
) -> None:
    bundle = compute_bundle()

    data = bundle["data"].copy()
    extra = data.iloc[[0]].copy()
    extra["date"] = fi.TEST_START
    data = pd.concat([data, extra], ignore_index=True)

    report = report_for(bundle, data=data)

    assert "test_period_excluded" in failed_checks(report)
    assert "trains_on_training_window_only" in failed_checks(report)


def test_quality_report_flags_densification_drift(workspace) -> None:
    bundle = compute_bundle()

    densification = bundle["densification"].copy()
    target = densification["store_id"] == fi.EXPECTED_SYNTHETIC_STORE
    densification.loc[target, "synthetic_days"] = 0
    densification.loc[target, "synthetic_dates"] = ""

    report = report_for(bundle, densification=densification)

    assert "densification_synthetic_day_count" in failed_checks(report)
    assert "densification_matches_phase11" in failed_checks(report)


def test_quality_report_flags_rmse_disagreement_with_phase12(
    workspace,
) -> None:
    bundle = compute_bundle()

    validation = bundle["validation"].copy()
    validation.loc[0, "rmse"] = validation.loc[0, "rmse"] + 1.0

    report = report_for(bundle, validation=validation)

    assert "forecast_rmse_reproduced" in failed_checks(report)


def test_quality_report_flags_bias_that_is_not_under_forecast(
    workspace,
) -> None:
    bundle = compute_bundle()

    errors = bundle["errors"].copy()
    errors.loc[0, "bias"] = -1.0

    report = report_for(bundle, errors=errors)

    assert "under_forecast_bias_positive" in failed_checks(report)
    assert "error_analysis_bias_reconciles" in failed_checks(report)


def test_quality_report_flags_broken_reorder_point_formula(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["scenarios"].copy()
    scenarios.loc[0, "reorder_point"] = 0.0

    report = report_for(bundle, scenarios=scenarios)

    assert "reorder_point_formula_holds" in failed_checks(report)
    assert "reorder_point_covers_lead_time_demand" in failed_checks(report)


def test_quality_report_flags_non_monotonic_safety_stock(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["scenarios"].copy()

    mask = (
        (scenarios["store_id"] == 1)
        & (scenarios["lead_time_days"] == 7)
        & (scenarios["service_level"] == 0.99)
    )

    scenarios.loc[mask, "safety_stock"] = 0.0

    report = report_for(bundle, scenarios=scenarios)

    assert "safety_stock_monotonic_in_service_level" in failed_checks(report)


def test_quality_report_flags_non_monotonic_lead_time_demand(
    workspace,
) -> None:
    bundle = compute_bundle()

    scenarios = bundle["scenarios"].copy()
    scenarios.loc[scenarios["lead_time_days"] == 28, "expected_lead_time_demand"] = 0.0

    report = report_for(bundle, scenarios=scenarios)

    assert "lead_time_demand_monotonic" in failed_checks(report)


def test_quality_report_flags_negative_safety_stock(workspace) -> None:
    bundle = compute_bundle()

    forecast_scenarios = bundle["forecast_scenarios"].copy()
    forecast_scenarios.loc[0, "safety_stock"] = -1.0

    report = report_for(bundle, forecast_scenarios=forecast_scenarios)

    assert "safety_stock_non_negative" in failed_checks(report)


def test_quality_report_flags_wrong_forecast_level(workspace) -> None:
    bundle = compute_bundle()

    forecast_scenarios = bundle["forecast_scenarios"].copy()
    forecast_scenarios.loc[0, "model_daily_demand"] = 0.0

    report = report_for(bundle, forecast_scenarios=forecast_scenarios)

    assert "forecast_level_is_bias_corrected" in failed_checks(report)


def test_quality_report_flags_incomplete_scenario_coverage(workspace) -> None:
    bundle = compute_bundle()

    scenarios = bundle["scenarios"].iloc[:-1].copy()

    report = report_for(bundle, scenarios=scenarios)

    assert "historical_scenario_coverage_complete" in failed_checks(report)


def test_quality_report_flags_missing_insight_type(workspace) -> None:
    bundle = compute_bundle()

    insights = bundle["insights"]
    insights = insights[insights["insight_type"] != "systematic_bias"]

    report = report_for(bundle, insights=insights)

    assert "insight_types_complete" in failed_checks(report)


def test_quality_report_flags_findings_missing_a_model(workspace) -> None:
    bundle = compute_bundle()

    report = report_for(bundle, findings_text="No store lines here.")

    assert "findings_state_every_selected_model" in failed_checks(report)


def test_quality_report_flags_the_stale_untuned_claim(workspace) -> None:
    bundle = compute_bundle()

    findings = (
        bundle["findings_text"]
        + "\n- Store 4 has no Phase 12 tuned forecasting configuration.\n"
    )

    report = report_for(bundle, findings_text=findings)

    assert "findings_no_false_untuned_claim" in failed_checks(report)


def test_quality_report_flags_model_selection_mismatch(workspace) -> None:
    bundle = compute_bundle()

    validation = bundle["validation"].copy()
    validation.loc[validation["store_id"] == 1, "model"] = "naive"

    report = report_for(bundle, validation=validation)

    assert "model_selection_matches_validation" in failed_checks(report)


def test_quality_report_flags_validation_scope_drift(workspace) -> None:
    bundle = compute_bundle()

    errors = bundle["errors"].copy()
    errors.loc[0, "validation_start"] = fi.TEST_START

    report = report_for(bundle, errors=errors)

    assert "validation_evidence_scoped_to_validation_period" in failed_checks(
        report
    )


# --- Workflow -----------------------------------------------------------


def test_main_writes_all_artifacts(workspace) -> None:
    fi.main()

    for name in (
        "DEMAND_SUMMARY_PATH",
        "VARIABILITY_PATH",
        "DENSIFICATION_PATH",
        "SCENARIOS_PATH",
        "FORECAST_SCENARIOS_PATH",
        "FORECAST_ERROR_PATH",
        "INSIGHTS_PATH",
        "FINDINGS_PATH",
        "QUALITY_REPORT_PATH",
    ):
        path = getattr(fi, name)

        assert path.exists(), name

    report = pd.read_csv(fi.QUALITY_REPORT_PATH)

    assert report["passed"].all()

    findings = fi.FINDINGS_PATH.read_text(encoding="utf-8")

    assert findings.rstrip().endswith("Quality report: all checks passed")


def test_main_writes_the_derived_store_mapping(workspace) -> None:
    fi.main()

    scenarios = pd.read_csv(fi.SCENARIOS_PATH)

    store_four = scenarios[scenarios["store_id"] == 4].iloc[0]

    assert store_four["model"] == "seasonal_naive"

    findings = fi.FINDINGS_PATH.read_text(encoding="utf-8")

    assert "Store 4: seasonal_naive" in findings
    assert "descriptive_only" not in findings


def test_main_outputs_are_deterministic(workspace) -> None:
    fi.main()

    first = pd.read_csv(fi.SCENARIOS_PATH)

    fi.main()

    second = pd.read_csv(fi.SCENARIOS_PATH)

    pd.testing.assert_frame_equal(first, second)


def test_main_missing_input_raises(workspace, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(fi, "INPUT_PATH", tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError):
        fi.main()


def test_main_raises_when_a_quality_check_fails(
    workspace, monkeypatch
) -> None:
    failing = pd.DataFrame(
        [
            {
                "check": "deliberate_failure",
                "passed": False,
                "actual": 1,
                "expected": 2,
            }
        ]
    )

    monkeypatch.setattr(fi, "build_quality_report", lambda **kwargs: failing)

    with pytest.raises(RuntimeError):
        fi.main()

    # The gate must run before any data artifact is written.
    assert not fi.DEMAND_SUMMARY_PATH.exists()
    assert not fi.FINDINGS_PATH.exists()

    # The report itself is still written, so the failure is diagnosable.
    assert fi.QUALITY_REPORT_PATH.exists()
