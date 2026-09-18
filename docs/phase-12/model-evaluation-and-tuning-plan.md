# Phase 12 — Model Evaluation & Tuning Plan

## Purpose

Phase 12 evaluates and tunes the forecasting models developed in Phase 11.

The objective is to determine whether improved model configurations can
outperform the initial Phase 11 configurations while preserving strict
time-series validation and preventing test-set leakage.

## Starting Point

Phase 11 implemented and verified:

- Naive forecasting (last observed value)
- Seasonal Naive forecasting (`season_length = 7`)
- ARIMA(1,1,1)

Phase 11 evaluated these models on the validation period and stored every
forecast in `data/analysis/forecasting_predictions.csv`. Phase 12 uses that
artifact as its reconciliation reference and the Phase 10 feature matrix as
its modeling input.

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

### Feature-Based Model

`feature_gbm` — HistGradientBoostingRegressor
(`learning_rate=0.1, max_iter=200, max_depth=3, min_samples_leaf=5,
l2_regularization=1.0, early_stopping=False, random_state=0`).

This candidate finally consumes the Phase 10 feature families. Phase 11–13
forecast daily store-level demand, so the 16 features are computed on the
densified store-day series rather than by summing the item-store matrix: the
lag features (`lag_1/7/14/28`), the rolling features
(`rolling_mean/std_7/28`) and the calendar features plus `series_age_days`
use the same definitions as Phase 10 but at the forecasting grain.

Forecasting beyond one step is recursive: the model predicts one day, that
prediction is appended to the history, and the feature frame is rebuilt
before the next step, so lag and rolling values always describe information
available before the day being forecast.

The candidate set therefore contains nine configurations (1 + 3 + 4 + 1).

## Cross-Validation

Expanding-window time-series cross-validation is used, on the training
period only.

- Requested folds: 3
- Forecast horizon: 28 days (fixed)
- Minimum initial training sample: 28 observations

The fold count adapts to the history a store actually has. The requested
three folds are used when the series can afford them; otherwise the largest
affordable count is used, so short-history stores are tuned rather than
silently dropped. A store that cannot support even one fold is recorded as
skipped with a reason, and store coverage is verified.

With the current dataset this yields three folds for stores 1–3 (training
windows ending 2023-11-18, 2023-12-16 and 2024-01-13; test windows
2023-11-19 to 2023-12-16, 2023-12-17 to 2024-01-13 and 2024-01-14 to
2024-02-10) and one fold for store 4 (2023-12-13 to 2024-01-13 training,
2024-01-14 to 2024-02-10 test), which first appears on 2023-12-13.

## Model Selection

Mean CV RMSE is the primary selection criterion.

Mean CV MAPE is used as a secondary tie-breaker.

Selection is verified after the fact: the quality report recomputes the
argmin over each store's cross-validation summary and confirms it matches
the recorded selection.

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

The test set remains reserved for a later final evaluation stage. The
quality report verifies that no cross-validation fold or validation window
reaches the test period.

## Outputs

Phase 12 produces:

- Cross-validation results (per store, configuration and fold, with fold windows)
- Cross-validation summaries
- Selected configurations
- Validation results
- Store-level error analysis
- Every fold and validation forecast (`model_evaluation_predictions.csv`)
- A machine-readable quality report (30 checks)
- Findings