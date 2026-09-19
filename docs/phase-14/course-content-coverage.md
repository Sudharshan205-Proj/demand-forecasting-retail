# Phase 14 — Course Content Coverage

Status: VERIFIED against the executed workflow and its generated artifacts.

## R Programming

| Course Concept | Project Evidence | Status |
|---|---|---|
| R programming | `r/r_analysis.R` (1,947 lines, executed) | IMPLEMENTED |
| Functions | 28 named functions, from `empty_checks()` to `main()` | IMPLEMENTED |
| Variables/objects | Analytical frames and returned result objects | IMPLEMENTED |
| Data structures | Tibbles, data frames, lists, named vectors, environment collector | IMPLEMENTED |
| Packages | `requireNamespace()` verification plus recorded versions | IMPLEMENTED |
| Comments | Section headers and rationale comments throughout | IMPLEMENTED |
| Troubleshooting | Explicit failure paths; malformed-input behaviour covered by tests | IMPLEMENTED |

## Tidyverse / dplyr

| Course Concept | Project Evidence | Status |
|---|---|---|
| Tidyverse | `library(tidyverse)` in the script and report | IMPLEMENTED |
| dplyr | `select`, `inner_join`, `left_join`, `group_by`, `summarise`, `arrange`, `filter`, `distinct`, `slice_max`, `slice_min`, `transmute`, `n_distinct` | IMPLEMENTED |
| Pipe workflow | `%>%` pipelines throughout the analysis | IMPLEMENTED |
| Data transformation | Store table, scenario summaries, reconciliation frames | IMPLEMENTED |
| Grouped analysis | Scenario summaries and grouped monotonicity checks | IMPLEMENTED |
| readr | `read_csv()`, `write_csv()` for every input and output | IMPLEMENTED |

## ggplot2

| Course Concept | Project Evidence | Status |
|---|---|---|
| ggplot2 | Four exported figures and two inline report figures | IMPLEMENTED |
| aes() | Store, variability, scenario and family mappings | IMPLEMENTED |
| Geoms | `geom_col`, `geom_line`, `geom_point` | IMPLEMENTED |
| Layering | ggplot2 `+` layers | IMPLEMENTED |
| Faceting | `facet_wrap(~ store_id)` | IMPLEMENTED |
| Labels/titles | `labs()` with titles, subtitles and axis labels | IMPLEMENTED |
| Exporting visuals | `ggsave()` producing four non-empty PNGs | IMPLEMENTED |

The internship material specifically covers ggplot2 layering, geoms,
aesthetics and faceting. It also covers exporting visuals with `ggsave()`.

## R Markdown

| Course Concept | Project Evidence | Status |
|---|---|---|
| R Markdown | `r/r_analysis_report.Rmd` (470 lines, knitted) | IMPLEMENTED |
| YAML | YAML header with title, author, date and `html_document` options | IMPLEMENTED |
| Markdown | Report narrative across 14 sections | IMPLEMENTED |
| Code chunks | Executable chunks that source and run the audited workflow | IMPLEMENTED |
| Knit | HTML report generated (1,430,678 B), no unresolved resources | VERIFIED |
| Reproducible reporting | Script + Rmd workflow; the report fails to knit if validation fails | IMPLEMENTED |

## tidymodels

`tidymodels` 1.5.0 is installed, verified and recorded, and its metrics
package `yardstick` 1.4.0 is genuinely used: the workflow recomputes RMSE,
MAE and MAPE from the 456 stored Phase 12 validation forecasts with
`rmse_vec()`, `mae_vec()` and `mape_vec()`, then reconciles them with the
reported values.

The project does not create an artificial predictive model merely to claim
package usage. Forecasting model development and evaluation were already
implemented in the Python workflow.

## RStudio

| Course Concept | Project Evidence | Status |
|---|---|---|
| RStudio | Not evidenced | NOT EVIDENCED |

RStudio is installed on the audit machine, but the executed workflow runs
through `Rscript` and the knitted report through `rmarkdown::render()`. No
RStudio project (`.Rproj`) is committed and no RStudio session is recorded,
so the row above is not claimed as implemented. The R code, packages,
R Markdown and reporting concepts are covered without it.

## Course Concepts Not Reimplemented

The following concepts are not duplicated where they would add no meaningful
project value:

- a second forecasting model solely for R;
- duplicate hyperparameter tuning;
- duplicate final test-set evaluation.

The reason is architectural consistency: Python is already the project's
primary forecasting implementation, while R provides independent analysis,
cross-language verification and reproducible reporting.

## Coverage Rule

A concept is considered implemented only when corresponding project evidence
exists. Every IMPLEMENTED row above is backed by a committed source file, a
generated artifact or a passing test.
