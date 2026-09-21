# Phase 3 — Spreadsheet-Based Analysis

## Purpose

Phase 3 applies spreadsheet analysis to the retail data, producing a workbook
that aggregates the raw sales file to spreadsheet-compatible summaries and
demonstrates the course's spreadsheet techniques.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Analytical datasets | Daily (761 rows), store (4 rows) and item (28,182 rows) summaries aggregated from `sales.csv` |
| Workbook | `data/analysis/retail_spreadsheet_analysis.xlsx` — 6 sheets: Workbook_ReadMe, Daily_Analysis, Store_Summary, Item_Summary, Formula_Analysis, Data_Validation |
| Course techniques | Sorting, multi-column sorting, filtering, freeze panes, formulas (SUM, AVERAGE, MIN, MAX, SUMPRODUCT, VLOOKUP, COUNTIF), data validation, conditional formatting, pivot-style summaries and validation checks |
| Generator | `scripts/create_spreadsheet_analysis.py` |
| Tests | `tests/test_create_spreadsheet_analysis.py` — 12 tests |

## Key results

| Measure | Value |
|---|---|
| Daily records | 761 (2022-08-28 → 2024-09-26) |
| Highest-demand date | 2023-12-30 (≈154,066.88) |
| Lowest-demand date | 2023-01-01 (≈19,245.05) |
| Total quantity (raw basis) | ≈41,938,165 |
| Total sales value (raw basis) | ≈5,658,351,681 |
| Highest-demand store | Store 1 (23,064,331.52 quantity) |
| Highest-demand item | `b0d24502fb66` (2,022,732 quantity) |

## Course coverage

Phase 3 demonstrates the course's spreadsheet concepts — sorting, filtering,
formulas, lookups, data validation, conditional formatting and aggregated
pivot-style analysis — each connected to the demand-forecasting problem
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`spreadsheet-methodology.md`](spreadsheet-methodology.md) — method
- [`spreadsheet-results.md`](spreadsheet-results.md) — results
- [`spreadsheet-quality-framework.md`](spreadsheet-quality-framework.md) — quality practices
