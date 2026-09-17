"""Perform statistical and analytical analysis of integrated retail demand data.

The script processes the large integrated dataset in chunks and produces
statistical summaries suitable for demand-forecasting decisions.

The analysis is descriptive and inferential. It does not train forecasting
models and does not create final forecasting features.

Every reported statistic is calculated from the complete integrated dataset.
Chunk-level centered sums are combined with stable parallel-accumulation
formulas, so the full dataset is never loaded into memory and no reported
statistic is computed from a sample. The only sampled artifact is the
price/demand scatter figure, which uses a deterministic systematic sample
(every SCATTER_SAMPLE_STEP-th eligible record) so that the figure spans the
complete date range instead of a contiguous block of the file.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "integrated_retail_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"

# Peak memory scales with the chunk size; 100,000 rows was measured to use
# about 24% less memory than 250,000 rows at the same runtime.
CHUNK_SIZE = 100_000
SCATTER_SAMPLE_STEP = 37
P_VALUE_FLOOR = 1e-300
HAC_MAX_LAGS = 14
MIN_PAIR_OBSERVATIONS = 3

RECONCILIATION_RELATIVE_TOLERANCE = 1e-12
RECONCILIATION_ABSOLUTE_TOLERANCE = 1e-6
DEGENERATE_VARIANCE_TOLERANCE = 1e-12

REQUIRED_COLUMNS = {
    "date",
    "item_id",
    "quantity",
    "price_base",
    "sum_total",
    "store_id",
}

OPTIONAL_COLUMNS = {
    "dept_name",
    "markdown_quantity",
    "markdown_record_count",
    "markdown_discount",
    "discount_record_count",
    "promo_discount_rate",
    "price_change_count",
    "online_quantity",
    "online_sales_value",
}

ANALYSIS_VARIABLES = (
    "price_base",
    "markdown_quantity",
    "markdown_discount",
    "promo_discount_rate",
    "markdown_record_count",
    "discount_record_count",
    "price_change_count",
    "online_quantity",
    "online_sales_value",
)

CORRELATION_COLUMNS = [
    "variable",
    "observations",
    "pearson_r",
    "covariance",
    "p_value",
    "absolute_correlation",
]

PRICE_COLUMNS = [
    "observations",
    "pearson_r",
    "p_value",
    "slope",
    "intercept",
    "r_squared",
]

PROMOTION_COLUMNS = [
    "comparison",
    "promotion_group",
    "observations",
    "mean_quantity",
    "median_quantity",
    "mean_promo_discount_rate",
    "mann_whitney_u",
    "p_value",
]

TREND_COLUMNS = [
    "observations",
    "slope_per_day",
    "intercept",
    "r_squared",
    "p_value",
    "standard_error",
    "hac_standard_error",
    "hac_p_value",
    "hac_max_lags",
]

MONTHLY_COLUMNS = [
    "year_month",
    "records",
    "distinct_items",
    "distinct_stores",
    "quantity",
    "revenue",
]


def validate_columns(columns: list[str]) -> None:
    """Validate the minimum schema required by the analysis."""
    missing = REQUIRED_COLUMNS.difference(columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )


def validate_input_file(input_path: Path | None = None) -> None:
    """Validate that the integrated dataset exists before analysis."""
    path = Path(input_path) if input_path is not None else INPUT_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Integrated dataset not found: {path}. "
            "Run scripts/integrate_retail_data.py (Phase 6) first."
        )


def safe_cv(series: pd.Series) -> float:
    """Return coefficient of variation, or NaN when undefined."""
    mean = series.mean()
    if pd.isna(mean) or mean == 0:
        return float("nan")

    return float(series.std(ddof=1) / mean)


def _concatenate(parts: list[np.ndarray]) -> np.ndarray:
    """Combine per-chunk arrays into one contiguous array."""
    if not parts:
        return np.empty(0, dtype=float)

    return np.concatenate(parts)


class PairMoments:
    """Numerically stable streaming moments for one variable pair.

    Each chunk contributes its own centered sums, which are then merged with
    the parallel-accumulation formula. Centering inside the chunk removes the
    cancellation that makes naive "sum of squares" accumulation inaccurate on
    large datasets, so the resulting correlation, covariance and regression
    statistics agree with a whole-array calculation without ever retaining the
    observations.
    """

    __slots__ = (
        "count",
        "mean_x",
        "mean_y",
        "covariance_sum",
        "variance_x_sum",
        "variance_y_sum",
    )

    def __init__(self) -> None:
        self.count = 0
        self.mean_x = 0.0
        self.mean_y = 0.0
        self.covariance_sum = 0.0
        self.variance_x_sum = 0.0
        self.variance_y_sum = 0.0

    def update(self, x: np.ndarray, y: np.ndarray) -> None:
        """Merge one chunk of paired observations."""
        count = int(x.size)

        if count == 0:
            return

        mean_x = float(x.mean())
        mean_y = float(y.mean())

        offset_x = x - mean_x
        offset_y = y - mean_y

        self._merge(
            count,
            mean_x,
            mean_y,
            float(offset_x @ offset_y),
            float(offset_x @ offset_x),
            float(offset_y @ offset_y),
        )

    def _merge(
        self,
        count: int,
        mean_x: float,
        mean_y: float,
        covariance_sum: float,
        variance_x_sum: float,
        variance_y_sum: float,
    ) -> None:
        """Combine a partial accumulation with the running totals."""
        if count == 0:
            return

        if self.count == 0:
            self.count = count
            self.mean_x = mean_x
            self.mean_y = mean_y
            self.covariance_sum = covariance_sum
            self.variance_x_sum = variance_x_sum
            self.variance_y_sum = variance_y_sum
            return

        total = self.count + count
        weight = (self.count * count) / total

        delta_x = mean_x - self.mean_x
        delta_y = mean_y - self.mean_y

        self.covariance_sum += covariance_sum + (delta_x * delta_y * weight)
        self.variance_x_sum += variance_x_sum + (delta_x * delta_x * weight)
        self.variance_y_sum += variance_y_sum + (delta_y * delta_y * weight)

        self.mean_x += delta_x * (count / total)
        self.mean_y += delta_y * (count / total)
        self.count = total

    def _carries_variation(self, variance_sum: float, mean: float) -> bool:
        """Report whether a variable has variation that can be correlated.

        A constant variable has no correlation, but rounding in the estimated
        mean can leave a variance that is tiny yet non-zero. Such a variance
        carries no information, so it is treated as undefined instead of
        producing a meaningless coefficient.
        """
        if variance_sum <= 0.0:
            return False

        scale = mean * mean * self.count

        if scale <= 0.0:
            return True

        return variance_sum > (DEGENERATE_VARIANCE_TOLERANCE * scale)

    @property
    def correlation(self) -> float:
        """Return the Pearson correlation, or NaN when undefined."""
        if self.count < 2:
            return float("nan")

        if not self._carries_variation(self.variance_x_sum, self.mean_x):
            return float("nan")

        if not self._carries_variation(self.variance_y_sum, self.mean_y):
            return float("nan")

        return self.covariance_sum / math.sqrt(
            self.variance_x_sum * self.variance_y_sum
        )

    @property
    def covariance(self) -> float:
        """Return the sample covariance (ddof=1), or NaN when undefined."""
        if self.count < 2:
            return float("nan")

        return self.covariance_sum / (self.count - 1)

    @property
    def slope(self) -> float:
        """Return the least-squares slope of y on x."""
        if self.count < 2:
            return float("nan")

        if not self._carries_variation(self.variance_x_sum, self.mean_x):
            return float("nan")

        return self.covariance_sum / self.variance_x_sum

    @property
    def intercept(self) -> float:
        """Return the least-squares intercept of y on x."""
        slope = self.slope

        if not math.isfinite(slope):
            return float("nan")

        return self.mean_y - (slope * self.mean_x)

    @property
    def r_squared(self) -> float:
        """Return the coefficient of determination."""
        correlation = self.correlation

        if not math.isfinite(correlation):
            return float("nan")

        return correlation * correlation

    @property
    def p_value(self) -> float:
        """Return the two-sided p-value for the correlation."""
        correlation = self.correlation

        if self.count < 3 or not math.isfinite(correlation):
            return float("nan")

        if abs(correlation) >= 1.0:
            return 0.0

        degrees_of_freedom = self.count - 2

        statistic = abs(correlation) * math.sqrt(
            degrees_of_freedom / (1.0 - correlation * correlation)
        )

        return float(2.0 * stats.t.sf(statistic, degrees_of_freedom))


@dataclass
class Streams:
    """Chunked aggregation results for the integrated dataset."""

    daily: pd.DataFrame
    store: pd.DataFrame
    category: pd.DataFrame
    monthly: pd.DataFrame
    pair_moments: dict[str, PairMoments]
    present_quantities: np.ndarray
    absent_quantities: np.ndarray
    positive_rate_quantities: np.ndarray
    non_positive_rate_quantities: np.ndarray
    finite_rates: np.ndarray
    scatter_prices: np.ndarray
    scatter_quantities: np.ndarray
    counters: dict[str, int]


def aggregate_chunks(input_path: Path) -> Streams:
    """Aggregate the large integrated dataset into analytical grains."""
    header = pd.read_csv(input_path, nrows=0)
    validate_columns(header.columns.tolist())

    available = set(header.columns)
    usecols = [
        column
        for column in sorted(REQUIRED_COLUMNS | OPTIONAL_COLUMNS)
        if column in available
    ]

    analysis_variables = [
        variable for variable in ANALYSIS_VARIABLES if variable in available
    ]

    numeric_columns = sorted(
        {"quantity", "price_base", "sum_total", *analysis_variables}
    )

    pair_moments = {
        variable: PairMoments() for variable in analysis_variables
    }

    daily_parts: list[pd.DataFrame] = []
    store_parts: list[pd.DataFrame] = []
    category_parts: list[pd.DataFrame] = []

    month_records: dict[str, int] = defaultdict(int)
    month_quantity: dict[str, float] = defaultdict(float)
    month_revenue: dict[str, float] = defaultdict(float)
    month_items: dict[str, set[int]] = defaultdict(set)
    month_stores: dict[str, set[int]] = defaultdict(set)

    promotion_quantities: dict[str, list[np.ndarray]] = {
        group: []
        for group in ("present", "absent", "positive", "non_positive")
    }
    finite_rate_parts: list[np.ndarray] = []
    scatter_prices: list[np.ndarray] = []
    scatter_quantities: list[np.ndarray] = []
    eligible_seen = 0

    counters = {
        "rows_read": 0,
        "invalid_date_rows": 0,
        "non_finite_quantity_rows": 0,
        "promotion_rate_missing_excluded": 0,
        "promotion_rate_infinite_excluded": 0,
    }

    for chunk in pd.read_csv(
        input_path,
        usecols=usecols,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        counters["rows_read"] += len(chunk)

        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")

        for column in numeric_columns:
            chunk[column] = (
                pd.to_numeric(chunk[column], errors="coerce").astype(float)
            )

        valid_dates = chunk["date"].notna()
        counters["invalid_date_rows"] += int((~valid_dates).sum())

        months = chunk["date"].dt.to_period("M").astype(str)
        chunk["year_month"] = months.where(valid_dates, other=pd.NA)

        daily = (
            chunk.groupby("date", as_index=False)
            .agg(
                quantity=("quantity", "sum"),
                revenue=("sum_total", "sum"),
                records=("item_id", "size"),
            )
        )
        daily_parts.append(daily)

        store = (
            chunk.groupby("store_id", as_index=False)
            .agg(
                quantity=("quantity", "sum"),
                revenue=("sum_total", "sum"),
                records=("item_id", "size"),
            )
        )
        store_parts.append(store)

        if "dept_name" in chunk.columns:
            category = (
                chunk.groupby("dept_name", dropna=False, as_index=False)
                .agg(
                    quantity=("quantity", "sum"),
                    revenue=("sum_total", "sum"),
                    records=("item_id", "size"),
                )
            )
            category_parts.append(category)

        for month, month_rows in chunk.groupby(
            "year_month",
            dropna=True,
            sort=False,
        ):
            key = str(month)

            month_records[key] += len(month_rows)
            month_quantity[key] += float(month_rows["quantity"].sum())
            month_revenue[key] += float(month_rows["sum_total"].sum())
            month_items[key].update(
                month_rows["item_id"].dropna().unique().tolist()
            )
            month_stores[key].update(
                month_rows["store_id"].dropna().unique().tolist()
            )

        quantities = chunk["quantity"].to_numpy(dtype=float)
        finite_quantity = np.isfinite(quantities)

        counters["non_finite_quantity_rows"] += int((~finite_quantity).sum())

        for variable, moments in pair_moments.items():
            values = chunk[variable].to_numpy(dtype=float)
            mask = finite_quantity & np.isfinite(values)

            if mask.any():
                # The analytical variable is the explanatory variable and
                # demand is the response, so the price regression estimates
                # quantity as a function of price.
                moments.update(values[mask], quantities[mask])

        if "discount_record_count" in chunk.columns:
            record_counts = chunk[
                "discount_record_count"
            ].to_numpy(dtype=float)

            # Missing or non-finite record counts are treated as "no discount
            # record", so the two presence groups partition the rows with a
            # finite demand value.
            has_record = record_counts > 0

            present = finite_quantity & has_record
            absent = finite_quantity & ~has_record

            promotion_quantities["present"].append(quantities[present])
            promotion_quantities["absent"].append(quantities[absent])

            if "promo_discount_rate" in chunk.columns:
                rates = chunk["promo_discount_rate"].to_numpy(dtype=float)
                finite_rate = np.isfinite(rates)

                counters["promotion_rate_missing_excluded"] += int(
                    (present & np.isnan(rates)).sum()
                )
                counters["promotion_rate_infinite_excluded"] += int(
                    (present & np.isinf(rates)).sum()
                )

                finite_rate_parts.append(rates[present & finite_rate])
                promotion_quantities["positive"].append(
                    quantities[present & finite_rate & (rates > 0)]
                )
                promotion_quantities["non_positive"].append(
                    quantities[present & finite_rate & (rates <= 0)]
                )

        prices = chunk["price_base"].to_numpy(dtype=float)
        scatter_mask = np.isfinite(prices) & finite_quantity
        positions = np.flatnonzero(scatter_mask)

        if positions.size:
            selected = positions + eligible_seen
            chosen = selected[selected % SCATTER_SAMPLE_STEP == 0]

            if chosen.size:
                local = chosen - eligible_seen
                scatter_prices.append(prices[local])
                scatter_quantities.append(quantities[local])

            eligible_seen += positions.size

    if not daily_parts or counters["rows_read"] == 0:
        raise ValueError(f"No rows could be read from {input_path}")

    daily_combined = (
        pd.concat(daily_parts, ignore_index=True)
        .groupby("date", as_index=False)
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            records=("records", "sum"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    store_combined = (
        pd.concat(store_parts, ignore_index=True)
        .groupby("store_id", as_index=False)
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            records=("records", "sum"),
        )
        .sort_values("store_id")
        .reset_index(drop=True)
    )

    if category_parts:
        category_combined = (
            pd.concat(category_parts, ignore_index=True)
            .groupby("dept_name", dropna=False, as_index=False)
            .agg(
                quantity=("quantity", "sum"),
                revenue=("revenue", "sum"),
                records=("records", "sum"),
            )
            .sort_values("quantity", ascending=False)
            .reset_index(drop=True)
        )
    else:
        category_combined = pd.DataFrame(
            columns=["dept_name", "quantity", "revenue", "records"]
        )

    monthly = pd.DataFrame(
        [
            {
                "year_month": month,
                "records": month_records[month],
                "distinct_items": len(month_items[month]),
                "distinct_stores": len(month_stores[month]),
                "quantity": month_quantity[month],
                "revenue": month_revenue[month],
            }
            for month in sorted(month_records)
        ],
        columns=MONTHLY_COLUMNS,
    )

    return Streams(
        daily=daily_combined,
        store=store_combined,
        category=category_combined,
        monthly=monthly,
        pair_moments=pair_moments,
        present_quantities=_concatenate(promotion_quantities["present"]),
        absent_quantities=_concatenate(promotion_quantities["absent"]),
        positive_rate_quantities=_concatenate(
            promotion_quantities["positive"]
        ),
        non_positive_rate_quantities=_concatenate(
            promotion_quantities["non_positive"]
        ),
        finite_rates=_concatenate(finite_rate_parts),
        scatter_prices=_concatenate(scatter_prices),
        scatter_quantities=_concatenate(scatter_quantities),
        counters=counters,
    )


def calculate_summary(
    daily: pd.DataFrame,
    store: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate high-level descriptive statistics."""
    quantity = daily["quantity"]

    return pd.DataFrame(
        [
            ["daily_records", len(daily)],
            ["daily_quantity_total", quantity.sum()],
            ["daily_quantity_mean", quantity.mean()],
            ["daily_quantity_median", quantity.median()],
            ["daily_quantity_std", quantity.std(ddof=1)],
            ["daily_quantity_min", quantity.min()],
            ["daily_quantity_max", quantity.max()],
            ["daily_quantity_cv", safe_cv(quantity)],
            ["daily_revenue_total", daily["revenue"].sum()],
            ["store_count", len(store)],
            ["date_min", daily["date"].min().date()],
            ["date_max", daily["date"].max().date()],
        ],
        columns=["metric", "value"],
    )


def calculate_correlations(
    pair_moments: dict[str, PairMoments],
) -> pd.DataFrame:
    """Calculate Pearson correlations and covariances for the quantity pairs."""
    rows: list[dict[str, object]] = []

    for variable, moments in pair_moments.items():
        if moments.count < MIN_PAIR_OBSERVATIONS:
            continue

        correlation = moments.correlation

        rows.append(
            {
                "variable": variable,
                "observations": moments.count,
                "pearson_r": correlation,
                "covariance": moments.covariance,
                "p_value": moments.p_value,
                "absolute_correlation": abs(correlation),
            }
        )

    return (
        pd.DataFrame(rows, columns=CORRELATION_COLUMNS)
        .sort_values(
            "absolute_correlation",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def calculate_price_analysis(
    moments: PairMoments,
) -> pd.DataFrame:
    """Calculate price-demand correlation and simple regression statistics."""
    if moments.count < MIN_PAIR_OBSERVATIONS:
        return pd.DataFrame(columns=PRICE_COLUMNS)

    return pd.DataFrame(
        [
            {
                "observations": moments.count,
                "pearson_r": moments.correlation,
                "p_value": moments.p_value,
                "slope": moments.slope,
                "intercept": moments.intercept,
                "r_squared": moments.r_squared,
            }
        ],
        columns=PRICE_COLUMNS,
    )


def _promotion_row(
    comparison: str,
    group: str,
    quantities: np.ndarray,
    rates: np.ndarray | None,
    statistic: float,
    p_value: float,
) -> dict[str, object]:
    """Build one promotion-comparison row."""
    has_quantities = quantities.size > 0
    has_rates = rates is not None and rates.size > 0

    return {
        "comparison": comparison,
        "promotion_group": group,
        "observations": int(quantities.size),
        "mean_quantity": (
            float(quantities.mean()) if has_quantities else float("nan")
        ),
        "median_quantity": (
            float(np.median(quantities)) if has_quantities else float("nan")
        ),
        "mean_promo_discount_rate": (
            float(rates.mean()) if has_rates else float("nan")
        ),
        "mann_whitney_u": statistic,
        "p_value": p_value,
    }


def calculate_promotion_analysis(
    present_quantities: np.ndarray,
    absent_quantities: np.ndarray,
    positive_rate_quantities: np.ndarray,
    non_positive_rate_quantities: np.ndarray,
    finite_rates: np.ndarray,
) -> pd.DataFrame:
    """Compare demand across promotion groups.

    The primary comparison follows the phase plan: records with a discount
    record are compared with records without one. A secondary breakdown splits
    the promoted records by the sign of the finite promotional discount rate.

    Only finite discount rates take part in the rate-sign breakdown; records
    with a missing or non-finite rate remain in the primary comparison and are
    counted separately by the quality report.
    """
    rate_groups = {
        "promotion_record_present": finite_rates,
        "promotion_rate_positive": finite_rates[finite_rates > 0],
        "promotion_rate_non_positive": finite_rates[finite_rates <= 0],
    }

    comparisons = (
        (
            "promotion_record_presence",
            "promotion_record_present",
            "promotion_record_absent",
            present_quantities,
            absent_quantities,
        ),
        (
            "promotion_rate_sign",
            "promotion_rate_positive",
            "promotion_rate_non_positive",
            positive_rate_quantities,
            non_positive_rate_quantities,
        ),
    )

    rows: list[dict[str, object]] = []

    for (
        comparison,
        positive_label,
        negative_label,
        positive_values,
        negative_values,
    ) in comparisons:
        statistic = float("nan")
        p_value = float("nan")

        if positive_values.size >= 2 and negative_values.size >= 2:
            test = stats.mannwhitneyu(
                positive_values,
                negative_values,
                alternative="two-sided",
            )
            statistic = float(test.statistic)
            p_value = float(test.pvalue)

        rows.append(
            _promotion_row(
                comparison,
                positive_label,
                positive_values,
                rate_groups.get(positive_label),
                statistic,
                p_value,
            )
        )
        rows.append(
            _promotion_row(
                comparison,
                negative_label,
                negative_values,
                rate_groups.get(negative_label),
                statistic,
                p_value,
            )
        )

    return pd.DataFrame(rows, columns=PROMOTION_COLUMNS)


def calculate_autocorrelation(
    daily: pd.DataFrame,
    max_lag: int = 14,
) -> pd.DataFrame:
    """Calculate autocorrelation of daily demand for recent lags."""
    rows = []

    series = daily["quantity"]

    for lag in range(1, max_lag + 1):
        correlation = series.autocorr(lag=lag)

        rows.append(
            {
                "lag_days": lag,
                "autocorrelation": correlation,
            }
        )

    return pd.DataFrame(rows, columns=["lag_days", "autocorrelation"])


def calculate_trend(
    daily: pd.DataFrame,
) -> pd.DataFrame:
    """Estimate the linear trend in daily aggregate demand.

    Both the ordinary least squares result and a Newey-West (HAC) robust
    result are reported. Daily demand is strongly autocorrelated, so the naive
    OLS standard error and p-value understate the uncertainty of the trend and
    the robust values are the defensible measure.
    """
    if len(daily) < MIN_PAIR_OBSERVATIONS:
        return pd.DataFrame(columns=TREND_COLUMNS)

    x = np.arange(len(daily), dtype=float)
    y = daily["quantity"].to_numpy(dtype=float)

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        x,
        y,
    )

    maxlags = max(1, min(HAC_MAX_LAGS, len(daily) - 1))
    design = sm.add_constant(x)

    robust = sm.OLS(y, design).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": maxlags},
        use_t=True,
    )

    return pd.DataFrame(
        [
            {
                "observations": len(daily),
                "slope_per_day": slope,
                "intercept": intercept,
                "r_squared": r_value**2,
                "p_value": p_value,
                "standard_error": std_err,
                "hac_standard_error": float(robust.bse[1]),
                "hac_p_value": float(robust.pvalues[1]),
                "hac_max_lags": maxlags,
            }
        ],
        columns=TREND_COLUMNS,
    )


def add_store_shares(store: pd.DataFrame) -> pd.DataFrame:
    """Add each store's share of total demand."""
    result = store.copy()
    total = float(result["quantity"].sum())

    if total == 0:
        result["quantity_share"] = float("nan")
    else:
        result["quantity_share"] = result["quantity"] / total

    return result


def _outputs_are_finite(
    frame: pd.DataFrame,
    columns: tuple[str, ...],
) -> bool:
    """Report whether a generated numeric output is present and finite."""
    if frame.empty:
        return False

    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce")

        if not np.isfinite(values.to_numpy(dtype=float)).all():
            return False

    return True


def _reconciles(first: float, second: float) -> bool:
    """Report whether two aggregates agree to floating-point tolerance."""
    return math.isclose(
        float(first),
        float(second),
        rel_tol=RECONCILIATION_RELATIVE_TOLERANCE,
        abs_tol=RECONCILIATION_ABSOLUTE_TOLERANCE,
    )


def _promotion_observations(
    promotion_analysis: pd.DataFrame,
    group: str,
) -> int:
    """Return the observation count recorded for a promotion group."""
    if promotion_analysis.empty:
        return 0

    selected = promotion_analysis[
        promotion_analysis["promotion_group"] == group
    ]

    return int(selected["observations"].sum())


def build_quality_report(
    streams: Streams,
    correlations: pd.DataFrame,
    price_analysis: pd.DataFrame,
    promotion_analysis: pd.DataFrame,
    autocorrelation: pd.DataFrame,
    trend: pd.DataFrame,
    figures_written: int,
) -> pd.DataFrame:
    """Assemble the statistical quality report required by the framework."""
    rows: list[list[object]] = []

    daily = streams.daily
    monthly = streams.monthly
    counters = streams.counters

    daily_quantity = float(daily["quantity"].sum()) if len(daily) else 0.0
    daily_revenue = float(daily["revenue"].sum()) if len(daily) else 0.0
    monthly_quantity = (
        float(monthly["quantity"].sum()) if len(monthly) else 0.0
    )
    monthly_revenue = float(monthly["revenue"].sum()) if len(monthly) else 0.0
    monthly_records = int(monthly["records"].sum()) if len(monthly) else 0

    daily_record_rows = int(daily["records"].sum()) if len(daily) else 0

    rows.append(["rows_read", counters["rows_read"]])
    rows.append(["daily_records", len(daily)])
    rows.append(["daily_record_rows", daily_record_rows])
    rows.append(["monthly_records", monthly_records])
    rows.append(
        [
            "monthly_records_reconciled",
            monthly_records == daily_record_rows,
        ]
    )
    rows.append(["distinct_months", len(monthly)])
    rows.append(["invalid_date_rows", counters["invalid_date_rows"]])
    rows.append(
        ["non_finite_quantity_rows", counters["non_finite_quantity_rows"]]
    )
    rows.append(["minimum_observations_required", MIN_PAIR_OBSERVATIONS])

    if len(daily):
        date_min = daily["date"].min()
        date_max = daily["date"].max()
        calendar_days = int((date_max - date_min).days) + 1

        rows.append(["date_min", date_min.date()])
        rows.append(["date_max", date_max.date()])
        rows.append(["calendar_days", calendar_days])
        rows.append(["missing_calendar_days", calendar_days - len(daily)])

    rows.append(["total_quantity", daily_quantity])
    rows.append(["total_revenue", daily_revenue])
    rows.append(["monthly_quantity_total", monthly_quantity])
    rows.append(["monthly_revenue_total", monthly_revenue])
    rows.append(
        ["quantity_reconciled", _reconciles(daily_quantity, monthly_quantity)]
    )
    rows.append(
        ["revenue_reconciled", _reconciles(daily_revenue, monthly_revenue)]
    )

    for variable, moments in streams.pair_moments.items():
        rows.append([f"observations_{variable}", moments.count])
        rows.append(
            [f"excluded_{variable}", counters["rows_read"] - moments.count]
        )

    correlation_values = (
        correlations["pearson_r"].to_numpy(dtype=float)
        if len(correlations)
        else np.empty(0, dtype=float)
    )
    finite_correlations = np.isfinite(correlation_values)

    rows.append(["correlation_variables", len(correlations)])
    rows.append(
        [
            "correlations_in_valid_range",
            int(
                (finite_correlations & (np.abs(correlation_values) <= 1.0)).sum()
            ),
        ]
    )
    rows.append(
        [
            "correlations_not_computed",
            int((~finite_correlations).sum()),
        ]
    )
    rows.append(
        [
            "p_values_underflowed",
            int(
                (
                    correlations["p_value"].to_numpy(dtype=float)
                    < P_VALUE_FLOOR
                ).sum()
            )
            if len(correlations)
            else 0,
        ]
    )

    rows.append(
        [
            "regression_outputs_finite",
            _outputs_are_finite(
                price_analysis,
                ("pearson_r", "p_value", "slope", "intercept", "r_squared"),
            ),
        ]
    )
    rows.append(
        [
            "autocorrelation_outputs_finite",
            _outputs_are_finite(autocorrelation, ("autocorrelation",)),
        ]
    )
    rows.append(
        [
            "trend_outputs_finite",
            _outputs_are_finite(
                trend,
                (
                    "slope_per_day",
                    "intercept",
                    "r_squared",
                    "p_value",
                    "standard_error",
                    "hac_standard_error",
                    "hac_p_value",
                ),
            ),
        ]
    )

    present = _promotion_observations(
        promotion_analysis,
        "promotion_record_present",
    )
    absent = _promotion_observations(
        promotion_analysis,
        "promotion_record_absent",
    )
    positive = _promotion_observations(
        promotion_analysis,
        "promotion_rate_positive",
    )
    non_positive = _promotion_observations(
        promotion_analysis,
        "promotion_rate_non_positive",
    )

    rows.append(["promotion_records_present", present])
    rows.append(["promotion_records_absent", absent])
    rows.append(
        [
            "promotion_records_reconciled",
            present + absent
            == counters["rows_read"] - counters["non_finite_quantity_rows"],
        ]
    )
    rows.append(["promotion_rate_observations_finite", positive + non_positive])
    rows.append(
        [
            "promotion_rate_missing_excluded",
            counters["promotion_rate_missing_excluded"],
        ]
    )
    rows.append(
        [
            "promotion_rate_infinite_excluded",
            counters["promotion_rate_infinite_excluded"],
        ]
    )
    rows.append(
        [
            "promotion_rate_rows_reconciled",
            positive
            + non_positive
            + counters["promotion_rate_missing_excluded"]
            + counters["promotion_rate_infinite_excluded"]
            == present,
        ]
    )

    rows.append(["scatter_sample_step", SCATTER_SAMPLE_STEP])
    rows.append(
        ["scatter_sample_points", int(streams.scatter_prices.size)]
    )
    rows.append(["p_value_floor", P_VALUE_FLOOR])
    rows.append(["hac_max_lags", HAC_MAX_LAGS])
    rows.append(["figures_written", figures_written])

    return pd.DataFrame(rows, columns=["metric", "value"])


def create_figures(
    daily: pd.DataFrame,
    store: pd.DataFrame,
    price_analysis: pd.DataFrame,
    autocorrelation: pd.DataFrame,
    scatter_prices: np.ndarray,
    scatter_quantities: np.ndarray,
) -> int:
    """Create statistical-analysis figures and report how many were written."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    written = 0

    if not daily.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(daily["date"], daily["quantity"])
        plt.title("Daily Retail Demand")
        plt.xlabel("Date")
        plt.ylabel("Quantity")
        plt.tight_layout()
        plt.savefig(
            FIGURE_DIR / "statistical_demand_trend.png",
            dpi=150,
        )
        plt.close()
        written += 1

    if not store.empty:
        plt.figure(figsize=(10, 6))
        plt.bar(
            store["store_id"].astype(str),
            store["quantity"],
        )
        plt.title("Demand by Store")
        plt.xlabel("Store")
        plt.ylabel("Quantity")
        plt.tight_layout()
        plt.savefig(
            FIGURE_DIR / "statistical_store_variability.png",
            dpi=150,
        )
        plt.close()
        written += 1

    if not price_analysis.empty and scatter_prices.size:
        plt.figure(figsize=(10, 6))
        plt.scatter(
            scatter_prices,
            scatter_quantities,
            s=8,
            alpha=0.25,
        )
        plt.title(
            "Price and Demand Relationship "
            f"(systematic sample, 1 per {SCATTER_SAMPLE_STEP} records)"
        )
        plt.xlabel("Price")
        plt.ylabel("Quantity")
        plt.tight_layout()
        plt.savefig(
            FIGURE_DIR / "statistical_price_demand.png",
            dpi=150,
        )
        plt.close()
        written += 1

    if not autocorrelation.empty:
        plt.figure(figsize=(10, 6))
        plt.bar(
            autocorrelation["lag_days"],
            autocorrelation["autocorrelation"],
        )
        plt.title("Daily Demand Autocorrelation")
        plt.xlabel("Lag (days)")
        plt.ylabel("Autocorrelation")
        plt.tight_layout()
        plt.savefig(
            FIGURE_DIR / "statistical_demand_autocorrelation.png",
            dpi=150,
        )
        plt.close()
        written += 1

    return written


def format_summary_value(value: object) -> str:
    """Format one summary value for presentation."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return str(value)

    return format_metric(float(value))


def format_metric(value: float, digits: int = 3) -> str:
    """Format a magnitude for presentation without floating-point noise."""
    number = float(value)

    if math.isnan(number):
        return "nan"

    if math.isinf(number):
        return "inf" if number > 0 else "-inf"

    if number == 0:
        return "0"

    text = f"{number:.{digits}f}"

    if float(text) == 0.0:
        return f"{number:.{digits}g}"

    return text.rstrip("0").rstrip(".")


def format_statistic(value: float, digits: int = 6) -> str:
    """Format a statistic for presentation using significant digits."""
    number = float(value)

    if math.isnan(number):
        return "nan"

    if math.isinf(number):
        return "inf" if number > 0 else "-inf"

    if number == 0:
        return "0"

    return f"{number:.{digits}g}"


def format_p_value(value: float) -> str:
    """Format a p-value, reporting underflow instead of an impossible zero."""
    number = float(value)

    if math.isnan(number):
        return "not computed"

    if number < P_VALUE_FLOOR:
        return f"< {P_VALUE_FLOOR:.0e}"

    return f"{number:.3g}"


def write_findings(
    summary: pd.DataFrame,
    trend: pd.DataFrame,
    correlations: pd.DataFrame,
    price_analysis: pd.DataFrame,
    promotion_analysis: pd.DataFrame,
    autocorrelation: pd.DataFrame,
) -> None:
    """Write a machine-readable text summary of statistical findings."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "Phase 8 — Statistical & Analytical Analysis",
        "",
        "This file contains automatically generated statistical findings.",
        "Statistical association must not be interpreted as causation.",
        "Every statistic is calculated from the complete integrated dataset;",
        "only the price/demand figure uses a systematic sample.",
        f"Probability values below {P_VALUE_FLOOR:.0e} are reported as",
        f"\"< {P_VALUE_FLOOR:.0e}\" because the computed value underflows double",
        "precision. At this sample size statistical significance is expected",
        "for almost every association and does not by itself indicate",
        "practical importance.",
        "",
        "Summary:",
    ]

    for row in summary.itertuples(index=False):
        lines.append(f"- {row.metric}: {format_summary_value(row.value)}")

    if not trend.empty:
        row = trend.iloc[0]
        lines.extend(
            [
                "",
                "Demand trend:",
                f"- slope_per_day: {format_statistic(row['slope_per_day'])}",
                f"- r_squared: {format_statistic(row['r_squared'])}",
                f"- p_value: {format_p_value(row['p_value'])}",
                "- standard_error (OLS): "
                f"{format_statistic(row['standard_error'])}",
                "- hac_standard_error: "
                f"{format_statistic(row['hac_standard_error'])}",
                f"- hac_p_value: {format_p_value(row['hac_p_value'])}",
                f"- hac_max_lags: {int(row['hac_max_lags'])}",
                "- note: daily demand is autocorrelated, so the HAC values are",
                "  the defensible measure of trend uncertainty.",
            ]
        )

    if not correlations.empty:
        lines.extend(
            [
                "",
                "Strongest numeric associations with quantity:",
            ]
        )

        for row in correlations.head(10).itertuples(index=False):
            lines.append(
                f"- {row.variable}: "
                f"n={int(row.observations)}, "
                f"r={format_statistic(row.pearson_r)}, "
                f"p={format_p_value(row.p_value)}"
            )

    if not price_analysis.empty:
        row = price_analysis.iloc[0]
        lines.extend(
            [
                "",
                "Price-demand relationship:",
                f"- observations: {int(row['observations'])}",
                f"- Pearson r: {format_statistic(row['pearson_r'])}",
                f"- p-value: {format_p_value(row['p_value'])}",
                "- regression slope: "
                f"{format_statistic(row['slope'])}",
                f"- R-squared: {format_statistic(row['r_squared'])}",
                "- note: this is an association, not a causal price elasticity.",
            ]
        )

    if not promotion_analysis.empty:
        lines.extend(
            [
                "",
                "Promotion analysis:",
                "- promotion_record_present groups records with a discount",
                "  record; promotion_record_absent groups records without one.",
                "- promotion_rate_positive and promotion_rate_non_positive split",
                "  the promoted records by the sign of the finite discount rate.",
            ]
        )

        for comparison, group in promotion_analysis.groupby(
            "comparison",
            sort=False,
        ):
            lines.append(f"- comparison: {comparison}")

            for row in group.itertuples(index=False):
                rate = ""

                if not math.isnan(float(row.mean_promo_discount_rate)):
                    rate = (
                        ", mean_promo_discount_rate="
                        f"{format_statistic(row.mean_promo_discount_rate)}"
                    )

                lines.append(
                    f"  - {row.promotion_group}: "
                    f"n={int(row.observations)}, "
                    f"mean={format_metric(row.mean_quantity)}, "
                    f"median={format_metric(row.median_quantity)}"
                    f"{rate}"
                )

            first = group.iloc[0]

            if not math.isnan(float(first["mann_whitney_u"])):
                lines.append(
                    "  - Mann-Whitney U: "
                    f"{format_statistic(first['mann_whitney_u'])}, "
                    f"p={format_p_value(first['p_value'])}"
                )

    if not autocorrelation.empty:
        strongest = autocorrelation.loc[
            autocorrelation["autocorrelation"]
            .abs()
            .idxmax()
        ]

        lines.extend(
            [
                "",
                "Strongest recent demand autocorrelation:",
                f"- lag_days: {int(strongest['lag_days'])}",
                "- autocorrelation: "
                f"{format_statistic(strongest['autocorrelation'])}",
            ]
        )

    (OUTPUT_DIR / "statistical_findings.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run the complete statistical-analysis workflow."""
    print("Running statistical and analytical analysis...")

    validate_input_file()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    streams = aggregate_chunks(INPUT_PATH)

    summary = calculate_summary(streams.daily, streams.store)
    store = add_store_shares(streams.store)
    correlations = calculate_correlations(streams.pair_moments)
    price_analysis = calculate_price_analysis(
        streams.pair_moments.get("price_base", PairMoments())
    )
    promotion_analysis = calculate_promotion_analysis(
        streams.present_quantities,
        streams.absent_quantities,
        streams.positive_rate_quantities,
        streams.non_positive_rate_quantities,
        streams.finite_rates,
    )
    autocorrelation = calculate_autocorrelation(streams.daily)
    trend = calculate_trend(streams.daily)

    outputs = {
        "statistical_summary.csv": summary,
        "statistical_correlations.csv": correlations,
        "statistical_store_analysis.csv": store,
        "statistical_category_analysis.csv": streams.category,
        "statistical_price_demand.csv": price_analysis,
        "statistical_promotion_analysis.csv": promotion_analysis,
        "statistical_autocorrelation.csv": autocorrelation,
        "statistical_trend.csv": trend,
        "statistical_monthly_activity.csv": streams.monthly,
    }

    for filename, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / filename, index=False)

    figures_written = create_figures(
        streams.daily,
        store,
        price_analysis,
        autocorrelation,
        streams.scatter_prices,
        streams.scatter_quantities,
    )

    write_findings(
        summary,
        trend,
        correlations,
        price_analysis,
        promotion_analysis,
        autocorrelation,
    )

    quality_report = build_quality_report(
        streams,
        correlations,
        price_analysis,
        promotion_analysis,
        autocorrelation,
        trend,
        figures_written,
    )

    quality_report.to_csv(
        OUTPUT_DIR / "statistical_quality_report.csv",
        index=False,
    )

    print("Statistical and analytical analysis completed successfully.")
    print(f"Summary: {OUTPUT_DIR / 'statistical_summary.csv'}")
    print(f"Findings: {OUTPUT_DIR / 'statistical_findings.txt'}")
    print(f"Quality report: {OUTPUT_DIR / 'statistical_quality_report.csv'}")
    print(f"Figures: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
