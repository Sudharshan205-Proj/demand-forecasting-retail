"""Tests for Phase 4 SQLite database construction."""

from __future__ import annotations

import sqlite3

import pandas as pd


def test_sqlite_tables_can_be_created(tmp_path):
    """Verify that the Phase 4 schema creates the expected tables."""
    database_path = tmp_path / "test.db"

    connection = sqlite3.connect(database_path)

    schema = """
    CREATE TABLE stores (
        store_id INTEGER PRIMARY KEY,
        city TEXT
    );

    CREATE TABLE catalog (
        item_id INTEGER PRIMARY KEY,
        dept_name TEXT
    );

    CREATE TABLE sales (
        date TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        sum_total REAL,
        store_id INTEGER NOT NULL
    );
    """

    connection.executescript(schema)

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    assert [row[0] for row in tables] == [
        "catalog",
        "sales",
        "stores",
    ]


def test_sales_row_count(tmp_path):
    """Verify that rows inserted into SQLite are counted correctly."""
    database_path = tmp_path / "test.db"

    connection = sqlite3.connect(database_path)

    dataframe = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "item_id": [1, 2],
            "quantity": [10, 20],
            "sum_total": [100.0, 200.0],
            "store_id": [1, 1],
        }
    )

    dataframe.to_sql(
        "sales",
        connection,
        index=False,
        if_exists="replace",
    )

    count = connection.execute(
        "SELECT COUNT(*) FROM sales"
    ).fetchone()[0]

    connection.close()

    assert count == 2


def test_store_sales_aggregation(tmp_path):
    """Verify SQLite aggregation produces the expected demand total."""
    database_path = tmp_path / "test.db"

    connection = sqlite3.connect(database_path)

    dataframe = pd.DataFrame(
        {
            "store_id": [1, 1, 2],
            "quantity": [10, 20, 30],
        }
    )

    dataframe.to_sql(
        "sales",
        connection,
        index=False,
        if_exists="replace",
    )

    result = connection.execute(
        """
        SELECT
            store_id,
            SUM(quantity) AS total_quantity
        FROM sales
        GROUP BY store_id
        ORDER BY store_id
        """
    ).fetchall()

    connection.close()

    assert result == [
        (1, 30.0),
        (2, 30.0),
    ]
