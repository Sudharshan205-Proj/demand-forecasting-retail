"""
Perform exploratory data analysis on the integrated retail dataset.

The analysis is intentionally chunked because the integrated dataset contains
millions of records.

Input:
    data/processed/integrated_retail_data.csv

Outputs:
    data/analysis/eda_summary.csv
    data/analysis/eda_monthly_demand.csv
    data/analysis/eda_store_summary.csv
    data/analysis/eda_category_summary.csv
    data/analysis/eda_top_items.csv
    data/analysis/eda_correlation.csv
    data/analysis/eda_findings.txt

Figures:
    reports/figures/eda_demand_over_time.png
    reports/figures/eda_monthly_demand.png
    reports/figures/eda_store_demand.png
    reports/figures/eda_top_categories.png
    reports/figures/eda_demand_distribution.png

The correlation summary is calculated from the complete integrated dataset
using chunked pairwise moments. Non-finite values (missing or infinite) are
excluded pairwise instead of being sampled.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "integrated_retail_data.csv"
)

ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

CHUNK_SIZE = 250_000

DTYPE_SAMPLE_ROWS = 10_000

REQUIRED_COLUMNS = [
    "date",
    "item_id",
    "quantity",
    "price_base",
    "sum_total",
    "store_id",
]

OPTIONAL_COLUMNS = [
    "dept_name",
    "class_name",
    "subclass_name",
    "online_quantity",
    "online_sales_value",
    "markdown_quantity",
    "markdown_record_count",
    "discount_record_count",
    "promo_discount_rate",
    "price_change_count",
]

CORRELATION_COLUMNS = [
    "quantity",
    "price_base",
    "sum_total",
    "online_quantity",
    "markdown_quantity",
    "promo_discount_rate",
    "price_change_count",
]


def validate_input_columns(columns: list[str]) -> None:
    """Validate that the integrated dataset contains required fields."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))

    if missing:
        raise ValueError(
            f"Integrated dataset is missing required columns: {missing}"
        )


def validate_input_file() -> None:
    """Validate that the integrated dataset exists before analysis."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Integrated dataset not found: {INPUT_PATH}. "
            "Run scripts/integrate_retail_data.py (Phase 6) first."
        )


def initialise_directories() -> None:
    """Create output directories."""
    ANALYSIS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def read_header() -> pd.DataFrame:
    """Read only the header of the integrated dataset."""
    return pd.read_csv(
        INPUT_PATH,
        nrows=0,
    )


def get_columns() -> list[str]:
    """Read only the column names of the integrated dataset."""
    return read_header().columns.tolist()


def read_numeric_columns(columns: list[str]) -> list[str]:
    """Identify numeric columns from a small sample of the dataset.

    The header row alone does not carry usable dtypes, so a small sample is
    read to determine which columns support numeric integrity checks.
    """
    sample = pd.read_csv(
        INPUT_PATH,
        usecols=columns,
        nrows=DTYPE_SAMPLE_ROWS,
    )

    return [
        column
        for column in columns
        if pd.api.types.is_numeric_dtype(sample[column])
    ]


def correlation_offsets(columns: list[str]) -> dict[str, float]:
    """Calculate a centering constant per column from finite values.

    The constants only keep the pairwise accumulators well conditioned.
    Any constant produces the same correlation, so the mean of the finite
    values is used because it keeps the accumulated terms small.
    """
    totals = np.zeros(len(columns))
    counts = np.zeros(len(columns))

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=columns,
        chunksize=CHUNK_SIZE,
    ):
        values = chunk[columns].to_numpy(dtype="float64")

        finite = np.isfinite(values)

        counts += finite.sum(axis=0)
        totals += np.where(finite, values, 0.0).sum(axis=0)

    offsets = np.divide(
        totals,
        counts,
        out=np.zeros_like(totals),
        where=counts > 0,
    )

    return dict(
        zip(columns, offsets)
    )


def accumulate_correlation(
    columns: list[str],
    offsets: dict[str, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Accumulate centered pairwise moments across every chunk.

    Returns the pairwise counts, centered sums, centered products and
    centered squares. Non-finite values are excluded pairwise.
    """
    size = len(columns)

    offset_values = np.array(
        [offsets[column] for column in columns],
        dtype="float64",
    )

    counts = np.zeros((size, size))
    centered_sums = np.zeros((size, size))
    centered_products = np.zeros((size, size))
    centered_squares = np.zeros((size, size))

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=columns,
        chunksize=CHUNK_SIZE,
    ):
        values = chunk[columns].to_numpy(dtype="float64")

        finite = np.isfinite(values)

        centered = np.where(
            finite,
            values - offset_values,
            0.0,
        )

        weights = finite.astype("float64")

        counts += weights.T @ weights
        centered_sums += centered.T @ weights
        centered_products += centered.T @ centered
        centered_squares += (centered * centered).T @ weights

    return (
        counts,
        centered_sums,
        centered_products,
        centered_squares,
    )


def pearson_from_accumulators(
    counts: np.ndarray,
    centered_sums: np.ndarray,
    centered_products: np.ndarray,
    centered_squares: np.ndarray,
    columns: list[str],
) -> pd.DataFrame:
    """Derive the pairwise-complete Pearson matrix from accumulators.

    Each correlation uses only the rows where both variables are finite.
    A variable correlates with itself as exactly 1. Pairs with fewer than
    two usable rows, or without variation, are reported as not available.
    """
    size = len(columns)

    matrix = np.full((size, size), np.nan)

    for i in range(size):
        for j in range(size):
            usable = counts[i, j]

            if usable < 2:
                continue

            covariance = (
                centered_products[i, j]
                - centered_sums[i, j] * centered_sums[j, i] / usable
            )

            variance_i = (
                centered_squares[i, j]
                - centered_sums[i, j] * centered_sums[i, j] / usable
            )

            variance_j = (
                centered_squares[j, i]
                - centered_sums[j, i] * centered_sums[j, i] / usable
            )

            if variance_i <= 0 or variance_j <= 0:
                continue

            if i == j:
                matrix[i, j] = 1.0
                continue

            matrix[i, j] = covariance / np.sqrt(
                variance_i * variance_j
            )

    correlation = pd.DataFrame(
        np.clip(matrix, -1.0, 1.0),
        index=columns,
        columns=columns,
    )

    return correlation.reset_index().rename(
        columns={"index": "variable"}
    )


def build_correlation() -> pd.DataFrame:
    """Calculate the exact full-dataset correlation matrix in chunks."""
    header_columns = get_columns()

    columns = [
        column
        for column in CORRELATION_COLUMNS
        if column in header_columns
    ]

    if len(columns) < 2:
        return pd.DataFrame()

    offsets = correlation_offsets(columns)

    (
        counts,
        centered_sums,
        centered_products,
        centered_squares,
    ) = accumulate_correlation(columns, offsets)

    return pearson_from_accumulators(
        counts,
        centered_sums,
        centered_products,
        centered_squares,
        columns,
    )


def describe_item_demand(items: pd.DataFrame) -> list[dict[str, object]]:
    """Describe the item-level demand distribution and concentration.

    Unusual item-level demand is identified for investigation only.
    No observation is removed, filtered or modified.
    """
    if items.empty:
        return []

    demand = (
        items["quantity"]
        .astype("float64")
        .sort_values(ascending=False)
        .reset_index(drop=True)
    )

    total = float(demand.sum())

    if total <= 0 or len(demand) < 2:
        return []

    q1 = float(demand.quantile(0.25))
    median = float(demand.quantile(0.5))
    q3 = float(demand.quantile(0.75))

    upper_fence = q3 + 1.5 * (q3 - q1)

    tail = demand[demand > upper_fence]

    top_count = max(1, int(round(len(demand) * 0.01)))

    return [
        {
            "metric": "item_demand_q1",
            "value": q1,
        },
        {
            "metric": "item_demand_median",
            "value": median,
        },
        {
            "metric": "item_demand_q3",
            "value": q3,
        },
        {
            "metric": "item_demand_upper_fence",
            "value": upper_fence,
        },
        {
            "metric": "items_above_upper_fence",
            "value": len(tail),
        },
        {
            "metric": "items_above_upper_fence_demand_share",
            "value": round(float(tail.sum()) / total, 6),
        },
        {
            "metric": "top_1pct_item_count",
            "value": top_count,
        },
        {
            "metric": "top_1pct_item_demand_share",
            "value": round(
                float(demand.head(top_count).sum()) / total,
                6,
            ),
        },
        {
            "metric": "top_10_item_demand_share",
            "value": round(
                float(demand.head(10).sum()) / total,
                6,
            ),
        },
    ]


def build_eda_summaries() -> dict[str, object]:
    """Process the integrated dataset in chunks."""
    validate_input_file()

    header = read_header()

    columns = header.columns.tolist()

    validate_input_columns(columns)

    use_columns = [
        column
        for column in REQUIRED_COLUMNS + OPTIONAL_COLUMNS
        if column in columns
    ]

    numeric_columns = read_numeric_columns(use_columns)

    total_rows = 0
    total_quantity = 0.0
    total_revenue = 0.0

    min_date = None
    max_date = None

    store_rows: list[pd.DataFrame] = []
    monthly_rows: list[pd.DataFrame] = []
    category_rows: list[pd.DataFrame] = []
    item_rows: list[pd.DataFrame] = []

    missing_totals = np.zeros(len(use_columns), dtype="int64")
    infinite_totals = np.zeros(len(numeric_columns), dtype="int64")

    discount_record_rows = 0
    markdown_record_rows = 0

    for chunk in pd.read_csv(
        INPUT_PATH,
        usecols=use_columns,
        chunksize=CHUNK_SIZE,
    ):
        total_rows += len(chunk)

        chunk["date"] = pd.to_datetime(
            chunk["date"],
            errors="coerce",
        )

        total_quantity += float(chunk["quantity"].sum())
        total_revenue += float(chunk["sum_total"].sum())

        chunk_min_date = chunk["date"].min()
        chunk_max_date = chunk["date"].max()

        if min_date is None or (
            pd.notna(chunk_min_date)
            and chunk_min_date < min_date
        ):
            min_date = chunk_min_date

        if max_date is None or (
            pd.notna(chunk_max_date)
            and chunk_max_date > max_date
        ):
            max_date = chunk_max_date

        missing_totals += (
            chunk[use_columns]
            .isna()
            .to_numpy()
            .sum(axis=0)
        )

        if numeric_columns:
            infinite_totals += (
                np.isinf(
                    chunk[numeric_columns].to_numpy(dtype="float64")
                )
                .sum(axis=0)
            )

        if "discount_record_count" in chunk.columns:
            discount_record_rows += int(
                (chunk["discount_record_count"] > 0).sum()
            )

        if "markdown_record_count" in chunk.columns:
            markdown_record_rows += int(
                (chunk["markdown_record_count"] > 0).sum()
            )

        chunk["year_month"] = (
            chunk["date"]
            .dt.to_period("M")
            .astype("string")
        )

        monthly_rows.append(
            chunk.groupby(
                "year_month",
                as_index=False,
            ).agg(
                quantity=("quantity", "sum"),
                revenue=("sum_total", "sum"),
                records=("quantity", "size"),
            )
        )

        store_rows.append(
            chunk.groupby(
                "store_id",
                as_index=False,
            ).agg(
                quantity=("quantity", "sum"),
                revenue=("sum_total", "sum"),
                records=("quantity", "size"),
            )
        )

        if "dept_name" in chunk.columns:
            category_rows.append(
                chunk.groupby(
                    "dept_name",
                    dropna=False,
                    as_index=False,
                ).agg(
                    quantity=("quantity", "sum"),
                    revenue=("sum_total", "sum"),
                    records=("quantity", "size"),
                )
            )

        item_rows.append(
            chunk.groupby(
                "item_id",
                as_index=False,
            ).agg(
                quantity=("quantity", "sum"),
                revenue=("sum_total", "sum"),
                records=("quantity", "size"),
            )
        )

    monthly = (
        pd.concat(
            monthly_rows,
            ignore_index=True,
        )
        .groupby(
            "year_month",
            as_index=False,
        )
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            records=("records", "sum"),
        )
        .sort_values("year_month")
    )

    stores = (
        pd.concat(
            store_rows,
            ignore_index=True,
        )
        .groupby(
            "store_id",
            as_index=False,
        )
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            records=("records", "sum"),
        )
        .sort_values("quantity", ascending=False)
    )

    if category_rows:
        categories = (
            pd.concat(
                category_rows,
                ignore_index=True,
            )
            .groupby(
                "dept_name",
                dropna=False,
                as_index=False,
            )
            .agg(
                quantity=("quantity", "sum"),
                revenue=("revenue", "sum"),
                records=("records", "sum"),
            )
            .sort_values("quantity", ascending=False)
        )
    else:
        categories = pd.DataFrame(
            columns=[
                "dept_name",
                "quantity",
                "revenue",
                "records",
            ]
        )

    items = (
        pd.concat(
            item_rows,
            ignore_index=True,
        )
        .groupby(
            "item_id",
            as_index=False,
        )
        .agg(
            quantity=("quantity", "sum"),
            revenue=("revenue", "sum"),
            records=("records", "sum"),
        )
        .sort_values(
            "quantity",
            ascending=False,
        )
    )

    correlation = build_correlation()

    summary_rows = [
        {
            "metric": "rows",
            "value": total_rows,
        },
        {
            "metric": "total_quantity",
            "value": total_quantity,
        },
        {
            "metric": "total_revenue",
            "value": total_revenue,
        },
        {
            "metric": "date_min",
            "value": (
                min_date.strftime("%Y-%m-%d")
                if pd.notna(min_date)
                else ""
            ),
        },
        {
            "metric": "date_max",
            "value": (
                max_date.strftime("%Y-%m-%d")
                if pd.notna(max_date)
                else ""
            ),
        },
        {
            "metric": "unique_stores",
            "value": stores["store_id"].nunique(),
        },
        {
            "metric": "unique_items",
            "value": items["item_id"].nunique(),
        },
    ]

    summary_rows.extend(
        {
            "metric": f"missing_{column}",
            "value": int(count),
        }
        for column, count in zip(use_columns, missing_totals)
    )

    summary_rows.extend(
        {
            "metric": f"infinite_{column}",
            "value": int(count),
        }
        for column, count in zip(numeric_columns, infinite_totals)
    )

    summary_rows.extend(
        [
            {
                "metric": "rows_with_discount_record",
                "value": discount_record_rows,
            },
            {
                "metric": "rows_with_markdown_record",
                "value": markdown_record_rows,
            },
        ]
    )

    summary_rows.extend(
        describe_item_demand(items)
    )

    summary = pd.DataFrame(summary_rows)

    summary.to_csv(
        ANALYSIS_DIR / "eda_summary.csv",
        index=False,
    )

    monthly.to_csv(
        ANALYSIS_DIR / "eda_monthly_demand.csv",
        index=False,
    )

    stores.to_csv(
        ANALYSIS_DIR / "eda_store_summary.csv",
        index=False,
    )

    categories.to_csv(
        ANALYSIS_DIR / "eda_category_summary.csv",
        index=False,
    )

    items.head(100).to_csv(
        ANALYSIS_DIR / "eda_top_items.csv",
        index=False,
    )

    correlation.to_csv(
        ANALYSIS_DIR / "eda_correlation.csv",
        index=False,
    )

    return {
        "summary": summary,
        "monthly": monthly,
        "stores": stores,
        "categories": categories,
        "items": items,
        "correlation": correlation,
    }


def chart_labels(
    values: pd.Series,
    fallback: str = "(unknown)",
) -> pd.Series:
    """Return categorical chart labels without missing or non-string values.

    Missing labels keep an explicit name instead of being dropped, because
    unmatched catalog records are a documented part of the analytical data.
    """
    return (
        values
        .astype("object")
        .where(values.notna(), fallback)
        .astype(str)
    )


def create_figures(results: dict[str, object]) -> None:
    """Create the main Phase 7 exploratory visualizations."""
    monthly = results["monthly"]
    stores = results["stores"]
    categories = results["categories"]
    items = results["items"]

    assert isinstance(monthly, pd.DataFrame)
    assert isinstance(stores, pd.DataFrame)
    assert isinstance(categories, pd.DataFrame)
    assert isinstance(items, pd.DataFrame)

    # Demand over time.
    plt.figure(figsize=(12, 6))
    plt.plot(
        chart_labels(monthly["year_month"]),
        monthly["quantity"],
    )
    plt.xticks(rotation=45)
    plt.xlabel("Month")
    plt.ylabel("Demand Quantity")
    plt.title("Monthly Retail Demand")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIR / "eda_demand_over_time.png",
        dpi=150,
    )
    plt.close()

    # Monthly demand.
    plt.figure(figsize=(12, 6))
    plt.bar(
        chart_labels(monthly["year_month"]),
        monthly["quantity"],
    )
    plt.xticks(rotation=45)
    plt.xlabel("Month")
    plt.ylabel("Demand Quantity")
    plt.title("Monthly Demand Distribution")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIR / "eda_monthly_demand.png",
        dpi=150,
    )
    plt.close()

    # Store demand.
    plt.figure(figsize=(8, 5))
    plt.bar(
        chart_labels(stores["store_id"]),
        stores["quantity"],
    )
    plt.xlabel("Store")
    plt.ylabel("Demand Quantity")
    plt.title("Demand by Store")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIR / "eda_store_demand.png",
        dpi=150,
    )
    plt.close()

    # Top departments.
    if not categories.empty:
        top_categories = categories.head(15)

        plt.figure(figsize=(12, 7))
        plt.barh(
            chart_labels(
                top_categories["dept_name"],
                fallback="(unmatched)",
            ),
            top_categories["quantity"],
        )
        plt.xlabel("Demand Quantity")
        plt.ylabel("Department")
        plt.title("Top Departments by Demand")
        plt.tight_layout()
        plt.savefig(
            FIGURES_DIR / "eda_top_categories.png",
            dpi=150,
        )
        plt.close()

    # Demand distribution based on item-level totals.
    plt.figure(figsize=(10, 6))
    plt.hist(
        items["quantity"],
        bins=50,
    )
    plt.xlabel("Item Demand")
    plt.ylabel("Frequency")
    plt.title("Distribution of Item-Level Demand")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIR / "eda_demand_distribution.png",
        dpi=150,
    )
    plt.close()


def format_metric(value: object, digits: int = 3) -> str:
    """Format a numeric metric for the findings file."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if not np.isfinite(number):
        return str(value)

    return f"{number:,.{digits}f}"


def format_identifier(value: object) -> str:
    """Format an identifier without floating-point artefacts."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if number.is_integer():
        return str(int(number))

    return f"{number:g}"


def write_findings(results: dict[str, object]) -> None:
    """Write automatically derived descriptive findings."""
    summary = results["summary"]
    monthly = results["monthly"]
    stores = results["stores"]
    categories = results["categories"]
    items = results["items"]

    assert isinstance(summary, pd.DataFrame)
    assert isinstance(monthly, pd.DataFrame)
    assert isinstance(stores, pd.DataFrame)
    assert isinstance(categories, pd.DataFrame)
    assert isinstance(items, pd.DataFrame)

    metrics = dict(
        zip(
            summary["metric"],
            summary["value"],
        )
    )

    lines = [
        "PHASE 7 — EXPLORATORY DATA ANALYSIS FINDINGS",
        "",
        "These findings are descriptive observations generated from the",
        "integrated dataset. They are not forecasting-model results.",
        "",
        f"Rows analysed: {format_metric(metrics.get('rows'), 0)}",
        f"Total quantity: {format_metric(metrics.get('total_quantity'))}",
        f"Total revenue: {format_metric(metrics.get('total_revenue'))}",
        f"Date range: {metrics.get('date_min')} to {metrics.get('date_max')}",
        f"Unique stores: {format_metric(metrics.get('unique_stores'), 0)}",
        f"Unique items: {format_metric(metrics.get('unique_items'), 0)}",
        "",
    ]

    if not monthly.empty:
        highest_month = monthly.loc[
            monthly["quantity"].idxmax()
        ]

        lowest_month = monthly.loc[
            monthly["quantity"].idxmin()
        ]

        lines.extend(
            [
                "Temporal observations:",
                (
                    "Highest-demand month: "
                    f"{highest_month['year_month']} "
                    f"({format_metric(highest_month['quantity'])})"
                ),
                (
                    "Lowest-demand month: "
                    f"{lowest_month['year_month']} "
                    f"({format_metric(lowest_month['quantity'])})"
                ),
                "",
            ]
        )

    if not stores.empty:
        highest_store = stores.iloc[0]

        lines.extend(
            [
                "Store observations:",
                (
                    f"Highest-demand store: "
                    f"{format_identifier(highest_store['store_id'])} "
                    f"({format_metric(highest_store['quantity'])})"
                ),
                "",
            ]
        )

    if not categories.empty:
        highest_category = categories.iloc[0]

        lines.extend(
            [
                "Product observations:",
                (
                    "Highest-demand department: "
                    f"{highest_category['dept_name']} "
                    f"({format_metric(highest_category['quantity'])})"
                ),
                "",
            ]
        )

    if metrics.get("items_above_upper_fence") is not None:
        lines.extend(
            [
                "Distribution and concentration observations:",
                (
                    "Item-level demand quartiles (Q1 / median / Q3): "
                    f"{format_metric(metrics.get('item_demand_q1'))} / "
                    f"{format_metric(metrics.get('item_demand_median'))} / "
                    f"{format_metric(metrics.get('item_demand_q3'))}"
                ),
                (
                    "Item-level upper fence (Q3 + 1.5 x IQR): "
                    f"{format_metric(metrics.get('item_demand_upper_fence'))}"
                ),
                (
                    "Items above the upper fence: "
                    f"{format_metric(metrics.get('items_above_upper_fence'), 0)} "
                    "(share of total demand: "
                    f"{format_metric(metrics.get('items_above_upper_fence_demand_share'), 4)})"
                ),
                (
                    "Top 1% of items "
                    f"({format_metric(metrics.get('top_1pct_item_count'), 0)}): "
                    "share of total demand "
                    f"{format_metric(metrics.get('top_1pct_item_demand_share'), 4)}"
                ),
                (
                    "Top 10 items: share of total demand "
                    f"{format_metric(metrics.get('top_10_item_demand_share'), 4)}"
                ),
                "",
            ]
        )

    if metrics.get("rows_with_discount_record") is not None:
        infinite_total = sum(
            int(value)
            for metric, value in metrics.items()
            if str(metric).startswith("infinite_")
        )

        lines.extend(
            [
                "Promotion and markdown observations:",
                (
                    "Rows with a discount record: "
                    f"{format_metric(metrics.get('rows_with_discount_record'), 0)}"
                ),
                (
                    "Rows with a markdown record: "
                    f"{format_metric(metrics.get('rows_with_markdown_record'), 0)}"
                ),
                (
                    "Rows with non-finite analytical values "
                    "(excluded from correlation): "
                    f"{format_metric(infinite_total, 0)}"
                ),
                "",
            ]
        )

    lines.extend(
        [
            "Interpretation note:",
            (
                "The descriptive findings should be interpreted together "
                "with the underlying summary tables and visualizations. "
                "Observed associations do not establish causation."
            ),
            "",
            "Data note:",
            (
                "Missing promotion and markdown values mean that no "
                "matching auxiliary record exists for that date, item and "
                "store after the Phase 6 left joins. They are not cleaning "
                "failures. Non-finite values are excluded from the pairwise "
                "correlation calculation."
            ),
        ]
    )

    (ANALYSIS_DIR / "eda_findings.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """Run the complete EDA pipeline."""
    print("Running exploratory data analysis...")

    initialise_directories()

    results = build_eda_summaries()

    create_figures(results)

    write_findings(results)

    print("Exploratory data analysis completed successfully.")
    print(
        f"Summary: {ANALYSIS_DIR / 'eda_summary.csv'}"
    )
    print(
        f"Findings: {ANALYSIS_DIR / 'eda_findings.txt'}"
    )
    print(
        f"Figures: {FIGURES_DIR}"
    )


if __name__ == "__main__":
    main()