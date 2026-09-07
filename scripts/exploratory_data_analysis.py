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
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
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


def validate_input_columns(columns: list[str]) -> None:
    """Validate that the integrated dataset contains required fields."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))

    if missing:
        raise ValueError(
            f"Integrated dataset is missing required columns: {missing}"
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


def get_columns() -> list[str]:
    """Read only the header of the integrated dataset."""
    return pd.read_csv(
        INPUT_PATH,
        nrows=0,
    ).columns.tolist()


def build_eda_summaries() -> dict[str, object]:
    """Process the integrated dataset in chunks."""
    columns = get_columns()

    validate_input_columns(columns)

    use_columns = [
        column
        for column in REQUIRED_COLUMNS + OPTIONAL_COLUMNS
        if column in columns
    ]

    total_rows = 0
    total_quantity = 0.0
    total_revenue = 0.0

    min_date = None
    max_date = None

    store_rows: list[pd.DataFrame] = []
    monthly_rows: list[pd.DataFrame] = []
    category_rows: list[pd.DataFrame] = []
    item_rows: list[pd.DataFrame] = []

    correlation_parts: list[pd.DataFrame] = []

    missing_counts = {
        column: 0
        for column in use_columns
    }

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

        total_quantity += chunk["quantity"].sum()
        total_revenue += chunk["sum_total"].sum()

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

        for column in use_columns:
            missing_counts[column] += int(
                chunk[column].isna().sum()
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

        correlation_columns = [
            column
            for column in [
                "quantity",
                "price_base",
                "sum_total",
                "online_quantity",
                "markdown_quantity",
                "promo_discount_rate",
                "price_change_count",
            ]
            if column in chunk.columns
        ]

        if len(correlation_columns) >= 2:
            correlation_parts.append(
                chunk[correlation_columns]
                .sample(
                    n=min(10_000, len(chunk)),
                    random_state=42,
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

    if correlation_parts:
        correlation_sample = pd.concat(
            correlation_parts,
            ignore_index=True,
        )

        correlation = (
            correlation_sample
            .corr(
                numeric_only=True
            )
            .reset_index()
            .rename(
                columns={"index": "variable"}
            )
        )
    else:
        correlation = pd.DataFrame()

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
            "value": count,
        }
        for column, count in missing_counts.items()
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
        monthly["year_month"].astype(str),
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
        monthly["year_month"].astype(str),
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
        stores["store_id"].astype(str),
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
            top_categories["dept_name"].astype(str),
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
        f"Rows analysed: {metrics.get('rows')}",
        f"Total quantity: {metrics.get('total_quantity')}",
        f"Total revenue: {metrics.get('total_revenue')}",
        f"Date range: {metrics.get('date_min')} to {metrics.get('date_max')}",
        f"Unique stores: {metrics.get('unique_stores')}",
        f"Unique items: {metrics.get('unique_items')}",
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
                    f"({highest_month['quantity']})"
                ),
                (
                    "Lowest-demand month: "
                    f"{lowest_month['year_month']} "
                    f"({lowest_month['quantity']})"
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
                    f"{highest_store['store_id']} "
                    f"({highest_store['quantity']})"
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
                    f"({highest_category['quantity']})"
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