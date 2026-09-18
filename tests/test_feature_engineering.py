"""Tests for Phase 10 feature engineering."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import scripts.feature_engineering as fe
from scripts.feature_engineering import (
    CALENDAR_FEATURES,
    FEATURE_COLUMNS,
    HISTORICAL_FEATURES,
    KEY_COLUMNS,
    add_calendar_features,
    add_series_features,
    create_feature_summary,
    create_quality_report,
    create_split_summary,
    create_summary,
    prepare_features,
    validate_input_columns,
    write_findings,
)


def make_sample_frame(periods: int = 35) -> pd.DataFrame:
    """Create a small deterministic retail time-series frame."""
    dates = pd.date_range("2024-01-01", periods=periods, freq="D")

    return pd.DataFrame(
        {
            "date": dates,
            "item_id": ["item_1"] * periods,
            "store_id": [1] * periods,
            "quantity": list(range(1, periods + 1)),
            "split": ["train"] * periods,
        }
    )


def make_split_frame(periods: int = 30) -> pd.DataFrame:
    """Create a frame carrying all three chronological split labels."""
    frame = make_sample_frame(periods)

    train = int(periods * 0.70)
    validation = int(periods * 0.85)

    frame["split"] = (
        ["train"] * train
        + ["validation"] * (validation - train)
        + ["test"] * (periods - validation)
    )

    return frame


def make_multi_series_frame(periods: int = 10) -> pd.DataFrame:
    """Create a frame with two independent item-store series."""
    dates = pd.date_range("2024-01-01", periods=periods, freq="D")

    return pd.DataFrame(
        {
            "date": list(dates) * 2,
            "item_id": ["a"] * periods + ["b"] * periods,
            "store_id": [1] * periods + [1] * periods,
            "quantity": list(range(1, periods + 1))
            + list(range(101, 101 + periods)),
            "split": ["train"] * (periods * 2),
        }
    )


# --- Schema ------------------------------------------------------------


def test_required_columns_are_validated() -> None:
    """Required forecasting columns must be accepted."""
    validate_input_columns(make_sample_frame().columns.tolist())


def test_missing_column_fails_validation() -> None:
    """Missing required fields must raise an error."""
    frame = make_sample_frame().drop(columns=["quantity"])

    with pytest.raises(ValueError):
        validate_input_columns(frame.columns.tolist())


# --- Calendar features -------------------------------------------------


def test_calendar_features_are_created() -> None:
    """Every calendar feature must be created."""
    result = add_calendar_features(make_sample_frame())

    assert set(CALENDAR_FEATURES).issubset(result.columns)


def test_calendar_values_are_correct() -> None:
    """Calendar values must be derived from the observation date."""
    result = add_calendar_features(make_sample_frame())

    assert result.loc[0, "day_of_week"] == 0
    assert result.loc[0, "day_of_month"] == 1
    assert result.loc[0, "month"] == 1
    assert result.loc[0, "quarter"] == 1
    assert result.loc[0, "year"] == 2024


def test_weekend_indicator_is_correct() -> None:
    """The weekend flag must mark Saturday and Sunday only."""
    result = add_calendar_features(make_sample_frame())

    # 2024-01-01 is a Monday, so index 5 is Saturday and index 6 Sunday.
    assert result.loc[0, "is_weekend"] == 0
    assert result.loc[5, "is_weekend"] == 1
    assert result.loc[6, "is_weekend"] == 1
    assert result.loc[7, "is_weekend"] == 0


def test_invalid_date_is_rejected() -> None:
    """An unparsable date must raise an error."""
    frame = make_sample_frame()
    frame["date"] = ["not-a-date"] + [
        value.isoformat()
        for value in frame["date"].iloc[1:]
    ]

    with pytest.raises((ValueError, TypeError)):
        prepare_features(frame)


# --- Historical features ----------------------------------------------


def test_lag_features_use_previous_observations() -> None:
    """Lags must reference prior observations only."""
    result = add_series_features(make_sample_frame())

    assert pd.isna(result.loc[0, "lag_1"])
    assert result.loc[1, "lag_1"] == 1
    assert result.loc[7, "lag_7"] == 1
    assert result.loc[14, "lag_14"] == 1
    assert result.loc[28, "lag_28"] == 1


def test_rolling_mean_excludes_current_target() -> None:
    """The rolling mean must not include the current observation."""
    result = add_series_features(make_sample_frame())

    assert pd.isna(result.loc[0, "rolling_mean_7"])
    assert result.loc[1, "rolling_mean_7"] == 1
    assert result.loc[7, "rolling_mean_7"] == 4
    assert result.loc[8, "rolling_mean_7"] == 5


def test_rolling_standard_deviation_values() -> None:
    """The rolling standard deviation must use prior observations."""
    result = add_series_features(make_sample_frame())

    assert pd.isna(result.loc[0, "rolling_std_7"])
    assert pd.isna(result.loc[1, "rolling_std_7"])
    assert result.loc[2, "rolling_std_7"] == pytest.approx(
        np.std([1.0, 2.0], ddof=1)
    )


def test_series_age_starts_at_zero() -> None:
    """A new series must start at age zero."""
    result = add_series_features(make_sample_frame())

    assert result.loc[0, "series_age_days"] == 0
    assert result.loc[10, "series_age_days"] == 10


def test_series_are_independent() -> None:
    """Lags must not cross between item-store series."""
    result = (
        add_series_features(make_multi_series_frame())
        .sort_values(KEY_COLUMNS, kind="mergesort")
        .reset_index(drop=True)
    )

    series_a = result[result["item_id"] == "a"].reset_index(drop=True)
    series_b = result[result["item_id"] == "b"].reset_index(drop=True)

    assert pd.isna(series_a.loc[0, "lag_1"])
    assert pd.isna(series_b.loc[0, "lag_1"])
    assert series_a.loc[1, "lag_1"] == 1
    assert series_b.loc[1, "lag_1"] == 101


# --- Prepare and preserve ---------------------------------------------


def test_feature_engineered_keys_are_unique() -> None:
    """The prepared matrix must keep a unique key."""
    result = prepare_features(make_sample_frame())

    assert result.duplicated(KEY_COLUMNS).sum() == 0


def test_prepare_features_preserves_row_count() -> None:
    """Prepare must not add or drop rows."""
    source = make_sample_frame()

    assert len(prepare_features(source)) == len(source)


def test_feature_engineering_preserves_target() -> None:
    """Feature engineering must not alter the demand target."""
    source = make_sample_frame()
    result = prepare_features(source)

    pd.testing.assert_series_equal(
        result.sort_values(KEY_COLUMNS)["quantity"].reset_index(drop=True),
        source.sort_values(KEY_COLUMNS)["quantity"].reset_index(drop=True),
        check_names=False,
    )


def test_prepare_features_preserves_split() -> None:
    """The Phase 9 split labels must be preserved."""
    source = make_split_frame()
    result = prepare_features(source)

    pd.testing.assert_series_equal(
        result.sort_values(KEY_COLUMNS)["split"].reset_index(drop=True),
        source.sort_values(KEY_COLUMNS)["split"].reset_index(drop=True),
        check_names=False,
    )


def test_prepare_features_creates_all_features() -> None:
    """Every engineered feature must be present."""
    result = prepare_features(make_sample_frame())

    assert set(FEATURE_COLUMNS).issubset(result.columns)


# --- Quality report ----------------------------------------------------


def test_quality_report_passes_for_valid_data() -> None:
    """A valid matrix must pass every quality check."""
    source = make_sample_frame()
    result = prepare_features(source)

    report = create_quality_report(result, source)

    assert bool(report["passed"].all())
    assert set(report.columns) == {
        "check",
        "passed",
        "actual",
        "expected",
    }


def test_quality_report_flags_duplicate_keys() -> None:
    """A duplicated key must be flagged."""
    source = make_sample_frame()
    result = prepare_features(source)
    duplicated = pd.concat([result, result.iloc[[0]]], ignore_index=True)

    report = create_quality_report(duplicated, source)

    row = report.loc[
        report["check"] == "duplicate_date_item_store_keys"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_flags_modified_target() -> None:
    """A changed target value must be flagged."""
    source = make_sample_frame()
    result = prepare_features(source)
    result = result.copy()
    result.loc[result.index[0], "quantity"] = 999.0

    report = create_quality_report(result, source)

    failed = set(report.loc[~report["passed"], "check"])

    assert "target_preserved_vs_input" in failed
    assert "quantity_total_reconciled" in failed


def test_quality_report_flags_changed_split() -> None:
    """A changed split label must be flagged."""
    source = make_sample_frame()
    result = prepare_features(source)
    result = result.copy()
    result["split"] = "test"

    report = create_quality_report(result, source)

    row = report.loc[
        report["check"] == "split_preserved_vs_input"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_flags_missing_feature() -> None:
    """A missing historical feature must be flagged."""
    source = make_sample_frame()
    result = prepare_features(source).drop(columns=["lag_7"])

    report = create_quality_report(result, source)

    row = report.loc[
        report["check"] == "historical_features_present"
    ].iloc[0]

    assert not bool(row["passed"])
    assert row["actual"] == len(HISTORICAL_FEATURES) - 1
    assert row["expected"] == len(HISTORICAL_FEATURES)


def test_quality_report_flags_current_inclusive_rolling() -> None:
    """A rolling mean that includes the current row must be flagged."""
    source = make_sample_frame()
    result = prepare_features(source)
    result = result.copy()

    result["rolling_mean_7"] = result.groupby(
        ["item_id", "store_id"],
        sort=False,
        observed=True,
    )["quantity"].transform(
        lambda series: series.rolling(window=7, min_periods=1).mean()
    )

    report = create_quality_report(result, source)

    row = report.loc[
        report["check"] == "rolling_excludes_current_target"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_flags_first_observation_history() -> None:
    """History at a series start must be flagged."""
    source = make_sample_frame()
    result = prepare_features(source)
    result = result.copy()
    result.loc[result.index[0], "lag_1"] = 5.0

    report = create_quality_report(result, source)

    row = report.loc[
        report["check"] == "first_observation_has_no_history"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_reports_present_feature_counts() -> None:
    """Presence checks must report real counts, not hardcoded values."""
    source = make_sample_frame()
    result = prepare_features(source)

    report = create_quality_report(result, source)

    calendar = report.loc[
        report["check"] == "calendar_features_present"
    ].iloc[0]
    historical = report.loc[
        report["check"] == "historical_features_present"
    ].iloc[0]

    assert calendar["actual"] == len(CALENDAR_FEATURES)
    assert historical["actual"] == len(HISTORICAL_FEATURES)
    assert not isinstance(calendar["actual"], bool)


# --- Feature summary and summary --------------------------------------


def test_feature_summary_covers_every_feature() -> None:
    """The feature summary must describe every engineered feature."""
    result = prepare_features(make_sample_frame())

    summary = create_feature_summary(result)

    assert summary["feature"].tolist() == FEATURE_COLUMNS
    assert set(summary["feature_group"]) == {"calendar", "historical"}


def test_feature_summary_records_lag_missingness() -> None:
    """The feature summary must count missing values correctly."""
    result = prepare_features(make_sample_frame())

    summary = create_feature_summary(result)

    lag_1 = summary.loc[
        summary["feature"] == "lag_1"
    ].iloc[0]

    assert lag_1["missing"] == 1
    assert lag_1["non_null"] == len(result) - 1


def test_summary_reports_split_rows() -> None:
    """The summary must record the preserved split row counts."""
    source = make_split_frame()
    result = prepare_features(source)

    summary = create_summary(result, source)
    values = dict(zip(summary["metric"], summary["value"]))

    assert int(values["rows"]) == len(result)
    assert int(values["source_rows"]) == len(source)
    assert int(values["feature_count"]) == len(FEATURE_COLUMNS)


def test_split_summary_is_ordered() -> None:
    """The split summary must order train, validation and test."""
    result = prepare_features(make_split_frame())

    summary = create_split_summary(result)

    assert summary["split"].tolist() == [
        "train",
        "validation",
        "test",
    ]
    assert int(summary["rows"].sum()) == len(result)


# --- Findings ----------------------------------------------------------


def test_findings_have_no_float_artefacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Findings text must not contain floating-point artefacts."""
    monkeypatch.setattr(fe, "FINDINGS_PATH", tmp_path / "findings.txt")

    source = make_split_frame()
    result = prepare_features(source)
    report = create_quality_report(result, source)
    feature_summary = create_feature_summary(result)
    split_summary = create_split_summary(result)

    write_findings(
        result,
        source,
        report,
        feature_summary,
        split_summary,
    )

    text = (tmp_path / "findings.txt").read_text(encoding="utf-8")

    assert "Source reconciliation:" in text
    assert "Leakage contract:" in text
    assert "Feature completeness" in text
    assert "All feature-engineering quality checks passed." in text
    assert not re.search(r"\d+\.\d{4,}", text)


# --- Main workflow -----------------------------------------------------


def test_main_writes_all_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The complete workflow must write every artifact."""
    input_path = tmp_path / "time_series_daily.csv"
    output_path = tmp_path / "feature_engineered_daily.csv"

    make_split_frame(40).to_csv(input_path, index=False)

    monkeypatch.setattr(fe, "INPUT_PATH", input_path)
    monkeypatch.setattr(fe, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(
        fe, "SUMMARY_PATH", tmp_path / "summary.csv"
    )
    monkeypatch.setattr(
        fe, "QUALITY_PATH", tmp_path / "quality.csv"
    )
    monkeypatch.setattr(
        fe,
        "FEATURE_SUMMARY_PATH",
        tmp_path / "feature_summary.csv",
    )
    monkeypatch.setattr(fe, "SPLIT_PATH", tmp_path / "split.csv")
    monkeypatch.setattr(fe, "FINDINGS_PATH", tmp_path / "findings.txt")

    fe.main()

    assert output_path.exists()
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "quality.csv").exists()
    assert (tmp_path / "feature_summary.csv").exists()
    assert (tmp_path / "split.csv").exists()
    assert (tmp_path / "findings.txt").exists()

    quality = pd.read_csv(tmp_path / "quality.csv")
    assert bool(quality["passed"].astype(bool).all())

    engineered = pd.read_csv(output_path)
    assert len(engineered) == 40
    assert set(FEATURE_COLUMNS).issubset(engineered.columns)


def test_main_missing_input_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing input dataset must raise FileNotFoundError."""
    monkeypatch.setattr(
        fe, "INPUT_PATH", tmp_path / "missing.csv"
    )

    with pytest.raises(FileNotFoundError):
        fe.main()
