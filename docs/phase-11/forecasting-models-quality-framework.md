# Phase 11 — Forecasting Models Quality Framework

## Objective

Ensure forecasting experiments are valid, reproducible, and free from temporal leakage.

The framework is implemented as a machine-readable quality report, `data/analysis/forecasting_quality_report.csv`, containing 24 checks. Each row records the check name, whether it passed, the actual value and the expected value. The pipeline refuses to write results when any check fails.

## Input Validation

Verify:

* required columns exist
* dates are parseable
* quantity is available
* split labels exist

Checks: `input_rows_positive`, `input_required_columns_present`, `input_target_complete`, `input_dates_parsed`.

The Phase 10 input is also reconciled at the store-day grain: `store_day_keys_unique` (no duplicate `date + store_id`), `store_day_demand_reconciled` (the store-day total equals the source total, `41,949,529.910`) and `store_count_preserved` (all four stores survive aggregation).

## Temporal Validation

Verify:

* training ends before validation
* validation ends before test
* forecasts correspond to the correct validation horizon
* observations are chronologically ordered

Checks: `training_window_ends_at_train_end`, `validation_window_matches_contract`, `validation_horizon_consistent`, `test_period_excluded_from_evaluation`, `test_partition_present_but_unused`, `store_series_chronological`, `store_series_regular_daily`.

The validation window must be identical for every store (`2024-02-11` to `2024-06-03`, 114 observations), and the observed horizon in the results must equal that length.

## Model Validation

Verify:

* naive baseline produces the correct forecast
* seasonal-naive forecast repeats the expected seasonal pattern
* ARIMA configuration is explicit
* model output contains the requested forecast horizon

Checks: `naive_matches_last_observation`, `seasonal_naive_matches_weekly_pattern`, `arima_configuration_explicit`, `models_evaluated_per_store`, `prediction_rows_match_horizons`, `predictions_have_no_missing_values`.

The baseline checks recompute the documented forecast definition from the training window and compare it element-wise with the stored predictions. A model that is skipped for any store fails `models_evaluated_per_store`, so a partial model set cannot be reported as a complete comparison.

## Metric Validation

Verify:

* RMSE is calculated correctly
* MAPE handles zero actual values explicitly
* actual and predicted lengths match

Checks: `rmse_reproduced_from_predictions`, `mape_reproduced_from_predictions`, `mape_finite_for_nonzero_actuals`, `summary_reconciles_with_results`.

RMSE and MAPE are recomputed from `forecasting_predictions.csv` and reconciled against the reported metrics for every store and model. The summary's per-model means and pooled metrics are reconciled against the underlying results and predictions.

## Leakage Validation

The following are prohibited:

* fitting models on validation data before evaluating validation performance
* using test observations for model selection
* random shuffling of temporal observations
* future information entering historical forecasts

`test_period_excluded_from_evaluation` verifies that no prediction date reaches the test start and that every configuration's training window ends at `2024-02-10`. `test_partition_present_but_unused` confirms the test partition exists (1,566,653 rows) and was available to be excluded. The naive and seasonal-naive checks independently confirm that the baselines use training observations only.

## Reproducibility

Record:

* model name
* model configuration
* training period
* validation period
* forecast horizon
* evaluation metrics

Checks: `training_window_ends_at_train_end` plus the configurations artifact, which carries the model, store, training window, validation window, horizon and configuration string for all 12 store-model combinations. ARIMA fitting is deterministic and the input is read with an explicit ISO date parse, so repeated runs reproduce the model results artifact byte-for-byte.

## Model Selection Policy

A model must not be described as superior unless the validation results support the claim.

Final model selection is deferred until the complete model-development and evaluation workflow is available.

In Phase 11 the seasonal-naive baseline achieves the lowest mean validation RMSE (3,223.0630) and the lowest pooled validation RMSE (3,928.6186) across the four stores, with a mean MAPE of 12.00%. ARIMA(1,1,1) records a higher mean RMSE (5,193.2159) and naive the highest (5,725.4922). These are validation-period results only; the test period remains untouched.
