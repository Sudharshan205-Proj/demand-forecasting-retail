# Phase 5 — Data Quality Framework

## Purpose

This document defines the quality dimensions used to evaluate the retail
sales data before later forecasting work.

## Quality dimensions

| Dimension | Definition | Project check |
|---|---|---|
| Completeness | Required information is present | Missing-value checks |
| Accuracy | Values represent valid observations | Range and consistency checks |
| Consistency | Related fields agree | Revenue consistency checks |
| Validity | Values follow expected formats/rules | Type and range validation |
| Uniqueness | Duplicate observations are controlled | Duplicate detection |
| Integrity | Relationships remain valid | Store referential-integrity checks |
| Timeliness | Dates fall within the relevant period | Temporal coverage checks |
| Reliability | Source and transformations are documented | Provenance and cleaning log |

## Required sales fields

The primary sales dataset requires:

- date
- item_id
- quantity
- price_base
- sum_total
- store_id

## Missing-data policy

Missing required fields are quality failures.

They are reported before cleaning.

Records missing required analytical fields are excluded from the cleaned
dataset.

## Duplicate policy

Exact duplicate rows are identified.

Confirmed duplicate rows are removed.

The before-and-after counts are recorded.

## Date policy

Dates are parsed explicitly.

Invalid dates are reported.

The minimum and maximum valid dates are recorded.

Temporal anomalies are investigated rather than silently deleted.

## Numeric policy

### Quantity

Expected:

- numeric
- suitable for demand analysis
- non-negative for the primary demand dataset

### Base price

Expected:

- numeric
- non-negative

### Revenue

Expected:

- numeric
- consistent with the source's monetary representation

Revenue consistency is evaluated but not blindly rewritten.

## Referential integrity

Store IDs are compared with the authoritative `stores.csv` lookup.

Unknown store IDs are reported.

Item IDs are checked for presence.

Catalog membership is treated as an informational integrity check because
catalog coverage can differ from sales coverage.

## Outlier policy

Outliers are not automatically removed.

An extreme value is not equivalent to an invalid value.

Potentially unusual observations are retained unless they violate an explicit
validity rule.

This prevents legitimate high-demand periods from being incorrectly removed.

## ROCCC

The project applies the ROCCC framework:

### Reliability

The source dataset, schema, and cleaning process are documented.

### Originality

The project preserves the supplied raw source data and does not overwrite
it.

### Comprehensiveness

The available files and known limitations are documented.

### Currency

Date ranges are checked and anomalous temporal coverage is recorded.

### Citation

The dataset source and project documentation identify the source of the data.

## Quality-assurance principle

Every cleaning operation must have:

1. A documented reason.
2. A deterministic rule.
3. A measurable before/after effect.
4. A validation check.

No cleaning step should be performed merely because a value looks unusual.