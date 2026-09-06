# Phase 4 — SQL and Database Analysis Plan

## Objective

Build a reproducible SQLite relational database from the retail demand
forecasting dataset and use SQL to answer business questions identified
during the earlier project phases.

## Scope

Phase 4 focuses on relational analysis.

The primary tables are:

- stores
- catalog
- sales
- markdowns
- price_history

The raw CSV files remain unchanged.

## Why SQLite?

SQLite provides a lightweight relational database suitable for:

- relational schema design
- SQL querying
- joins
- aggregation
- filtering
- subqueries
- CTEs
- validation

It is appropriate for this internship project because it demonstrates
relational database skills without requiring a separate database server.

## Large-data strategy

The sales dataset contains millions of rows.

The database loader therefore reads sales.csv in chunks rather than
loading the entire file into memory at once.

## SQL skills demonstrated

The analysis will demonstrate:

- SELECT
- WHERE
- ORDER BY
- GROUP BY
- HAVING
- COUNT
- COUNT DISTINCT
- SUM
- AVG
- calculated fields
- aliases
- INNER JOIN
- LEFT JOIN
- subqueries
- CTEs
- validation queries
- time-based aggregation

## Business questions

1. How does demand differ between stores?
2. Which items have the greatest recorded demand?
3. How does demand vary over time?
4. Which departments generate the greatest demand?
5. Which stores generate the greatest recorded sales value?
6. How can store and product metadata be incorporated into demand analysis?
7. What markdown activity is recorded?
8. Are there data-integrity problems in relational joins?

## Limitations

Markdown analysis is descriptive and associational.

It does not establish that markdowns caused changes in demand.

The online and discounts-history datasets are not incorporated into the
initial relational model because their coverage and data-quality
characteristics require additional investigation.