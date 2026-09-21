# Phase 4 — SQL Analysis

## Purpose

This document records the SQL-based analysis performed against the SQLite retail
demand database.

## Analysis techniques

- Filtering with WHERE
- Sorting with ORDER BY
- Aggregation with SUM, AVG and COUNT
- Grouping with GROUP BY
- Group filtering with HAVING
- Aliases
- Calculated fields
- Relational joins
- Subqueries
- Common table expressions
- Data validation
- Time-based aggregation

## Analytical areas

### Store performance

Store-level aggregation compares recorded demand and sales value between stores.

### Product demand

Item-level aggregation identifies products with the highest recorded demand.

### Department analysis

Sales are joined to catalog metadata to examine demand by department.

### Time patterns

Daily and monthly aggregations provide historical demand patterns that inform
the later forecasting work.

### Markdown activity

Markdown records are summarized by store and date. This analysis is descriptive
and does not establish causal effects.

## Validation

SQL validation queries check whether sales records have matching store records
and catalog records, and check temporal coverage and record counts.

## Reproducibility

The SQL queries are stored in `sql/retail_analysis.sql`.

The database is rebuilt with `scripts/create_sqlite_database.py`.

The SQL results are regenerated with `scripts/run_sql_analysis.py`.
