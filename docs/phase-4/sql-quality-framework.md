# Phase 4 — SQL Quality Framework

The SQL workflow maintains the quality principles below. Each principle is
stated with how it is enforced; a principle that cannot be checked mechanically
is listed under "Not mechanically enforced" rather than claimed. The
requirements are implemented in `scripts/create_sqlite_database.py` and
`scripts/run_sql_analysis.py`, defined in `sql/schema.sql` and
`sql/retail_analysis.sql`, evidenced by `data/analysis/retail_demand.db` and the
18 files in `data/analysis/sql_results/`, and asserted by
`tests/test_create_sqlite_database.py` (3 tests) and `tests/test_sql_analysis.py`
(8 tests).

## Report format

Phase 4 produces **no machine-readable pass/fail report**, so it contributes
nothing to the run-gating quality total. Its quality is enforced by in-script
guards and asserted by the two test modules below.

## 1. Input and schema integrity

- every required input exists before the database is created;
- the schema declares the documented keys and indexes;
- the database is regenerable from the raw files alone.

*Implementation:* `require_files()` raises `FileNotFoundError` naming the
missing path before any table is dropped. `sql/schema.sql` drops and recreates
the five tables, declares `stores.store_id` and `catalog.item_id` as primary
keys, declares the item and store foreign keys on `sales`, `markdowns` and
`price_history`, and creates seven indexes:

| Index | Table (columns) |
|---|---|
| `idx_sales_date` | `sales (date)` |
| `idx_sales_item` | `sales (item_id)` |
| `idx_sales_store` | `sales (store_id)` |
| `idx_sales_store_date` | `sales (store_id, date)` |
| `idx_markdowns_item` | `markdowns (item_id)` |
| `idx_markdowns_store_date` | `markdowns (store_id, date)` |
| `idx_price_history_item_store_date` | `price_history (item_id, store_id, date)` |

The bulk load runs with `PRAGMA foreign_keys = OFF` and turns it back on at the
end of the build, with `PRAGMA journal_mode = WAL` and
`PRAGMA synchronous = NORMAL`. The raw CSVs are never modified.

*Tests:* `test_sqlite_tables_can_be_created`.

## 2. Row-count reconciliation

Every loaded table matches its source row count, and a mismatch stops the build
rather than publishing a partial database.

*Implementation:* `validate_counts()` compares each table against the source
file it was loaded from and raises `RuntimeError` on a mismatch, before the
database is published. Measured counts:

| Table | Source | Rows |
|---|---|---:|
| `stores` | `stores.csv` | 4 |
| `catalog` | `catalog.csv` | 219,810 |
| `sales` | `sales.csv` | 7,432,685 |
| `markdowns` | `markdowns.csv` | 8,979 |
| `price_history` | `price_history.csv` | 698,626 |

Sales coverage is 2022-08-28 to 2024-09-26 across **761** distinct dates.

*Tests:* `test_sales_row_count`, `test_store_sales_aggregation`.

## 3. Query integrity

Every labelled query parses, runs and writes its own result file, and a missing
database or an empty query set fails loudly.

*Implementation:* `load_queries()` parses the 18 labelled queries
(`-- Query 1` … `-- Query 18`) from `sql/retail_analysis.sql`, and
`run_analysis()` raises `RuntimeError("No SQL queries were found.")` when none
load. `execute_query()` writes each result to
`data/analysis/sql_results/query_N.csv`, and the run reports "Generated 18
result files."

*Tests:* `test_load_queries_parses_all_labelled_queries`,
`test_require_inputs_reports_missing_database`, and six query-shape tests
(`test_group_by_store`, `test_join_sales_to_stores`,
`test_join_sales_to_catalog`, `test_having_filters_aggregated_groups`,
`test_subquery_compares_against_average`, `test_cte_monthly_aggregation`).

## 4. Course-technique coverage

The 18 queries cover SELECT, WHERE, ORDER BY, GROUP BY, HAVING, aggregate
functions, calculated fields, aliases, JOIN, LEFT JOIN, a subquery, a CTE, time
aggregation and three validation queries (Queries 16-18).

**Temporary tables** are the one deliberate exception: Query 11 uses a common
table expression instead of an explicit temporary table, and the course row is
recorded as not applicable rather than adding a temporary table only to claim
coverage.

## 5. Referential integrity: measured, not enforced

The catalog gap is measured, recorded and handled rather than silently forced.

`PRAGMA foreign_key_check` on the database reports **42,426** unsatisfied
catalog references — **36,585** in `sales` (948 distinct items), **5,690** in
`price_history` (1,174 distinct items) and **151** in `markdowns` (3 distinct
items). Unknown-store violations are **0**. Catalog references are informational
rather than enforced: the analysis joins retain unmatched rows through left
joins. The figures are recorded in [`sql-results.md`](sql-results.md),
[`database-schema.md`](database-schema.md) and
[`../phase-6/integration-results.md`](../phase-6/integration-results.md).

## 6. Scope and leakage control

The SQL analysis is descriptive. It introduces no forecasting, no model selection
and no look-ahead: every query reads the historical tables only, and no later
phase consumes a SQL result as a model input.

## 7. Failure behaviour

| Situation | Behaviour |
|---|---|
| An input CSV absent | `require_files()` raises `FileNotFoundError` naming the path; no table is touched |
| An input CSV absent at query time | `require_inputs()` raises `FileNotFoundError` naming the database |
| Row-count mismatch after load | `validate_counts()` raises `RuntimeError`; the database is not published |
| No labelled queries parsed | `run_analysis()` raises `RuntimeError("No SQL queries were found.")` |
| Long run | `run_sql_analysis.py` performs large full-table scans and can take 22–57 minutes. Results are written per query, so a long run is not a failure; it is documented with its expected duration in the reproducibility runbook |

## 8. Not mechanically enforced

- **Query-result correctness.** The tests assert the *shape* of six query
  families; the values in each `query_N.csv` are reconciled against their
  sources in [`sql-results.md`](sql-results.md).
- Index usage and query plans; no execution-plan assertion exists.
- Temporary-table coverage (see §4).

## 9. Reproducibility

Two commands rebuild the demonstration from the raw files
(`scripts/create_sqlite_database.py` then `scripts/run_sql_analysis.py`). The
database is ~1.06 GB and both it and the 18 result files are generated
artifacts excluded from Git. Re-execution reproduces the row counts in §2 and
the 18 result files.

## 10. Documentation

The plan, schema, query set and results are recorded in
[`sql-analysis-plan.md`](sql-analysis-plan.md),
[`database-schema.md`](database-schema.md),
[`sql-analysis.md`](sql-analysis.md) and [`sql-results.md`](sql-results.md),
with the course mapping in [`course-content-coverage.md`](course-content-coverage.md)
and the phase summary in [`phase-4-checklist.md`](phase-4-checklist.md).
