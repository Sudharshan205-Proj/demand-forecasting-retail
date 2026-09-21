# Phase 8 — Statistical & Analytical Analysis

## Purpose

Phase 8 quantifies demand relationships, variability, trend and statistical
evidence to inform the forecasting phases.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Analysis tables | `statistical_summary.csv`, `statistical_correlations.csv`, `statistical_store_analysis.csv`, `statistical_category_analysis.csv`, `statistical_price_demand.csv`, `statistical_promotion_analysis.csv`, `statistical_autocorrelation.csv`, `statistical_trend.csv`, `statistical_monthly_activity.csv` |
| Validation report | `statistical_quality_report.csv` — 56 metrics |
| Findings | `statistical_findings.txt` |
| Figures | 4 `statistical_*.png` figures in `reports/figures/` |
| Pipeline | `scripts/statistical_analytical_analysis.py` (chunked at 100,000 rows; peak 483.4 MB, no retained analysis frame) |
| Tests | `tests/test_statistical_analytical_analysis.py` — 46 tests |

## Key results

| Finding | Value |
|---|---|
| Mean daily quantity | 55,124.218 (CV 0.351) |
| Strongest association | `markdown_quantity` r = 0.6979 (8,709 rows) |
| Price/demand | r = -0.044422, R² = 0.001973 (negligible) |
| Promoted vs unpromoted mean demand | 5.951 vs 5.567 |
| Trend | +66.98/day, Newey-West SE 4.30 |
| Autocorrelation | peaks at lag 14 (0.885), lag 1 (0.882), lag 7 (0.874) — weekly periodicity |
| Level shift | 2023-11 → 2023-12 is a coverage and assortment change (Store 4 enters 2023-12-13) |

## Method notes

- Every statistic uses the complete dataset; the only sampled artifact is the
  price/demand scatter (deterministic systematic sample, 200,839 points).
- Non-finite values are excluded pairwise, and a variable with no usable
  variation yields an undefined correlation.
- Trend significance is autocorrelation-robust (Newey-West, 14 lags); p-values
  below 1e-300 are reported as `< 1e-300`.

## Course coverage

Phase 8 demonstrates relational and descriptive statistics, significance testing,
trend and autocorrelation analysis, and data-driven interpretation
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`statistical-methodology.md`](statistical-methodology.md) — method
- [`statistical-quality-framework.md`](statistical-quality-framework.md) — quality practices
- [`statistical-results.md`](statistical-results.md) — results
