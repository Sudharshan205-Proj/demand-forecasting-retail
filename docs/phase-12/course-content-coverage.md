# Phase 12 — Course Content Coverage

## Purpose

This document records the internship course concepts demonstrated by Phase 12.

## Model Evaluation

### Concept

Model evaluation compares model predictions against observed outcomes using
appropriate metrics.

### Project Application

Phase 12 evaluates nine forecasting configurations per store using RMSE and MAPE,
over 90 cross-validation fold evaluations and four validation evaluations. Every
metric is recomputed from the stored forecasts.

Evidence:

- `scripts/evaluate_and_tune_models.py`
- `tests/test_evaluate_and_tune_models.py`
- `data/analysis/model_tuning_results.csv`, `tuned_validation_results.csv`
- `data/analysis/model_evaluation_predictions.csv`

## Time-Aware Validation

### Concept

Time-series data must be evaluated chronologically to avoid leakage.

### Project Application

Phase 12 uses expanding-window cross-validation with fixed 28-day forecast
windows on the training period only, and evaluates the selected configurations
on the untouched validation period. The quality report verifies that no fold or
validation window reaches the test period.

## Analytical Thinking

### Concept

Different analytical approaches should be compared against a baseline.

### Project Application

The project retains the Naive model as a benchmark and compares it with three
seasonal-naive periods, four ARIMA orders and the feature-based candidate — nine
configurations per store.

## Statistical Analysis

### Concept

Statistical modeling should be evaluated using measurable error metrics.

### Project Application

ARIMA orders and the feature-based candidate are compared using cross-validation
and validation RMSE and MAPE. Seasonal-naive is a strong benchmark: it wins store
4's single fold and is the runner-up for stores 1–3.

## Feature Engineering

### Concept

Engineered features should feed the models that use them.

### Project Application

The 16 Phase 10 feature families (lag, rolling and calendar) are consumed by the
`feature_gbm` candidate, recomputed at the store-day forecasting grain with the
Phase 10 definitions and used recursively for multi-step forecasting. The feature
model wins the training-period cross-validation for stores 1–3 and improves the
validation RMSE for stores 1 and 2 over the Phase 11 benchmark.

Evidence: `build_feature_frame` / `feature_forecast` in
`scripts/evaluate_and_tune_models.py`; the feature-leakage and determinism checks
in `model_evaluation_quality_report.csv`.

## Machine Learning

### Concept

Machine learning applies learned models to prediction tasks.

### Project Application

`HistGradientBoostingRegressor` (scikit-learn, an existing project dependency) is
fitted per fold on the store-day feature matrix, with a fixed random seed and
early stopping disabled for determinism. It is selected for stores 1–3 on
cross-validation evidence.

## Model Selection

### Concept

Models should be selected using evidence rather than assumptions.

### Project Application

Configurations are selected using training-period cross-validation results
(lowest mean CV RMSE, mean CV MAPE as tie-break). The quality report recomputes
the argmin and verifies the recorded selection. The validation period then shows
the selection is strong but not infallible: store 3's cross-validation winner is
0.32% worse than the weekly benchmark on validation.

## Data Integrity

### Concept

Analytical conclusions require valid and appropriately structured data.

### Project Application

Phase 12 reconciles the store-day aggregate against the 7,431,026-row /
41,949,529.910-quantity Phase 10 source, verifies the exact split boundaries,
rejects duplicate store-day rows, and covers all four stores.

## Reproducibility

### Concept

Analytical work should be reproducible.

### Project Application

The project records typed model configurations (never parsed from display
strings), every fold's training and test window, per-fold and validation metrics,
the selection rule, and all 2,976 forecasts. The feature model's determinism is
verified by re-running a fold.

## Coverage Rule

A concept is considered implemented only when corresponding project evidence
exists.

## Concepts Outside This Phase

Deep learning is not part of the delivered model set, so no course credit is
claimed for it.

Visualization and Tableau are delivered by Phase 15, and the R analysis is
delivered by Phase 14.
