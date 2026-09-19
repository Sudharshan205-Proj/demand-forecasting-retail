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

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
