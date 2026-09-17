# Phase 4 — SQL Results

## Status

COMPLETE — VERIFIED

The SQLite database was created and all 18 SQL analysis queries were executed
successfully during the Phase 17 re-audit.

## Database validation

Table row counts verified from the regenerated database:

| Table | Expected source | Actual rows |
|---|---:|---:|
| stores | stores.csv | 4 |
| catalog | catalog.csv | 219,810 |
| sales | sales.csv | 7,432,685 |
| markdowns | markdowns.csv | 8,979 |
| price_history | price_history.csv | 698,626 |

Sales date coverage: 2022-08-28 to 2024-09-26 (761 distinct dates).

## SQL analysis

All 18 queries in `sql/retail_analysis.sql` were executed successfully and their
results written to `data/analysis/sql_results/query_N.csv`.

### Query summaries

| Query | Area | Key result |
|---|---|---|
| 1 | Basic SELECT / ORDER BY | Stores present (4) |
| 2 | WHERE filter | High-quantity sales (quantity > 100) |
| 3 | Aggregate functions | 7,432,685 rows; 28,182 items; 4 stores |
| 4 | GROUP BY | Store demand ranking |
| 5 | HAVING | Stores with > 1,000,000 demand |
| 6 | Calculated field | Sales value per unit by store |
| 7–9 | JOIN / LEFT JOIN | Store, catalog and department demand enrichment |
| 10 | Subquery | Items above average demand |
| 11–12 | Time aggregation | Monthly and daily demand |
| 13 | Top items | Highest recorded demand items |
| 14 | Markdown analysis | Markdown records and average markdown % by store |
| 15 | CTE + LEFT JOIN | Markdown and demand by date |
| 16 | Validation | Unmatched store records: 0 |
| 17 | Validation | Unmatched catalog records: 36,585 rows (948 distinct items) |
| 18 | Date coverage | Earliest/latest sales dates and distinct date count |

### Notable validation finding

Query 17 reports **36,585 sales rows whose `item_id` has no matching catalog
record**, corresponding to **948 distinct sales items**. This is a genuine
data-coverage finding (not a parsing artifact) and indicates that some sold
items do not appear in the catalog table. Later phases should account for this
when joining sales to catalog metadata.

**Resolution (Phase 17):** Phase 5 now reports this gap as an informational
reference check (36,585 rows / 948 distinct items on the raw basis; 36,580 rows
on the cleaned basis), and Phase 6 handles it with a left join that retains the
unmatched sales rows and records `unmatched_catalog_rows`.

## Important limitation

The SQL analysis is descriptive.

Markdown analysis does not establish causal impact on demand.

## Phase 17 Re-Audit Record

During the Phase 17 re-audit, `scripts/create_sqlite_database.py` was re-executed
(rebuilding the 1.06 GB database), and `scripts/run_sql_analysis.py` was
re-executed, regenerating all 18 query result CSVs. Row counts and representative
query outputs were inspected and match the Phase 2 verified dataset facts. The
catalog ragged-line artifact documented in Phase 2 persists in the catalog table
(219,810 rows) but does not affect the `item_id` join key.