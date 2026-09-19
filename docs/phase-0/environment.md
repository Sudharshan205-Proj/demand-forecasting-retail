# Development Environment

## Operating Environment

The development environment is documented using verified versions. Version information below reflects the environment re-executed on the Phase 17 audit runner.

## Required Software

### Python

Purpose:

- Data processing
- Analysis
- Forecasting
- Testing
- Application development

Status:

VERIFIED

### pip

Purpose:

- Python dependency management

Status:

VERIFIED

### Git

Purpose:

- Version control

Status:

VERIFIED

### GitHub

Purpose:

- Remote repository
- Project history
- Portfolio presentation

Status:

VERIFIED

### VS Code

Purpose:

- Primary development environment

Status:

VERIFIED

### R

Purpose:

- Course-required analytical workflow

Status:

VERIFIED

### RStudio

Purpose:

- R development environment

Status:

INSTALLED; PROJECT-LEVEL SETUP STATUS NOT RE-VERIFIED DURING PHASE 0 AUDIT

### SQLite

Purpose:

- Relational SQL analysis
- Database demonstrations

Status:

VERIFIED

### BigQuery

Purpose:

- Demonstrate cloud SQL/data-analysis workflow where appropriate

Status:

NOT REQUIRED FOR THE CURRENT IMPLEMENTATION

### Excel / Google Sheets

Purpose:

- Spreadsheet analysis required by course

Status:

PROJECT ARTIFACT GENERATION VERIFIED; LOCAL APPLICATION VERSION NOT RECORDED

### Tableau / Tableau Public

Purpose:

- Interactive visualization and storytelling

Status:

INSTALLED; VERSION NOT RECORDED; PUBLISHED WORKBOOK VERIFIED

The Phase 15 re-audit verified that the project's dashboard is published and
publicly reachable: HTTP 200 on 19 September 2026 at
`https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning`.
The committed workbook was authored with Tableau 2026.2.2, which is recorded
in its own `source-build` attribute. The installed *client* version still
cannot be read from the command line and remains unrecorded.

## Python Environment

A project-local `.venv` is used.

## Initial Python Dependencies

- numpy
- pandas
- matplotlib
- scipy
- scikit-learn
- statsmodels
- openpyxl
- jupyter
- pytest

Additional dependencies will only be introduced when justified by a later phase.

## R Packages

The R workflow uses course-aligned packages. The Phase 14 re-audit verified
every package against the executed workflow and recorded the versions in
`data/analysis/r/r_environment.csv`, which the run writes itself.

| Package | Version | Role in Phase 14 |
|---|---|---|
| tidyverse | 2.0.0 | Umbrella for the analytical packages |
| dplyr | 1.2.1 | Joins, grouping, summaries |
| ggplot2 | 4.0.3 | Exported and inline figures |
| readr | 2.2.0 | CSV input and output |
| tidymodels | 1.5.0 | Modelling framework; `yardstick` is its metrics package |
| yardstick | 1.4.0 | `rmse_vec()`, `mae_vec()`, `mape_vec()` |
| knitr | 1.52 | R Markdown rendering |
| rmarkdown | 2.32 | HTML report generation |
| pandoc | 3.11 | Supplied by rmarkdown for the HTML report |

## Version Recording

| Tool | Version | Status |
|---|---|---|
| Python | 3.12.10 | VERIFIED |
| pip | 26.2.1 | VERIFIED |
| Git | 2.55.0.windows.5 | VERIFIED |
| GitHub CLI | 2.98.0 | VERIFIED |
| VS Code | 1.136.2 | VERIFIED |
| R | 4.6.1 | VERIFIED |
| RStudio | Installed; version not recorded and not evidenced as used | PARTIALLY VERIFIED |
| SQLite | 3.53.4 | VERIFIED |
| Tableau Public | Published workbook verified; client version not recorded | PARTIALLY VERIFIED |

## Phase 0 Audit Record (Phase 17 Re-Audit)

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).

## Phase 16 Audit Record (Phase 17 Re-Audit)

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).

## Phase 15 Audit Record (Phase 17 Re-Audit)

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).

## Phase 14 Audit Record (Phase 17 Re-Audit)

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
