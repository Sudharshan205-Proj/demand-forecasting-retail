# Phase 11 — Forecasting Models

## Purpose

Phase 11 builds the classical forecasting layer of the project: two benchmarks
and a statistical model, fitted on the chronological training window and
evaluated on the validation window with the test period untouched.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Models | Naive (last observed value), seasonal-naive (`season_length = 7`), ARIMA(1,1,1) |
| Forecasts | `data/analysis/forecasting_predictions.csv` — 1,368 rows (12 store-model combinations × 114 validation days) |
| Results | `forecasting_model_results.csv`, `forecasting_summary.csv`, `forecasting_model_configurations.csv` |
| Findings | `forecasting_findings.txt` |
| Pipeline | `scripts/forecasting_models.py` |
| Tests | `tests/test_forecasting_models.py` — 52 tests, all passing |
| Quality record | `forecasting_quality_report.csv` — 24 checks, all True |

## Key results

| Finding | Value |
|---|---|
| Forecasting grain | Daily store-level demand, reconciled to 41,949,529.910 quantity |
| Validation period | 2024-02-11 to 2024-06-03 — 114 days for every store |
| Best validation model | Seasonal-naive — mean RMSE 3,223.0630, pooled RMSE 3,928.6186, mean MAPE 12.00% |
| ARIMA(1,1,1) | Mean RMSE 5,193.2159, pooled RMSE 6,595.6688 — better than naive, behind the weekly benchmark |
| Naive baseline | Mean RMSE 5,725.4922, pooled RMSE 6,943.0530 |
| Test isolation | No prediction reaches 2024-06-04; 1,566,653 test rows excluded |
| Store-day densification | 1 zero-filled store-day (store 3, 2022-10-16) |

## Course coverage

Phase 11 carries the **Analyze → Share** forecasting stage: time-series analysis,
predictive modeling, model evaluation with RMSE and MAPE, baseline modeling,
advanced data science (ARIMA), pattern identification, leakage-aware train/test
separation and reproducibility
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`forecasting-models-methodology.md`](forecasting-models-methodology.md) — method
- [`forecasting-models-quality-framework.md`](forecasting-models-quality-framework.md) — quality practices
- [`forecasting-models-results.md`](forecasting-models-results.md) — results
