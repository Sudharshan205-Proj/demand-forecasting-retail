"""Tests for Phase 12 model evaluation and tuning."""

from __future__ import annotations

from types import SimpleNamespace
from unittest import mock

import numpy as np
import pandas as pd
import pytest

import scripts.evaluate_and_tune_models as et
from scripts.evaluate_and_tune_models import (
    CV_FOLDS,
    CV_HORIZON,
    FEATURE_COLUMNS,
    FEATURE_MODEL,
    MIN_TRAIN_OBSERVATIONS,
    ModelConfiguration,
    build_configurations,
    build_feature_frame,
    configuration_fields,
    configuration_key,
    create_cv_folds,
    create_error_analysis,
    create_quality_report,
    evaluate_forecast,
    feature_forecast,
    forecast_configuration,
    mape,
    naive_forecast,
    rmse,
    run_cross_validation,
    seasonal_naive_forecast,
    select_configurations,
    summarize_cv_results,
    validate_splits,
)

FIXTURE_START = "2023-09-23"
FIXTURE_END = "2024-09-26"

_WORKFLOW_CACHE: dict[tuple[int, ...], SimpleNamespace] = {}


def make_daily_frame(stores: tuple[int, ...] = (1,)) -> pd.DataFrame:
    """Create a small deterministic store-day frame spanning the real splits."""
    dates = pd.date_range(FIXTURE_START, FIXTURE_END, freq="D")

    records = []

    for store_id in stores:
        for position, date in enumerate(dates):
            if date <= et.TRAIN_END:
                split = "train"
            elif date <= et.VALIDATION_END:
                split = "validation"
            else:
                split = "test"

            records.append(
                {
                    "date": date,
                    "store_id": store_id,
                    "quantity": (
                        100.0
                        + (position % 7) * 5
                        + position * 0.1
                        + store_id * 10
                    ),
                    "split": split,
                }
            )

    return pd.DataFrame(records)


def make_train_series(observations: int) -> pd.Series:
    """Create a regular daily series with a fixed training length."""
    index = pd.date_range("2023-06-01", periods=observations, freq="D")

    series = pd.Series(
        100.0 + np.arange(observations, dtype=float) * 0.5,
        index=index,
    )
    series.index.freq = "D"

    return series


def build_quality(workflow: SimpleNamespace, **overrides) -> pd.DataFrame:
    """Build a quality report for a workflow, allowing targeted corruption."""
    arguments = {
        "data": workflow.data,
        "source_facts": workflow.source_facts,
        "configurations": workflow.configurations,
        "cv_results": workflow.cv_results,
        "skipped": workflow.skipped,
        "cv_summary": workflow.cv_summary,
        "selected": workflow.selected,
        "validation_results": workflow.validation_results,
        "error_analysis": workflow.error_analysis,
        "predictions": workflow.predictions,
    }
    arguments.update(overrides)

    with mock.patch.object(
        et, "EXPECTED_STORES", workflow.store_count
    ):
        return create_quality_report(**arguments)


def get_workflow(stores: tuple[int, ...] = (1,)) -> SimpleNamespace:
    """Build (and cache) the complete Phase 12 workflow on a fixture."""
    if stores in _WORKFLOW_CACHE:
        return _WORKFLOW_CACHE[stores]

    data = make_daily_frame(stores)
    source_facts = {
        "rows": float(len(data)),
        "quantity": float(data["quantity"].sum()),
    }

    configurations = build_configurations()
    registry = {
        configuration_key(configuration): configuration
        for configuration in configurations
    }

    cv_results, skipped, cv_predictions = run_cross_validation(
        data, configurations
    )
    cv_summary = summarize_cv_results(cv_results)
    selected = select_configurations(cv_summary)
    validation_results, validation_predictions = (
        et.evaluate_selected_on_validation(data, selected, registry)
    )
    error_analysis = create_error_analysis(validation_predictions)

    predictions = pd.concat(
        [cv_predictions, validation_predictions],
        ignore_index=True,
    )

    workflow = SimpleNamespace(
        data=data,
        source_facts=source_facts,
        configurations=configurations,
        registry=registry,
        cv_results=cv_results,
        skipped=skipped,
        cv_summary=cv_summary,
        selected=selected,
        validation_results=validation_results,
        validation_predictions=validation_predictions,
        error_analysis=error_analysis,
        predictions=predictions,
        store_count=len(stores),
    )

    workflow.quality = build_quality(workflow)

    _WORKFLOW_CACHE[stores] = workflow

    return workflow


def check_row(report: pd.DataFrame, name: str) -> pd.Series:
    """Return the quality-report row for a named check."""
    return report.loc[report["check"] == name].iloc[0]


# --- Metrics -----------------------------------------------------------


def test_rmse_is_zero_for_perfect_predictions() -> None:
    assert rmse(pd.Series([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0])) == 0.0


def test_rmse_calculates_expected_value() -> None:
    actual = pd.Series([1.0, 2.0])
    predicted = np.array([2.0, 4.0])

    assert rmse(actual, predicted) == pytest.approx(np.sqrt(2.5))


def test_rmse_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        rmse(pd.Series([1.0, 2.0]), np.array([1.0]))


def test_rmse_rejects_empty_forecast() -> None:
    with pytest.raises(ValueError):
        rmse(np.array([]), np.array([]))


def test_mape_excludes_zero_actual_values() -> None:
    actual = pd.Series([0.0, 100.0])
    predicted = np.array([50.0, 110.0])

    assert mape(actual, predicted) == pytest.approx(10.0)


def test_mape_returns_nan_for_all_zero_actuals() -> None:
    actual = pd.Series([0.0, 0.0])
    predicted = np.array([1.0, 2.0])

    assert np.isnan(mape(actual, predicted))


def test_mape_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        mape(pd.Series([1.0, 2.0]), np.array([1.0]))


def test_evaluate_forecast_returns_both_metrics() -> None:
    result = evaluate_forecast(
        pd.Series([10.0, 20.0]),
        np.array([10.0, 20.0]),
    )

    assert result == (0.0, 0.0)


# --- Forecast primitives ----------------------------------------------


def test_naive_forecast_repeats_last_value() -> None:
    forecast = naive_forecast(pd.Series([10.0, 20.0, 30.0]), 3)

    assert forecast.tolist() == [30.0, 30.0, 30.0]


def test_naive_forecast_rejects_empty_history() -> None:
    with pytest.raises(ValueError):
        naive_forecast(pd.Series(dtype=float), 3)


def test_naive_forecast_rejects_non_positive_horizon() -> None:
    with pytest.raises(ValueError):
        naive_forecast(pd.Series([1.0, 2.0]), 0)


def test_seasonal_naive_repeats_pattern() -> None:
    history = pd.Series([1.0, 2.0, 3.0, 4.0])

    forecast = seasonal_naive_forecast(
        history,
        horizon=6,
        season_length=2,
    )

    assert forecast.tolist() == [3.0, 4.0, 3.0, 4.0, 3.0, 4.0]


def test_seasonal_naive_rejects_insufficient_history() -> None:
    with pytest.raises(ValueError):
        seasonal_naive_forecast(
            pd.Series([1.0, 2.0]),
            horizon=3,
            season_length=7,
        )


def test_seasonal_naive_rejects_non_positive_horizon() -> None:
    with pytest.raises(ValueError):
        seasonal_naive_forecast(
            pd.Series([1.0] * 7),
            horizon=0,
            season_length=7,
        )


# --- Feature engineering at the store-day grain ------------------------


def test_feature_frame_contains_every_feature() -> None:
    frame = build_feature_frame(make_train_series(60))

    assert set(FEATURE_COLUMNS).issubset(frame.columns)
    assert len(FEATURE_COLUMNS) == 16


def test_feature_lag_1_matches_previous_observation() -> None:
    series = make_train_series(40)

    frame = build_feature_frame(series)

    values = series.to_numpy(dtype=float)
    expected = np.concatenate([[np.nan], values[:-1]])

    assert np.allclose(
        frame["lag_1"].to_numpy(dtype=float),
        expected,
        equal_nan=True,
    )


def test_feature_rolling_excludes_current_observation() -> None:
    series = make_train_series(40)

    frame = build_feature_frame(series)

    values = series.to_numpy(dtype=float)

    for position in range(1, 12):
        expected = float(np.mean(values[max(0, position - 7):position]))
        assert frame["rolling_mean_7"].iloc[position] == pytest.approx(
            expected
        )


def test_feature_target_is_preserved() -> None:
    series = make_train_series(40)

    frame = build_feature_frame(series)

    assert np.allclose(
        frame["quantity"].to_numpy(dtype=float),
        series.to_numpy(dtype=float),
    )


def test_feature_series_age_starts_at_zero() -> None:
    frame = build_feature_frame(make_train_series(10))

    assert frame["series_age_days"].iloc[0] == 0
    assert frame["series_age_days"].iloc[-1] == 9


def test_feature_forecast_returns_requested_horizon() -> None:
    forecast = feature_forecast(make_train_series(120), 28)

    assert forecast.shape == (28,)
    assert np.all(np.isfinite(forecast))


def test_feature_forecast_is_deterministic() -> None:
    history = make_train_series(120)

    first = feature_forecast(history, 14)
    second = feature_forecast(history, 14)

    assert np.array_equal(first, second)


def test_feature_forecast_rejects_empty_history() -> None:
    with pytest.raises(ValueError):
        feature_forecast(pd.Series(dtype=float), 3)


def test_feature_forecast_rejects_non_positive_horizon() -> None:
    with pytest.raises(ValueError):
        feature_forecast(make_train_series(40), 0)


# --- Typed configuration dispatch --------------------------------------


def test_configuration_fields_are_explicit() -> None:
    configuration = ModelConfiguration(
        model="arima",
        configuration="order=(1, 1, 1)",
        order=(1, 1, 1),
    )

    fields = configuration_fields(configuration)

    assert fields == {"season_length": "", "order": "(1, 1, 1)"}


def test_configuration_key_is_stable() -> None:
    configuration = ModelConfiguration(
        model="seasonal_naive",
        configuration="season_length=7",
        season_length=7,
    )

    assert configuration_key(configuration) == (
        "seasonal_naive",
        "season_length=7",
    )


def test_dispatch_routes_naive() -> None:
    configuration = ModelConfiguration(
        model="naive", configuration="last observed value"
    )

    result = forecast_configuration(
        pd.Series([1.0, 2.0]), 2, configuration
    )

    assert result.tolist() == [2.0, 2.0]


def test_dispatch_requires_season_length() -> None:
    configuration = ModelConfiguration(
        model="seasonal_naive", configuration="missing"
    )

    with pytest.raises(ValueError):
        forecast_configuration(pd.Series([1.0] * 10), 2, configuration)


def test_dispatch_requires_order() -> None:
    configuration = ModelConfiguration(model="arima", configuration="missing")

    with pytest.raises(ValueError):
        forecast_configuration(pd.Series([1.0] * 10), 2, configuration)


def test_dispatch_rejects_unknown_model() -> None:
    configuration = ModelConfiguration(model="mystery", configuration="x")

    with pytest.raises(ValueError):
        forecast_configuration(pd.Series([1.0] * 10), 2, configuration)


def test_build_configurations_covers_every_family() -> None:
    configurations = build_configurations()

    assert {configuration.model for configuration in configurations} == {
        "naive",
        "seasonal_naive",
        "arima",
        FEATURE_MODEL,
    }
    assert len(configurations) == 9


# --- Cross-validation folds --------------------------------------------


def test_cv_folds_use_requested_count_when_affordable() -> None:
    folds = create_cv_folds(make_train_series(400))

    assert len(folds) == CV_FOLDS

    for history, actual in folds:
        assert len(actual) == CV_HORIZON


def test_cv_folds_adapt_to_short_history() -> None:
    """A 60-observation store can still be tuned with one fold."""
    folds = create_cv_folds(make_train_series(60))

    assert len(folds) == 1
    assert len(folds[0][0]) == 60 - CV_HORIZON
    assert len(folds[0][1]) == CV_HORIZON
    assert len(folds[0][0]) >= MIN_TRAIN_OBSERVATIONS


def test_cv_folds_reduce_count_when_history_is_limited() -> None:
    folds = create_cv_folds(make_train_series(84))

    assert len(folds) == min(CV_FOLDS, (84 - MIN_TRAIN_OBSERVATIONS) // CV_HORIZON)


def test_cv_folds_preserve_temporal_order() -> None:
    for history, actual in create_cv_folds(make_train_series(400)):
        assert history.index.max() < actual.index.min()


def test_cv_folds_expand() -> None:
    folds = create_cv_folds(make_train_series(400))

    lengths = [len(history) for history, _ in folds]

    assert lengths == sorted(lengths)
    assert len(set(lengths)) == len(lengths)


def test_cv_folds_reject_series_too_short() -> None:
    with pytest.raises(ValueError):
        create_cv_folds(make_train_series(30))


def test_cv_folds_reject_invalid_arguments() -> None:
    with pytest.raises(ValueError):
        create_cv_folds(make_train_series(400), horizon=0)

    with pytest.raises(ValueError):
        create_cv_folds(make_train_series(400), min_train=0)

    with pytest.raises(ValueError):
        create_cv_folds(make_train_series(400), folds=0)


# --- Split validation ---------------------------------------------------


def test_validate_splits_accepts_chronological_data() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03"]
            ),
            "store_id": [1, 1, 1],
            "quantity": [1.0, 2.0, 3.0],
            "split": ["train", "validation", "test"],
        }
    )

    validate_splits(data)


def test_validate_splits_rejects_temporal_leakage() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-03", "2024-01-01", "2024-01-02"]
            ),
            "store_id": [1, 1, 1],
            "quantity": [1.0, 2.0, 3.0],
            "split": ["train", "validation", "test"],
        }
    )

    with pytest.raises(ValueError):
        validate_splits(data)


def test_validate_splits_rejects_duplicate_store_day() -> None:
    data = make_daily_frame((1,))
    data = pd.concat([data, data.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError):
        validate_splits(data)


# --- Tuning behaviour ---------------------------------------------------


def test_cross_validation_covers_every_store_and_records_windows() -> None:
    workflow = get_workflow()

    assert workflow.skipped.empty
    assert sorted(workflow.cv_results["store_id"].unique()) == [1]
    assert set(workflow.cv_results["status"]) == {"success"}
    assert workflow.cv_results["horizon"].unique().tolist() == [CV_HORIZON]

    for row in workflow.cv_results.itertuples(index=False):
        assert row.fold_train_end < row.fold_test_start
        assert row.fold_train_start == pd.Timestamp(FIXTURE_START).date()


def test_cross_validation_records_skipped_stores_with_a_reason() -> None:
    """A store that cannot support a single fold is recorded, not dropped."""
    data = pd.concat(
        [
            make_daily_frame((1,)),
            make_daily_frame((9,)).head(20),
        ],
        ignore_index=True,
    )

    _, skipped, _ = run_cross_validation(data, build_configurations())

    assert skipped["store_id"].tolist() == [9]
    assert skipped["reason"].str.contains("too short").all()
    assert (skipped["training_observations"] == 20).all()


def test_cross_validation_records_fold_predictions() -> None:
    workflow = get_workflow()

    expected_rows = len(workflow.cv_results) * CV_HORIZON

    assert len(workflow.predictions[
        workflow.predictions["scope"] == "cv_fold"
    ]) == expected_rows


def test_summary_aggregates_cv_folds() -> None:
    workflow = get_workflow()

    for row in workflow.cv_summary.itertuples(index=False):
        group = workflow.cv_results[
            (workflow.cv_results["store_id"] == row.store_id)
            & (workflow.cv_results["model"] == row.model)
            & (workflow.cv_results["configuration"] == row.configuration)
        ]

        assert row.cv_folds == len(group)
        assert row.mean_rmse == pytest.approx(group["rmse"].mean())


def test_select_configurations_chooses_lowest_cv_rmse() -> None:
    summary = pd.DataFrame(
        {
            "store_id": [1, 1, 1, 2],
            "model": ["naive", "seasonal_naive", "arima", "naive"],
            "configuration": ["a", "b", "c", "d"],
            "season_length": ["", 7, "", ""],
            "order": ["", "", "(1, 1, 1)", ""],
            "cv_folds": [3, 3, 3, 3],
            "mean_rmse": [100.0, 50.0, 75.0, 20.0],
            "mean_mape_percent": [20.0, 10.0, 15.0, 5.0],
            "median_rmse": [100.0, 50.0, 75.0, 20.0],
            "median_mape_percent": [20.0, 10.0, 15.0, 5.0],
        }
    )

    selected = select_configurations(summary)

    store_one = selected[selected["store_id"] == 1].iloc[0]

    assert store_one["model"] == "seasonal_naive"
    assert store_one["configuration"] == "b"
    assert len(selected) == 2


def test_select_configurations_breaks_ties_on_mape() -> None:
    summary = pd.DataFrame(
        {
            "store_id": [1, 1],
            "model": ["a", "b"],
            "configuration": ["x", "y"],
            "season_length": ["", ""],
            "order": ["", ""],
            "cv_folds": [3, 3],
            "mean_rmse": [10.0, 10.0],
            "mean_mape_percent": [9.0, 5.0],
            "median_rmse": [10.0, 10.0],
            "median_mape_percent": [9.0, 5.0],
        }
    )

    selected = select_configurations(summary)

    assert selected.iloc[0]["configuration"] == "y"


def test_selected_configurations_resolve_without_parsing() -> None:
    workflow = get_workflow()

    for row in workflow.selected.to_dict("records"):
        key = (str(row["model"]), str(row["configuration"]))
        assert key in workflow.registry


def test_validation_evaluation_reproduces_selected_forecast() -> None:
    workflow = get_workflow()

    for row in workflow.validation_results.itertuples(index=False):
        group = workflow.validation_predictions[
            (workflow.validation_predictions["store_id"] == row.store_id)
            & (workflow.validation_predictions["model"] == row.model)
        ]

        assert len(group) == row.forecast_horizon
        assert rmse(
            group["actual"].to_numpy(dtype=float),
            group["predicted"].to_numpy(dtype=float),
        ) == pytest.approx(row.rmse, rel=1e-9)


def test_error_analysis_uses_stored_validation_predictions() -> None:
    workflow = get_workflow()

    assert len(workflow.error_analysis) == 2 * len(
        workflow.validation_results
    )

    for row in workflow.error_analysis.itertuples(index=False):
        assert np.isfinite(row.rmse)
        assert row.mean_absolute_error >= 0


# --- Quality report -----------------------------------------------------


def test_quality_report_passes_on_valid_workflow() -> None:
    workflow = get_workflow()

    assert len(workflow.quality) >= 28
    assert bool(workflow.quality["passed"].astype(bool).all())
    assert workflow.quality["check"].is_unique


def test_quality_report_flags_split_boundary_change() -> None:
    workflow = get_workflow()

    data = workflow.data.copy()
    data = data[
        ~(
            (data["split"] == "validation")
            & (data["date"] == et.TRAIN_END + pd.Timedelta(days=1))
        )
    ]

    report = build_quality(workflow, data=data)

    assert not bool(check_row(report, "split_boundaries_exact")["passed"])


def test_quality_report_flags_store_coverage_gap() -> None:
    workflow = get_workflow()

    extra = make_daily_frame((2,))
    data = pd.concat([workflow.data, extra], ignore_index=True)

    report = build_quality(workflow, data=data)

    assert not bool(check_row(report, "store_coverage_complete")["passed"])


def test_quality_report_flags_configuration_coverage_gap() -> None:
    workflow = get_workflow()

    results = workflow.cv_results.iloc[:-1]

    report = build_quality(workflow, cv_results=results)

    assert not bool(
        check_row(report, "configuration_coverage_complete")["passed"]
    )


def test_quality_report_flags_wrong_fold_horizon() -> None:
    workflow = get_workflow()

    results = workflow.cv_results.copy()
    results.loc[0, "horizon"] = CV_HORIZON - 1

    report = build_quality(workflow, cv_results=results)

    assert not bool(check_row(report, "fold_horizon_fixed")["passed"])


def test_quality_report_flags_cv_metric_mismatch() -> None:
    workflow = get_workflow()

    results = workflow.cv_results.copy()
    results.loc[0, "rmse"] = results.loc[0, "rmse"] + 1.0

    report = build_quality(workflow, cv_results=results)

    assert not bool(
        check_row(
            report, "cv_metrics_reproduced_from_predictions"
        )["passed"]
    )


def test_quality_report_flags_summary_mismatch() -> None:
    workflow = get_workflow()

    summary = workflow.cv_summary.copy()
    summary.loc[0, "mean_rmse"] = summary.loc[0, "mean_rmse"] + 5.0

    report = build_quality(workflow, cv_summary=summary)

    assert not bool(
        check_row(report, "cv_summary_reconciles_with_results")["passed"]
    )


def test_quality_report_flags_selection_mismatch() -> None:
    workflow = get_workflow()

    selected = workflow.selected.copy()
    selected.loc[:, "mean_rmse"] = selected["mean_rmse"] + 100.0

    report = build_quality(workflow, selected=selected)

    assert not bool(check_row(report, "selection_rule_verified")["passed"])


def test_quality_report_flags_validation_metric_mismatch() -> None:
    workflow = get_workflow()

    results = workflow.validation_results.copy()
    results.loc[0, "rmse"] = results.loc[0, "rmse"] + 1.0

    report = build_quality(workflow, validation_results=results)

    assert not bool(
        check_row(
            report, "validation_metrics_reproduced_from_predictions"
        )["passed"]
    )


def test_quality_report_flags_error_analysis_mismatch() -> None:
    workflow = get_workflow()

    error_analysis = workflow.error_analysis.copy()
    error_analysis.loc[0, "rmse"] = error_analysis.loc[0, "rmse"] + 1.0

    report = build_quality(workflow, error_analysis=error_analysis)

    assert not bool(
        check_row(
            report, "error_analysis_reconciles_with_predictions"
        )["passed"]
    )


def test_quality_report_flags_test_period_leakage() -> None:
    workflow = get_workflow()

    predictions = workflow.predictions.copy()
    predictions.loc[0, "date"] = et.TEST_START

    report = build_quality(workflow, predictions=predictions)

    assert not bool(
        check_row(report, "predictions_avoid_test_period")["passed"]
    )


def test_quality_report_flags_incomplete_validation_predictions() -> None:
    workflow = get_workflow()

    predictions = workflow.predictions[
        workflow.predictions["scope"] != "validation"
    ]

    report = build_quality(workflow, predictions=predictions)

    assert not bool(
        check_row(report, "validation_predictions_complete")["passed"]
    )


# --- Main workflow ------------------------------------------------------


def test_main_writes_all_artifacts(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "feature_engineered_daily.csv"

    make_daily_frame((1,)).to_csv(input_path, index=False)

    monkeypatch.setattr(et, "INPUT_PATH", input_path)
    monkeypatch.setattr(et, "RESULTS_PATH", tmp_path / "results.csv")
    monkeypatch.setattr(et, "SUMMARY_PATH", tmp_path / "summary.csv")
    monkeypatch.setattr(et, "SELECTED_PATH", tmp_path / "selected.csv")
    monkeypatch.setattr(et, "VALIDATION_PATH", tmp_path / "validation.csv")
    monkeypatch.setattr(et, "ERROR_PATH", tmp_path / "error.csv")
    monkeypatch.setattr(
        et, "PREDICTIONS_PATH", tmp_path / "predictions.csv"
    )
    monkeypatch.setattr(et, "QUALITY_PATH", tmp_path / "quality.csv")
    monkeypatch.setattr(et, "FINDINGS_PATH", tmp_path / "findings.txt")
    monkeypatch.setattr(
        et,
        "PHASE11_PREDICTIONS_PATH",
        tmp_path / "phase11_missing.csv",
    )
    monkeypatch.setattr(et, "EXPECTED_STORES", 1)

    et.main()

    for name in (
        "results.csv",
        "summary.csv",
        "selected.csv",
        "validation.csv",
        "error.csv",
        "predictions.csv",
        "quality.csv",
        "findings.txt",
    ):
        assert (tmp_path / name).exists()

    quality = pd.read_csv(tmp_path / "quality.csv")
    assert bool(quality["passed"].astype(bool).all())

    selected = pd.read_csv(tmp_path / "selected.csv")
    assert len(selected) == 1
    assert {
        "store_id",
        "model",
        "configuration",
        "season_length",
        "order",
    }.issubset(selected.columns)

    predictions = pd.read_csv(tmp_path / "predictions.csv")
    assert set(predictions["scope"]) == {"cv_fold", "validation"}


def test_main_missing_input_raises(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(et, "INPUT_PATH", tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError):
        et.main()


def test_main_raises_when_quality_check_fails(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "feature_engineered_daily.csv"

    make_daily_frame((1,)).to_csv(input_path, index=False)

    failing = pd.DataFrame(
        [
            {
                "check": "synthetic_failure",
                "passed": False,
                "actual": 0,
                "expected": 1,
            }
        ]
    )

    monkeypatch.setattr(et, "INPUT_PATH", input_path)
    monkeypatch.setattr(et, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(et, "create_quality_report", lambda *a, **k: failing)

    with pytest.raises(RuntimeError):
        et.main()
