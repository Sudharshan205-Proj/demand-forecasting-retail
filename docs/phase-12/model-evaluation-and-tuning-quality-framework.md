# Phase 12 — Model Evaluation & Tuning Quality Framework

## Data Integrity

- Confirm required columns exist.
- Confirm dates are parseable.
- Confirm store identifiers are valid.
- Confirm duplicate store/date observations are absent after aggregation.
- Confirm train, validation, and test periods are chronological.

## Leakage Controls

- Never use test observations during tuning.
- Never randomly shuffle temporal observations.
- Keep validation observations after the training period.
- Keep test observations after the validation period.

## Cross-Validation Quality

- Use expanding training windows.
- Use fixed forecast horizons.
- Record every fold.
- Record failed configurations explicitly.

## Model Quality

For every configuration record:

- model name
- configuration
- store
- CV fold
- forecast horizon
- RMSE
- MAPE
- execution status

## Selection Quality

A configuration must not be selected using test performance.

Selection is based on:

1. mean CV RMSE
2. mean CV MAPE as tie-breaker

## Validation Quality

Selected configurations are evaluated against the untouched validation
period.

## Reproducibility

Record:

- model parameters
- preprocessing assumptions
- split dates
- evaluation metrics
- configuration selection rule

## Testing

The implementation must include automated tests covering:

- metric calculations
- Naive forecasting
- Seasonal Naive forecasting
- temporal fold creation
- chronological split validation
- configuration selection

## Documentation

Documentation must correspond to the actual implementation and actual
executed results.