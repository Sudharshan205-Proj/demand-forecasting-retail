# Phase 13 — Forecasting & Inventory Insights Quality Framework

## Data Validation

Verify:

- required columns exist;
- the source matrix reconciles on rows and quantity;
- the training, validation and test partitions each reconcile on row count;
- training demand is non-empty;
- quantity is numeric;
- quantity is non-negative;
- duplicate date/store combinations do not exist after aggregation.

Checks: `input_rows_positive`, `input_required_columns_present`,
`source_rows_reconciled` (7,431,026 rows), `source_quantity_reconciled`
(41,949,529.910), `training_rows_reconciled` (4,315,416),
`training_quantity_reconciled` (24,038,416.097), `validation_rows_reconciled`
(1,548,957), `test_rows_reconciled` (1,566,653), `input_target_complete`,
`store_day_keys_unique`.

## Densification

Verify:

- the densified store-day count is measured and matches Phase 11;
- exactly one day is zero-filled, and it is Store 3, 2022-10-16;
- every store's densified length equals its own date span;
- densification adds no quantity.

Checks: `densified_training_days_measured` (1,656),
`densification_synthetic_day_count`, `densification_matches_phase11`,
`densified_days_match_span`, `densified_quantity_preserved`.

This check family keeps Phase 13's descriptive statistics on the same series
Phase 11 and Phase 12 fitted: without it the phase would describe a 531-day
Store 3 series while the models were fitted on 532 days.

## Partition Integrity

Verify:

- the analysis spans the training window exactly;
- the test period contributes no observations;
- store coverage is preserved.

Checks: `trains_on_training_window_only` (2022-08-28 to 2024-02-10),
`test_period_excluded`, `store_count_preserved`.

## Forecasting Evidence

Verify:

- selected model files exist and carry typed configuration fields;
- exactly one configuration is selected per store;
- the selection and the validation results agree;
- every store in the demand data has a selection;
- the stored validation predictions are complete.

Checks: `typed_configuration_present`, `model_selection_one_per_store`,
`model_selection_covers_stores`, `model_selection_matches_validation`,
`validation_predictions_complete` (456 forecasts, four stores × 114 days).

## Forecast-Error Reconciliation

Verify:

- RMSE recomputed from stored predictions equals Phase 12's recorded value;
- MAPE recomputed from stored predictions equals Phase 12's recorded value;
- the evidence is scoped to the validation window;
- the bias direction is recorded;
- Phase 12's segment error analysis reconciles with the recomputed statistics.

Checks: `forecast_rmse_reproduced`, `forecast_mape_reproduced`,
`validation_evidence_scoped_to_validation_period`, `under_forecast_bias_positive`,
`error_analysis_bias_reconciles`, `error_analysis_rmse_reconciles`.

The last two reconstruct Phase 12's half-period segments: the mean of the two
segment biases must equal the recomputed bias, and the root mean of the two
squared segment RMSEs must equal the recomputed RMSE. Both hold exactly, so the
phase's error evidence is consistent with the artifact Phase 12 published.

## Inventory Calculation Validation

Verify:

- lead-time demand increases with lead time;
- safety stock increases with service level;
- reorder point equals expected lead-time demand plus safety stock;
- safety stock is non-negative;
- reorder point is greater than or equal to expected lead-time demand;
- both scenario families are covered completely;
- the forecast family's level is the bias-corrected one, and that identity with
  the realised validation mean is asserted explicitly.

Checks: `lead_time_demand_monotonic`,
`safety_stock_monotonic_in_service_level`, `reorder_point_formula_holds`,
`reorder_point_covers_lead_time_demand`, `safety_stock_non_negative`,
`historical_scenario_coverage_complete`, `forecast_scenario_coverage_complete`,
`forecast_level_is_bias_corrected`, `forecast_level_recovers_validation_mean`.

`forecast_level_recovers_validation_mean` exists because the bias-adjusted level
is algebraically the validation-period mean. Asserting the identity forces the
artifacts and the documentation to describe that number as a recovered demand
level rather than a forward forecast.

## Assumption Controls

Clearly identify:

- assumed lead times;
- assumed service levels;
- mathematical assumptions;
- which uncertainty input each family uses.

The findings report states the assumption set, both uncertainty inputs, and the
status of the forecast family's level in explicit terms.

Scenario assumptions are not presented as observed business facts.

## Leakage Controls

The test period is not used for:

- model selection;
- tuning;
- inventory-model calibration;
- performance optimization.

`trains_on_training_window_only` and `test_period_excluded` enforce this in code,
and `validation_evidence_scoped_to_validation_period` prevents the error
statistics from drifting outside the validation window.

## Interpretation Quality

Business findings distinguish:

- observed demand;
- forecast evidence;
- scenario assumptions;
- actionable implications;
- limitations.

The insights artifact separates demand observations, forecast-evidence findings,
the systematic bias, and the two scenario families into distinct insight types,
and the findings report keeps limitations in their own section.

Checks: `insight_types_complete` (all seven insight types are present),
`insight_store_mapping_valid` (every insight row names a store that exists in the
demand evidence), `findings_state_every_selected_model` and
`findings_no_false_untuned_claim` (the findings report names each selected model
and never states that a store went untuned), and `quality_report_gates_run`
(`main()` raises when any check fails, so the report is the gate). Together with
the families named above, these complete the report's **43** rows.

## Testing

Automated tests verify:

- data validation;
- densification and its measurement;
- safety-stock calculation;
- reorder-point calculation;
- scenario coverage in both families;
- monotonicity of lead-time demand;
- monotonicity of safety stock;
- handling of stores without validated models;
- forecast-error recomputation and reconciliation;
- the quality report's pass and failure paths;
- the full `main()` workflow.

Implemented: 78 tests, covering validation, densification, both descriptive
summaries, model-evidence loading and its rejection paths, forecast-error
recomputation, both scenario families, typed configuration propagation, insight
selection and its relative-error reframing, findings generation, the quality
report (one pass case and eighteen deliberate-failure cases), and `main()`
including the missing-input and failed-gate paths.

## Documentation

Documentation corresponds to the actual implementation and actual executed
results.

The results are recorded in
[`forecasting-and-inventory-insights-results.md`](forecasting-and-inventory-insights-results.md)
and asserted by the reproduction runbook in that document.
