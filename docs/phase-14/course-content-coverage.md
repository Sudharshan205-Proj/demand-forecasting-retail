# Phase 14 — Course Content Coverage

## R Programming

| Course concept | Project evidence |
|---|---|
| R programming | `r/r_analysis.R` (1,947 lines, executed) |
| Functions | Named functions, from `empty_checks()` to `main()` |
| Variables/objects | Analytical frames and returned result objects |
| Data structures | Tibbles, data frames, lists, named vectors, environment collector |
| Packages | `requireNamespace()` verification plus recorded versions |
| Comments | Section headers and rationale comments throughout |
| Troubleshooting | Explicit failure paths; malformed-input behaviour covered by tests |

## Tidyverse / dplyr

| Course concept | Project evidence |
|---|---|
| Tidyverse | `library(tidyverse)` in the script and report |
| dplyr | `select`, `inner_join`, `left_join`, `group_by`, `summarise`, `arrange`, `filter`, `distinct`, `slice_max`, `slice_min`, `transmute`, `n_distinct` |
| Pipe workflow | `%>%` pipelines throughout the analysis |
| Data transformation | Store table, scenario summaries, reconciliation frames |
| Grouped analysis | Scenario summaries and grouped monotonicity checks |
| readr | `read_csv()`, `write_csv()` for every input and output |

## ggplot2

| Course concept | Project evidence |
|---|---|
| ggplot2 | Four exported figures and two inline report figures |
| aes() | Store, variability, scenario and family mappings |
| Geoms | `geom_col`, `geom_line`, `geom_point` |
| Layering | ggplot2 `+` layers |
| Faceting | `facet_wrap(~ store_id)` |
| Labels/titles | `labs()` with titles, subtitles and axis labels |
| Exporting visuals | `ggsave()` producing four non-empty PNGs |

The internship material specifically covers ggplot2 layering, geoms, aesthetics
and faceting, together with exporting visuals with `ggsave()`.

## R Markdown

| Course concept | Project evidence |
|---|---|
| R Markdown | `r/r_analysis_report.Rmd` (470 lines, knitted) |
| YAML | YAML header with title, author, date and `html_document` options |
| Markdown | Report narrative across 14 sections |
| Code chunks | Executable chunks that source and run the verified workflow |
| Knit | HTML report generated (1,430,678 B), no unresolved resources |
| Reproducible reporting | Script + Rmd workflow; the report fails to knit if validation fails |

## tidymodels

`tidymodels` 1.5.0 is installed, verified and recorded, and its metrics package
`yardstick` 1.4.0 is genuinely used: the workflow recomputes RMSE, MAE and MAPE
from the 456 stored Phase 12 validation forecasts with `rmse_vec()`,
`mae_vec()` and `mape_vec()`, then reconciles them with the reported values.

The project does not create an artificial predictive model merely to claim
package usage. Forecasting model development and evaluation are implemented in
the Python workflow.

## RStudio

| Course concept | Project evidence |
|---|---|
| RStudio | `demand-forecasting-retail.Rproj`; script sourced and report knitted from the IDE (2026-09-19) |

An RStudio project is present at the repository root, and on 19 September 2026
the workflow was run from the IDE — `r/r_analysis.R` sourced, then
`r/r_analysis_report.Rmd` knitted through `rmarkdown::render()`. The run wrote its
12 files and 4 figures to `data/analysis/r/` and passed 91 of 91 quality checks.
The committed project file is what makes the row verifiable; the IDE session
directories and console history are gitignored. The outcome is recorded in
[`r-analysis-results.md`](r-analysis-results.md).

## Course Concepts Not Reimplemented

The following concepts are not duplicated where they would add no meaningful
project value:

- a second forecasting model solely for R;
- duplicate hyperparameter tuning;
- duplicate final test-set evaluation.

The reason is architectural consistency: Python is the project's primary
forecasting implementation, while R provides independent analysis, cross-language
verification and reproducible reporting.

## Coverage Rule

A concept is considered implemented only when corresponding project evidence
exists. Every row above is backed by a committed source file, a generated artifact
or a passing test.
