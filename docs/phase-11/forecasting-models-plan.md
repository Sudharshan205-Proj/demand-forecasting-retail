# Phase 11 — Forecasting Models Plan

## Objective

Develop classical forecasting models for retail physical demand and establish reproducible validation results.

## Forecasting Target

`quantity`

The target represents physical retail demand.

Online demand is not combined with physical sales demand.

## Modeling Unit

The primary Phase 10 modeling grain is:

`date + item_id + store_id`

However, classical ARIMA experimentation in Phase 11 uses daily store-level demand because the source contains substantial gaps and thousands of sparse item-store series.

## Models

### Naive Baseline

The forecast equals the most recently observed demand.

This provides a simple benchmark that advanced models must improve upon.

### Seasonal-Naive Baseline

The most recent seven-observation demand pattern is repeated into the forecast horizon.

This provides a weekly-seasonality benchmark.

### ARIMA

ARIMA is implemented with:

`(p, d, q) = (1, 1, 1)`

The configuration is intentionally simple and reproducible.

## Validation

The training period ends on:

`2024-02-10`

The validation period is:

`2024-02-11` through `2024-06-03`

The test period begins on:

`2024-06-04`

The test period is not used for model selection.

## Metrics

### RMSE

Root Mean Squared Error measures the square root of average squared forecast errors.

Lower is better.

### MAPE

Mean Absolute Percentage Error measures average absolute percentage error.

Zero-actual observations are excluded because percentage error is undefined when the actual value is zero.

## Reproducibility

Model configurations, validation dates, forecast horizons, and metrics are recorded as machine-readable outputs.

## Scope Boundary

Phase 11 establishes classical forecasting models.

Final model selection, extensive tuning, machine-learning forecasting, and deep-learning forecasting belong to later phases.
