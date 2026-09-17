"""Tests for Phase 8 statistical and analytical analysis."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest
from scipy import stats

# Figures are verified without a display; the project environment cannot
# create the interactive Tk backend used by the system matplotlib settings.
matplotlib.use("Agg")

from scripts import statistical_analytical_analysis as stats_module
from scripts.statistical_analytical_analysis import (
    CORRELATION_COLUMNS,
    PROMOTION_COLUMNS,
    REQUIRED_COLUMNS,
    TREND_COLUMNS,
    PairMoments,
    add_store_shares,
    aggregate_chunks,
    build_quality_report,
    calculate_autocorrelation,
    calculate_correlations,
    calculate_price_analysis,
    calculate_promotion_analysis,
    calculate_summary,
    calculate_trend,
    create_figures,
    format_metric,
    format_p_value,
    format_statistic,
    format_summary_value,
    safe_cv,
    validate_columns,
    validate_input_file,
    write_findings,
)

INTEGRATED_COLUMNS = [
    "date",
    "item_id",
    "store_id",
    "quantity",
    "price_base",
    "sum_total",
    "dept_name",
    "markdown_quantity",
    "markdown_record_count",
    "markdown_discount",
    "discount_record_count",
    "promo_discount_rate",
    "price_change_count",
    "online_quantity",
    "online_sales_value",
]


def integrated_fixture(rows: int = 40) -> pd.DataFrame:
    """Build a deterministic integrated-dataset fixture."""
    records = []

    for index in range(rows):
        quantity = float(2 + (index % 5))
        price = float(10 + (index % 4))

        records.append(
            {
                "date": (
                    pd.Timestamp("2024-01-01") + pd.Timedelta(days=index)
                ).strftime("%Y-%m-%d"),
                "item_id": 100 + (index % 3),
                "store_id": 1 + (index % 2),
                "quantity": quantity,
                "price_base": price,
                "sum_total": quantity * price,
                "dept_name": ("Bakery", "Dairy")[index % 2],
                "markdown_quantity": (
                    float(index) if index % 3 == 0 else float("nan")
                ),
                "markdown_record_count": 1 if index % 3 == 0 else 0,
                "markdown_discount": (
                    0.1 if index % 4 == 0 else float("nan")
                ),
                "discount_record_count": 1 if index % 2 == 0 else 0,
                "promo_discount_rate": (
                    0.15 if index % 2 == 0 else float("nan")
                ),
                "price_change_count": index % 2,
                "online_quantity": float(index % 3),
                "online_sales_value": float(index % 3) * 5.0,
            }
        )

    return pd.DataFrame(records, columns=INTEGRATED_COLUMNS)


def write_dataset(frame: pd.DataFrame, path: Path) -> Path:
    """Write an integrated-dataset fixture to disk."""
    frame.to_csv(path, index=False)

    return path


def promotion_dataset() -> pd.DataFrame:
    """Build a fixture covering every promotion group.

    Four promoted records have a positive rate, three have a zero rate, two
    have a non-finite rate and five have no discount record at all.
    """
    rates = [0.1, 0.2, 0.3, 0.4, 0.0, 0.0, 0.0, np.inf, -np.inf]

    records = []

    for index, rate in enumerate([*rates, *([float("nan")] * 5)]):
        records.append(
            {
                "date": (
                    pd.Timestamp("2024-01-01") + pd.Timedelta(days=index)
                ).strftime("%Y-%m-%d"),
                "item_id": 200 + index,
                "store_id": 1,
                "quantity": float(10 + index),
                "price_base": 5.0,
                "sum_total": float(10 + index) * 5.0,
                "dept_name": "Bakery",
                "markdown_quantity": float("nan"),
                "markdown_record_count": 0,
                "markdown_discount": float("nan"),
                "discount_record_count": (
                    0 if index >= len(rates) else 1
                ),
                "promo_discount_rate": rate,
                "price_change_count": 0,
                "online_quantity": 0.0,
                "online_sales_value": 0.0,
            }
        )

    return pd.DataFrame(records, columns=INTEGRATED_COLUMNS)


def promotion_arguments(
    streams: stats_module.Streams,
) -> dict[str, np.ndarray]:
    """Collect the promotion arguments produced by the aggregation."""
    return {
        "present_quantities": streams.present_quantities,
        "absent_quantities": streams.absent_quantities,
        "positive_rate_quantities": streams.positive_rate_quantities,
        "non_positive_rate_quantities": (
            streams.non_positive_rate_quantities
        ),
        "finite_rates": streams.finite_rates,
    }


def test_required_columns_are_accepted() -> None:
    """The integrated dataset must contain the required analysis fields."""
    validate_columns(sorted(REQUIRED_COLUMNS))


def test_missing_required_column_fails() -> None:
    """Missing required fields must stop analysis."""
    with pytest.raises(ValueError):
        validate_columns(
            [
                "date",
                "item_id",
                "quantity",
                "price_base",
                "store_id",
            ]
        )


def test_validate_input_file_rejects_missing_dataset(
    tmp_path: Path,
) -> None:
    """A missing integrated dataset must stop analysis with a clear error."""
    with pytest.raises(FileNotFoundError):
        validate_input_file(tmp_path / "missing.csv")


def test_validate_input_file_accepts_existing_dataset(
    tmp_path: Path,
) -> None:
    """An existing integrated dataset must pass validation."""
    path = tmp_path / "integrated.csv"
    path.write_text("date\n", encoding="utf-8")

    validate_input_file(path)


def test_safe_cv_returns_expected_value() -> None:
    """Coefficient of variation should be standard deviation divided by mean."""
    series = pd.Series([10.0, 20.0, 30.0])

    expected = series.std(ddof=1) / series.mean()

    assert safe_cv(series) == pytest.approx(expected)


def test_safe_cv_handles_zero_mean() -> None:
    """Zero-mean data should not cause division by zero."""
    series = pd.Series([0.0, 0.0, 0.0])

    assert np.isnan(safe_cv(series))


def test_pair_moments_match_whole_array_statistics() -> None:
    """Streaming moments must reproduce whole-array statistics."""
    generator = np.random.default_rng(20240918)
    x = generator.normal(50.0, 12.0, size=5_000)
    y = (0.4 * x) + generator.normal(0.0, 3.0, size=5_000)

    moments = PairMoments()
    moments.update(x, y)

    expected_r, expected_p = stats.pearsonr(x, y)
    expected_slope, expected_intercept, expected_rvalue, _, _ = (
        stats.linregress(x, y)
    )

    assert moments.count == 5_000
    assert moments.mean_x == pytest.approx(float(x.mean()))
    assert moments.mean_y == pytest.approx(float(y.mean()))
    assert moments.correlation == pytest.approx(expected_r, rel=1e-12)
    assert moments.covariance == pytest.approx(
        float(np.cov(x, y, ddof=1)[0, 1]),
        rel=1e-12,
    )
    assert moments.slope == pytest.approx(expected_slope, rel=1e-12)
    assert moments.intercept == pytest.approx(expected_intercept, rel=1e-9)
    assert moments.r_squared == pytest.approx(expected_rvalue**2, rel=1e-12)
    assert moments.p_value == pytest.approx(expected_p, rel=1e-6)


def test_pair_moments_are_chunk_independent() -> None:
    """Splitting the same observations into chunks must not change results."""
    generator = np.random.default_rng(7)
    x = generator.normal(0.0, 5.0, size=503)
    y = generator.normal(0.0, 5.0, size=503)

    single = PairMoments()
    single.update(x, y)

    chunked = PairMoments()

    for start in range(0, 503, 7):
        chunked.update(x[start : start + 7], y[start : start + 7])

    assert chunked.count == single.count
    assert chunked.mean_x == pytest.approx(single.mean_x, rel=1e-12)
    assert chunked.mean_y == pytest.approx(single.mean_y, rel=1e-12)
    assert chunked.correlation == pytest.approx(
        single.correlation,
        rel=1e-12,
    )
    assert chunked.covariance == pytest.approx(
        single.covariance,
        rel=1e-12,
    )
    assert chunked.slope == pytest.approx(single.slope, rel=1e-12)


def test_pair_moments_handle_single_observation() -> None:
    """One observation cannot define a correlation."""
    moments = PairMoments()
    moments.update(
        np.array([1.0]),
        np.array([2.0]),
    )

    assert moments.count == 1
    assert np.isnan(moments.correlation)
    assert np.isnan(moments.covariance)
    assert np.isnan(moments.slope)
    assert np.isnan(moments.p_value)


def test_pair_moments_treat_negligible_variation_as_undefined() -> None:
    """A variable without usable variation cannot produce a coefficient."""
    moments = PairMoments()
    moments.update(
        np.full(20, 0.15),
        np.arange(20, dtype=float),
    )

    assert moments.variance_y_sum > 0
    assert np.isnan(moments.correlation)
    assert np.isnan(moments.slope)


def test_pair_moments_handle_constant_series() -> None:
    """A constant series has no covariance and undefined correlation."""
    moments = PairMoments()
    moments.update(
        np.array([1.0, 1.0, 1.0]),
        np.array([1.0, 2.0, 3.0]),
    )

    assert np.isnan(moments.correlation)
    assert np.isnan(moments.slope)
    assert moments.covariance == pytest.approx(0.0)


def test_pair_moments_handle_empty_update() -> None:
    """An empty chunk must leave the accumulator untouched."""
    moments = PairMoments()
    moments.update(np.array([]), np.array([]))

    assert moments.count == 0


def test_aggregate_chunks_builds_expected_grains(tmp_path: Path) -> None:
    """Aggregation must produce the documented analytical grains."""
    frame = integrated_fixture(rows=40)
    path = write_dataset(frame, tmp_path / "integrated.csv")

    streams = aggregate_chunks(path)

    assert len(streams.daily) == 40
    assert len(streams.store) == 2
    assert len(streams.category) == 2
    assert len(streams.monthly) == 2
    assert set(streams.monthly["year_month"]) == {"2024-01", "2024-02"}
    assert list(streams.daily["date"]) == sorted(streams.daily["date"])


def test_aggregate_chunks_reconciles_rows_and_totals(
    tmp_path: Path,
) -> None:
    """Chunked aggregates must reconcile with the source dataset."""
    frame = integrated_fixture(rows=40)
    path = write_dataset(frame, tmp_path / "integrated.csv")

    streams = aggregate_chunks(path)

    assert streams.counters["rows_read"] == len(frame)
    assert streams.counters["invalid_date_rows"] == 0
    assert int(streams.daily["records"].sum()) == len(frame)
    assert int(streams.monthly["records"].sum()) == len(frame)
    assert float(streams.daily["quantity"].sum()) == pytest.approx(
        float(frame["quantity"].sum())
    )
    assert float(streams.daily["revenue"].sum()) == pytest.approx(
        float(frame["sum_total"].sum())
    )
    assert float(streams.monthly["revenue"].sum()) == pytest.approx(
        float(frame["sum_total"].sum())
    )


def test_aggregate_chunks_is_chunk_size_independent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The same dataset must aggregate identically at any chunk size."""
    frame = integrated_fixture(rows=40)
    path = write_dataset(frame, tmp_path / "integrated.csv")

    reference = aggregate_chunks(path)

    monkeypatch.setattr(stats_module, "CHUNK_SIZE", 3)
    chunked = aggregate_chunks(path)

    pd.testing.assert_frame_equal(chunked.daily, reference.daily)
    pd.testing.assert_frame_equal(chunked.monthly, reference.monthly)
    pd.testing.assert_frame_equal(chunked.store, reference.store)
    pd.testing.assert_frame_equal(chunked.category, reference.category)

    for variable, moments in reference.pair_moments.items():
        assert (
            chunked.pair_moments[variable].count == moments.count
        )
        assert chunked.pair_moments[variable].correlation == pytest.approx(
            moments.correlation,
            rel=1e-12,
            nan_ok=True,
        )


def test_aggregate_chunks_excludes_non_finite_values(
    tmp_path: Path,
) -> None:
    """Non-finite values must be excluded and counted, never silently used."""
    frame = integrated_fixture(rows=20)
    frame.loc[0, "quantity"] = np.inf
    frame.loc[1, "price_base"] = np.nan
    frame.loc[2, "promo_discount_rate"] = np.inf
    frame.loc[4, "promo_discount_rate"] = np.nan

    path = write_dataset(frame, tmp_path / "integrated.csv")
    streams = aggregate_chunks(path)

    assert streams.counters["non_finite_quantity_rows"] == 1
    assert streams.counters["promotion_rate_infinite_excluded"] == 1
    assert streams.counters["promotion_rate_missing_excluded"] == 1

    price_moments = streams.pair_moments["price_base"]

    assert price_moments.count == 18
    assert streams.pair_moments["markdown_quantity"].count == 6


def test_aggregate_chunks_rejects_empty_dataset(tmp_path: Path) -> None:
    """A dataset with headers but no rows cannot be analysed."""
    frame = integrated_fixture(rows=0)
    path = write_dataset(frame, tmp_path / "integrated.csv")

    with pytest.raises(ValueError):
        aggregate_chunks(path)


def test_aggregate_chunks_rejects_missing_columns(tmp_path: Path) -> None:
    """A dataset without the required schema must be rejected."""
    frame = integrated_fixture(rows=5).drop(columns=["sum_total"])
    path = write_dataset(frame, tmp_path / "integrated.csv")

    with pytest.raises(ValueError):
        aggregate_chunks(path)


def test_scatter_sample_is_a_systematic_sample(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The scatter sample must take every n-th eligible record."""
    frame = integrated_fixture(rows=40)
    path = write_dataset(frame, tmp_path / "integrated.csv")

    monkeypatch.setattr(stats_module, "SCATTER_SAMPLE_STEP", 4)
    monkeypatch.setattr(stats_module, "CHUNK_SIZE", 7)

    streams = aggregate_chunks(path)

    expected_prices = frame["price_base"].to_numpy(dtype=float)[::4]
    expected_quantities = frame["quantity"].to_numpy(dtype=float)[::4]

    assert streams.scatter_prices.size == expected_prices.size
    assert np.array_equal(streams.scatter_prices, expected_prices)
    assert np.array_equal(
        streams.scatter_quantities,
        expected_quantities,
    )


def test_promotion_presence_groups_partition_rows(tmp_path: Path) -> None:
    """Promoted and unpromoted groups must cover every usable row."""
    path = write_dataset(
        promotion_dataset(),
        tmp_path / "integrated.csv",
    )

    streams = aggregate_chunks(path)

    present = streams.present_quantities.size
    absent = streams.absent_quantities.size

    assert present + absent == 14
    assert present == 9
    assert absent == 5


def test_promotion_analysis_labels_presence_comparison(
    tmp_path: Path,
) -> None:
    """The primary comparison must group by presence of a discount record."""
    path = write_dataset(
        promotion_dataset(),
        tmp_path / "integrated.csv",
    )

    streams = aggregate_chunks(path)
    result = calculate_promotion_analysis(**promotion_arguments(streams))

    presence = result[
        result["comparison"] == "promotion_record_presence"
    ]

    assert list(presence["promotion_group"]) == [
        "promotion_record_present",
        "promotion_record_absent",
    ]
    assert list(presence["observations"]) == [9, 5]
    assert list(result.columns) == PROMOTION_COLUMNS


def test_promotion_rate_sign_breakdown_excludes_non_finite(
    tmp_path: Path,
) -> None:
    """Only finite discount rates may define the rate-sign groups."""
    path = write_dataset(
        promotion_dataset(),
        tmp_path / "integrated.csv",
    )

    streams = aggregate_chunks(path)
    result = calculate_promotion_analysis(**promotion_arguments(streams))

    sign = result[result["comparison"] == "promotion_rate_sign"]

    assert list(sign["promotion_group"]) == [
        "promotion_rate_positive",
        "promotion_rate_non_positive",
    ]
    assert list(sign["observations"]) == [4, 3]

    assert streams.counters["promotion_rate_infinite_excluded"] == 2
    assert (
        streams.positive_rate_quantities.size
        + streams.non_positive_rate_quantities.size
        + streams.counters["promotion_rate_infinite_excluded"]
        + streams.counters["promotion_rate_missing_excluded"]
        == streams.present_quantities.size
    )


def test_promotion_analysis_matches_manual_statistics(
    tmp_path: Path,
) -> None:
    """Group statistics must match directly calculated values."""
    path = write_dataset(
        promotion_dataset(),
        tmp_path / "integrated.csv",
    )

    streams = aggregate_chunks(path)
    result = calculate_promotion_analysis(**promotion_arguments(streams))

    presence = result[
        result["comparison"] == "promotion_record_presence"
    ].set_index("promotion_group")

    present = streams.present_quantities
    absent = streams.absent_quantities

    assert presence.loc["promotion_record_present", "mean_quantity"] == (
        pytest.approx(float(present.mean()))
    )
    assert presence.loc["promotion_record_present", "median_quantity"] == (
        pytest.approx(float(np.median(present)))
    )
    assert presence.loc["promotion_record_absent", "mean_quantity"] == (
        pytest.approx(float(absent.mean()))
    )

    expected = stats.mannwhitneyu(
        present,
        absent,
        alternative="two-sided",
    )

    assert presence.loc[
        "promotion_record_present",
        "mann_whitney_u",
    ] == pytest.approx(float(expected.statistic))
    assert presence.loc[
        "promotion_record_present",
        "p_value",
    ] == pytest.approx(float(expected.pvalue))

    assert np.isnan(
        presence.loc["promotion_record_absent", "mean_promo_discount_rate"]
    )
    assert presence.loc[
        "promotion_record_present",
        "mean_promo_discount_rate",
    ] == pytest.approx(float(streams.finite_rates.mean()))


def test_promotion_analysis_handles_empty_groups() -> None:
    """Groups that are too small must not raise or fabricate a test."""
    result = calculate_promotion_analysis(
        np.array([1.0, 2.0, 3.0]),
        np.array([]),
        np.array([1.0]),
        np.array([]),
        np.array([0.5]),
    )

    assert len(result) == 4
    assert np.isnan(
        result.loc[
            result["promotion_group"] == "promotion_record_absent",
            "mean_quantity",
        ].iloc[0]
    )
    assert result["mann_whitney_u"].isna().all()
    assert result["p_value"].isna().all()


def test_calculate_correlations_schema_and_ordering(
    tmp_path: Path,
) -> None:
    """Correlation output must be ordered by absolute correlation."""
    path = write_dataset(
        integrated_fixture(rows=40),
        tmp_path / "integrated.csv",
    )

    streams = aggregate_chunks(path)
    result = calculate_correlations(streams.pair_moments)

    assert list(result.columns) == CORRELATION_COLUMNS
    assert len(result) == len(streams.pair_moments)
    assert (
        result["absolute_correlation"]
        .dropna()
        .is_monotonic_decreasing
    )
    assert result["observations"].tolist() == [
        streams.pair_moments[variable].count
        for variable in result["variable"]
    ]

    price_row = result[result["variable"] == "price_base"].iloc[0]

    assert price_row["covariance"] == pytest.approx(
        streams.pair_moments["price_base"].covariance
    )
    assert abs(price_row["pearson_r"]) <= 1.0


def test_calculate_correlations_skips_insufficient_observations() -> None:
    """Variables without enough paired observations are not reported."""
    moments = {"price_base": PairMoments()}
    moments["price_base"].update(np.array([1.0]), np.array([2.0]))

    result = calculate_correlations(moments)

    assert result.empty
    assert list(result.columns) == CORRELATION_COLUMNS


def test_price_analysis_matches_scipy_regression() -> None:
    """Price-demand regression statistics must match scipy."""
    generator = np.random.default_rng(11)
    prices = generator.normal(100.0, 20.0, size=2_000)
    quantities = (500.0 - 1.5 * prices) + generator.normal(0.0, 4.0, 2_000)

    moments = PairMoments()
    moments.update(prices, quantities)

    result = calculate_price_analysis(moments).iloc[0]

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        prices,
        quantities,
    )

    assert result["observations"] == 2_000
    assert result["slope"] == pytest.approx(slope, rel=1e-12)
    assert result["intercept"] == pytest.approx(intercept, rel=1e-9)
    assert result["r_squared"] == pytest.approx(r_value**2, rel=1e-12)
    assert result["pearson_r"] == pytest.approx(r_value, rel=1e-12)
    assert result["p_value"] == pytest.approx(p_value, rel=1e-6)


def test_price_analysis_regresses_quantity_on_price(tmp_path: Path) -> None:
    """Demand must be the regression response and price the predictor."""
    generator = np.random.default_rng(3)
    prices = generator.normal(50.0, 8.0, size=60)

    frame = integrated_fixture(rows=60)
    frame["price_base"] = prices
    frame["quantity"] = (
        200.0 - (1.8 * prices) + generator.normal(0.0, 2.0, 60)
    )
    frame["sum_total"] = frame["quantity"] * frame["price_base"]

    path = write_dataset(frame, tmp_path / "integrated.csv")
    streams = aggregate_chunks(path)

    result = calculate_price_analysis(
        streams.pair_moments["price_base"]
    ).iloc[0]

    slope, intercept, r_value, _, _ = stats.linregress(
        frame["price_base"],
        frame["quantity"],
    )

    assert result["slope"] == pytest.approx(slope, rel=1e-9)
    assert result["intercept"] == pytest.approx(intercept, rel=1e-9)
    assert result["pearson_r"] == pytest.approx(r_value, rel=1e-9)


def test_price_analysis_returns_empty_frame_when_insufficient() -> None:
    """Price analysis needs at least three paired observations."""
    moments = PairMoments()
    moments.update(np.array([1.0, 2.0]), np.array([2.0, 4.0]))

    assert calculate_price_analysis(moments).empty


def test_autocorrelation_uses_integer_lags(tmp_path: Path) -> None:
    """Autocorrelation output must contain one integer row per lag."""
    path = write_dataset(
        integrated_fixture(rows=40),
        tmp_path / "integrated.csv",
    )

    daily = aggregate_chunks(path).daily
    result = calculate_autocorrelation(daily, max_lag=5)

    assert result["lag_days"].tolist() == [1, 2, 3, 4, 5]
    assert result["lag_days"].dtype.kind == "i"

    for lag in range(1, 6):
        expected = daily["quantity"].autocorr(lag=lag)

        assert result.loc[
            result["lag_days"] == lag,
            "autocorrelation",
        ].iloc[0] == pytest.approx(expected)


def test_trend_matches_linregress_and_adds_robust_errors(
    tmp_path: Path,
) -> None:
    """The trend must report OLS values plus HAC-robust inference."""
    path = write_dataset(
        integrated_fixture(rows=40),
        tmp_path / "integrated.csv",
    )

    daily = aggregate_chunks(path).daily
    result = calculate_trend(daily).iloc[0]

    x = np.arange(len(daily), dtype=float)
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        x,
        daily["quantity"].to_numpy(dtype=float),
    )

    assert list(calculate_trend(daily).columns) == TREND_COLUMNS
    assert result["observations"] == len(daily)
    assert result["slope_per_day"] == pytest.approx(slope, rel=1e-12)
    assert result["intercept"] == pytest.approx(intercept, rel=1e-9)
    assert result["r_squared"] == pytest.approx(r_value**2, rel=1e-12)
    assert result["p_value"] == pytest.approx(p_value, rel=1e-12)
    assert result["standard_error"] == pytest.approx(std_err, rel=1e-12)
    assert np.isfinite(result["hac_standard_error"])
    assert np.isfinite(result["hac_p_value"])
    assert result["hac_standard_error"] > 0
    assert result["hac_max_lags"] == min(
        stats_module.HAC_MAX_LAGS,
        len(daily) - 1,
    )


def test_trend_returns_empty_frame_for_short_series() -> None:
    """Trend estimation needs at least three daily observations."""
    daily = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=2),
            "quantity": [1.0, 2.0],
        }
    )

    result = calculate_trend(daily)

    assert result.empty
    assert list(result.columns) == TREND_COLUMNS


def test_store_shares_sum_to_one(tmp_path: Path) -> None:
    """Store demand shares must sum to one."""
    path = write_dataset(
        integrated_fixture(rows=40),
        tmp_path / "integrated.csv",
    )

    store = add_store_shares(aggregate_chunks(path).store)

    assert "quantity_share" in store.columns
    assert float(store["quantity_share"].sum()) == pytest.approx(1.0)


def test_store_shares_handle_zero_total() -> None:
    """A store table without demand must not divide by zero."""
    store = pd.DataFrame(
        {
            "store_id": [1, 2],
            "quantity": [0.0, 0.0],
            "revenue": [0.0, 0.0],
            "records": [0, 0],
        }
    )

    result = add_store_shares(store)

    assert result["quantity_share"].isna().all()


def quality_inputs(
    tmp_path: Path,
    rows: int = 40,
) -> tuple[
    stats_module.Streams,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Build the frames required by the quality report."""
    path = write_dataset(
        integrated_fixture(rows=rows),
        tmp_path / "integrated.csv",
    )

    streams = aggregate_chunks(path)
    correlations = calculate_correlations(streams.pair_moments)
    price = calculate_price_analysis(streams.pair_moments["price_base"])
    promotion = calculate_promotion_analysis(**promotion_arguments(streams))
    autocorrelation = calculate_autocorrelation(streams.daily)
    trend = calculate_trend(streams.daily)

    return streams, correlations, price, promotion, autocorrelation, trend


def test_quality_report_records_reconciliation(tmp_path: Path) -> None:
    """The quality report must evidence the framework's checks."""
    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    report = build_quality_report(
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
        4,
    )

    metrics = dict(report.itertuples(index=False))

    assert metrics["rows_read"] == 40
    assert metrics["daily_records"] == 40
    assert metrics["daily_record_rows"] == 40
    assert metrics["monthly_records"] == 40
    assert metrics["monthly_records_reconciled"] is True
    assert metrics["quantity_reconciled"] is True
    assert metrics["revenue_reconciled"] is True
    assert (
        metrics["correlations_in_valid_range"]
        + metrics["correlations_not_computed"]
        == len(correlations)
    )
    assert metrics["observations_price_base"] == 40
    assert metrics["excluded_price_base"] == 0
    assert metrics["regression_outputs_finite"] is True
    assert metrics["trend_outputs_finite"] is True
    assert metrics["autocorrelation_outputs_finite"] is True
    assert metrics["promotion_records_reconciled"] is True
    assert metrics["promotion_rate_rows_reconciled"] is True
    assert metrics["scatter_sample_points"] == 2
    assert metrics["figures_written"] == 4
    assert metrics["invalid_date_rows"] == 0
    assert metrics["missing_calendar_days"] == 0


def test_quality_report_reconciles_monthly_records_with_rows(
    tmp_path: Path,
) -> None:
    """Monthly records must be reconciled against rows, not against days."""
    frame = integrated_fixture(rows=40)
    frame["date"] = "2024-01-01"

    path = write_dataset(frame, tmp_path / "integrated.csv")
    streams = aggregate_chunks(path)

    correlations = calculate_correlations(streams.pair_moments)
    price = calculate_price_analysis(streams.pair_moments["price_base"])
    promotion = calculate_promotion_analysis(
        **promotion_arguments(streams)
    )
    autocorrelation = calculate_autocorrelation(streams.daily)
    trend = calculate_trend(streams.daily)

    report = build_quality_report(
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
        4,
    )

    metrics = dict(report.itertuples(index=False))

    assert metrics["daily_records"] == 1
    assert metrics["daily_record_rows"] == 40
    assert metrics["monthly_records"] == 40
    assert metrics["monthly_records_reconciled"] is True


def test_quality_report_flags_mismatched_monthly_totals(
    tmp_path: Path,
) -> None:
    """A monthly total that disagrees with the daily total must be flagged."""
    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    streams.monthly.loc[0, "records"] += 1

    report = build_quality_report(
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
        4,
    )

    metrics = dict(report.itertuples(index=False))

    assert metrics["monthly_records_reconciled"] is False


def test_quality_report_flags_non_finite_outputs(tmp_path: Path) -> None:
    """Non-finite regression output must fail the framework's check."""
    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    price.loc[0, "slope"] = np.inf

    report = build_quality_report(
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
        4,
    )

    metrics = dict(report.itertuples(index=False))

    assert metrics["regression_outputs_finite"] is False


def test_findings_report_never_prints_an_impossible_p_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Underflowed p-values must be reported as a bound, not as zero."""
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", tmp_path)

    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    correlations.loc[0, "p_value"] = 0.0
    price.loc[0, "p_value"] = 0.0
    trend.loc[0, "p_value"] = 0.0

    summary = calculate_summary(streams.daily, streams.store)

    write_findings(
        summary,
        trend,
        correlations,
        price,
        promotion,
        autocorrelation,
    )

    text = (tmp_path / "statistical_findings.txt").read_text(
        encoding="utf-8",
    )

    assert "< 1e-300" in text
    assert "p=0.0" not in text
    assert "- p-value: 0.0" not in text


def test_findings_report_formats_numbers_for_reading(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Findings must not leak floating-point artefacts or float lags."""
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", tmp_path)

    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    summary = calculate_summary(streams.daily, streams.store)

    write_findings(
        summary,
        trend,
        correlations,
        price,
        promotion,
        autocorrelation,
    )

    text = (tmp_path / "statistical_findings.txt").read_text(
        encoding="utf-8",
    )

    assert not re.search(r"\d+\.\d{10,}", text)
    assert re.search(r"- lag_days: \d+$", text, flags=re.MULTILINE)
    assert not re.search(r"- lag_days: \d+\.0$", text, flags=re.MULTILINE)


def test_findings_report_documents_promotion_comparisons(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both promotion comparisons must be documented in the findings."""
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", tmp_path)

    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    summary = calculate_summary(streams.daily, streams.store)

    write_findings(
        summary,
        trend,
        correlations,
        price,
        promotion,
        autocorrelation,
    )

    text = (tmp_path / "statistical_findings.txt").read_text(
        encoding="utf-8",
    )

    assert "comparison: promotion_record_presence" in text
    assert "comparison: promotion_rate_sign" in text
    assert "promotion_record_absent" in text
    assert "not be interpreted as causation" in text


def test_format_helpers_handle_edge_cases() -> None:
    """Formatting helpers must be stable for zero, NaN and tiny values."""
    assert format_metric(154068.88199999998) == "154068.882"
    assert format_metric(0.0) == "0"
    assert format_metric(0.00001) == "1e-05"
    assert format_metric(float("nan")) == "nan"
    assert format_statistic(-0.04442191209544705) == "-0.0444219"
    assert format_statistic(0.0) == "0"
    assert format_p_value(0.0) == "< 1e-300"
    assert format_p_value(7.914481840229211e-07) == "7.91e-07"
    assert format_p_value(float("nan")) == "not computed"
    assert format_summary_value(40) == "40"
    assert format_summary_value(np.float64(41949529.91)) == "41949529.91"
    assert format_summary_value(pd.Timestamp("2024-01-01").date()) == (
        "2024-01-01"
    )


def test_create_figures_writes_every_figure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Figure generation must write the documented charts."""
    monkeypatch.setattr(stats_module, "FIGURE_DIR", tmp_path / "figures")

    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    store = add_store_shares(streams.store)

    written = create_figures(
        streams.daily,
        store,
        price,
        autocorrelation,
        streams.scatter_prices,
        streams.scatter_quantities,
    )

    assert written == 4

    figures = sorted((tmp_path / "figures").glob("statistical_*.png"))

    assert len(figures) == 4

    for figure in figures:
        assert figure.stat().st_size > 0


def test_create_figures_skips_scatter_without_sample(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without a scatter sample no price/demand figure is produced."""
    monkeypatch.setattr(stats_module, "FIGURE_DIR", tmp_path / "figures")

    (
        streams,
        correlations,
        price,
        promotion,
        autocorrelation,
        trend,
    ) = quality_inputs(tmp_path)

    store = add_store_shares(streams.store)

    written = create_figures(
        streams.daily,
        store,
        price,
        autocorrelation,
        np.empty(0, dtype=float),
        np.empty(0, dtype=float),
    )

    assert written == 3


def test_main_runs_the_complete_workflow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The workflow must produce every documented output."""
    input_path = write_dataset(
        integrated_fixture(rows=40),
        tmp_path / "integrated.csv",
    )
    output_dir = tmp_path / "analysis"
    figure_dir = tmp_path / "figures"

    monkeypatch.setattr(stats_module, "INPUT_PATH", input_path)
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(stats_module, "FIGURE_DIR", figure_dir)

    stats_module.main()

    expected = [
        "statistical_summary.csv",
        "statistical_correlations.csv",
        "statistical_store_analysis.csv",
        "statistical_category_analysis.csv",
        "statistical_price_demand.csv",
        "statistical_promotion_analysis.csv",
        "statistical_autocorrelation.csv",
        "statistical_trend.csv",
        "statistical_monthly_activity.csv",
        "statistical_quality_report.csv",
        "statistical_findings.txt",
    ]

    for filename in expected:
        path = output_dir / filename

        assert path.exists(), filename
        assert path.stat().st_size > 0, filename

    assert len(list(figure_dir.glob("statistical_*.png"))) == 4

    store = pd.read_csv(output_dir / "statistical_store_analysis.csv")

    assert "quantity_share" in store.columns

    monthly = pd.read_csv(output_dir / "statistical_monthly_activity.csv")

    assert list(monthly.columns) == [
        "year_month",
        "records",
        "distinct_items",
        "distinct_stores",
        "quantity",
        "revenue",
    ]

    promotion = pd.read_csv(
        output_dir / "statistical_promotion_analysis.csv"
    )

    assert set(promotion["comparison"]) == {
        "promotion_record_presence",
        "promotion_rate_sign",
    }

    quality = pd.read_csv(output_dir / "statistical_quality_report.csv")

    metrics = dict(quality.itertuples(index=False))

    assert int(metrics["rows_read"]) == 40
    assert str(metrics["monthly_records_reconciled"]) == "True"


def test_main_fails_without_input(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The workflow must stop when the integrated dataset is missing."""
    monkeypatch.setattr(
        stats_module,
        "INPUT_PATH",
        tmp_path / "missing.csv",
    )
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", tmp_path / "analysis")
    monkeypatch.setattr(stats_module, "FIGURE_DIR", tmp_path / "figures")

    with pytest.raises(FileNotFoundError):
        stats_module.main()
