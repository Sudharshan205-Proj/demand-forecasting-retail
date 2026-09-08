# Phase 12 — Model Evaluation & Tuning Methodology

## 1. Evaluation Strategy

The project uses chronological forecasting evaluation rather than random
cross-validation.

This prevents future observations from entering earlier training windows.

## 2. Training Period

The verified training period is:

2022-08-28 through 2024-02-10

## 3. Validation Period

The verified validation period is:

2024-02-11 through 2024-06-03

## 4. Test Period

The verified test period is:

2024-06-04 through 2024-09-26

The test period is intentionally excluded from Phase 12 tuning.

## 5. Cross-Validation

An expanding-window approach is used.

Each fold:

1. trains on all observations available before the forecast window;
2. forecasts 28 days;
3. evaluates the forecast;
4. expands the training window for the next fold.

## 6. Metrics

### RMSE

Root Mean Squared Error measures the square root of the average squared
forecast error.

Lower RMSE indicates smaller prediction error.

### MAPE

Mean Absolute Percentage Error measures average absolute percentage error.

Zero-demand observations are excluded because percentage error is undefined
when the actual value is zero.

## 7. Model Selection

Mean CV RMSE is the primary selection criterion.

Mean CV MAPE is used as a secondary criterion where required.

## 8. Error Analysis

Validation errors are examined by store and by the first and second halves
of the validation period.

This helps identify whether forecasting accuracy changes over time.

## 9. Leakage Prevention

The test period is never used for:

- tuning
- model selection
- hyperparameter search
- configuration comparison

The validation period is used only after configurations have been selected
using training-period cross-validation.

## 10. Reproducibility

The project records:

- model configurations
- cross-validation design
- evaluation metrics
- dataset split definitions
- selected configurations
- validation results