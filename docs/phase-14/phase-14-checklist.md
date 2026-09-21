# Phase 14 — R Analysis

## Purpose

Phase 14 uses R, RStudio and R Markdown to perform reproducible analytical work on
the retail demand forecasting project, and to verify the project's published
evidence independently of the Python implementation.

## What the phase delivered

| Deliverable | Content |
|---|---|
| R workflow | `r/r_analysis.R` — 28 named functions ending in `main()`, consuming 9 Phase 13/Phase 12 artifacts |
| Reports | `r/r_analysis_report.Rmd` knitted to `data/analysis/r/r_analysis_report.html` (1,430,678 B) |
| Figures | Four ggplot2 figures exported with `ggsave()`, plus two rendered inline in the report |
| Analysis outputs | Store analysis, both scenario summaries, the 14-day / 95 % planning point for both families, the Phase 13 reconciliation and the Phase 12 metric reconciliation |
| Findings | `r_analysis_findings.txt` |
| Environment record | `r_environment.csv` — R 4.6.1, pandoc 3.11 and every package version |
| Tests | `tests/test_r_analysis.py` — including twelve failure paths |
| Quality record | `r_analysis_quality_report.csv` — 91 checks, all True, gating the run |

## R environment

| Tool | Version |
|---|---|
| R | 4.6.1 (2026-06-24 ucrt) |
| pandoc | 3.11 |
| RStudio | 2026.8.2.200 |
| tidyverse | 2.0.0 |
| dplyr | 1.2.1 |
| ggplot2 | 4.0.3 |
| readr | 2.2.0 |
| tidymodels | 1.5.0 |
| yardstick | 1.4.0 |
| knitr | 1.52 |
| rmarkdown | 2.32 |

An RStudio project is present at the repository root
(`demand-forecasting-retail.Rproj`). The reproducible path exercised by the test
suite is `Rscript`; the workflow was additionally run from the RStudio IDE on
2026-09-19 (script sourced, report knitted) with the same 91 of 91 result. The
outcome is recorded in [`r-analysis-results.md`](r-analysis-results.md) and the
RStudio version in [`../phase-0/environment.md`](../phase-0/environment.md).

## Key results

| Finding | Value |
|---|---|
| Highest average daily demand | Store 1 — 29,711.253352 |
| Highest relative variability | Store 4 — CV 0.380098 on 60 training days |
| Reorder point at 14 days / 95 % | Historical family 448,302.49 / 95,240.14 / 91,617.64 / 476,010.14; forecast-error family 475,036.85 / 98,037.76 / 99,790.96 / 474,241.71 |
| Phase 13 reconciliation | All 13 insight rows match on store, metric name and value; maximum relative difference 0.0 |
| Phase 12 metric reconciliation | RMSE and MAPE reproduced across all four stores; relative differences ≤ 5.6e-13 |
| Densification | 1,656 densified store-days, 1,655 observed, 1 zero-filled (Store 3, 2022-10-16) |

## Commands

```bash
Rscript r/r_analysis.R
Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(), 'data', 'analysis', 'r'))"
```

## Course coverage

Phase 14 carries the **Analyze → Share** stage's R strand: R programming,
tidyverse/dplyr data manipulation, ggplot2 visualization, R Markdown reporting,
tidymodels metric verification and RStudio use
([`course-content-coverage.md`](course-content-coverage.md)).

## Limitations

Inventory values remain planning scenarios rather than operational requirements;
the dataset provides no supplier lead times, service-level requirements, cost
inputs, current stock, purchase orders or warehouse constraints. R does not refit
or re-select the validated Python forecasting models.

## Related documents

- [`r-analysis-methodology.md`](r-analysis-methodology.md) — method
- [`r-analysis-quality-framework.md`](r-analysis-quality-framework.md) — quality practices
- [`r-analysis-results.md`](r-analysis-results.md) — results
