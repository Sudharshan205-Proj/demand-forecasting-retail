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
| Phase 16 | Application Development & Deployment | COMPLETE (local); hosted deployment pending |
| Phase 17 | Testing, Documentation & Final Audit | COMPLETE |

## Repository Structure

The repository is organized into:

- `app/` — Streamlit application code (Phase 16)
- `deploy/` — frozen artifact bundle so a repository build can start the app (Phase 16)
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

### Reproducing the Phase 15 visualizations

Run from the repository root:

```text
.venv\Scripts\python.exe scripts/create_visualizations.py
.venv\Scripts\python.exe scripts/sync_tableau_workbook_schema.py --check
```

The workflow reads five Phase 12/13 analytical outputs and writes four figures
to `data/analysis/visualizations/` plus `visualization_quality_report.csv` and
`visualization_manifest.csv` to `data/analysis/` (all excluded from Git). It
records 55 quality checks, stops and draws nothing if any check fails, and the
manifest records each figure's byte size and SHA-256 digest.

The schema-sync command reports whether the committed Tableau workbook's
cached field schema still matches the current CSV headers; run it without
`--check` to repair the workbook in place. The dashboard is published at
<https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning>.

Test the phase with:

```text
.venv\Scripts\python.exe -m pytest tests/test_create_visualizations.py -q
```

### Running the Phase 16 application

Run from the repository root:

```text
.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

The application reads seven compact CSV artifacts and never retrains a model.
It resolves them, in order, from the `APP_ANALYSIS_DIR` environment variable,
from `data/analysis/` when that directory is complete, or from the committed
`deploy/artifacts/` bundle. The bundle exists because `data/analysis/` is
excluded from Git, so a host that builds from the repository would otherwise
start with no data; `tests/test_application.py` reconciles every bundled file
against the pipeline output by SHA-256 so the two cannot silently drift.

Model evidence for each store — the selected model, its configuration, its
cross-validation fold count and its validation metrics — is derived from the
Phase 12 tables rather than hardcoded, and a store whose selection rests on a
single fold is labelled as validated with an explicit caveat.

Test the phase with:

```text
.venv\Scripts\python.exe -m pytest tests/test_application.py -q
```

## Final Deliverables

The project closes with a consolidated audit and a portfolio case study:

- `docs/phase-17/final-audit-report.md` — the final project audit across
  structure, code, tests, data, models, evaluation, configuration, Git,
  documentation, deployment, security, reproducibility and course coverage.
- `docs/phase-17/final-case-study.md` — the full case study in course order
  (problem → future scope).
- `docs/phase-17/final-presentation.md` — presentation script and Q&A.
- `docs/phase-17/portfolio-packaging.md` — internship submission guide.
- `docs/phase-17/phase-17-checklist.md` — the Phase 17 checklist.

Run the full test suite with:

```text
.venv\Scripts\python.exe -m pytest -q
```

## Known Limitations

The following are recorded rather than presented as finished work; the full
register is in `docs/phase-17/final-audit-report.md`.

- The hosted Streamlit deployment requires a one-time owner authorisation; no
  public URL exists yet. The application is verified running locally.
- The published Tableau dashboard reflects the extract built on 8 September
  2026; refreshing it requires Tableau Desktop.
- No human usability or accessibility review of the rendered interface has been
  performed.
- The reserved final test-period evaluation has no owning phase.
- The dataset contains no holiday field, no lead times, costs or stock levels;
  holiday analysis is Not Applicable and inventory scenarios are conditional.
- RStudio is installed but unevidenced; the R workflow runs through `Rscript`.

## Disclaimer

Forecasts are analytical estimates and should support inventory decision-making rather than being treated as guaranteed future demand.