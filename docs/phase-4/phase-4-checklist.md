# Phase 4 — SQL & Database Analysis

## Purpose

Phase 4 builds the relational SQLite database from the retail dataset and uses
SQL to answer the project's store, product, department, time and markdown
questions.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Database schema | `sql/schema.sql` — five tables (stores, catalog, sales, markdowns, price_history), primary and foreign keys, seven indexes |
| SQL analysis | `sql/retail_analysis.sql` — 18 labelled queries |
| Builders | `scripts/create_sqlite_database.py` (chunked load, ~1.06 GB database) and `scripts/run_sql_analysis.py` (writes 18 result CSVs) |
| Tests | `tests/test_create_sqlite_database.py` (3) and `tests/test_sql_analysis.py` (8) — 11 tests |

## SQL techniques demonstrated

SELECT, WHERE, ORDER BY, GROUP BY, HAVING, aggregate functions, calculated
fields, aliases, JOIN, LEFT JOIN, a subquery, CTEs, time aggregation and three
validation queries. Temporary tables are not used: the analysis uses common
table expressions instead, and the course row is recorded as not applicable.

## Key results

| Table | Rows |
|---|---:|
| stores | 4 |
| catalog | 219,810 |
| sales | 7,432,685 |
| markdowns | 8,979 |
| price_history | 698,626 |

Sales coverage is 2022-08-28 → 2024-09-26 (761 distinct dates). Query 17
identifies 36,585 sales rows (948 distinct items) with no catalog match; the
analysis retains them through left joins and records the gap.

## Course coverage

Phase 4 demonstrates the course's relational-database and SQL concepts against
the retail demand problem ([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`sql-analysis-plan.md`](sql-analysis-plan.md) — plan
- [`database-schema.md`](database-schema.md) — schema
- [`sql-analysis.md`](sql-analysis.md) — analysis
- [`sql-results.md`](sql-results.md) — results
- [`sql-quality-framework.md`](sql-quality-framework.md) — quality practices
