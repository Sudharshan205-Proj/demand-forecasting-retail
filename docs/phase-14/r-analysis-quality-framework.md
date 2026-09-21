# Phase 14 — R Analysis Quality Framework

## 1. Purpose

This document defines what the Phase 14 R workflow proves before its results are
accepted. Every requirement below is enforced in `r/r_analysis.R`, recorded in
`data/analysis/r/r_analysis_quality_report.csv` and exercised by
`tests/test_r_analysis.py`.

## 2. Check Inventory

`data/analysis/r/r_analysis_quality_report.csv` is the authoritative
enumeration: **91 rows, every one `passed = True`**. A family that applies to
each of the nine inputs expands to one concrete row per input. The 91 rows
partition as:

| Family | Rows |
|---|---:|
| Input shape and emptiness (`<input>_columns_present`, `_no_missing_values`, `_not_empty`, nine inputs) | 27 |
| Run-level readiness (`required_input_files_present`, `inputs_ready_for_analysis`) | 2 |
| Historical scenario rules (`historical_*`) | 12 |
| Forecast scenario rules (`forecast_*`) | 12 |
| Phase 13 insight reconciliation (`phase13_*`) | 11 |
| Recomputed Phase 12 metrics and prediction scope | 6 |
| Store identity and internal value identities | 11 |
| Densification reconciliation beyond the shape rows | 4 |
| Figure checks (`plots_*`) | 3 |
| Leakage (`test_period_excluded`) | 1 |
| Forecast-family extras (`forecast_error_matches_validation`, `forecast_scenarios_use_tuned_configuration`) | 2 |
| **Total** | **91** |

Read the CSV for exact membership; the families below group the same rows by
concern.

## 3. Failure Behaviour

The workflow writes the quality report and the environment record, then stops if
any check failed. The findings report is withheld entirely on failure, and the R
Markdown report refuses to render because it calls the same `main()` and asserts
the gate explicitly.

| Situation | Behaviour |
|---|---|
| Missing input file | `required_input_files_present` and `inputs_ready_for_analysis` fail; run stops |
| Missing required column | `<input>_columns_present` and `inputs_ready_for_analysis` fail; no downstream indexing is attempted |
| Missing values or an empty dataset | `<input>_no_missing_values` / `<input>_not_empty` fail |
| Duplicate or mismatched store sets | `store_ids_unique_in_*` / `store_sets_identical_across_inputs` fail |
| Negative demand, spread or scenario quantities | the corresponding non-negativity check fails |
| Formula violation in either scenario family | the named identity check fails |
| Phase 13 insight that R cannot reproduce | `phase13_<insight_type>_reconciles` fails |
| Recomputed metric disagreement | `recomputed_<metric>_reconciles_with_phase12` fails |
| Densification disagreement | `densification_*` or `synthetic_days_*` fails |

## 4. Input Validation

Checks: `required_input_files_present`, `<input>_columns_present`,
`<input>_no_missing_values`, `<input>_not_empty` for all nine inputs,
`inputs_ready_for_analysis`.

The nine inputs are the Phase 13 demand, variability, historical-scenario,
forecast-scenario, forecast-error and densification summaries plus
`forecast_inventory_insights.csv`, and the Phase 12
`tuned_validation_results.csv` and `model_evaluation_predictions.csv`.

## 5. Store Identity and Value Consistency

Checks: `store_ids_unique_in_demand`, `store_ids_unique_in_variability`,
`store_sets_identical_across_inputs`, `training_days_positive`,
`demand_values_non_negative`, `variability_values_non_negative`,
`percentiles_ordered`.

Internal identities are verified rather than assumed:

- `mean_matches_total_over_days` — `total_quantity ÷ training_days`.
- `variance_matches_standard_deviation` — `variance = σ²`.
- `coefficient_of_variation_matches_ratio` — `CV = σ ÷ mean`, and the demand and
  variability summaries must agree on the same CV.
- `validation_results_non_negative`.

Tolerance: relative, `1e-6`.

## 6. Scenario Validation

Both families are validated with the same function, so a rule cannot hold in one
family and lapse in the other.

Checks per family (`historical_*` and `forecast_*`):
`scenario_coverage_complete` (36 rows = 4 stores × 3 lead times × 3 service
levels), `lead_times_complete`, `service_levels_complete`,
`service_level_z_values_match` (`z_value = Φ⁻¹(service_level)`, tolerance
`1e-9`), `expected_lead_time_demand_formula_holds`
(`expected = level × lead_time`), `safety_stock_formula_holds`
(`safety = z × spread × √lead_time`), `reorder_point_formula_holds`
(`ROP = expected + safety`), `safety_stock_non_negative`,
`reorder_point_covers_lead_time_demand`,
`safety_stock_monotonic_in_service_level`,
`lead_time_demand_monotonic_in_lead_time`.

The level/spread columns differ by family, which is what makes the checks
meaningful:

- Historical: level = `mean_daily_demand`, spread = `std_daily_demand`.
- Forecast-error: level = `bias_adjusted_daily_demand`, spread = `residual_std`.

Additional forecast-family checks: `forecast_level_is_bias_corrected`
(`model_daily_demand + bias = bias_adjusted_daily_demand`),
`forecast_scenarios_use_tuned_configuration` (the model and configuration match
Phase 12's selected rows) and `forecast_error_matches_validation` (the error
summary reconciles with the tuned validation metrics, tolerance `1e-4`).

`historical_and_forecast_scenarios_share_store_set` prevents one family from
silently covering a different set of stores.

## 7. Cross-Phase Validation

R independently reproduces the Phase 13 findings, and it reproduces the values as
well as the labels:

- `phase13_insight_types_complete` — all seven insight types are present.
- `phase13_insight_rows_reconciled` — every published row is matched.
- `phase13_<insight_type>_reconciles` — per type, the store **and** the published
  value reconcile within `1e-6` relative tolerance.
- `phase13_metric_names_reconcile` — each insight publishes the canonical metric
  for its type, so a relabelled metric cannot pass.
- `phase13_highest_demand_store_reconciles` — an absent or mismatched store row
  is reported rather than assumed.
- `densification_matches_training_days`, `densification_totals_reconcile`
  (1,656 store-days), `synthetic_days_measured_consistently`,
  `zero_filled_days_are_minimal` (exactly one synthetic day).

`r_phase13_reconciliation.csv` preserves the per-row evidence, and a mismatch
stops the run rather than being reported as a difference.

## 8. Cross-Language Metric Verification

R recomputes the validation metrics from the stored Phase 12 forecasts using
`yardstick` (the tidymodels metrics package) rather than trusting the reported
numbers.

Checks: `prediction_scopes_recognised` (only `cv_fold` and `validation`),
`test_period_excluded` (zero `test` rows), `validation_predictions_present`
(456 rows), `recomputed_metrics_cover_all_stores`,
`recomputed_observations_reconcile`,
`recomputed_rmse_reconciles_with_phase12`,
`recomputed_mape_reconciles_with_phase12`.

Tolerance: `1e-4` relative, because the stored predictions carry six decimal
places while the reported metrics were computed at full precision. Mean absolute
error is reported as R-derived evidence; Phase 12 did not publish it, so it is
not presented as a reconciliation.

`r_metric_reconciliation.csv` records the recomputed values, the reported values
and the relative differences.

## 9. Reproducibility

- `r_environment.csv` records the R version, platform, pandoc version, run
  timestamp, input directory and the version of every required package.
- Paths are resolved from a discovered project root, never hardcoded; the
  checkout directory may have any name.
- `R_ANALYSIS_PROJECT_ROOT`, `R_ANALYSIS_INPUT_DIR` and `R_ANALYSIS_OUTPUT_DIR`
  make the workflow location-independent and allow the tests to run it into a
  temporary directory.
- The workflow is deterministic: no random sampling and no model fitting.

## 10. Visualization Validation

Checks: `plots_written`, `plots_non_empty` (every PNG is larger than zero bytes)
and `plots_regenerated_from_analytical_data` (the written set equals the expected
set of four figures).

Every figure is produced from the loaded analytical frames inside the run, so no
value is entered by hand, and the report embeds the same files.

## 11. Leakage Control

The R analysis does not introduce future observations into the forecasting
workflow. It reads established Phase 13 outputs and the validation-scoped Phase 12
predictions only; `test_period_excluded` fails the run if any test-period row
appears. The Phase 11/12 train–validation–test separation remains intact.

## 12. Model Integrity

R does not replace, retrain or re-select the Phase 12 models. It recomputes their
reported validation metrics and reconciles the scenario families that Phase 13
derived from them. Every forecast-based scenario carries the caveat that its level
is the realised validation demand, not a forward forecast.

## 13. Course Integrity

Course concepts are marked as implemented only where the corresponding artifacts
exist. The coverage record marks RStudio as implemented because an RStudio project
is present at the repository root and the workflow was executed from the IDE on
2026-09-19 (`r/r_analysis.R` sourced, `r/r_analysis_report.Rmd` knitted) with 91
of 91 checks passing. The coverage record marks `tidymodels` because `yardstick`
is genuinely used.

## 14. Known Limitations

The analysis does not provide operational inventory recommendations, because the
dataset lacks supplier lead times, service-level requirements, holding costs,
ordering costs, stockout costs, current stock, purchase orders and warehouse
constraints.

Store 4's 60 training days and single cross-validation fold mean its variability
and forecast-error estimates rest on fewer observations; the generated findings
repeat that caveat rather than leaving it to prose.
