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

### Adaptive fold count

The requested design is three folds with a fixed 28-day horizon and a
minimum initial training sample of 28 observations. The fold count then
adapts to the history a store actually has: the requested three folds are
used when the series can afford them, otherwise the largest affordable
count is used.

This matters because the stores do not share the same history. Stores 1–3
span the full training period and use all three folds. Store 4 first appears
on 2023-12-13, leaving 60 training observations, which supports one 28-day
fold (training window 2023-12-13 to 2024-01-13, test window 2024-01-14 to
2024-02-10). A store that cannot support a single fold is recorded as
skipped with its reason and training length rather than being silently
dropped, and the quality report fails if any store is left uncovered.

Every fold's training and test window dates are recorded in
`model_tuning_results.csv`.

## 6. Metrics

### RMSE

Root Mean Squared Error measures the square root of the average squared
forecast error.

Lower RMSE indicates smaller prediction error.

### MAPE

Mean Absolute Percentage Error measures average absolute percentage error.

Zero-demand observations are excluded because percentage error is undefined
when the actual value is zero. At the store-day grain no validation or
fold observation has zero demand, so the rule is a verified safety
guarantee rather than an adjustment to the reported values.

## 7. Model Selection

Mean CV RMSE is the primary selection criterion.

Mean CV MAPE is used as a secondary criterion where required.

Selection is only ever based on training-period cross-validation columns.
The quality report recomputes the argmin over each store's cross-validation
summary, with the MAPE tie-break, and verifies it equals the recorded
selection.

## 8. Error Analysis

Validation errors are examined by store and by the first and second halves
of the validation period (split at the midpoint of the 114-day window).
Each segment records the mean error (bias), the mean absolute error and the
RMSE.

This helps identify whether forecasting accuracy changes over time, and
whether a model is systematically over- or under-forecasting. Every segment
statistic is computed from the stored validation predictions and is
recomputed independently by the quality report.

In the verified run every selected model under-forecast on average in both
halves, with the bias growing in the second half.

## 9. Leakage Prevention

The test period is never used for:

- tuning
- model selection
- hyperparameter search
- configuration comparison

The validation period is used only after configurations have been selected
using training-period cross-validation.

The quality report verifies the boundary rather than trusting it: no
cross-validation fold window and no validation window may contain a date at
or after 2024-06-04, and the recorded split boundaries must match the
Phase 9 contract exactly (train to 2024-02-10, validation 2024-02-11 to
2024-06-03, test 2024-06-04 to 2024-09-26).

Feature construction is leakage-safe by construction. Every lag and rolling
feature in the feature model is built from the shifted series, so the
target day's own demand never enters its own features, and recursive
forecasting rebuilds the frame from predictions only.

## 10. Reproducibility

The project records:

- model configurations (including explicit `season_length` and `order`
  columns rather than something a later stage has to parse back out of a
  display string)
- cross-validation design and every fold's training and test windows
- evaluation metrics per fold and per configuration
- dataset split definitions
- selected configurations and the selection basis
- validation results
- every fold and validation forecast, so any metric can be recomputed

The feature model is deterministic (`random_state=0`, early stopping
disabled), and the quality report re-runs one fold's feature forecast to
confirm it.

## 11. Feature-Based Candidate

Phase 10 engineered 16 features at the item-store grain but no later phase
consumed them. Phase 12 gives the feature families a model at the grain the
forecasting phases actually use.

The feature frame is built on the densified store-day series with the same
feature definitions as Phase 10:

- `lag_1`, `lag_7`, `lag_14`, `lag_28` — previous observations;
- `rolling_mean_7`, `rolling_std_7`, `rolling_mean_28`, `rolling_std_28` —
  computed on the shifted series, so the current day is excluded;
- `day_of_week`, `day_of_month`, `week_of_year`, `month`, `quarter`, `year`,
  `is_weekend`, `series_age_days` — calendar features.

Because the Phase 11–13 forecasting unit is the store-day, the features are
recomputed at that grain rather than aggregated from the item-store matrix:
summing item-level lags is not a leakage-safe store-level lag. The feature
families, windows and min-periods match Phase 10 so the two remain
comparable.

Multi-step forecasting is recursive. The model is fitted once on the
history's feature frame, then applied one step at a time; each step appends
the prediction to the working series and rebuilds the feature frame, so
the lag and rolling values entering a prediction describe demand observed
before that day.

The learner is `HistGradientBoostingRegressor` (scikit-learn, already a
project dependency). It tolerates the missing values that appear in the
early rows of every series and in the `rolling_std` warm-up window.

## 12. Quality Verification

`data/analysis/model_evaluation_quality_report.csv` records 30 checks and
the run is gated on all of them passing. The checks cover input
reconciliation, split boundaries, store and configuration coverage, fold
structure, leakage controls, the selection rule, feature leakage, metric
reproduction and error-analysis reconciliation.

## 13. Phase 11 Reconciliation

Where a selected configuration is the same model with the same parameters
as a Phase 11 model, the validation forecasts must be identical. The
findings report compares the stored Phase 12 validation forecasts against
Phase 11's predictions and records the number of matching configurations
and the maximum absolute difference.