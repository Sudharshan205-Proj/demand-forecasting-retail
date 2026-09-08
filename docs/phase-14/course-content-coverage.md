# Phase 14 — Course Content Coverage

## R Programming

| Course Concept | Project Evidence | Status |
|---|---|---|
| R programming | `r/r_analysis.R` | IMPLEMENTED |
| Functions | R script functions and package functions | IMPLEMENTED |
| Variables/objects | R analysis objects | IMPLEMENTED |
| Data frames/tibbles | CSV data loaded with readr/tidyverse | IMPLEMENTED |
| Packages | Required packages loaded | IMPLEMENTED |
| Comments | R script comments | IMPLEMENTED |

## Tidyverse / dplyr

| Course Concept | Project Evidence | Status |
|---|---|---|
| Tidyverse | `r/r_analysis.R` | IMPLEMENTED |
| dplyr | select, left_join, group_by, summarise, arrange, filter | IMPLEMENTED |
| Pipe workflow | `%>%` pipelines | IMPLEMENTED |
| Data transformation | Store and scenario transformations | IMPLEMENTED |
| Grouped analysis | Inventory scenario summaries | IMPLEMENTED |

## ggplot2

| Course Concept | Project Evidence | Status |
|---|---|---|
| ggplot2 | R analysis and R Markdown | IMPLEMENTED |
| aes() | Chart mappings | IMPLEMENTED |
| Geoms | geom_col, geom_line, geom_point | IMPLEMENTED |
| Layering | ggplot2 `+` layers | IMPLEMENTED |
| Faceting | `facet_wrap(~ store_id)` | IMPLEMENTED |
| Labels/titles | labs() | IMPLEMENTED |
| Exporting visuals | ggsave() | IMPLEMENTED |

The internship material specifically covers ggplot2 layering, geoms,
aesthetics and faceting. It also covers exporting visuals with `ggsave()`.
 
## R Markdown

| Course Concept | Project Evidence | Status |
|---|---|---|
| R Markdown | `r/r_analysis_report.Rmd` | IMPLEMENTED |
| YAML | R Markdown header | IMPLEMENTED |
| Markdown | Report narrative | IMPLEMENTED |
| Code chunks | Executable R chunks | IMPLEMENTED |
| Knit | HTML report generation | TO BE VERIFIED |
| Reproducible reporting | Script + Rmd workflow | IMPLEMENTED |

## tidymodels

`tidymodels` is installed and loaded in the Phase 14 environment.

The project does not create an artificial predictive model merely to claim
package usage. Forecasting model development and evaluation were already
implemented in the Python workflow.

Therefore, inappropriate duplicate forecasting is intentionally excluded.

## Course Concepts Not Reimplemented

The following concepts are not duplicated where they would add no meaningful
project value:

- a second forecasting model solely for R;
- duplicate hyperparameter tuning;
- duplicate final test-set evaluation.

The reason is architectural consistency: Python is already the project's
primary forecasting implementation, while R provides independent analysis and
reproducible reporting.