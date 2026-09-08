# Phase 14 — R Analysis Quality Framework

## 1. Input Validation

The R workflow verifies:

- required input files exist;
- required columns exist;
- datasets are non-empty;
- demand values are non-negative;
- standard deviations are non-negative;
- safety stock is non-negative;
- reorder points are non-negative.

## 2. Reproducibility

The analysis:

- uses project-relative paths;
- loads project-generated analytical outputs;
- generates outputs programmatically;
- generates visualizations programmatically;
- uses R Markdown for reproducible reporting.

## 3. Cross-Phase Validation

R independently reproduces the principal Phase 13 findings:

- highest average-demand store;
- highest relative-variability store.

A mismatch causes the R script to fail rather than silently accepting
different results.

## 4. Visualization Validation

Visualizations are generated from analytical data rather than manually
constructed values.

## 5. Leakage Control

The R analysis does not introduce future observations into the forecasting
workflow.

It operates on established Phase 13 analytical outputs.

The Phase 11/12 forecasting train-validation-test separation remains intact.

## 6. Model Integrity

R does not replace or retrain the selected Python forecasting models.

This avoids introducing a second forecasting methodology solely for
demonstrating software coverage.

## 7. Course Integrity

Course concepts are only marked as implemented when corresponding R project
artifacts exist.

## 8. Known Limitations

The analysis does not provide operational inventory recommendations because
the dataset lacks:

- supplier lead times;
- service-level requirements;
- holding costs;
- ordering costs;
- current stock;
- purchase orders;
- warehouse constraints.

## 9. Failure Behaviour

Missing input files, missing columns, invalid numerical values, or cross-phase
consistency failures cause the analysis to stop with an explicit error.