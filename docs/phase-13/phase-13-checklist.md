# Phase 13 — Forecasting & Inventory Insights

## Purpose

Phase 13 translates the validated forecasting work into business-facing demand
and inventory-planning insights, on the same densified store-day series the
models were fitted to.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Demand statistics | `inventory_demand_summary.csv` — level, percentiles and coefficient of variation per store |
| Variability statistics | `inventory_variability_summary.csv` — standard deviation, variance, P90/P95/P99 |
| Densification record | `inventory_densification_summary.csv` — 1,656 densified training store-days, 1 zero-filled (Store 3, 2022-10-16) |
| Forecast evidence | `inventory_forecast_error_summary.csv` — bias, residual standard deviation, RMSE and MAPE recomputed from Phase 12's stored validation forecasts |
| Inventory scenarios | Two families (historical-variability and forecast-error), each with 36 combinations of 7/14/28-day lead times and 90/95/99% service levels |
| Insights | `inventory_insights.csv` — 13 insight rows across seven insight types |
| Findings | `inventory_findings.txt` |
| Pipeline | `scripts/forecasting_inventory_insights.py` |
| Tests | `tests/test_forecasting_inventory_insights.py` — 78 tests, all passing |
| Quality record | `forecasting_inventory_quality_report.csv` — 43 checks, all True |

## Key results

| Finding | Value |
|---|---|
| Highest average daily demand | Store 1 — 29,711.253352 |
| Highest relative variability | Store 4 — CV 0.380098, on 60 observations |
| Forecast bias | All four selected models under-forecast; mean bias 1,409.941 units per day, largest at Store 4 (3,871.035404) |
| Reorder point at 14-day lead time / 95% service level | Historical-variability 448,302.4918 / 95,240.1416 / 91,617.6408 / 476,010.1398; forecast-error 475,036.8481 / 98,037.7574 / 99,790.9617 / 474,241.7074 |
| Safety stock | Forecast-error safety stock is 20.19%–57.67% lower than historical-variability safety stock at every store |
| Leakage | Test period never read; analysis spans 2022-08-28 to 2024-02-10 only |

## Course coverage

Phase 13 carries the **Analyze → Share → Act** stage: making predictions, finding
patterns, discovering connections, data-driven decision making, communicating
findings, analytical thinking, statistical analysis, data integrity and
reproducibility ([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`forecasting-and-inventory-insights-methodology.md`](forecasting-and-inventory-insights-methodology.md) — method
- [`forecasting-and-inventory-insights-quality-framework.md`](forecasting-and-inventory-insights-quality-framework.md) — quality practices
- [`forecasting-and-inventory-insights-results.md`](forecasting-and-inventory-insights-results.md) — results
