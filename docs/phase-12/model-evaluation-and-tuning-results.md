# Phase 12 — Model Evaluation & Tuning Results

## Status

NOT YET EXECUTED

This document is the Phase 12 results record.

Actual numerical results must be added only after the Phase 12 evaluation
script has executed successfully.

## Evaluation Design

The phase uses:

- training-period expanding-window cross-validation;
- three cross-validation folds;
- 28-day forecast horizons;
- RMSE as the primary selection metric;
- MAPE as a complementary metric.

## Candidate Models

### Naive

Last observed value.

### Seasonal Naive

Candidate season lengths:

- 7
- 14
- 28

### ARIMA

Candidate orders:

- (0,1,1)
- (1,1,0)
- (1,1,1)
- (2,1,1)

## Test-Set Protection

The test period is not used during Phase 12 tuning.

## Results

Results will be populated from:

- `data/analysis/model_tuning_results.csv`
- `data/analysis/model_tuning_summary.csv`
- `data/analysis/selected_model_configurations.csv`
- `data/analysis/tuned_validation_results.csv`
- `data/analysis/model_error_analysis.csv`

## Interpretation Rule

No model will be declared superior until the actual Phase 12 results have
been generated and verified.