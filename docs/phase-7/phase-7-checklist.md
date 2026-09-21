# Phase 7 — Exploratory Data Analysis

## Purpose

Phase 7 explores the integrated dataset to characterise demand over time, across
stores, products and departments, to quantify demand concentration, and to
establish the relationships and forecasting implications that the later phases
build on.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Summaries | `eda_summary.csv` (45 metric rows), `eda_monthly_demand.csv` (26 months), `eda_store_summary.csv` (4 stores), `eda_category_summary.csv` (182 rows), `eda_top_items.csv` (100 items), `eda_correlation.csv` (7×7 matrix) |
| Findings | `eda_findings.txt` |
| Figures | Five `eda_*.png` figures in `reports/figures/` |
| Pipeline | `scripts/exploratory_data_analysis.py` |
| Tests | `tests/test_exploratory_data_analysis.py` — 34 tests |

## Key results

| Finding | Value |
|---|---|
| Rows analysed | 7,431,026 |
| Total quantity / revenue | 41,949,529.910 / 5,659,219,309.900 |
| Highest-demand month | 2024-05 (2,456,964.945) |
| Highest-demand store | Store 1 — 55.0% of demand |
| Highest-demand item | `b0d24502fb66` — 4.82% of demand |
| Demand concentration | Top 1% of items hold 40.89%; top 10 items 11.14% |
| Item-level outliers above the IQR fence | 4,007 items (85.27% of demand), retained |
| Strongest associations | `quantity` vs `markdown_quantity` 0.6979; vs `sum_total` 0.4074 |
| Level shift | 2023-11 → 2023-12, a coverage and assortment change (Store 4 first appears 2023-12-13) |

## Course coverage

Phase 7 carries the **Analyze** stage's exploratory half: aggregation, sorting,
pattern identification, relationship analysis, outlier identification, data
completeness, invalid-value handling, visual analysis and findings communication
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`eda-methodology.md`](eda-methodology.md) — method
- [`eda-quality-framework.md`](eda-quality-framework.md) — quality practices
- [`eda-results.md`](eda-results.md) — results
