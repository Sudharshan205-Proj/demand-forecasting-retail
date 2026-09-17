"""
Integrate the cleaned retail datasets at the canonical analytical grain.

Canonical grain:
    date + item_id + store_id

The cleaned sales dataset is the primary fact table. Supporting datasets
are aggregated to the canonical grain before they are joined so that
many-to-many joins cannot multiply sales records.

Generated files:
    data/processed/integrated_retail_data.csv
    data/processed/integration_quality_report.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

SALES_PATH = PROCESSED_DIR / "sales_clean.csv"
STORES_PATH = RAW_DIR / "stores.csv"
CATALOG_PATH = RAW_DIR / "catalog.csv"
PRICE_HISTORY_PATH = RAW_DIR / "price_history.csv"
MARKDOWNS_PATH = RAW_DIR / "markdowns.csv"
DISCOUNTS_PATH = RAW_DIR / "discounts_history.csv"
ONLINE_PATH = RAW_DIR / "online.csv"
ACTUAL_MATRIX_PATH = RAW_DIR / "actual_matrix.csv"

OUTPUT_PATH = PROCESSED_DIR / "integrated_retail_data.csv"
QUALITY_REPORT_PATH = PROCESSED_DIR / "integration_quality_report.csv"

CHUNK_SIZE = 250_000

KEY_COLUMNS = ["date", "item_id", "store_id"]

SALES_COLUMNS = [
    "date",
    "item_id",
    "quantity",
    "price_base",
    "sum_total",
    "store_id",
]


def require_columns(
    frame: pd.DataFrame,
    required: list[str],
    source_name: str,
) -> None:
    """Raise an informative error when required columns are missing."""
    missing = sorted(set(required) - set(frame.columns))

    if missing:
        raise ValueError(
            f"{source_name} is missing required columns: {missing}"
        )


def normalise_keys(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalise integration keys without changing their meaning."""
    frame = frame.copy()

    frame["date"] = pd.to_datetime(
        frame["date"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    frame["item_id"] = frame["item_id"].astype("string").str.strip()

    frame["store_id"] = pd.to_numeric(
        frame["store_id"],
        errors="coerce",
    ).astype("Int64")

    return frame


def aggregate_catalog() -> pd.DataFrame:
    """Load the item-level catalog and enforce one row per item."""
    columns = [
        "item_id",
        "dept_name",
        "class_name",
        "subclass_name",
        "item_type",
        "weight_volume",
        "weight_netto",
        "fatness",
    ]

    catalog = pd.read_csv(
        CATALOG_PATH,
        usecols=columns,
    )

    catalog["item_id"] = (
        catalog["item_id"]
        .astype("string")
        .str.strip()
    )

    catalog = catalog.drop_duplicates(
        subset=["item_id"],
        keep="first",
    )

    return catalog


def aggregate_stores() -> pd.DataFrame:
    """Load store attributes and enforce one row per store."""
    columns = [
        "store_id",
        "division",
        "format",
        "city",
        "area",
    ]

    stores = pd.read_csv(
        STORES_PATH,
        usecols=columns,
    )

    stores["store_id"] = pd.to_numeric(
        stores["store_id"],
        errors="coerce",
    ).astype("Int64")

    stores = stores.drop_duplicates(
        subset=["store_id"],
        keep="first",
    )

    return stores


def aggregate_price_history() -> pd.DataFrame:
    """
    Aggregate price changes to date/item/store.

    Price history represents price-change events, not necessarily a complete
    daily price series. Therefore Phase 6 records the price-change event
    rather than forward-filling future prices. Forward-filling belongs to
    later feature engineering and must respect chronological ordering.

    When several price events share the same date/item/store key, ``last``
    resolves the tie by file order. The raw files are not chronologically
    sorted, so the representative price and code for such a same-day tie are
    file-order dependent. This is a tie-break within one key (the key already
    contains the date), not a temporal-ordering issue.
    """
    columns = [
        "date",
        "item_id",
        "price",
        "code",
        "store_id",
    ]

    frame = pd.read_csv(
        PRICE_HISTORY_PATH,
        usecols=columns,
    )

    frame = normalise_keys(frame)

    frame["price"] = pd.to_numeric(
        frame["price"],
        errors="coerce",
    )

    return (
        frame.groupby(KEY_COLUMNS, as_index=False)
        .agg(
            price_change_count=("price", "size"),
            price_history_price=("price", "last"),
            price_change_code=("code", "last"),
        )
    )


def aggregate_markdowns() -> pd.DataFrame:
    """Aggregate markdown records to the canonical grain."""
    columns = [
        "date",
        "item_id",
        "normal_price",
        "price",
        "quantity",
        "store_id",
    ]

    frame = pd.read_csv(
        MARKDOWNS_PATH,
        usecols=columns,
    )

    frame = normalise_keys(frame)

    for column in [
        "normal_price",
        "price",
        "quantity",
    ]:
        frame[column] = pd.to_numeric(
            frame[column],
            errors="coerce",
        )

    frame["markdown_discount"] = (
        1
        - (
            frame["price"]
            / frame["normal_price"]
        )
    )

    return (
        frame.groupby(KEY_COLUMNS, as_index=False)
        .agg(
            markdown_record_count=("price", "size"),
            markdown_quantity=("quantity", "sum"),
            markdown_price=("price", "mean"),
            markdown_normal_price=("normal_price", "mean"),
            markdown_discount=("markdown_discount", "mean"),
        )
    )


def aggregate_discounts() -> pd.DataFrame:
    """Aggregate promotion records to the canonical grain."""
    columns = [
        "date",
        "item_id",
        "sale_price_before_promo",
        "sale_price_time_promo",
        "promo_type_code",
        "doc_id",
        "number_disc_day",
        "store_id",
    ]

    frame = pd.read_csv(
        DISCOUNTS_PATH,
        usecols=columns,
        chunksize=CHUNK_SIZE,
    )

    parts: list[pd.DataFrame] = []

    for chunk in frame:
        chunk = normalise_keys(chunk)

        for column in [
            "sale_price_before_promo",
            "sale_price_time_promo",
            "number_disc_day",
        ]:
            chunk[column] = pd.to_numeric(
                chunk[column],
                errors="coerce",
            )

        chunk["discount_rate"] = (
            1
            - (
                chunk["sale_price_time_promo"]
                / chunk["sale_price_before_promo"]
            )
        )

        grouped = (
            chunk.groupby(KEY_COLUMNS, as_index=False)
            .agg(
                discount_record_count=(
                    "sale_price_time_promo",
                    "size",
                ),
                promo_price_before=(
                    "sale_price_before_promo",
                    "mean",
                ),
                promo_price_during=(
                    "sale_price_time_promo",
                    "mean",
                ),
                promo_discount_rate=(
                    "discount_rate",
                    "mean",
                ),
                promo_day_number=(
                    "number_disc_day",
                    "max",
                ),
            )
        )

        parts.append(grouped)

    combined = pd.concat(
        parts,
        ignore_index=True,
    )

    return (
        combined.groupby(KEY_COLUMNS, as_index=False)
        .agg(
            discount_record_count=(
                "discount_record_count",
                "sum",
            ),
            promo_price_before=(
                "promo_price_before",
                "mean",
            ),
            promo_price_during=(
                "promo_price_during",
                "mean",
            ),
            promo_discount_rate=(
                "promo_discount_rate",
                "mean",
            ),
            promo_day_number=(
                "promo_day_number",
                "max",
            ),
        )
    )


def aggregate_online() -> pd.DataFrame:
    """
    Aggregate online sales separately.

    Online sales are not added to physical sales quantity because doing so
    would change the meaning of the primary sales target and could double
    count demand.
    """
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]

    parts: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        ONLINE_PATH,
        usecols=columns,
        chunksize=CHUNK_SIZE,
    ):
        chunk = normalise_keys(chunk)

        for column in [
            "quantity",
            "price_base",
            "sum_total",
        ]:
            chunk[column] = pd.to_numeric(
                chunk[column],
                errors="coerce",
            )

        parts.append(
            chunk.groupby(
                KEY_COLUMNS,
                as_index=False,
            ).agg(
                online_quantity=("quantity", "sum"),
                online_sales_value=("sum_total", "sum"),
                online_average_price=("price_base", "mean"),
            )
        )

    combined = pd.concat(
        parts,
        ignore_index=True,
    )

    return (
        combined.groupby(
            KEY_COLUMNS,
            as_index=False,
        ).agg(
            online_quantity=("online_quantity", "sum"),
            online_sales_value=("online_sales_value", "sum"),
            online_average_price=("online_average_price", "mean"),
        )
    )


def aggregate_actual_matrix() -> pd.DataFrame:
    """
    Aggregate actual-matrix records to the canonical grain.

    The indicator means that an actual-matrix record exists for the exact
    date/item/store key. It does not infer availability for dates not
    represented by the source.
    """
    columns = [
        "item_id",
        "date",
        "store_id",
    ]

    frame = pd.read_csv(
        ACTUAL_MATRIX_PATH,
        usecols=columns,
    )

    frame = normalise_keys(frame)

    frame["matrix_record_flag"] = 1

    return (
        frame.groupby(
            KEY_COLUMNS,
            as_index=False,
        )["matrix_record_flag"]
        .max()
    )


def build_integration() -> dict[str, int]:
    """Build the integrated dataset and return quality metrics."""
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stores = aggregate_stores()
    catalog = aggregate_catalog()
    price_history = aggregate_price_history()
    markdowns = aggregate_markdowns()
    discounts = aggregate_discounts()
    online = aggregate_online()
    actual_matrix = aggregate_actual_matrix()

    sales_rows = 0
    output_rows = 0
    duplicate_output_rows = 0
    unknown_store_rows = 0
    unmatched_catalog_rows = 0
    total_demand_quantity = 0.0
    total_sales_revenue = 0.0
    unique_item_ids: set[str] = set()
    unique_store_ids: set[int] = set()
    date_min: str | None = None
    date_max: str | None = None

    first_write = True

    for chunk in pd.read_csv(
        SALES_PATH,
        usecols=SALES_COLUMNS,
        chunksize=CHUNK_SIZE,
    ):
        chunk = normalise_keys(chunk)

        sales_rows += len(chunk)

        unique_item_ids.update(chunk["item_id"].dropna().tolist())
        unique_store_ids.update(chunk["store_id"].dropna().tolist())

        chunk_dates = chunk["date"].dropna()

        if not chunk_dates.empty:
            chunk_min = chunk_dates.min()
            chunk_max = chunk_dates.max()

            if date_min is None or chunk_min < date_min:
                date_min = chunk_min

            if date_max is None or chunk_max > date_max:
                date_max = chunk_max

        total_demand_quantity += float(chunk["quantity"].sum())
        total_sales_revenue += float(chunk["sum_total"].sum())

        chunk = chunk.merge(
            stores,
            on="store_id",
            how="left",
            validate="many_to_one",
        )

        unknown_store_rows += int(
            chunk["division"].isna().sum()
        )

        chunk = chunk.merge(
            catalog,
            on="item_id",
            how="left",
            validate="many_to_one",
        )

        unmatched_catalog_rows += int(
            chunk["dept_name"].isna().sum()
        )

        chunk = chunk.merge(
            price_history,
            on=KEY_COLUMNS,
            how="left",
            validate="many_to_one",
        )

        chunk = chunk.merge(
            markdowns,
            on=KEY_COLUMNS,
            how="left",
            validate="many_to_one",
        )

        chunk = chunk.merge(
            discounts,
            on=KEY_COLUMNS,
            how="left",
            validate="many_to_one",
        )

        chunk = chunk.merge(
            online,
            on=KEY_COLUMNS,
            how="left",
            validate="many_to_one",
        )

        chunk = chunk.merge(
            actual_matrix,
            on=KEY_COLUMNS,
            how="left",
            validate="many_to_one",
        )

        chunk["matrix_record_flag"] = (
            chunk["matrix_record_flag"]
            .fillna(0)
            .astype("int8")
        )

        for column in [
            "online_quantity",
            "online_sales_value",
            "online_average_price",
            "price_change_count",
            "markdown_record_count",
            "discount_record_count",
        ]:
            chunk[column] = chunk[column].fillna(0)

        duplicate_output_rows += int(
            chunk.duplicated(
                subset=KEY_COLUMNS,
                keep=False,
            ).sum()
        )

        output_rows += len(chunk)

        chunk.to_csv(
            OUTPUT_PATH,
            mode="w" if first_write else "a",
            header=first_write,
            index=False,
        )

        first_write = False

    report = pd.DataFrame(
        [
            {
                "metric": "sales_rows_read",
                "value": sales_rows,
            },
            {
                "metric": "integrated_rows_written",
                "value": output_rows,
            },
            {
                "metric": "row_count_difference",
                "value": sales_rows - output_rows,
            },
            {
                "metric": "duplicate_canonical_grain_rows",
                "value": duplicate_output_rows,
            },
            {
                "metric": "unknown_store_rows",
                "value": unknown_store_rows,
            },
            {
                "metric": "unmatched_catalog_rows",
                "value": unmatched_catalog_rows,
            },
            {
                "metric": "date_min",
                "value": date_min,
            },
            {
                "metric": "date_max",
                "value": date_max,
            },
            {
                "metric": "unique_items",
                "value": len(unique_item_ids),
            },
            {
                "metric": "unique_stores",
                "value": len(unique_store_ids),
            },
            {
                "metric": "total_demand_quantity",
                "value": round(total_demand_quantity, 2),
            },
            {
                "metric": "total_sales_revenue",
                "value": round(total_sales_revenue, 2),
            },
        ]
    )

    report.to_csv(
        QUALITY_REPORT_PATH,
        index=False,
    )

    if sales_rows != output_rows:
        raise RuntimeError(
            "Integration changed the number of sales rows."
        )

    if duplicate_output_rows != 0:
        raise RuntimeError(
            "Integration produced duplicate canonical-grain rows."
        )

    print("Retail data integration completed successfully.")
    print(f"Rows integrated: {output_rows:,}")
    print(f"Date coverage: {date_min} to {date_max}")
    print(f"Unique items: {len(unique_item_ids):,}")
    print(f"Integrated dataset: {OUTPUT_PATH}")
    print(f"Quality report: {QUALITY_REPORT_PATH}")

    return {
        "sales_rows": sales_rows,
        "output_rows": output_rows,
        "duplicate_rows": duplicate_output_rows,
    }


def main() -> None:
    """Run the Phase 6 integration pipeline."""
    print("Integrating cleaned retail datasets...")
    build_integration()


if __name__ == "__main__":
    main()