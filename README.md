# Demand Forecasting for Retail

An end-to-end retail demand forecasting project designed to forecast product demand and support inventory planning.

## Project Goal

Forecast future product demand using historical retail data, including sales, promotions, holidays, and other relevant demand drivers.

The project will demonstrate the complete analytical and software lifecycle:

Ask → Prepare → Process → Analyze → Share → Act

## Core Forecasting Requirement

The project must:

- Use historical sales data.
- Incorporate promotions where available.
- Incorporate holidays where available.
- Develop time-series forecasting models.
- Include ARIMA.
- Evaluate forecasts using RMSE and MAPE where appropriate.
- Compare forecasting approaches.
- Translate forecasts into inventory-related business insights.
- Provide a usable application.
- Be documented, tested, reproducible, and deployment-ready.

## Course Coverage

The project will deliberately incorporate relevant concepts from all eight internship course videos.

Course coverage includes:

- Data analytics foundations
- Analytical thinking
- Problem definition
- SMART analytical questions
- Data preparation
- Data organization
- Data ethics
- Data privacy
- Data security
- Data quality
- Spreadsheets
- SQL
- SQLite
- Python
- R
- RStudio
- R Markdown
- Data visualization
- Tableau
- Data storytelling
- Statistical analysis
- Machine learning concepts
- Model evaluation
- Case-study methodology

Course concepts will only be marked as implemented when actual project evidence exists.

## Project Lifecycle

1. Phase 0 — Project Setup & Curriculum Audit
2. Phase 1 — Business Understanding & Planning
3. Phase 2 — Data Acquisition & Data Understanding
4. Phase 3 — Spreadsheet-Based Analysis
5. Phase 4 — SQL & Database Analysis
6. Phase 5 — Data Cleaning & Quality Assurance
7. Phase 6 — Data Integration
8. Phase 7 — Exploratory Data Analysis
9. Phase 8 — Statistical & Analytical Analysis
10. Phase 9 — Time-Series Preparation
11. Phase 10 — Feature Engineering 
12. Phase 11 — Forecasting Models
13. Phase 12 — Model Evaluation & Tuning
14. Phase 13 — Forecasting & Inventory Insights
15. Phase 14 — R Analysis
16. Phase 15 — Visualization & Tableau
17. Phase 16 — Application Development & Deployment
18. Phase 17 — Testing, Documentation & Final Audit

## Project Status

| Phase | Name | Status |
|---|---|---|
| Phase 0 | Project Setup & Curriculum Audit | COMPLETE |
| Phase 1 | Business Understanding & Planning | COMPLETE |
| Phase 2 | Data Acquisition & Data Understanding | COMPLETE |
| Phase 3 | Spreadsheet-Based Analysis | COMPLETE |
| Phase 4 | SQL & Database Analysis | COMPLETE |
| Phase 5 | Data Cleaning & Quality Assurance | COMPLETE |
| Phase 6 | Data Integration | COMPLETE |
| Phase 7 | Exploratory Data Analysis | COMPLETE |
| Phase 8 | Statistical & Analytical Analysis | COMPLETE |
| Phase 9 | Time-Series Preparation | COMPLETE |
| Phase 10 | Feature Engineering | COMPLETE |
| Phase 11 | Forecasting Models | COMPLETE |
| Phase 12 | Model Evaluation & Tuning | COMPLETE |
| Phase 13 | Forecasting & Inventory Insights | COMPLETE |
| Phase 14 | R Analysis | COMPLETE |
| Phase 15 | Visualization & Tableau | COMPLETE |
| Phase 16 | Application Development & Deployment | COMPLETE |
| Phase 17 | Testing, Documentation & Final Audit | IN PROGRESS |

## Repository Structure

The repository is organized into:

- `app/` — Streamlit application code (Phase 16)
- `data/` — raw, interim, processed, external and analysis data (raw and generated data excluded from Git; directory placeholders tracked)
- `docs/` — phase-by-phase project documentation
- `r/` — R analysis scripts and R Markdown report (Phase 14)
- `reports/` — generated analysis reports and findings
- `scripts/` — phase-owned Python data and analysis scripts
- `sql/` — SQL schema and analysis queries (Phase 4)
- `tableau/` — Tableau workbook and dashboard documentation (Phase 15)
- `tests/` — pytest test suite

## Reproducibility

All important project decisions, dependencies, preprocessing steps, model parameters, evaluation metrics, and dataset information will be documented.

### Reproducing the Phase 14 R analysis

Run both commands from the repository root:

```text
Rscript r/r_analysis.R
Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(), 'data', 'analysis', 'r'))"
```

The workflow reads the Phase 12 and Phase 13 analytical outputs and writes its
artifacts to `data/analysis/r/` (excluded from Git). It records 91 quality
checks in `r_analysis_quality_report.csv`, stops if any check fails, and only
then writes its findings; the R Markdown report calls the same workflow and
refuses to render when validation fails. R, pandoc and package versions are
recorded in `data/analysis/r/r_environment.csv`.

Test the workflow with:

```text
.venv\Scripts\python.exe -m pytest tests/test_r_analysis.py -q
```

Python remains the project's primary forecasting implementation; R provides
independent analysis, cross-language verification and reproducible reporting.

## Disclaimer

Forecasts are analytical estimates and should support inventory decision-making rather than being treated as guaranteed future demand.