# Phase 5 — Data Cleaning Plan

## Purpose

This phase establishes a reproducible data-cleaning and quality-assurance
process for the retail demand forecasting project.

The objective is to produce a trustworthy analytical sales dataset without
modifying the original raw source files.

## Primary source

The primary source for the cleaned demand dataset is:

`data/raw/sales.csv`

Supporting reference data:

- `data/raw/stores.csv`
- `data/raw/catalog.csv`

The following files are not part of the primary Phase 5 sales-cleaning
pipeline:

- `online.csv`
- `markdowns.csv`
- `price_history.csv`
- `discounts_history.csv`
- `actual_matrix.csv`

They remain available for later analysis and integration where appropriate.

## Why sales.csv is the primary cleaning target

The project objective is retail demand forecasting.

The sales table contains the principal historical demand variables:

- date
- item_id
- quantity
- price_base
- sum_total
- store_id

Cleaning this table provides the foundation for later forecasting work.

## Raw-data protection

The raw dataset must never be overwritten.

The cleaning process reads from:

`data/raw/sales.csv`

and writes the cleaned dataset to:

`data/processed/sales_clean.csv`

## Required columns

The cleaned sales dataset requires:

- date
- item_id
- quantity
- price_base
- sum_total
- store_id

The original CSV index column is not part of the analytical schema.

## Cleaning checks

The pipeline will check:

1. Required columns
2. Data types
3. Missing values
4. Duplicate records
5. Invalid dates
6. Invalid quantities
7. Invalid prices
8. Invalid revenue values
9. Invalid store identifiers
10. Invalid item identifiers
11. Revenue consistency
12. Date-range consistency
13. Referential integrity with stores

## Missing values

Missing values in required analytical fields are treated as data-quality
issues.

Records with missing required fields cannot reliably represent a sales
observation and will therefore be excluded from the cleaned sales dataset.

The number of affected records must be reported before removal.

## Duplicate records

Exact duplicate records are checked explicitly.

Confirmed duplicate records are removed from the cleaned dataset.

The number of duplicates removed must be recorded in the quality report.

## Dates

Dates are converted to a standard date representation.

Invalid dates are identified and reported.

Dates outside the documented primary sales period are not automatically
deleted solely because they are unusual. They must first be identified and
documented.

## Quantity

Quantity is expected to be numeric.

Negative demand quantities are treated as invalid for the primary demand
dataset unless a documented business interpretation establishes that they
represent legitimate returns or adjustments.

The pipeline therefore reports negative quantities separately before applying
the cleaning rule.

## Price

`price_base` is expected to be numeric and non-negative.

Negative prices are treated as invalid.

Zero prices are retained unless there is evidence that they are invalid,
because zero-valued prices may represent legitimate business records.

## Revenue

`sum_total` is expected to be numeric.

Negative revenue is treated as a quality issue.

Where appropriate, the pipeline compares:

`quantity × price_base`

with `sum_total`.

Differences are reported rather than silently overwritten.

This distinction is important because discounts, rounding, or other source
logic may explain legitimate differences.

## Store identifiers

Store IDs must correspond to the known stores table.

Unknown store IDs are reported as referential-integrity failures.

## Item identifiers

Item IDs must be present for demand observations.

Missing item IDs are treated as invalid required fields.

Catalog membership is reported as a reference check rather than used as an
automatic deletion rule because the catalog and sales datasets do not
necessarily have identical coverage.

## Outliers

Extreme values are not automatically deleted.

A large quantity or price may represent a legitimate retail observation.

Phase 5 therefore distinguishes:

- invalid values
- suspicious values
- legitimate extreme values

Potential outliers are reported for later exploratory analysis.

## Transformations

The cleaning pipeline may:

- remove the raw CSV index column
- convert dates to a standard date type
- convert numeric columns to numeric data types
- remove confirmed duplicate records
- remove records missing required analytical fields
- remove records failing explicitly documented validity rules

The pipeline must not silently alter business values.

## Reproducibility

The cleaning process must be executable from the repository root:

```text
python scripts/clean_retail_data.py
```

No absolute machine-specific paths may be used.

## Validation principle

The cleaned dataset is not considered valid merely because the script
completed.

Post-cleaning quality checks must verify that the resulting dataset satisfies
the documented rules.

## Scope boundary

This phase focuses on data cleaning and quality assurance.

Forecasting models, feature engineering, model training, hyperparameter
tuning, and application development belong to later phases.

## Phase 17 Re-Audit Record

AUDITED — COMPLETE

The planned cleaning checks were reconciled against the executed pipeline.
Two checks that the plan required were not implemented in the original script
and were added during this audit:

- catalog membership reported as an informational reference check
  ("Item identifiers" and check 10), and
- valid-date coverage recording (check 12).

No cleaning rule, threshold or output schema was changed: 7,432,685 rows are
read and 7,431,026 are written, exactly as before. All other checks
(required columns, types, missing values, duplicates, invalid dates, invalid
quantities, invalid prices, invalid revenue, store referential integrity and
revenue consistency) were verified against the executed output in
`data-quality-results.md`.