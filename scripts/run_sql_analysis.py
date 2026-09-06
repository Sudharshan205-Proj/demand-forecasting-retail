"""Run the Phase 4 SQL analysis against the SQLite database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "analysis" / "retail_demand.db"
SQL_PATH = PROJECT_ROOT / "sql" / "retail_analysis.sql"
RESULTS_DIR = PROJECT_ROOT / "data" / "analysis" / "sql_results"


def require_inputs() -> None:
    """Verify the database and SQL analysis file exist."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DATABASE_PATH}"
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(
            f"SQL analysis file not found: {SQL_PATH}"
        )


def load_queries() -> list[tuple[str, str]]:
    """Extract labelled SQL queries from the analysis file."""
    text = SQL_PATH.read_text(encoding="utf-8")

    sections = text.split("-- Query ")

    queries: list[tuple[str, str]] = []

    for section in sections[1:]:
        lines = section.splitlines()

        if not lines:
            continue

        query_number = lines[0].split(" ", 1)[0]
        sql = "\n".join(lines[1:]).strip()

        sql_lines = [
            line
            for line in sql.splitlines()
            if not line.strip().startswith("--")
        ]

        cleaned_sql = "\n".join(sql_lines).strip()

        if cleaned_sql:
            queries.append((query_number, cleaned_sql))

    return queries


def execute_query(
    connection: sqlite3.Connection,
    sql: str,
) -> tuple[list[str], list[tuple]]:
    """Execute one SQL statement and return headers and rows."""
    cursor = connection.execute(sql)

    headers = [
        description[0]
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    return headers, rows


def write_result(
    query_number: str,
    headers: list[str],
    rows: list[tuple],
) -> Path:
    """Write one query result to CSV."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RESULTS_DIR / f"query_{query_number}.csv"

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    return output_path


def run_analysis() -> list[Path]:
    """Run every SQL analysis query and save its results."""
    require_inputs()

    queries = load_queries()

    if not queries:
        raise RuntimeError("No SQL queries were found.")

    connection = sqlite3.connect(DATABASE_PATH)

    output_files: list[Path] = []

    try:
        for query_number, sql in queries:
            headers, rows = execute_query(connection, sql)
            output_path = write_result(
                query_number,
                headers,
                rows,
            )

            output_files.append(output_path)

            print(
                f"Query {query_number}: "
                f"{len(rows):,} result rows -> {output_path.name}"
            )

    finally:
        connection.close()

    return output_files


def main() -> None:
    """Run the analysis and print a completion message."""
    output_files = run_analysis()

    print(
        f"SQL analysis completed successfully. "
        f"Generated {len(output_files)} result files."
    )


if __name__ == "__main__":
    main()
