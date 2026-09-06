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