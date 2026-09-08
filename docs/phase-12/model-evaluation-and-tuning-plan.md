# Phase 12 — Model Evaluation & Tuning Plan

## Purpose

Phase 12 evaluates and tunes the forecasting models developed in Phase 11.

The objective is to determine whether improved model configurations can
outperform the initial Phase 11 configurations while preserving strict
time-series validation and preventing test-set leakage.

## Starting Point

Phase 11 implemented:

- Naive forecasting
- Seasonal Naive forecasting
- ARIMA(1,1,1)

Phase 11 evaluated these models on the validation period.

## Phase 12 Models

### Naive

The Naive model remains a benchmark using the last observed value.

### Seasonal Naive

Candidate seasonal periods:

- 7 days
- 14 days
- 28 days

The 7-day configuration represents weekly seasonality.

### ARIMA

Candidate orders:

- (0,1,1)
- (1,1,0)
- (1,1,1)
- (2,1,1)

The search is intentionally limited to maintain reasonable runtime and
interpretability.

## Cross-Validation

Three expanding-window folds are used.

Each fold has a 28-day forecasting horizon.

Only the training period is used for cross-validation.

## Model Selection

Mean CV RMSE is the primary selection criterion.

Mean CV MAPE is used as a secondary tie-breaker.

## Validation

After configuration selection, the selected configuration for each store
is fitted using the complete training period and evaluated on the untouched
validation period.

## Test Set

The test period is not used during:

- model tuning
- configuration selection
- hyperparameter search
- validation-based model development

The test set remains reserved for a later final evaluation stage.

## Outputs

Phase 12 produces:

- Cross-validation results
- Cross-validation summaries
- Selected configurations
- Validation results
- Store-level error analysis
- Findings