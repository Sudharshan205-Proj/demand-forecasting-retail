"""Tests for Phase 4 SQL analytical patterns."""

from __future__ import annotations

import sqlite3


def build_test_database():
    """Create a small relational database for SQL tests."""
    connection = sqlite3.connect(":memory:")

    connection.executescript(
        """
        CREATE TABLE stores (
            store_id INTEGER PRIMARY KEY,
            city TEXT
        );

        CREATE TABLE catalog (
            item_id INTEGER PRIMARY KEY,
            dept_name TEXT
        );

        CREATE TABLE sales (
            date TEXT,
            item_id INTEGER,
            quantity REAL,
            sum_total REAL,
            store_id INTEGER
        );

        INSERT INTO stores VALUES
            (1, 'City A'),
            (2, 'City B');

        INSERT INTO catalog VALUES
            (100, 'Food'),
            (200, 'Drinks');

        INSERT INTO sales VALUES
            ('2024-01-01', 100, 10, 100, 1),
            ('2024-01-01', 200, 20, 200, 1),
            ('2024-01-02', 100, 30, 300, 2);
        """
    )

    return connection


def test_group_by_store():
    """Verify demand aggregation by store."""
    connection = build_test_database()

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


def test_join_sales_to_stores():
    """Verify relational joins return store attributes."""
    connection = build_test_database()

    result = connection.execute(
        """
        SELECT
            stores.city,
            SUM(sales.quantity) AS total_quantity
        FROM sales
        INNER JOIN stores
            ON sales.store_id = stores.store_id
        GROUP BY stores.city
        ORDER BY stores.city
        """
    ).fetchall()

    connection.close()

    assert result == [
        ("City A", 30.0),
        ("City B", 30.0),
    ]


def test_join_sales_to_catalog():
    """Verify sales can be joined to item metadata."""
    connection = build_test_database()

    result = connection.execute(
        """
        SELECT
            catalog.dept_name,
            SUM(sales.quantity) AS total_quantity
        FROM sales
        INNER JOIN catalog
            ON sales.item_id = catalog.item_id
        GROUP BY catalog.dept_name
        ORDER BY catalog.dept_name
        """
    ).fetchall()

    connection.close()

    assert result == [
        ("Drinks", 20.0),
        ("Food", 40.0),
    ]


def test_having_filters_aggregated_groups():
    """Verify HAVING filters grouped analytical results."""
    connection = build_test_database()

    result = connection.execute(
        """
        SELECT
            store_id,
            SUM(quantity) AS total_quantity
        FROM sales
        GROUP BY store_id
        HAVING SUM(quantity) > 30
        """
    ).fetchall()

    connection.close()

    assert result == []


def test_subquery_compares_against_average():
    """Verify a subquery can compare item totals with an average."""
    connection = build_test_database()

    result = connection.execute(
        """
        SELECT
            item_id,
            total_quantity
        FROM (
            SELECT
                item_id,
                SUM(quantity) AS total_quantity
            FROM sales
            GROUP BY item_id
        )
        WHERE total_quantity > (
            SELECT AVG(item_total)
            FROM (
                SELECT
                    item_id,
                    SUM(quantity) AS item_total
                FROM sales
                GROUP BY item_id
            )
        )
        ORDER BY item_id
        """
    ).fetchall()

    connection.close()

    assert result == [
        (100, 40.0),
    ]


def test_cte_monthly_aggregation():
    """Verify a CTE can create a reusable analytical result."""
    connection = build_test_database()

    result = connection.execute(
        """
        WITH monthly_demand AS (
            SELECT
                substr(date, 1, 7) AS sales_month,
                store_id,
                SUM(quantity) AS total_quantity
            FROM sales
            GROUP BY sales_month, store_id
        )
        SELECT
            sales_month,
            store_id,
            total_quantity
        FROM monthly_demand
        ORDER BY sales_month, store_id
        """
    ).fetchall()

    connection.close()

    assert result == [
        ("2024-01", 1, 30.0),
        ("2024-01", 2, 30.0),
    ]


def test_load_queries_parses_all_labelled_queries():
    """Every labelled query in the production SQL file must be parseable.

    Guards the SQL parser against a malformed `-- Query N` section header,
    which would silently drop a required analysis query.
    """
    from scripts.run_sql_analysis import load_queries

    queries = load_queries()

    numbers = [number for number, _ in queries]

    assert numbers == [str(number) for number in range(1, 19)]


def test_require_inputs_reports_missing_database(tmp_path, monkeypatch):
    """The SQL runner must fail clearly when the database is missing."""
    import pytest

    import scripts.run_sql_analysis as runner

    monkeypatch.setattr(runner, "DATABASE_PATH", tmp_path / "missing.db")

    with pytest.raises(FileNotFoundError):
        runner.require_inputs()
