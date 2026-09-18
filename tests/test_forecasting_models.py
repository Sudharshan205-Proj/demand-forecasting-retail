"""Tests for Phase 11 forecasting models."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import scripts.forecasting_models as fc
from scripts.forecasting_models import (
    ARIMA_ORDER,
    MODELS,
    REQUIRED_COLUMNS,
    SEASONAL_PERIOD,
    aggregate_daily_demand,
    create_quality_report,
    create_summary,
    evaluate_forecast,
    iter_store_series,
    load_feature_matrix,
    mape,
    naive_forecast,
    rmse,
    run_models_for_store,
    seasonal_naive_forecast,
    summarize_input,
    to_regular_daily_series,
    validate_input_columns,
    write_findings,
)


def make_source_frame(store_ids: tuple[int, ...] = (1,)) -> pd.DataFrame:
    """Create a small deterministic store-day forecasting frame.

    The frame spans the real Phase 11 contract boundaries: training ends
    on ``TRAIN_END``, validation runs the full 114 days to
    ``VALIDATION_END`` and a short test partition follows.
    """
    dates = pd.date_range("2024-01-01", "2024-06-10", freq="D")

    records = []

    for store_id in store_ids:
        for position, date in enumerate(dates):
            if date <= fc.TRAIN_END:
                split = "train"
            elif date <= fc.VALIDATION_END:
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


def build_workflow(store_ids: tuple[int, ...] = (1,)) -> SimpleNamespace:
    """Run the complete Phase 11 workflow on the synthetic frame."""
    source = make_source_frame(store_ids)
    daily = aggregate_daily_demand(source)
    series_by_store = dict(iter_store_series(daily))

    results: list[dict] = []
    configurations: list[dict] = []
    predictions: list[dict] = []

    for store_id, series in series_by_store.items():
        store_results, store_configurations, store_predictions = (
            run_models_for_store(series, store_id)
        )
        results.extend(store_results)
        configurations.extend(store_configurations)
        predictions.extend(store_predictions)

    results_frame = pd.DataFrame(results)
    configurations_frame = pd.DataFrame(configurations)
    predictions_frame = pd.DataFrame(predictions)

    summary = create_summary(results_frame, predictions_frame)

    quality = create_quality_report(
        source,
        daily,
        series_by_store,
        results_frame,
        configurations_frame,
        predictions_frame,
        summary,
    )

    return SimpleNamespace(
        source=source,
        daily=daily,
        series_by_store=series_by_store,
        results=results_frame,
        configurations=configurations_frame,
        predictions=predictions_frame,
        summary=summary,
        quality=quality,
    )


def check_row(report: pd.DataFrame, name: str) -> pd.Series:
    """Return the quality-report row for a named check."""
    return report.loc[report["check"] == name].iloc[0]


# --- Schema ------------------------------------------------------------


def test_validate_input_columns_accepts_complete_schema() -> None:
    validate_input_columns(list(REQUIRED_COLUMNS))


def test_validate_input_columns_rejects_missing_column() -> None:
    with pytest.raises(ValueError):
        validate_input_columns(["date", "store_id", "quantity"])


# --- Loading -----------------------------------------------------------


def test_load_feature_matrix_reads_and_sorts(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The loader must read only the required columns, sorted by key."""
    path = tmp_path / "feature_engineered_daily.csv"

    frame = make_source_frame((1, 2))[["date", "store_id", "quantity", "split"]]
    frame = frame.sample(frac=1.0, random_state=0).assign(
        extra_feature=1.0
    )
    frame.to_csv(path, index=False)

    monkeypatch.setattr(fc, "INPUT_PATH", path)

    loaded = load_feature_matrix()

    assert loaded.columns.tolist() == REQUIRED_COLUMNS
    assert loaded[["store_id", "date"]].apply(
        tuple, axis=1
    ).is_monotonic_increasing


def test_load_feature_matrix_missing_file_raises(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fc, "INPUT_PATH", tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError):
        load_feature_matrix()


def test_summarize_input_records_reconciliation_facts() -> None:
    source = make_source_frame((1, 2))

    facts = summarize_input(source)

    assert facts["rows"] == len(source)
    assert facts["stores"] == 2
    assert facts["quantity_total"] == pytest.approx(
        float(source["quantity"].sum())
    )
    assert facts["date_min"] == source["date"].min()
    assert sum(facts["split_rows"].values()) == len(source)


def test_aggregate_daily_demand_reconciles_and_keys_unique() -> None:
    source = make_source_frame((1, 2, 3))

    daily = aggregate_daily_demand(source)

    assert float(daily["quantity"].sum()) == pytest.approx(
        float(source["quantity"].sum())
    )
    assert int(daily.duplicated(["date", "store_id"]).sum()) == 0
    assert daily["store_id"].nunique() == 3


# --- Series preparation ------------------------------------------------


def test_to_regular_daily_series_zero_fills_gaps() -> None:
    """An intermediate missing date must be filled with zero demand."""
    index = pd.to_datetime(
        ["2024-01-01", "2024-01-02", "2024-01-04"]
    )
    series = pd.Series([1.0, 2.0, 4.0], index=index, name="quantity")

    regular = to_regular_daily_series(series, 1)

    assert len(regular) == 4
    assert regular.index.freqstr == "D"
    assert regular.loc[pd.Timestamp("2024-01-03")] == 0.0
    assert regular.tolist() == [1.0, 2.0, 0.0, 4.0]


def test_to_regular_daily_series_rejects_empty() -> None:
    series = pd.Series(
        dtype=float,
        index=pd.DatetimeIndex([]),
    )

    with pytest.raises(ValueError):
        to_regular_daily_series(series, 1)


def test_to_regular_daily_series_rejects_non_datetime_index() -> None:
    series = pd.Series([1.0, 2.0])

    with pytest.raises(TypeError):
        to_regular_daily_series(series, 1)


def test_to_regular_daily_series_rejects_unsorted_index() -> None:
    index = pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"])
    series = pd.Series([3.0, 1.0, 2.0], index=index)

    with pytest.raises(ValueError):
        to_regular_daily_series(series, 1)


def test_iter_store_series_yields_regular_ordered_series() -> None:
    daily = aggregate_daily_demand(make_source_frame((2, 1)))

    series_by_store = dict(iter_store_series(daily))

    assert list(series_by_store) == [1, 2]
    for series in series_by_store.values():
        assert series.index.is_monotonic_increasing
        assert series.index.freqstr == "D"


# --- Forecast definitions ---------------------------------------------


def test_naive_forecast_uses_last_observation() -> None:
    history = pd.Series([10.0, 20.0, 30.0])

    result = naive_forecast(history, 4)

    assert result.tolist() == [30.0, 30.0, 30.0, 30.0]


def test_naive_forecast_rejects_empty_history() -> None:
    with pytest.raises(ValueError):
        naive_forecast(pd.Series(dtype=float), 3)


def test_naive_forecast_rejects_non_positive_horizon() -> None:
    with pytest.raises(ValueError):
        naive_forecast(pd.Series([1.0, 2.0]), 0)


def test_seasonal_naive_forecast_repeats_pattern() -> None:
    history = pd.Series(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    )

    result = seasonal_naive_forecast(
        history,
        10,
        season_length=7,
    )

    assert result.tolist() == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        1.0,
        2.0,
        3.0,
    ]


def test_seasonal_naive_requires_enough_history() -> None:
    history = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        seasonal_naive_forecast(
            history,
            2,
            season_length=SEASONAL_PERIOD,
        )


def test_seasonal_naive_rejects_non_positive_horizon() -> None:
    history = pd.Series([1.0] * 7)

    with pytest.raises(ValueError):
        seasonal_naive_forecast(history, 0)


def test_arima_configuration_is_explicit() -> None:
    assert ARIMA_ORDER == (1, 1, 1)
    assert SEASONAL_PERIOD == 7
    assert MODELS == ("naive", "seasonal_naive", "arima")


# --- Metrics -----------------------------------------------------------


def test_rmse_is_zero_for_perfect_predictions() -> None:
    actual = np.array([1.0, 2.0, 3.0])
    predicted = np.array([1.0, 2.0, 3.0])

    assert rmse(actual, predicted) == 0.0


def test_rmse_calculates_expected_value() -> None:
    actual = np.array([1.0, 2.0])
    predicted = np.array([2.0, 4.0])

    assert rmse(actual, predicted) == pytest.approx(np.sqrt(2.5))


def test_rmse_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        rmse(np.array([1.0, 2.0]), np.array([1.0]))


def test_rmse_rejects_empty_forecast() -> None:
    with pytest.raises(ValueError):
        rmse(np.array([]), np.array([]))


def test_mape_excludes_zero_actual_values() -> None:
    actual = np.array([0.0, 100.0])
    predicted = np.array([50.0, 110.0])

    assert mape(actual, predicted) == pytest.approx(10.0)


def test_mape_returns_nan_when_all_actual_values_are_zero() -> None:
    actual = np.array([0.0, 0.0])
    predicted = np.array([1.0, 2.0])

    assert np.isnan(mape(actual, predicted))


def test_mape_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        mape(np.array([1.0, 2.0]), np.array([1.0]))


def test_evaluation_requires_equal_lengths() -> None:
    actual = pd.Series([1.0, 2.0])
    predicted = np.array([1.0])

    with pytest.raises(ValueError):
        evaluate_forecast(actual, predicted)


def test_evaluation_returns_required_metrics() -> None:
    actual = pd.Series([10.0, 20.0])
    predicted = np.array([10.0, 20.0])

    result = evaluate_forecast(actual, predicted)

    assert set(result) == {"rmse", "mape_percent"}
    assert result["rmse"] == 0.0
    assert result["mape_percent"] == 0.0


# --- Per-store model run ------------------------------------------------


def test_run_models_for_store_records_configuration_and_horizon() -> None:
    daily = aggregate_daily_demand(make_source_frame((1,)))
    series = dict(iter_store_series(daily))[1]

    results, configurations, predictions = run_models_for_store(series, 1)

    assert {row["model"] for row in results} == set(MODELS)

    horizons = {row["forecast_horizon"] for row in results}
    assert horizons == {114}

    for configuration in configurations:
        assert configuration["training_end"] == "2024-02-10"
        assert configuration["validation_start"] == "2024-02-11"
        assert configuration["validation_end"] == "2024-06-03"
        assert configuration["forecast_horizon"] == 114


def test_run_models_for_store_reproduces_baseline_definitions() -> None:
    """The stored predictions must equal the documented baselines."""
    daily = aggregate_daily_demand(make_source_frame((1,)))
    series = dict(iter_store_series(daily))[1]
    train = series.loc[: fc.TRAIN_END]
    validation = series.loc[
        (series.index > fc.TRAIN_END)
        & (series.index <= fc.VALIDATION_END)
    ]

    _, _, predictions = run_models_for_store(series, 1)

    frame = pd.DataFrame(predictions)

    naive = frame.loc[frame["model"] == "naive", "predicted"].to_numpy()
    assert np.allclose(naive, float(train.iloc[-1]))

    seasonal = frame.loc[
        frame["model"] == "seasonal_naive", "predicted"
    ].to_numpy()
    assert np.allclose(
        seasonal,
        seasonal_naive_forecast(train, len(validation)),
    )

    assert frame["date"].nunique() == len(validation)
    assert np.allclose(
        frame.loc[frame["model"] == "arima", "actual"].to_numpy(),
        validation.to_numpy(dtype=float),
    )


def test_run_models_for_store_rejects_empty_validation() -> None:
    index = pd.date_range("2024-01-01", "2024-02-10", freq="D")
    series = pd.Series(
        np.arange(len(index), dtype=float),
        index=index,
    )
    series.index.freq = "D"

    with pytest.raises(ValueError):
        run_models_for_store(series, 1)


# --- Summary -----------------------------------------------------------


def test_summary_pooled_metrics_reconcile_with_predictions() -> None:
    workflow = build_workflow()

    for row in workflow.summary.itertuples(index=False):
        group = workflow.predictions.loc[
            workflow.predictions["model"] == row.model
        ]

        assert row.pooled_observations == len(group)
        assert row.pooled_rmse == pytest.approx(
            rmse(group["actual"], group["predicted"])
        )
        assert row.pooled_mape_percent == pytest.approx(
            mape(group["actual"], group["predicted"])
        )


def test_summary_is_sorted_by_mean_rmse() -> None:
    workflow = build_workflow()

    assert workflow.summary["mean_rmse"].is_monotonic_increasing
    assert workflow.summary["stores_evaluated"].tolist() == [1, 1, 1]


def test_summary_reports_all_models() -> None:
    workflow = build_workflow((1, 2))

    assert set(workflow.summary["model"]) == set(MODELS)
    assert workflow.summary["stores_evaluated"].tolist() == [2, 2, 2]


# --- Quality report ----------------------------------------------------


def test_quality_report_passes_on_valid_workflow() -> None:
    workflow = build_workflow((1, 2))

    assert len(workflow.quality) >= 20
    assert bool(workflow.quality["passed"].astype(bool).all())
    assert workflow.quality["check"].is_unique


def test_quality_report_flags_duplicate_store_day_key() -> None:
    workflow = build_workflow()

    daily = pd.concat(
        [workflow.daily, workflow.daily.iloc[[0]]],
        ignore_index=True,
    )

    report = create_quality_report(
        workflow.source,
        daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(check_row(report, "store_day_keys_unique")["passed"])


def test_quality_report_flags_demand_not_reconciled() -> None:
    workflow = build_workflow()

    daily = workflow.daily.copy()
    daily.loc[0, "quantity"] += 1000.0

    report = create_quality_report(
        workflow.source,
        daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    row = check_row(report, "store_day_demand_reconciled")

    assert not bool(row["passed"])
    assert row["actual"] != row["expected"]


def test_quality_report_flags_missing_target_value() -> None:
    workflow = build_workflow()

    source = workflow.source.copy()
    source.loc[0, "quantity"] = np.nan

    report = create_quality_report(
        source,
        workflow.daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(check_row(report, "input_target_complete")["passed"])


def test_quality_report_flags_wrong_validation_window() -> None:
    workflow = build_workflow()

    truncated = {
        store_id: series.loc[: pd.Timestamp("2024-06-02")]
        for store_id, series in workflow.series_by_store.items()
    }

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        truncated,
        workflow.results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "validation_window_matches_contract")["passed"]
    )


def test_quality_report_flags_inconsistent_horizon() -> None:
    workflow = build_workflow()

    results = workflow.results.copy()
    results.loc[0, "forecast_horizon"] = 113

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "validation_horizon_consistent")["passed"]
    )


def test_quality_report_flags_test_period_leakage() -> None:
    workflow = build_workflow()

    predictions = workflow.predictions.copy()
    predictions.loc[0, "date"] = fc.TEST_START

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "test_period_excluded_from_evaluation")["passed"]
    )


def test_quality_report_flags_incomplete_model_coverage() -> None:
    workflow = build_workflow()

    results = workflow.results.loc[
        workflow.results["model"] != "arima"
    ]

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "models_evaluated_per_store")["passed"]
    )


def test_quality_report_flags_wrong_naive_prediction() -> None:
    workflow = build_workflow()

    predictions = workflow.predictions.copy()
    mask = predictions["model"] == "naive"
    predictions.loc[mask, "predicted"] += 1.0

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "naive_matches_last_observation")["passed"]
    )


def test_quality_report_flags_wrong_seasonal_pattern() -> None:
    workflow = build_workflow()

    predictions = workflow.predictions.copy()
    mask = predictions["model"] == "seasonal_naive"
    predictions.loc[mask, "predicted"] += 1.0

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "seasonal_naive_matches_weekly_pattern")["passed"]
    )


def test_quality_report_flags_rmse_mismatch() -> None:
    workflow = build_workflow()

    results = workflow.results.copy()
    results.loc[0, "rmse"] += 1.0

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "rmse_reproduced_from_predictions")["passed"]
    )


def test_quality_report_flags_mape_mismatch() -> None:
    workflow = build_workflow()

    results = workflow.results.copy()
    results.loc[0, "mape_percent"] += 1.0

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        results,
        workflow.configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "mape_reproduced_from_predictions")["passed"]
    )


def test_quality_report_flags_missing_arima_configuration() -> None:
    workflow = build_workflow()

    configurations = workflow.configurations.copy()
    mask = configurations["model"] == "arima"
    configurations.loc[mask, "configuration"] = "order=(1, 1, 0)"

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        workflow.results,
        configurations,
        workflow.predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "arima_configuration_explicit")["passed"]
    )


def test_quality_report_flags_missing_prediction_rows() -> None:
    workflow = build_workflow()

    predictions = workflow.predictions.iloc[:-1]

    report = create_quality_report(
        workflow.source,
        workflow.daily,
        workflow.series_by_store,
        workflow.results,
        workflow.configurations,
        predictions,
        workflow.summary,
    )

    assert not bool(
        check_row(report, "prediction_rows_match_horizons")["passed"]
    )


# --- Findings ----------------------------------------------------------


def test_findings_report_uses_verified_validation_period(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The findings report must not label the training end as validation."""
    monkeypatch.setattr(fc, "FINDINGS_PATH", tmp_path / "findings.txt")

    workflow = build_workflow()

    write_findings(
        summarize_input(workflow.source),
        workflow.daily,
        workflow.series_by_store,
        workflow.summary,
        workflow.results,
        workflow.quality,
    )

    text = (tmp_path / "findings.txt").read_text(encoding="utf-8")

    assert "validation period: 2024-02-11 to 2024-06-03" in text
    assert "training end: 2024-02-10" in text
    assert "test period (excluded from selection): 2024-06-04" in text
    assert "Best model by mean validation RMSE:" in text
    assert "all 24 passed" in text
    assert "zero-filled store-days" in text


def test_findings_report_lists_failed_checks(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fc, "FINDINGS_PATH", tmp_path / "findings.txt")

    workflow = build_workflow()
    quality = workflow.quality.copy()
    quality.loc[0, "passed"] = False

    write_findings(
        summarize_input(workflow.source),
        workflow.daily,
        workflow.series_by_store,
        workflow.summary,
        workflow.results,
        quality,
    )

    text = (tmp_path / "findings.txt").read_text(encoding="utf-8")

    assert "1 failed" in text
    assert f"failed: {quality.loc[0, 'check']}" in text


# --- Main workflow -----------------------------------------------------


def test_main_writes_all_artifacts(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "feature_engineered_daily.csv"

    make_source_frame((1, 2)).to_csv(input_path, index=False)

    monkeypatch.setattr(fc, "INPUT_PATH", input_path)
    monkeypatch.setattr(
        fc, "RESULTS_PATH", tmp_path / "results.csv"
    )
    monkeypatch.setattr(
        fc, "CONFIG_PATH", tmp_path / "configs.csv"
    )
    monkeypatch.setattr(
        fc, "SUMMARY_PATH", tmp_path / "summary.csv"
    )
    monkeypatch.setattr(
        fc, "PREDICTIONS_PATH", tmp_path / "predictions.csv"
    )
    monkeypatch.setattr(
        fc, "QUALITY_PATH", tmp_path / "quality.csv"
    )
    monkeypatch.setattr(fc, "FINDINGS_PATH", tmp_path / "findings.txt")

    fc.main()

    for name in (
        "results.csv",
        "configs.csv",
        "summary.csv",
        "predictions.csv",
        "quality.csv",
        "findings.txt",
    ):
        assert (tmp_path / name).exists()

    quality = pd.read_csv(tmp_path / "quality.csv")
    assert bool(quality["passed"].astype(bool).all())

    results = pd.read_csv(tmp_path / "results.csv")
    assert len(results) == 2 * len(MODELS)
    assert set(results["model"]) == set(MODELS)

    predictions = pd.read_csv(tmp_path / "predictions.csv")
    assert len(predictions) == 2 * len(MODELS) * 114


def test_main_missing_input_raises(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fc, "INPUT_PATH", tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError):
        fc.main()


def test_main_raises_when_quality_check_fails(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "feature_engineered_daily.csv"

    make_source_frame((1,)).to_csv(input_path, index=False)

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

    monkeypatch.setattr(fc, "INPUT_PATH", input_path)
    monkeypatch.setattr(fc, "create_quality_report", lambda *a, **k: failing)

    with pytest.raises(RuntimeError):
        fc.main()
