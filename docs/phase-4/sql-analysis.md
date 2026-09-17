# Phase 4 — SQL Analysis

## Purpose

This document records the SQL-based analysis performed against the
SQLite retail demand database.

## Analysis techniques

The SQL analysis demonstrates:

- filtering with WHERE
- sorting with ORDER BY
- aggregation with SUM, AVG, and COUNT
- grouping with GROUP BY
- group filtering with HAVING
- aliases
- calculated fields
- relational joins
- subqueries
- common table expressions
- data validation
- time-based aggregation

## Analytical areas

### Store performance

Store-level aggregation compares recorded demand and sales value
between stores.

### Product demand

Item-level aggregation identifies products with the highest recorded
demand.

### Department analysis

Sales are joined to catalog metadata to examine demand by department.

### Time patterns

Daily and monthly aggregations provide historical demand patterns that
can be used as inputs to later forecasting work.

### Markdown activity

Markdown records are summarized by store and date.

This analysis is descriptive and does not establish causal effects.

## Validation

SQL validation queries check whether sales records have matching:

- store records
- catalog records

Additional validation checks temporal coverage and record counts.

## Reproducibility

The SQL queries are stored in:

`sql/retail_analysis.sql`

The database can be rebuilt using:

`scripts/create_sqlite_database.py`

The SQL results can be regenerated using:

`scripts/run_sql_analysis.py`

## Phase 17 Re-Audit Record

The Phase 4 SQL analysis was re-verified during the Phase 17 audit. The
database was rebuilt and all 18 queries re-executed successfully.

Verified analytical areas:

- **Store performance:** 4 stores ranked by total quantity and sales value;
  stores 1 and 4 lead. Store aggregation totals match the Phase 3 workbook.
- **Product demand:** 28,182 distinct sales items; top item by quantity
  `b0d24502fb66` (2,022,732).
- **Department analysis:** sales joined to catalog metadata; top departments
  include Auxiliary Group, Bread and Fruits by quantity.
- **Time patterns:** 761 daily records from 2022-08-28 to 2024-09-26; monthly
  aggregation supports trend inspection.
- **Markdown activity:** markdown records summarized by store (stores 1, 2, 4);
  average markdown percentage ≈ 38–44% by store.

### Data-integrity finding (Query 17)

Query 17 found **36,585 sales rows (948 distinct items) with no matching
catalog record**. This is a genuine data-coverage finding: some sold items are
absent from the catalog. Later phases that join sales to catalog metadata must
account for this (e.g., LEFT JOIN with null handling). The catalog table also
retains the 27,571 ragged lines described in Phase 2 (garbled trailing
attributes), but these do not affect the `item_id` join key.