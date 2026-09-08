# Development Environment

## Operating Environment

The development environment is documented using verified versions where available. Version information below reflects the project owner's verified environment state; versions were not independently re-executed on the audit runner.

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

INSTALLED; VERSION NOT RECORDED

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

The R workflow uses course-aligned packages. Package installation was verified before the Phase 14 workflow was validated.

Verified packages include:

- tidyverse
- dplyr
- ggplot2
- tidymodels
- rmarkdown

## Version Recording

| Tool | Version | Status |
|---|---|---|
| Python | 3.12.10 | VERIFIED |
| pip | 25.3 | VERIFIED |
| Git | 2.55.0.windows.5 | VERIFIED |
| GitHub CLI | 2.98.0 | VERIFIED |
| VS Code | 1.135.0 | VERIFIED |
| R | 4.6.1 | VERIFIED |
| RStudio | Installed; version not recorded | PARTIALLY VERIFIED |
| SQLite | 3.53.4 | VERIFIED |
| Tableau Public | Installed; version not recorded | PARTIALLY VERIFIED |

## Phase 0 Audit Record

Phase 0 originally left the environment as `NOT YET VERIFIED`. The project owner's subsequent environment verification is now recorded above so the setup documentation no longer contradicts the established development environment. No dependency was added or removed during this audit.