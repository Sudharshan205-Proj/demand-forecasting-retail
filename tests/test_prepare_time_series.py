"""Tests for Phase 9 time-series preparation."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import scripts.prepare_time_series as pts
from scripts.prepare_time_series import (
    _format_quantity,
    aggregate_daily,
    assign_split,
    calculate_gap_summary,
    calculate_quality_report,
    calculate_split_boundaries,
    calculate_split_summary,
    validate_columns,
    validate_unique_keys,
    write_findings,
)

COLUMNS = ["date", "item_id", "store_id", "quantity"]


def _write_dataset(
    path: Path,
    rows: list[tuple[str, str, int, float]],
) -> None:
    """Write a minimal integrated-style CSV for the aggregation tests."""
    frame = pd.DataFrame(rows, columns=COLUMNS)
    frame.to_csv(path, index=False)


def _make_prepared(
    periods: int = 90,
) -> pd.DataFrame:
    """Build a small chronologically split forecasting frame."""
    dates = pd.date_range(
        "2024-01-01",
        periods=periods,
        freq="D",
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "item_id": ["A"] * periods,
            "store_id": [1] * periods,
            "quantity": np.arange(1, periods + 1, dtype=float),
        }
    )

    train_end, validation_end = calculate_split_boundaries(
        data["date"]
    )

    return assign_split(data, train_end, validation_end)


def _source_stats(prepared: pd.DataFrame) -> dict[str, object]:
    """Build matching source statistics for a prepared frame."""
    return {
        "rows": len(prepared),
        "quantity": float(prepared["quantity"].sum()),
        "date_min": prepared["date"].min(),
        "date_max": prepared["date"].max(),
        "within_chunk_duplicate_keys": 0,
    }


# --- Column validation -------------------------------------------------


def test_required_columns_are_validated() -> None:
    """Required forecasting columns must be accepted."""
    validate_columns(
        [
            "date",
            "item_id",
            "quantity",
            "store_id",
        ]
    )


def test_missing_column_fails_validation() -> None:
    """Missing required fields must raise an error."""
    with pytest.raises(ValueError):
        validate_columns(
            [
                "date",
                "item_id",
                "quantity",
            ]
        )


# --- Aggregation -------------------------------------------------------


def test_aggregate_daily_reduces_to_unique_grain(
    tmp_path: Path,
) -> None:
    """Aggregation must produce one row per date-item-store key."""
    path = tmp_path / "source.csv"

    _write_dataset(
        path,
        [
            ("2024-01-01", "A", 1, 10.0),
            ("2024-01-01", "A", 1, 5.0),
            ("2024-01-02", "A", 1, 7.0),
        ],
    )

    prepared, stats = aggregate_daily(path)

    assert len(prepared) == 2
    assert stats["rows"] == 3
    assert float(prepared["quantity"].sum()) == 22.0
    assert prepared.duplicated(COLUMNS[:3]).sum() == 0


def test_aggregate_daily_reports_within_chunk_duplicates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Duplicate source keys in one chunk must be counted."""
    path = tmp_path / "source.csv"

    _write_dataset(
        path,
        [
            ("2024-01-01", "A", 1, 10.0),
            ("2024-01-01", "A", 1, 5.0),
            ("2024-01-02", "A", 1, 7.0),
        ],
    )

    monkeypatch.setattr(pts, "CHUNK_SIZE", 100_000)

    prepared, stats = aggregate_daily(path)

    assert stats["within_chunk_duplicate_keys"] == 1
    assert len(prepared) == 2


def test_aggregate_daily_is_chunk_size_independent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Splitting the same rows into chunks must not change the result."""
    path = tmp_path / "source.csv"

    rows = [
        (f"2024-01-{day:02d}", "A", 1, float(day))
        for day in range(1, 11)
    ]

    _write_dataset(path, rows)

    monkeypatch.setattr(pts, "CHUNK_SIZE", 100_000)
    default_result, _ = aggregate_daily(path)

    monkeypatch.setattr(pts, "CHUNK_SIZE", 2)
    chunked_result, _ = aggregate_daily(path)

    pd.testing.assert_frame_equal(default_result, chunked_result)


def test_aggregate_daily_coerces_numeric_strings(
    tmp_path: Path,
) -> None:
    """Numeric quantity strings must be coerced to float."""
    path = tmp_path / "source.csv"

    path.write_text(
        "date,item_id,store_id,quantity\n"
        "2024-01-01,A,1,3.5\n",
        encoding="utf-8",
    )

    prepared, _ = aggregate_daily(path)

    assert prepared["quantity"].dtype.kind == "f"
    assert float(prepared.iloc[0]["quantity"]) == 3.5


def test_aggregate_daily_rejects_invalid_dates(
    tmp_path: Path,
) -> None:
    """An unparsable date must raise an error."""
    path = tmp_path / "source.csv"

    _write_dataset(
        path,
        [("not-a-date", "A", 1, 1.0)],
    )

    with pytest.raises(ValueError):
        aggregate_daily(path)


def test_aggregate_daily_rejects_invalid_quantity(
    tmp_path: Path,
) -> None:
    """A non-numeric quantity must raise an error."""
    path = tmp_path / "source.csv"

    path.write_text(
        "date,item_id,store_id,quantity\n"
        "2024-01-01,A,1,abc\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        aggregate_daily(path)


def test_aggregate_daily_rejects_missing_column(
    tmp_path: Path,
) -> None:
    """A file missing a required column must raise an error."""
    path = tmp_path / "source.csv"

    path.write_text(
        "date,item_id,quantity\n"
        "2024-01-01,A,1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        aggregate_daily(path)


def test_aggregate_daily_sorts_by_series_and_date(
    tmp_path: Path,
) -> None:
    """Output must be ordered by item, store and date."""
    path = tmp_path / "source.csv"

    _write_dataset(
        path,
        [
            ("2024-01-02", "A", 1, 1.0),
            ("2024-01-01", "A", 1, 1.0),
            ("2024-01-01", "B", 1, 1.0),
        ],
    )

    prepared, _ = aggregate_daily(path)

    assert prepared["item_id"].tolist() == ["A", "A", "B"]
    assert all(
        group["date"].is_monotonic_increasing
        for _, group in prepared.groupby(
            ["item_id", "store_id"],
            sort=False,
        )
    )


# --- Duplicate key contract -------------------------------------------


def test_duplicate_date_item_store_keys_are_detected() -> None:
    """Duplicate forecasting keys must be counted."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01"]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    assert validate_unique_keys(data) == 1


def test_unique_date_item_store_keys_have_zero_duplicates() -> None:
    """Unique forecasting keys should have no duplicates."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02"]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    assert validate_unique_keys(data) == 0


# --- Gap analysis ------------------------------------------------------


def test_gap_summary_detects_missing_day() -> None:
    """An absent intermediate date should be reported."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-03",
                ]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    result = calculate_gap_summary(data)

    assert result.iloc[0]["maximum_gap_days"] == 2
    assert result.iloc[0]["missing_intermediate_days"] == 1


def test_no_gap_is_reported_for_consecutive_dates() -> None:
    """Consecutive dates should not produce missing days."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "item_id": ["A", "A"],
            "store_id": [1, 1],
            "quantity": [10, 20],
        }
    )

    result = calculate_gap_summary(data)

    assert result.iloc[0]["maximum_gap_days"] == 1
    assert result.iloc[0]["missing_intermediate_days"] == 0


def test_single_observation_series_has_no_gap() -> None:
    """A series with one observation cannot contain a gap."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "item_id": ["A"],
            "store_id": [1],
            "quantity": [10],
        }
    )

    result = calculate_gap_summary(data)

    assert result.iloc[0]["observed_dates"] == 1
    assert result.iloc[0]["maximum_gap_days"] == 0
    assert result.iloc[0]["missing_intermediate_days"] == 0


def test_gap_summary_separates_series() -> None:
    """Each item-store pair must be summarized independently."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-03",
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "item_id": ["A", "A", "A", "A"],
            "store_id": [1, 1, 2, 2],
            "quantity": [10, 20, 10, 20],
        }
    )

    result = calculate_gap_summary(data)

    assert len(result) == 2

    store_one = result.loc[result["store_id"] == 1].iloc[0]
    store_two = result.loc[result["store_id"] == 2].iloc[0]

    assert store_one["missing_intermediate_days"] == 1
    assert store_two["missing_intermediate_days"] == 0


def test_gap_metric_matches_series_span() -> None:
    """Missing days must equal span minus observed transitions."""
    dates = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-05",
            "2024-01-10",
        ]
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "item_id": ["A"] * 3,
            "store_id": [1] * 3,
            "quantity": [1.0, 1.0, 1.0],
        }
    )

    result = calculate_gap_summary(data)

    span = (dates.max() - dates.min()).days
    expected = span - (len(dates) - 1)

    assert result.iloc[0]["missing_intermediate_days"] == expected


# --- Split boundaries --------------------------------------------------


def test_split_boundaries_are_chronological() -> None:
    """Train boundary must precede validation boundary."""
    dates = pd.Series(
        pd.date_range(
            "2024-01-01",
            periods=100,
            freq="D",
        )
    )

    train_end, validation_end = calculate_split_boundaries(dates)

    assert train_end < validation_end


def test_split_boundaries_reject_fewer_than_three_dates() -> None:
    """Fewer than three unique dates cannot be split chronologically."""
    dates = pd.Series(
        pd.to_datetime(["2024-01-01", "2024-01-02"])
    )

    with pytest.raises(ValueError):
        calculate_split_boundaries(dates)


def test_split_boundaries_support_three_dates() -> None:
    """Exactly three unique dates must yield three non-empty partitions."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "item_id": ["A"] * 3,
            "store_id": [1] * 3,
            "quantity": [1.0, 2.0, 3.0],
        }
    )

    train_end, validation_end = calculate_split_boundaries(
        data["date"]
    )

    result = assign_split(data, train_end, validation_end)

    assert set(result["split"]) == {
        "train",
        "validation",
        "test",
    }


def test_split_proportions_are_approximately_70_15_15() -> None:
    """A 761-day history must split into approximately 70/15/15."""
    dates = pd.Series(
        pd.date_range(
            "2022-08-28",
            periods=761,
            freq="D",
        )
    )

    train_end, validation_end = calculate_split_boundaries(dates)

    train_count = int((dates <= train_end).sum())
    validation_count = int(
        ((dates > train_end) & (dates <= validation_end)).sum()
    )
    test_count = int((dates > validation_end).sum())

    assert train_count == 532
    assert validation_count == 114
    assert test_count == 115


def test_split_assignment_is_time_aware() -> None:
    """Rows must be assigned without temporal shuffling."""
    dates = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "item_id": ["A"] * 100,
            "store_id": [1] * 100,
            "quantity": range(100),
        }
    )

    train_end, validation_end = calculate_split_boundaries(
        data["date"]
    )

    result = assign_split(
        data,
        train_end,
        validation_end,
    )

    assert result.iloc[0]["split"] == "train"
    assert result.iloc[-1]["split"] == "test"
    assert result["split"].notna().all()


def test_chronological_split_has_no_overlap() -> None:
    """Partition date ranges must not overlap."""
    dates = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "item_id": ["A"] * 100,
            "store_id": [1] * 100,
            "quantity": range(100),
        }
    )

    train_end, validation_end = calculate_split_boundaries(
        data["date"]
    )

    result = assign_split(
        data,
        train_end,
        validation_end,
    )

    train_max = result.loc[
        result["split"] == "train",
        "date",
    ].max()

    validation_min = result.loc[
        result["split"] == "validation",
        "date",
    ].min()

    validation_max = result.loc[
        result["split"] == "validation",
        "date",
    ].max()

    test_min = result.loc[
        result["split"] == "test",
        "date",
    ].min()

    assert train_max < validation_min
    assert validation_max < test_min


def test_split_summary_has_all_partitions() -> None:
    """The split summary should contain train, validation and test."""
    data = pd.DataFrame(
        {
            "date": pd.date_range(
                "2024-01-01",
                periods=100,
                freq="D",
            ),
            "item_id": ["A"] * 100,
            "store_id": [1] * 100,
            "quantity": range(100),
            "split": (
                ["train"] * 70
                + ["validation"] * 15
                + ["test"] * 15
            ),
        }
    )

    result = calculate_split_summary(data)

    assert result["split"].tolist() == [
        "train",
        "validation",
        "test",
    ]


def test_split_summary_rows_reconcile() -> None:
    """Split row counts must reconcile with the prepared frame."""
    prepared = _make_prepared(90)

    result = calculate_split_summary(prepared)

    assert int(result["rows"].sum()) == len(prepared)


# --- Quality report ----------------------------------------------------


def test_quality_report_passes_on_valid_input() -> None:
    """A valid prepared frame must pass every quality check."""
    prepared = _make_prepared(90)
    stats = _source_stats(prepared)
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=True,
    )

    assert bool(report["passed"].all())
    assert {
        "source_quantity_equals_prepared_quantity",
        "partitions_chronological_without_overlap",
        "split_rows_reconcile_with_prepared",
        "source_file_not_modified",
    }.issubset(set(report["check"]))


def test_quality_report_flags_quantity_mismatch() -> None:
    """A source quantity that disagrees must be flagged."""
    prepared = _make_prepared(90)
    stats = _source_stats(prepared)
    stats["quantity"] = float(stats["quantity"]) + 1.0
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=True,
    )

    failed = set(
        report.loc[~report["passed"], "check"]
    )

    assert "source_quantity_equals_prepared_quantity" in failed


def test_quality_report_flags_duplicate_keys() -> None:
    """A non-zero duplicate count must be flagged."""
    prepared = _make_prepared(90)
    stats = _source_stats(prepared)
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=3,
        source_unchanged=True,
    )

    row = report.loc[
        report["check"] == "duplicate_date_item_store_keys"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_flags_missing_partitions() -> None:
    """A frame with one partition must fail the partition checks."""
    prepared = _make_prepared(90)
    prepared = prepared.assign(split="train")

    stats = _source_stats(prepared)
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=True,
    )

    failed = set(
        report.loc[~report["passed"], "check"]
    )

    assert "all_partitions_present" in failed
    assert "partitions_chronological_without_overlap" in failed


def test_quality_report_flags_modified_source() -> None:
    """A modified source file must be flagged."""
    prepared = _make_prepared(90)
    stats = _source_stats(prepared)
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=False,
    )

    row = report.loc[
        report["check"] == "source_file_not_modified"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_flags_dates_outside_source_range() -> None:
    """Prepared dates beyond the source range must be flagged."""
    prepared = _make_prepared(90)
    stats = _source_stats(prepared)
    stats["date_max"] = prepared["date"].max() - pd.Timedelta(days=5)
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=True,
    )

    row = report.loc[
        report["check"]
        == "prepared_dates_within_source_range"
    ].iloc[0]

    assert not bool(row["passed"])


def test_quality_report_flags_missing_quantity() -> None:
    """A missing quantity must fail the completeness check."""
    prepared = _make_prepared(90)
    prepared.loc[prepared.index[0], "quantity"] = np.nan

    stats = _source_stats(prepared)
    gaps = calculate_gap_summary(prepared)

    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=True,
    )

    row = report.loc[
        report["check"] == "quantity_numeric_and_complete"
    ].iloc[0]

    assert not bool(row["passed"])


# --- Formatting and findings ------------------------------------------


def test_format_quantity_has_no_artefacts() -> None:
    """Quantity formatting must not leak floating-point artefacts."""
    assert _format_quantity(41949529.910000004) == "41949529.910"


def test_findings_have_no_float_artefacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Findings text must not contain floating-point artefacts."""
    monkeypatch.setattr(pts, "OUTPUT_DIR", tmp_path)

    prepared = _make_prepared(90)
    stats = _source_stats(prepared)
    gaps = calculate_gap_summary(prepared)
    splits = calculate_split_summary(prepared)
    report = calculate_quality_report(
        prepared,
        stats,
        gaps,
        duplicate_keys=0,
        source_unchanged=True,
    )

    write_findings(
        prepared,
        stats,
        gaps,
        splits,
        report,
    )

    text = (
        tmp_path / "time_series_findings.txt"
    ).read_text(encoding="utf-8")

    assert "Source reconciliation:" in text
    assert "Series and gaps:" in text
    assert "Quality checks:" in text
    assert not re.search(r"\d+\.\d{4,}", text)


# --- End-to-end workflow ----------------------------------------------


def test_main_writes_all_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The complete workflow must write every artifact."""
    input_path = tmp_path / "integrated.csv"
    output_dataset = tmp_path / "time_series_daily.csv"
    output_dir = tmp_path / "analysis"

    rows = [
        (f"2024-01-{day:02d}", "A", 1, float(day))
        for day in range(1, 11)
    ] + [
        (f"2024-02-{day:02d}", "A", 1, float(day))
        for day in range(1, 11)
    ]

    _write_dataset(input_path, rows)

    monkeypatch.setattr(pts, "INPUT_PATH", input_path)
    monkeypatch.setattr(pts, "OUTPUT_DATASET", output_dataset)
    monkeypatch.setattr(pts, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(pts, "CHUNK_SIZE", 3)

    pts.main()

    assert output_dataset.exists()
    assert (output_dir / "time_series_summary.csv").exists()
    assert (output_dir / "time_series_gap_summary.csv").exists()
    assert (output_dir / "time_series_split_summary.csv").exists()
    assert (output_dir / "time_series_quality_report.csv").exists()
    assert (output_dir / "time_series_findings.txt").exists()

    quality = pd.read_csv(
        output_dir / "time_series_quality_report.csv"
    )

    assert bool(quality["passed"].astype(bool).all())

    summary = pd.read_csv(
        output_dir / "time_series_summary.csv"
    )

    assert int(
        summary.loc[
            summary["metric"] == "prepared_rows",
            "value",
        ].iloc[0]
    ) == len(rows)


def test_main_missing_input_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing input dataset must raise FileNotFoundError."""
    monkeypatch.setattr(
        pts,
        "INPUT_PATH",
        tmp_path / "missing.csv",
    )

    with pytest.raises(FileNotFoundError):
        pts.main()
