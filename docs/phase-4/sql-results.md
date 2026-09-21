# Phase 4 — SQL Results

## Database validation

Table row counts:

| Table | Source | Rows |
|---|---:|---:|
| stores | stores.csv | 4 |
| catalog | catalog.csv | 219,810 |
| sales | sales.csv | 7,432,685 |
| markdowns | markdowns.csv | 8,979 |
| price_history | price_history.csv | 698,626 |

Sales date coverage: 2022-08-28 to 2024-09-26 (761 distinct dates).

## SQL analysis

The 18 queries in `sql/retail_analysis.sql` execute and write their results to
`data/analysis/sql_results/query_N.csv`.

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

### Validation finding

Query 17 reports **36,585 sales rows whose `item_id` has no matching catalog
record**, corresponding to **948 distinct sales items**. This is a genuine
data-coverage characteristic: some sold items do not appear in the catalog
table. Phase 5 reports the gap as an informational reference check (36,585 rows
on the raw basis; 36,580 on the cleaned basis), and Phase 6 handles it with a
left join that retains the unmatched sales rows and records
`unmatched_catalog_rows`.

`PRAGMA foreign_key_check` on the database reports **42,426** unsatisfied
catalog references in total: 36,585 in `sales` (the documented gap above), 5,690
in `price_history` (1,174 distinct items) and 151 in `markdowns` (3 distinct
items). Catalog references are informational rather than enforced: the analysis
joins retain unmatched rows, and unknown-store violations are zero.

## Limitation

The SQL analysis is descriptive, and the markdown analysis does not establish
causal impact on demand.
