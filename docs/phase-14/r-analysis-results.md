# Phase 14 — R Analysis Results

## Status

VERIFIED — executed, validated and audited against the current Phase 11–13
evidence.

Every figure below was produced by `r/r_analysis.R` and reproduced by the
R Markdown report. Nothing in this document was entered by hand.

## R Environment

| Tool | Version | Evidence |
|---|---|---|
| R | 4.6.1 (2026-06-24 ucrt) | `r_environment.csv` |
| Platform | x86_64-w64-mingw32 | `r_environment.csv` |
| pandoc | 3.11 | `r_environment.csv` |

| Package | Version | Use |
|---|---|---|
| tidyverse | 2.0.0 | Data manipulation and visualisation |
| dplyr | 1.2.1 | Joins, grouping, summaries |
| ggplot2 | 4.0.3 | Layered figures, faceting, `ggsave()` |
| readr | 2.2.0 | CSV input and output |
| tidymodels | 1.5.0 | Modelling framework (metric recomputation) |
| yardstick | 1.4.0 | `rmse_vec()`, `mae_vec()`, `mape_vec()` |
| knitr | 1.52 | R Markdown rendering |
| rmarkdown | 2.32 | HTML report generation |

## Workflow Execution

| Item | Value |
|---|---|
| Command (repository root) | `Rscript r/r_analysis.R` |
| Command (from `r/`) | `Rscript r_analysis.R` — verified to resolve the same root |
| Result | Exit 0, `Phase 14 R analysis completed successfully.` |
| Quality checks | 91 of 91 passing |
| Inputs consumed | 9 Phase 13/Phase 12 artifacts |
| Outputs written | 11 data/report files, 4 figures |

## Generated Artifacts

| Artifact | Size | Content |
|---|---|---|
| `r_store_analysis.csv` | 882 B | 4 stores joined from demand and variability |
| `r_inventory_scenario_summary.csv` | 678 B | 9 historical scenario groups |
| `r_forecast_inventory_scenario_summary.csv` | 680 B | 9 forecast-error scenario groups |
| `r_baseline_inventory_scenario.csv` | 1,036 B | 4 stores at 14 days / 95 % |
| `r_baseline_forecast_inventory_scenario.csv` | 1,282 B | 4 stores at 14 days / 95 % |
| `r_phase13_consistency.csv` | 105 B | store-label consistency, both checks `TRUE` |
| `r_phase13_reconciliation.csv` | 1,186 B | 13 published insights reconciled on store and value |
| `r_metric_reconciliation.csv` | 734 B | RMSE, MAE and MAPE recomputed from stored forecasts |
| `r_analysis_quality_report.csv` | 6,276 B | 91 checks, all passing |
| `r_environment.csv` | 377 B | R, pandoc and package versions |
| `r_analysis_findings.txt` | 2,257 B | Findings derived from the loaded evidence |
| `plots/average_daily_demand_by_store.png` | 26,614 B | ggplot2 bar chart |
| `plots/demand_variability_by_store.png` | 26,705 B | ggplot2 bar chart |
| `plots/inventory_reorder_point_scenarios.png` | 96,022 B | faceted line chart, historical family |
| `plots/inventory_scenario_family_comparison.png` | 130,907 B | faceted comparison of both families |
| `r_analysis_report.html` | 1,430,678 B | knitted R Markdown report |

All outputs are generated artifacts and are excluded from Git under the
project's generated-artifact policy (`data/analysis/*`).

## Evidence Basis

| Input | Rows | Source |
|---|---|---|
| `inventory_demand_summary.csv` | 4 | Phase 13 |
| `inventory_variability_summary.csv` | 4 | Phase 13 |
| `inventory_scenarios.csv` | 36 | Phase 13, historical family |
| `inventory_forecast_scenarios.csv` | 36 | Phase 13, forecast-error family |
| `inventory_forecast_error_summary.csv` | 4 | Phase 13 |
| `inventory_densification_summary.csv` | 4 | Phase 13 |
| `forecast_inventory_insights.csv` | 13 | Phase 13, seven insight types |
| `tuned_validation_results.csv` | 4 | Phase 12 |
| `model_evaluation_predictions.csv` | 2,976 (456 validation) | Phase 12 |

## Store-Level Demand

Densified training-period demand, exactly as Phase 13 computed it on the
series Phases 11–12 fitted.

| Store | Training days | Mean daily demand | Median | Minimum | Maximum | Standard deviation | CV |
|---|---|---|---|---|---|---|---|
| 1 | 532 | 29,711.253352 | 27,946.1695 | 14,053.423 | 68,811.417 | 5,255.513309 | 0.176886 |
| 2 | 532 | 6,355.192286 | 6,536.3150 | 2,405.134 | 10,172.994 | 1,018.355882 | 0.160240 |
| 3 | 532 | 5,832.890242 | 6,530.1280 | 0.000 | 8,712.819 | 1,617.875022 | 0.277371 |
| 4 | 60 | 29,132.823483 | 25,336.9450 | 36.000 | 73,203.762 | 11,073.336036 | 0.380098 |

- Highest average daily demand: **Store 1** (29,711.253).
- Highest relative variability: **Store 4** (CV 0.380098), whose history is
  the shortest of the four stores.
- Store 3 carries the single zero-filled day (2022-10-16), so its minimum is
  0.000 rather than an observed low.

## Inventory Scenario Analysis

Both Phase 13 scenario families are analysed. Reorder points at the 14-day /
95 % planning point:

| Store | Historical variability | Forecast-error based |
|---|---|---|
| 1 | 448,302.49 | 475,036.85 |
| 2 | 95,240.14 | 98,037.76 |
| 3 | 91,617.64 | 99,790.96 |
| 4 | 476,010.14 | 474,241.71 |

The historical family sizes buffers from observed demand spread; the
forecast-error family sizes them from the selected model's realised
validation error and its bias-corrected validation demand level. Neither is
an operational requirement.

## Cross-Language Verification

### Phase 13 insight reconciliation

All 13 published insight rows reconcile on store, metric name and value. The
maximum relative difference across the reconciliation is 0.0.

| Insight type | Store | Metric | Phase 13 value | R value | Match |
|---|---|---|---|---|---|
| highest_average_demand | 1 | mean_daily_demand | 29,711.253351503758 | 29,711.253351503758 | TRUE |
| highest_relative_variability | 4 | coefficient_of_variation | 0.3800982778780511 | 0.3800982778780511 | TRUE |
| lowest_validation_rmse | 2 | validation_rmse | 711.2066768532256 | 711.2066768532256 | TRUE |
| lowest_relative_validation_error | 2 | validation_mape_percent | 8.14135610180036 | 8.14135610180036 | TRUE |
| systematic_bias | 4 | mean_forecast_bias | 3,871.035403508772 | 3,871.035403508772 | TRUE |
| inventory_scenario | 1–4 | reorder_point | 448,302.49 / 95,240.14 / 91,617.64 / 476,010.14 | identical | TRUE |
| forecast_inventory_scenario | 1–4 | reorder_point | 475,036.85 / 98,037.76 / 99,790.96 / 474,241.71 | identical | TRUE |

### Phase 12 forecast verification

The 456 stored validation forecasts were recomputed in R with `yardstick`:

| Store | Observations | RMSE (R) | MAE (R) | MAPE % (R) | Reported RMSE | Reported MAPE % | RMSE rel. diff | MAPE rel. diff |
|---|---|---|---|---|---|---|---|---|
| 1 | 114 | 4,233.491867 | 3,048.568107 | 9.071513 | 4,233.491867 | 9.071513 | 2.26e-13 | 4.15e-13 |
| 2 | 114 | 711.206677 | 538.446860 | 8.141356 | 711.206677 | 8.141356 | 2.94e-13 | 5.56e-13 |
| 3 | 114 | 1,309.960034 | 1,101.513980 | 16.283339 | 1,309.960034 | 16.283339 | 1.10e-13 | 4.66e-13 |
| 4 | 114 | 6,063.055906 | 4,566.850894 | 14.060535 | 6,063.055906 | 14.060535 | 1.50e-16 | 1.26e-16 |

The residual differences are floating-point round-trips of the six-decimal
predictions artifact. Mean absolute error was not published by Phase 12, so
it is R-derived evidence rather than a reconciliation.

### Densification reconciliation

| Store | Observed days | Densified days | Synthetic days |
|---|---|---|---|
| 1 | 532 | 532 | 0 |
| 2 | 532 | 532 | 0 |
| 3 | 531 | 532 | 1 |
| 4 | 60 | 60 | 0 |

Totals: 1,656 densified store-days, 1,655 observed, one zero-filled
(Store 3, 2022-10-16), matching Phase 11's and Phase 13's measurement.

## Quality Validation

`r_analysis_quality_report.csv` records 91 checks across eight groups; the run
stops if any fails and the findings report is not written.

| Group | Examples | Result |
|---|---|---|
| Input integrity | required files, required columns, missing values, non-empty | pass |
| Store identity | unique store ids, identical store sets across seven inputs | pass |
| Value consistency | non-negative demand, positive training days, percentile ordering | pass |
| Internal identities | mean = total ÷ days, variance = σ², CV = σ ÷ mean | pass |
| Scenario validation (both families) | coverage of 36, lead times, service levels, z-value mapping, `ROP = expected + safety`, `SS = z·σ·√L`, monotonicity | pass |
| Cross-phase reconciliation | seven insight types on store, metric and value; densification totals | pass |
| Cross-language metrics | RMSE, MAPE and observation counts reconciled with Phase 12 | pass |
| Output verification | 11 files written, 4 figures written and non-empty, test period excluded | pass |

## Visualization

Four figures are exported with `ggsave()`:

1. Average daily demand by store.
2. Relative demand variability by store.
3. Historical reorder-point scenarios faceted by store.
4. A faceted comparison of the historical and forecast-error families.

The report renders two further figures inline, demonstrating `aes()`
mappings, layered geoms, `facet_wrap()` and labels, and embeds the exported
figures.

## R Markdown Report

| Item | Value |
|---|---|
| Source | `r/r_analysis_report.Rmd` |
| Output | `data/analysis/r/r_analysis_report.html` (1,430,678 B) |
| Command | `Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(), 'data', 'analysis', 'r'))"` |
| Structure | YAML header, narrative, executable chunks, tables, figures, `sessionInfo()` |
| Gate | Sources `r/r_analysis.R`, calls `main()`, and refuses to render if any check fails |

## Reproducibility

- Both the script and the report resolve the project root by walking up to
  `pyproject.toml` + `docs/`; neither depends on the checkout directory name.
- `R_ANALYSIS_PROJECT_ROOT`, `R_ANALYSIS_INPUT_DIR` and
  `R_ANALYSIS_OUTPUT_DIR` override the resolved paths, which is how the tests
  run the complete workflow into a temporary directory.
- R, pandoc and every package version are recorded in `r_environment.csv`.
- The workflow is deterministic: no random sampling, no model fitting.
- Re-running both commands reproduces every artifact above.

## Assumptions and Limitations

- Inventory values are planning scenarios, not operational requirements.
- The dataset provides no supplier lead times, service-level requirements,
  holding costs, ordering costs, stockout costs, current stock, purchase
  orders or warehouse constraints.
- Store 4 has 60 training days and one cross-validation fold; its variability
  and forecast-error estimates rest on fewer observations.
- R does not replace or retrain the validated Python forecasting models.

---

## Phase 17 Re-Audit Record

**Audit status: AUDITED — COMPLETE.**

### Files reviewed

| Type | Files |
|---|---|
| Script | `r/r_analysis.R` |
| Report | `r/r_analysis_report.Rmd` |
| Tests | `tests/test_r_analysis.py` (new) |
| Phase 14 documents | all six files in `docs/phase-14/` |
| Generated artifacts | `r_store_analysis.csv`, `r_inventory_scenario_summary.csv`, `r_forecast_inventory_scenario_summary.csv`, `r_baseline_inventory_scenario.csv`, `r_baseline_forecast_inventory_scenario.csv`, `r_phase13_consistency.csv`, `r_phase13_reconciliation.csv`, `r_metric_reconciliation.csv`, `r_analysis_quality_report.csv`, `r_environment.csv`, `r_analysis_findings.txt`, `plots/*.png`, `r_analysis_report.html` |
| Upstream | Phase 13 analytical outputs, Phase 12 `tuned_validation_results.csv` and `model_evaluation_predictions.csv` |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-0/environment.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-1/analytical-questions.md`, `docs/phase-12/course-content-coverage.md`, `docs/phase-13/forecasting-and-inventory-insights-results.md`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Every artifact predated the Phase 13 inputs it consumes | All eight outputs and the HTML report were dated 8 Sep 12:48–12:52; the Phase 13 inputs were regenerated on 19 Sep 01:27. `r_store_analysis.csv` still carried Store 3 as 531 days / 5,843.874970 / minimum 173.898 — the pre-audit Phase 13 values that Phase 13's own re-audit replaced with 532 / 5,832.890242 / 0.000 | High |
| F2 | No machine-readable validation and no run gate | The quality framework listed input, cross-phase, visualisation, leakage, model-integrity and course-integrity requirements; the implementation was a handful of `stopifnot` clauses that recorded nothing | High |
| F3 | No automated tests, and no testing item in the phase checklist | `tests/` contained no R test and the script defined no functions, so nothing was testable | High |
| F4 | Scenario mathematics were asserted, never verified | The plan, methodology and quality framework stated `ROP = expected + safety` and `SS = z·σ·√L`, but nothing checked either identity, the z-value to service-level mapping, the 36-scenario coverage or monotonicity | Medium |
| F5 | Phase 13's newer evidence was unused | R read only `inventory_scenarios.csv` and 2 of the 7 insight types, ignoring the forecast-error scenario family, the forecast-error summary, the densification summary and the stored Phase 12 forecasts that Phase 13's audit had recorded as artifacts Phase 14 "may consume" | Medium |
| F6 | The cross-phase check compared labels only | `r_phase13_consistency.csv` compared two store names; no published value was reconciled and five insight types were ignored | Medium |
| F7 | No reproducibility record | No R version, package version, pandoc version, run timestamp or input directory was recorded anywhere machine-readable | Medium |
| F8 | Project-root detection was machine-dependent | The root was inferred by testing `basename(dirname(getwd())) == "demand-forecasting-retail"`, so a differently-named checkout resolved the wrong tree | Medium |
| F9 | The report could not be knitted from anywhere but `r/`, and could not fail | The Rmd hardcoded `file.path("..", "data", "analysis")`, pandoc could not fetch any of the three exported figures, and the consistency chunk only printed the `match` column — contradicting quality-framework §3 | Medium |
| F10 | Malformed inputs crashed instead of reporting | Required columns were read before presence was gated, so a missing key column produced an R error, and a published insight naming a store R did not select crashed the consistency check | Medium |
| F11 | `tidymodels` was a hard load gate but was never used | The script stopped if the package was missing while calling no tidymodels function, yet the coverage table claimed it | Low |
| F12 | Findings were partly hardcoded | The closing claims, including "R-derived analysis agrees with the corresponding Phase 13 store-level findings", were literal strings carrying no R version, quality summary, reconciliation count or artifact evidence | Low |
| F13 | The exported figures were never verified | Nothing checked that the PNGs existed, were non-empty or derived from the analytical data | Low |
| F14 | Status documents contradicted the artifacts | `r-analysis-results.md` said NOT YET EXECUTED while `README.md` marked Phase 14 COMPLETE; all 25 checklist boxes were unticked despite commit `bdaea3f`; Phase 13's audit record cited the wrong path `scripts/r_analysis.*` and labelled the phase unexecuted | Medium |

### Corrections applied

- The workflow was rebuilt around named functions (`find_project_root`,
  `resolve_paths`, `load_inputs`, `validate_inputs`,
  `validate_scenario_family`, `summarise_scenarios`, `reconcile_phase13`,
  `recompute_validation_metrics`, `reconcile_densification`, `build_plots`,
  `write_findings`, `write_quality_report`, `gate_quality_report`, `main`).
- It now consumes nine inputs: both scenario families, the forecast-error
  summary, the densification summary and the stored Phase 12 predictions.
- All 91 checks are written to `r_analysis_quality_report.csv`, the run stops
  on any failure, and the findings report is withheld on failure.
- All seven insight types are reconciled on store, metric name and value.
- RMSE, MAE and MAPE are recomputed in R from the 456 stored validation
  forecasts through `yardstick`, which makes the previously idle `tidymodels`
  dependency genuine.
- The project root, input directory and output directory are resolved
  robustly, with environment overrides for the tests.
- The report sources the script, asserts the quality gate, resolves figures
  relative to itself and embeds `sessionInfo()`.
- The findings report is derived entirely from the run's own objects.
- `tests/test_r_analysis.py` adds 36 tests, including twelve failure paths.

### Leakage audit

The workflow reads no raw data and no test-period data. The predictions
artifact is filtered to `scope == "validation"` (456 rows) and the run
asserts `test_period_excluded` (zero `test` rows) and
`prediction_scopes_recognised`. Phase 11/12's train-validation-test
separation is untouched.

### Verification

| Check | Result |
|---|---|
| `Rscript r/r_analysis.R` from the repository root | exit 0, 91 of 91 checks |
| `Rscript r/r_analysis.R` from `r/` | exit 0, identical artifacts |
| `rmarkdown::render(...)` | HTML written, 1,430,678 B, no unresolved resources |
| Failure path (negative demand) | exit 1, `demand_values_non_negative`, `mean_matches_total_over_days` and `inputs_ready_for_analysis` recorded and reported; no findings file |
| Failure path (missing key column) | exit 1, `demand_columns_present` reported without an R error |
| Failure paths (formula, z-value, insight, metric and densification corruptions) | each caught by its specific named check |
| Phase 14 tests | 36 of 36 passing |
| Full pytest suite | 477 passing (441 before the audit) |

### Documentation changes

All six Phase 14 documents were rewritten under their existing headings, and
the cross-phase records listed under "Files reviewed" were synchronised.

### Remaining issues

- None open for Phase 14.
- CLOSED in the Phase 15 re-audit: `docs/phase-15/visualization-and-tableau-plan.md`
  listed Phase 14 as an input while the Phase 15 script consumed no R output.
  The plan was corrected — Phase 15 consumes Phase 13/12 evidence, and the R
  figures belong to Phase 14's own report.
- CLOSED in the Phase 15 re-audit: Phase 15's results document said NOT YET
  EXECUTED against a phase that had already been committed and executed. That
  document has been rewritten with verified results.
- Still open downstream: Phase 16's generated artifacts require re-execution
  during their own audit.
- RStudio itself is installed but is not evidenced as used: the workflow runs
  through `Rscript`. The course-coverage record states this explicitly.
