"""Create the SQLite database used for Phase 4 SQL analysis.

The script loads selected retail source tables into a reproducible SQLite
database. Large transaction tables are loaded in chunks to avoid requiring
the complete sales dataset to fit in memory.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATABASE_PATH = PROJECT_ROOT / "data" / "analysis" / "retail_demand.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"

SALES_PATH = RAW_DATA_DIR / "sales.csv"
STORES_PATH = RAW_DATA_DIR / "stores.csv"
CATALOG_PATH = RAW_DATA_DIR / "catalog.csv"
MARKDOWNS_PATH = RAW_DATA_DIR / "markdowns.csv"
PRICE_HISTORY_PATH = RAW_DATA_DIR / "price_history.csv"

SALES_CHUNK_SIZE = 250_000


def require_files() -> None:
    """Verify that all required source files exist."""
    required_files = [
        SALES_PATH,
        STORES_PATH,
        CATALOG_PATH,
        MARKDOWNS_PATH,
        PRICE_HISTORY_PATH,
        SCHEMA_PATH,
    ]

    missing = [path for path in required_files if not path.exists()]

    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(
            f"Required Phase 4 files are missing:\n{missing_text}"
        )


def create_schema(connection: sqlite3.Connection) -> None:
    """Create the database schema from the SQL schema file."""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema_sql)


def load_stores(connection: sqlite3.Connection) -> int:
    """Load the store lookup table."""
    columns = [
        "store_id",
        "division",
        "format",
        "city",
        "area",
    ]

    dataframe = pd.read_csv(STORES_PATH, usecols=columns)

    dataframe.to_sql(
        "stores",
        connection,
        if_exists="append",
        index=False,
    )

    return len(dataframe)


def load_catalog(connection: sqlite3.Connection) -> int:
    """Load the item catalog."""
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

    dataframe = pd.read_csv(CATALOG_PATH, usecols=columns)

    dataframe.to_sql(
        "catalog",
        connection,
        if_exists="append",
        index=False,
    )

    return len(dataframe)


def load_sales(connection: sqlite3.Connection) -> int:
    """Load the large sales table in chunks."""
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]

    total_rows = 0

    for chunk in pd.read_csv(
        SALES_PATH,
        usecols=columns,
        chunksize=SALES_CHUNK_SIZE,
    ):
        chunk.to_sql(
            "sales",
            connection,
            if_exists="append",
            index=False,
        )

        total_rows += len(chunk)

    return total_rows


def load_markdowns(connection: sqlite3.Connection) -> int:
    """Load markdown records."""
    columns = [
        "date",
        "item_id",
        "normal_price",
        "price",
        "quantity",
        "store_id",
    ]

    dataframe = pd.read_csv(MARKDOWNS_PATH, usecols=columns)

    dataframe.to_sql(
        "markdowns",
        connection,
        if_exists="append",
        index=False,
    )

    return len(dataframe)


def load_price_history(connection: sqlite3.Connection) -> int:
    """Load historical price records."""
    columns = [
        "date",
        "item_id",
        "price",
        "code",
        "store_id",
    ]

    dataframe = pd.read_csv(PRICE_HISTORY_PATH, usecols=columns)

    dataframe.to_sql(
        "price_history",
        connection,
        if_exists="append",
        index=False,
    )

    return len(dataframe)


def validate_counts(
    connection: sqlite3.Connection,
) -> dict[str, int]:
    """Return row counts for all Phase 4 tables."""
    tables = [
        "stores",
        "catalog",
        "sales",
        "markdowns",
        "price_history",
    ]

    counts: dict[str, int] = {}

    for table in tables:
        query = f"SELECT COUNT(*) FROM {table}"
        counts[table] = connection.execute(query).fetchone()[0]

    return counts


def create_database() -> dict[str, int]:
    """Create and validate the Phase 4 SQLite database."""
    require_files()

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA foreign_keys = OFF")

        create_schema(connection)

        stores_rows = load_stores(connection)
        catalog_rows = load_catalog(connection)
        sales_rows = load_sales(connection)
        markdown_rows = load_markdowns(connection)
        price_history_rows = load_price_history(connection)

        connection.commit()

        connection.execute("PRAGMA foreign_keys = ON")

        counts = validate_counts(connection)

        expected = {
            "stores": stores_rows,
            "catalog": catalog_rows,
            "sales": sales_rows,
            "markdowns": markdown_rows,
            "price_history": price_history_rows,
        }

        if counts != expected:
            raise RuntimeError(
                f"Database row-count validation failed.\n"
                f"Expected: {expected}\n"
                f"Actual: {counts}"
            )

        return counts

    finally:
        connection.close()


def main() -> None:
    """Create the database and print the validation summary."""
    counts = create_database()

    print("SQLite database created successfully.")
    print(f"Output: {DATABASE_PATH}")

    for table, count in counts.items():
        print(f"{table}: {count:,} rows")


if __name__ == "__main__":
    main()
