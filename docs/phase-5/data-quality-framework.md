# Phase 5 — Data Quality Framework

## Purpose

This document defines the quality dimensions applied to the retail sales data
before the later forecasting work.

## Report format

`data/processed/data_quality_report.csv` is a **metric/value table**, not a
pass/fail gate: it records one row per measured quantity (`metric`, `value`) so
that every figure in [`data-quality-results.md`](data-quality-results.md) is
reproducible from a single file. It carries no `passed` column by design, and
the dimensions below are enforced by `tests/test_clean_retail_data.py`. It is
excluded from the run-gating quality total, which counts only the reports that
gate a run.

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

date, item_id, quantity, price_base, sum_total, store_id.

## Missing-data policy

Missing required fields are quality failures, reported before cleaning.
Records missing required analytical fields are excluded from the cleaned
dataset.

## Duplicate policy

Exact duplicate rows are identified and confirmed duplicates removed; the
before-and-after counts are recorded.

## Date policy

Dates are parsed explicitly, invalid dates are reported, and the minimum and
maximum valid dates are recorded. Temporal anomalies are investigated rather
than silently deleted.

## Numeric policy

- **Quantity** — numeric, non-negative for the primary demand dataset.
- **Base price** — numeric, non-negative.
- **Revenue** — numeric and consistent with the source's monetary
  representation. Revenue consistency is evaluated but not blindly rewritten.

## Referential integrity

Store IDs are compared with the authoritative `stores.csv` lookup and unknown
store IDs are reported. Item IDs are checked for presence. Catalog membership is
an informational integrity check, because catalog coverage can differ from sales
coverage.

## Outlier policy

Outliers are not automatically removed: an extreme value is not equivalent to an
invalid value. Potentially unusual observations are retained unless they violate
an explicit validity rule, which prevents legitimate high-demand periods from
being removed.

## ROCCC

- **Reliability** — the source dataset, schema and cleaning process are
  documented.
- **Originality** — the supplied raw source data is preserved and never
  overwritten.
- **Comprehensiveness** — the available files and known limitations are
  documented.
- **Currency** — date ranges are checked and anomalous temporal coverage is
  recorded.
- **Citation** — the dataset source is identified in the project documentation.

## Quality-assurance principle

Every cleaning operation has a documented reason, a deterministic rule, a
measurable effect and a validation check. No cleaning step is performed merely
because a value looks unusual.
