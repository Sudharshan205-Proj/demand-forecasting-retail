"""Perform statistical and analytical analysis of integrated retail demand data.

The script processes the large integrated dataset in chunks and produces
statistical summaries suitable for demand-forecasting decisions.

The analysis is descriptive and inferential. It does not train forecasting
models and does not create final forecasting features.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "integrated_retail_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"

CHUNK_SIZE = 250_000
RANDOM_SEED = 42

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


def validate_columns(columns: list[str]) -> None:
    """Validate the minimum schema required by the analysis."""
    missing = REQUIRED_COLUMNS.difference(columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )


def safe_cv(series: pd.Series) -> float:
    """Return coefficient of variation, or NaN when undefined."""
    mean = series.mean()
    if pd.isna(mean) or mean == 0:
        return float("nan")

    return float(series.std(ddof=1) / mean)


def clean_pair(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Drop rows with NaN or infinite values in the given columns."""
    return df[columns].replace([np.inf, -np.inf], np.nan).dropna()


def aggregate_chunks(
    input_path: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Aggregate the large integrated dataset into analytical grains."""
    header = pd.read_csv(input_path, nrows=0)
    validate_columns(header.columns.tolist())

    daily_parts: list[pd.DataFrame] = []
    store_parts: list[pd.DataFrame] = []
    category_parts: list[pd.DataFrame] = []
    relationship_parts: list[pd.DataFrame] = []

    usecols = sorted(REQUIRED_COLUMNS | OPTIONAL_COLUMNS)
    available = set(header.columns)
    usecols = [column for column in usecols if column in available]

    for chunk in pd.read_csv(
        input_path,
        usecols=usecols,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")

        chunk["quantity"] = pd.to_numeric(
            chunk["quantity"],
            errors="coerce",
        )

        chunk["price_base"] = pd.to_numeric(
            chunk["price_base"],
            errors="coerce",
        )

        chunk["sum_total"] = pd.to_numeric(
            chunk["sum_total"],
            errors="coerce",
        )

        chunk["year_month"] = chunk["date"].dt.to_period("M").astype(str)

        daily = (
            chunk.groupby("date", as_index=False)
            .agg(
                quantity=("quantity", "sum"),
                revenue=("sum_total", "sum"),
                records=("item_id", "size"),
                average_price=("price_base", "mean"),
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

        relationship_columns = [
            column
            for column in [
                "quantity",
                "price_base",
                "markdown_quantity",
                "markdown_discount",
                "promo_discount_rate",
                "markdown_record_count",
                "discount_record_count",
                "price_change_count",
                "online_quantity",
                "online_sales_value",
            ]
            if column in chunk.columns
        ]

        relationship_parts.append(chunk[relationship_columns].copy())

    daily_combined = (
        pd.concat(daily_parts, ignore_index=True)
        .groupby("date", as_index=False)
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            records=("records", "sum"),
            average_price=("average_price", "mean"),
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

    relationship_combined = pd.concat(
        relationship_parts,
        ignore_index=True,
    )

    return (
        daily_combined,
        store_combined,
        category_combined,
        relationship_combined,
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
    relationships: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate Pearson correlations for available numeric variables."""
    numeric = relationships.select_dtypes(include="number")

    rows: list[dict[str, object]] = []

    for column in numeric.columns:
        if column == "quantity":
            continue

        pair = clean_pair(relationships, ["quantity", column])

        if len(pair) < 3:
            continue

        correlation, p_value = stats.pearsonr(
            pair["quantity"],
            pair[column],
        )

        rows.append(
            {
                "variable": column,
                "observations": len(pair),
                "pearson_r": correlation,
                "p_value": p_value,
                "absolute_correlation": abs(correlation),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(
            "absolute_correlation",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def calculate_price_analysis(
    relationships: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate price-demand correlation and simple regression statistics."""
    pair = clean_pair(relationships, ["quantity", "price_base"])

    if len(pair) < 3:
        return pd.DataFrame(
            columns=[
                "observations",
                "pearson_r",
                "p_value",
                "slope",
                "intercept",
                "r_squared",
            ]
        )

    correlation, p_value = stats.pearsonr(
        pair["quantity"],
        pair["price_base"],
    )

    slope, intercept, r_value, _, _ = stats.linregress(
        pair["price_base"],
        pair["quantity"],
    )

    return pd.DataFrame(
        [
            {
                "observations": len(pair),
                "pearson_r": correlation,
                "p_value": p_value,
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_value**2,
            }
        ]
    )


def calculate_promotion_analysis(
    relationships: pd.DataFrame,
) -> pd.DataFrame:
    """Compare demand across records with and without promotional activity."""
    if "promo_discount_rate" not in relationships.columns:
        return pd.DataFrame(
            columns=[
                "promotion_group",
                "observations",
                "mean_quantity",
                "median_quantity",
            ]
        )

    data = relationships[
        ["quantity", "promo_discount_rate"]
    ].dropna()

    if data.empty:
        return pd.DataFrame(
            columns=[
                "promotion_group",
                "observations",
                "mean_quantity",
                "median_quantity",
            ]
        )

    data = data.copy()
    data["promotion_group"] = np.where(
        data["promo_discount_rate"] > 0,
        "promotion_discount_present",
        "no_promotion_discount",
    )

    result = (
        data.groupby("promotion_group")
        .agg(
            observations=("quantity", "size"),
            mean_quantity=("quantity", "mean"),
            median_quantity=("quantity", "median"),
        )
        .reset_index()
    )

    groups = [
        group["quantity"].to_numpy()
        for _, group in data.groupby("promotion_group")
        if len(group) >= 2
    ]

    if len(groups) == 2:
        statistic, p_value = stats.mannwhitneyu(
            groups[0],
            groups[1],
            alternative="two-sided",
        )

        result["mann_whitney_u"] = statistic
        result["p_value"] = p_value

    return result


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

    return pd.DataFrame(rows)


def calculate_trend(
    daily: pd.DataFrame,
) -> pd.DataFrame:
    """Estimate the linear trend in daily aggregate demand."""
    x = np.arange(len(daily), dtype=float)
    y = daily["quantity"].to_numpy(dtype=float)

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        x,
        y,
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
            }
        ]
    )


def create_figures(
    daily: pd.DataFrame,
    store: pd.DataFrame,
    price_analysis: pd.DataFrame,
    autocorrelation: pd.DataFrame,
) -> None:
    """Create statistical-analysis figures."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

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

    if not price_analysis.empty:
        plt.figure(figsize=(10, 6))
        sample = pd.read_csv(
            INPUT_PATH,
            usecols=["quantity", "price_base"],
            nrows=200_000,
        ).dropna()

        plt.scatter(
            sample["price_base"],
            sample["quantity"],
            s=8,
            alpha=0.25,
        )
        plt.title("Price and Demand Relationship")
        plt.xlabel("Price")
        plt.ylabel("Quantity")
        plt.tight_layout()
        plt.savefig(
            FIGURE_DIR / "statistical_price_demand.png",
            dpi=150,
        )
        plt.close()

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
        "",
        "Summary:",
    ]

    for row in summary.itertuples(index=False):
        lines.append(f"- {row.metric}: {row.value}")

    if not trend.empty:
        row = trend.iloc[0]
        lines.extend(
            [
                "",
                "Demand trend:",
                f"- slope_per_day: {row['slope_per_day']}",
                f"- r_squared: {row['r_squared']}",
                f"- p_value: {row['p_value']}",
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
                f"r={row.pearson_r}, p={row.p_value}"
            )

    if not price_analysis.empty:
        row = price_analysis.iloc[0]
        lines.extend(
            [
                "",
                "Price-demand relationship:",
                f"- Pearson r: {row['pearson_r']}",
                f"- p-value: {row['p_value']}",
                f"- regression slope: {row['slope']}",
                f"- R-squared: {row['r_squared']}",
            ]
        )

    if not promotion_analysis.empty:
        lines.extend(
            [
                "",
                "Promotion analysis:",
            ]
        )

        for row in promotion_analysis.itertuples(index=False):
            lines.append(
                f"- {row.promotion_group}: "
                f"n={row.observations}, "
                f"mean={row.mean_quantity}, "
                f"median={row.median_quantity}"
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
                f"- lag_days: {strongest['lag_days']}",
                (f"- autocorrelation: "
                 f"{strongest['autocorrelation']}"),
            ]
        )

    (OUTPUT_DIR / "statistical_findings.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run the complete statistical-analysis workflow."""
    print("Running statistical and analytical analysis...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (
        daily,
        store,
        category,
        relationships,
    ) = aggregate_chunks(INPUT_PATH)

    summary = calculate_summary(daily, store)
    correlations = calculate_correlations(relationships)
    price_analysis = calculate_price_analysis(relationships)
    promotion_analysis = calculate_promotion_analysis(relationships)
    autocorrelation = calculate_autocorrelation(daily)
    trend = calculate_trend(daily)

    summary.to_csv(
        OUTPUT_DIR / "statistical_summary.csv",
        index=False,
    )

    correlations.to_csv(
        OUTPUT_DIR / "statistical_correlations.csv",
        index=False,
    )

    store.to_csv(
        OUTPUT_DIR / "statistical_store_analysis.csv",
        index=False,
    )

    category.to_csv(
        OUTPUT_DIR / "statistical_category_analysis.csv",
        index=False,
    )

    price_analysis.to_csv(
        OUTPUT_DIR / "statistical_price_demand.csv",
        index=False,
    )

    promotion_analysis.to_csv(
        OUTPUT_DIR / "statistical_promotion_analysis.csv",
        index=False,
    )

    autocorrelation.to_csv(
        OUTPUT_DIR / "statistical_autocorrelation.csv",
        index=False,
    )

    trend.to_csv(
        OUTPUT_DIR / "statistical_trend.csv",
        index=False,
    )

    create_figures(
        daily,
        store,
        price_analysis,
        autocorrelation,
    )

    write_findings(
        summary,
        trend,
        correlations,
        price_analysis,
        promotion_analysis,
        autocorrelation,
    )

    print("Statistical and analytical analysis completed successfully.")
    print(f"Summary: {OUTPUT_DIR / 'statistical_summary.csv'}")
    print(f"Findings: {OUTPUT_DIR / 'statistical_findings.txt'}")
    print(f"Figures: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
