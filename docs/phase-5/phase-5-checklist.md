# Phase 5 — Data Cleaning & Quality Assurance

## Purpose

Phase 5 cleans the raw sales data under documented, deterministic rules and
produces the analytical dataset and quality records that the later phases
consume.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Cleaned dataset | `data/processed/sales_clean.csv` (7,431,026 rows, canonical header `date,item_id,quantity,price_base,sum_total,store_id`) |
| Quality report | `data/processed/data_quality_report.csv` — one row per measured quantity |
| Cleaning summary | `data/processed/cleaning_summary.csv` |
| Pipeline | `scripts/clean_retail_data.py` |
| Tests | `tests/test_clean_retail_data.py` — 19 tests |

## Quality dimensions applied

Completeness, accuracy, consistency, validity, uniqueness, referential
integrity, temporal coverage and reliability ([`data-quality-framework.md`](data-quality-framework.md)).

## Key results

| Metric | Result |
|---|---:|
| Rows read | 7,432,685 |
| Rows written | 7,431,026 |
| Rows removed | 1,659 (about 0.02%) |
| Revenue mismatches (reported, not rewritten) | 1,041,252 |
| Potential quantity outliers (screening, retained) | 73,507 |
| Sales rows with no catalog match | 36,585 (948 distinct items) |
| Valid-date coverage | 2022-08-28 → 2024-09-26 |

## Course coverage

Phase 5 carries the **Process** stage's cleaning and validation half:
completeness, accuracy, consistency, duplicates, missing data, type conversion,
error checking and verification
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`data-cleaning-methodology.md`](data-cleaning-methodology.md) — method
- [`data-quality-framework.md`](data-quality-framework.md) — quality practices
- [`data-quality-results.md`](data-quality-results.md) — results
