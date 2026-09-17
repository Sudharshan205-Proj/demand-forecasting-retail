# Phase 4 — Course Content Coverage

## Course: Data Analysis and Organization — Spreadsheets and SQL

| Course concept | Project evidence |
|---|---|
| SQL | `sql/retail_analysis.sql` |
| SELECT | Queries 1–18 |
| WHERE | Query 2 |
| ORDER BY | Queries 1–5 and others |
| GROUP BY | Queries 4, 5, 6, 8, 9, 12–14 |
| HAVING | Query 5 |
| COUNT | Query 3 |
| COUNT DISTINCT | Query 3 |
| SUM | Multiple aggregation queries |
| AVG | Queries 3, 6, 10, 14 |
| Calculated fields | Query 6 |
| Aliases | Throughout the SQL analysis |
| JOIN | Queries 7–9 |
| LEFT JOIN | Queries 15–17 |
| Subquery | Query 10 |
| CTE | Queries 11 and 15 |
| Validation | Queries 16–18 |
| Aggregation | Store, item, department, daily, and monthly analysis |
| Relational analysis | `sql/schema.sql` and joined queries |

## Practical application

The course concepts are applied to the retail demand forecasting
problem rather than demonstrated only with tutorial examples.

## Concepts deferred

Some course concepts are better demonstrated in other project phases.

Spreadsheet-specific functionality was demonstrated in Phase 3.

R programming belongs to the later R-analysis phase.

Visualization and Tableau belong to the visualization phase.

Advanced statistical modelling belongs to later forecasting phases.

## Phase 17 Re-Audit Record

The SQL concepts listed above were verified against the actual executed
analysis during the Phase 17 audit. `sql/retail_analysis.sql` contains 18
labelled queries; `scripts/run_sql_analysis.py` parses and executes all 18
(regression-tested). Each claimed concept (SELECT, WHERE, ORDER BY, GROUP BY,
HAVING, COUNT/COUNT DISTINCT, SUM, AVG, calculated fields, aliases, JOIN,
LEFT JOIN, subquery, CTE, validation, aggregation) is evidenced by the stored
SQL and regenerated result files.