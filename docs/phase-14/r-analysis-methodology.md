# Phase 14 — R Analysis Methodology

## 1. Analytical Approach

The R workflow is an independent re-analysis and verification pass over the
evidence the project already produced. It consumes nine compact artifacts
rather than reloading the 1.28 GB integrated dataset:

| Input | Producer | Role |
|---|---|---|
| `inventory_demand_summary.csv` | Phase 13 | Store-level demand on the densified training series |
| `inventory_variability_summary.csv` | Phase 13 | Spread, variance, percentiles, CV |
| `inventory_scenarios.csv` | Phase 13 | 36 historical-variability scenarios |
| `inventory_forecast_scenarios.csv` | Phase 13 | 36 forecast-error scenarios |
| `inventory_forecast_error_summary.csv` | Phase 13 | Per-store validation error statistics |
| `inventory_densification_summary.csv` | Phase 13 | Observed, densified and synthetic day counts |
| `forecast_inventory_insights.csv` | Phase 13 | 13 published insights across 7 types |
| `tuned_validation_results.csv` | Phase 12 | Selected configuration and reported metrics |
| `model_evaluation_predictions.csv` | Phase 12 | 2,976 stored forecasts (456 validation) |

Loading compact outputs keeps R fast and keeps the analysis honest: R never
re-derives the modelling decisions, it verifies the numbers those decisions
produced.

## 2. Workflow Structure

`r/r_analysis.R` defines named functions and ends in `main()`:

| Function | Responsibility |
|---|---|
| `find_project_root()` | Walk up to `pyproject.toml` + `docs/`, honouring `R_ANALYSIS_PROJECT_ROOT` |
| `resolve_paths()` | Resolve the input, output and plot directories, honouring the directory overrides |
| `check_required_packages()` | Verify every required package and record its version |
| `load_inputs()` | Read the nine artifacts, recording which are present |
| `validate_inputs()` | File, column, missing-value, emptiness, identity and value checks |
| `build_store_analysis()` | Join demand and variability into the store table |
| `validate_scenario_family()` | Coverage, z-value, formula and monotonicity checks per family |
| `validate_scenario_families()` | Both families plus the forecast-specific checks |
| `summarise_scenarios()` / `baseline_scenario()` | Scenario summaries and the 14-day / 95 % planning point |
| `reconcile_phase13()` | Reproduce all seven insight types and reconcile store, metric and value |
| `recompute_validation_metrics()` | Recompute RMSE, MAE and MAPE with `yardstick` and reconcile with Phase 12 |
| `reconcile_densification()` | Reconcile observed, densified and synthetic day counts |
| `build_plots()` / `verify_plots()` | Produce and verify the four exported figures |
| `write_findings()` | Derive the findings report from the run's own objects |
| `write_quality_report()` / `gate_quality_report()` | Persist the 91 checks and stop the run if any failed |
| `main()` | Orchestrate the workflow and return every object for the report |

`main()` is invoked only when the file is executed as a script
(`sys.nframe() == 0L`), so the R Markdown report can source it and call it
itself.

## 3. Tidy Data Workflow

The analysis uses tidyverse and dplyr operations to load, select, join, group,
summarise and arrange:

1. `readr::read_csv()` for typed input loading.
2. `dplyr::inner_join()` to align the demand and variability summaries, and
   to align the published insights with R's independently computed values.
3. `dplyr::group_by()` / `dplyr::summarise()` for scenario summaries and for
   grouped monotonicity checks.
4. `dplyr::slice_max()` / `dplyr::slice_min()` with `with_ties = FALSE` to
   select the headline stores deterministically.
5. `dplyr::arrange()` for stable output ordering.
6. `readr::write_csv()` and `writeLines()` for outputs.

## 4. Demand Analysis

Store-level demand is evaluated using mean, median, minimum and maximum daily
demand, total quantity, densified training-day count, standard deviation,
variance, the p90/p95/p99 percentiles and the coefficient of variation.

The workflow also verifies the summary's internal arithmetic, so a demand
summary that does not equal its own total over its own day count fails the
run instead of being reported.

## 5. Variability

Relative variability is represented using the coefficient of variation:

CV = standard deviation / mean

A higher CV indicates greater demand variability relative to the store's
average demand. R verifies that the demand summary and the variability
summary publish the same CV, and that the CV equals σ ÷ mean in both.

## 6. Inventory Scenarios

Two scenario families are analysed, both derived by Phase 13 and both
re-deriving their mathematics here:

Reorder point: ROP = expected lead-time demand + safety stock
Safety stock: SS = z × σ × √L

where:

- z = standard-normal quantile of the service level, checked against
  `qnorm()`;
- σ = the family's spread (historical `std_daily_demand` or forecast
  `residual_std`);
- L = assumed lead time.

Scenario assumptions remain:

- 7-day, 14-day and 28-day lead times;
- 90 %, 95 % and 99 % service levels;
- 4 stores, giving 36 scenarios per family.

For the forecast family, the level is the model's bias-corrected validation
demand (`model_daily_demand + bias`), and the workflow asserts that identity
so the family cannot be described as a forward forecast.

## 7. Cross-Language Verification

The workflow recomputes RMSE, MAE and MAPE from the 456 stored validation
forecasts with `yardstick::rmse_vec()`, `mae_vec()` and `mape_vec()`, then
reconciles them with Phase 12's reported values and with Phase 13's
forecast-error summary. `yardstick` reports MAPE as a percentage, matching
the Phase 12 field.

This is the reason the `tidymodels` dependency is claimed: `yardstick` is its
metrics package and is genuinely used, rather than loaded and ignored.

## 8. Visualization

ggplot2 is used to demonstrate:

- data-to-aesthetic mapping with `aes()`;
- geometric layers (`geom_col()`, `geom_line()`, `geom_point()`);
- faceting with `facet_wrap()`;
- labels, titles and subtitles with `labs()`;
- programmatic export with `ggsave()`.

Four figures are exported; the run verifies that each was written and is
non-empty.

## 9. Reproducible Reporting

The R Markdown report sources `r/r_analysis.R`, calls `main()`, and therefore
renders exactly the evidence the script verifies. It contains:

- YAML metadata;
- Markdown narrative;
- executable R code chunks;
- generated tables and visualizations;
- the quality-report summary;
- `sessionInfo()` for the environment.

The report's final chunk stops the knit if any quality check failed, and
figures are referenced relative to the report so it can be knitted from the
repository root.

## 10. Forecasting Boundary

The R phase does not replace the validated forecasting workflow.

Forecast model selection and tuning remain based on the Python implementation
established in Phases 11 and 12. R neither refits a model nor re-selects a
configuration.

## 11. Interpretation

Observed demand statistics describe historical training-period behaviour on
the densified series Phases 11–13 use.

Inventory values are scenario estimates rather than operational requirements.

No causal interpretation is assigned to descriptive relationships, and
cross-store comparisons of scale-bound error measures are not made.
