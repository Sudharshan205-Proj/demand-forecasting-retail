# Phase 12 — Model Evaluation & Tuning Quality Framework

## Data Integrity

- Confirm required columns exist.
- Confirm dates are parseable.
- Confirm store identifiers are valid.
- Confirm duplicate store/date observations are absent after aggregation.
- Confirm train, validation, and test periods are chronological.

Checks: `input_rows_positive`, `input_required_columns_present`,
`input_target_complete`, `store_day_keys_unique`, `source_rows_reconciled`,
`source_quantity_reconciled` (the store-day aggregate reconciles with the
7,431,026-row / 41,949,529.910-quantity Phase 10 source),
`store_count_preserved`, `split_boundaries_exact` (the phases' exact
dates), `split_partitions_contiguous`.

## Leakage Controls

- Never use test observations during tuning.
- Never randomly shuffle temporal observations.
- Keep validation observations after the training period.
- Keep test observations after the validation period.

Checks: `predictions_avoid_test_period` (no fold or validation forecast
date may reach 2024-06-04), `test_partition_present_but_unused` (the test
partition exists and was excluded), and `fold_windows_chronological` (each
fold's training window ends strictly before its test window).

The feature model's lag and rolling features are additionally verified to
use prior observations only (`feature_lag_matches_previous_observation`,
`feature_rolling_excludes_current`, `feature_target_preserved`).

## Cross-Validation Quality

- Use expanding training windows.
- Use fixed forecast horizons.
- Record every fold.
- Record failed configurations explicitly.

Checks: `fold_horizon_fixed` (every fold forecasts exactly 28 days),
`fold_windows_expanding`, `fold_windows_chronological`,
`fold_minimum_training_respected`, `fold_count_rule_applied` (the fold
count equals the requested count or the largest affordable count),
`store_coverage_complete` (every store is tuned or recorded as skipped with
a reason), `configuration_coverage_complete` (every store covers every
candidate configuration for each of its folds).

Each fold records its training and test window dates. A configuration that
raises during a fold is recorded with a `failed: <Error>` status rather than
being dropped.

## Model Quality

For every configuration record:

- model name
- configuration
- explicit `season_length` and `order` (never parsed from a string)
- store
- CV fold and its training/test window dates
- forecast horizon
- RMSE
- MAPE
- execution status

Checks: `cv_metrics_reproduced_from_predictions` (RMSE and MAPE recomputed
from the stored fold forecasts) and `cv_summary_reconciles_with_results`
(fold counts, means and medians).

## Selection Quality

A configuration must not be selected using test performance.

Selection is based on:

1. mean CV RMSE
2. mean CV MAPE as tie-breaker

Checks: `selection_rule_verified` (the recorded selection equals the argmin
over that store's cross-validation summary) and
`selected_configurations_resolve` (every selected row resolves to a typed
registered configuration).

## Validation Quality

Selected configurations are evaluated against the untouched validation
period.

Checks: `validation_predictions_complete` (one prediction per store per
validation day, with no missing values) and
`validation_metrics_reproduced_from_predictions` (RMSE and MAPE recomputed
from the stored validation forecasts). `error_analysis_reconciles_with_predictions`
recomputes every error-analysis segment from the same forecasts.

## Reproducibility

Record:

- model parameters (including the feature model's hyperparameters)
- preprocessing assumptions (densification, feature construction)
- split dates and every fold window
- evaluation metrics
- configuration selection rule
- every forecast used to compute those metrics

Checks: `feature_forecast_deterministic` (the feature model reproduces its
fold forecast exactly) and `feature_columns_complete` (all 16 features
present).

## Testing

The implementation must include automated tests covering:

- metric calculations
- Naive forecasting
- Seasonal Naive forecasting
- temporal fold creation
- chronological split validation
- configuration selection

Implemented: 64 tests, covering the metrics, forecast primitives, the
feature builder (including its leakage properties), the typed dispatcher,
adaptive fold creation, split validation, cross-validation coverage and
skip recording, summary aggregation, the selection rule and its MAPE
tie-break, the feature model's determinism, the quality report (one pass
case and eleven deliberate-failure cases), the error analysis and the full
`main()` workflow with its failure paths.

## Documentation

Documentation must correspond to the actual implementation and actual
executed results.

The verified results are recorded in
`docs/phase-12/model-evaluation-and-tuning-results.md` and asserted by the
reproduction runbook in that document.