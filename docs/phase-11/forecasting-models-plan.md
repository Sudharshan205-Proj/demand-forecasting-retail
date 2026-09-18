# Phase 11 — Forecasting Models Plan

## Objective

Develop classical forecasting models for retail physical demand and establish reproducible validation results. Phase 11 does not select a final model; it builds the baseline, the seasonally-aware benchmark and the classical ARIMA configuration that Phase 12 evaluates and tunes.

## Forecasting Target

`quantity`

The target represents physical retail demand.

Online demand is not combined with physical sales demand.

## Modeling Unit

The primary Phase 10 modeling grain is:

`date + item_id + store_id`

However, classical ARIMA experimentation in Phase 11 uses daily store-level demand because the source contains substantial gaps and thousands of sparse item-store series. The forecasting grain is therefore:

`date + store_id`

Aggregating 7,431,026 observed date-item-store records produces 2,571 observed store-days across 4 stores and 761 calendar dates. Every store series is densified onto a complete daily calendar; the densification adds exactly one store-day (store 3, 2022-10-16) because that store has no observed record on that date, and the zero quantity is the correct interpretation at the store level. The densification is measured and recorded rather than assumed.

## Models

### Naive Baseline

The forecast equals the most recently observed training demand, repeated across the horizon.

This provides a simple benchmark that the other models must improve upon.

### Seasonal-Naive Baseline

The most recent seven-observation training pattern (`season_length = 7`) is repeated into the validation horizon.

This provides a weekly-seasonality benchmark.

### ARIMA

ARIMA is implemented with:

`(p, d, q) = (1, 1, 1)`

The configuration is intentionally simple and reproducible. It is fitted on the training period only, with `enforce_stationarity=False` and `enforce_invertibility=False`, and forecast across the full validation horizon.

## Validation

The training period ends on:

`2024-02-10`

The validation period is:

`2024-02-11` through `2024-06-03` (114 daily observations)

The test period begins on:

`2024-06-04` and ends on `2024-09-26`.

The test period is not used for model selection, tuning or evaluation in Phase 11.

Store 1–3 have training observations from 2022-08-28. Store 4 first appears on 2023-12-13, so its ARIMA model is fitted on 60 training observations.

## Metrics

### RMSE

Root Mean Squared Error measures the square root of the average squared forecast errors.

Lower is better.

### MAPE

Mean Absolute Percentage Error measures the average absolute percentage error, expressed as a percentage.

Zero-actual observations are excluded because percentage error is undefined when the actual value is zero. The validation store-days contain no zero-demand observations (the minimum validation store-day demand is 3152.575), so the exclusion rule protects against a case the data does not currently exercise.

The summary reports both per-store mean/median metrics and pooled metrics across every store-day validation observation, because those answer different questions about model quality.

## Reproducibility

Model configurations, training windows, validation windows, forecast horizons and metrics are recorded as machine-readable outputs. Naive and seasonal-naive predictions are verified to reproduce their documented definitions, and ARIMA's order is recorded explicitly for every store.

## Artifacts

| Artifact | Content |
|---|---|
| `data/analysis/forecasting_model_results.csv` | Per store and model: validation window, horizon, RMSE, MAPE |
| `data/analysis/forecasting_model_configurations.csv` | Per store and model: training window, validation window, horizon, configuration |
| `data/analysis/forecasting_summary.csv` | Per model: store count, mean/median and pooled RMSE and MAPE |
| `data/analysis/forecasting_predictions.csv` | Every store-day forecast (actual and predicted) |
| `data/analysis/forecasting_quality_report.csv` | 24 machine-readable validation checks |
| `data/analysis/forecasting_findings.txt` | Human-readable reconciliation, results and limitations |

These outputs are reproducible generated artifacts and are excluded from Git under the project's generated-artifact policy.

## Scope Boundary

Phase 11 establishes classical forecasting models.

Final model selection, extensive tuning, machine-learning forecasting, and deep-learning forecasting belong to later phases. The Phase 10 engineered lag, rolling and calendar features are not used as predictors by this phase — the classical models consume the demand target only. That integration gap remains open for Phases 12–13.
