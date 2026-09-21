# Documentation Index

Project documentation for **Demand Forecasting for Retail** — an end-to-end
retail demand forecasting and inventory-planning case study. The project is
organized into 18 phases; each phase owns a folder (`docs/phase-0/` …
`docs/phase-17/`) holding its methodology, results, quality framework and a
short phase summary.

Alongside `docs/`, the tracked repository layout is `app/` (the Streamlit
application), `.streamlit/config.toml` (the application's runtime
configuration), `deploy/` (the frozen artifact bundle that lets a repository
build start the app), `r/` (R analysis and R Markdown report), `reports/`
(generated figures), `scripts/` (phase-owned Python scripts), `sql/` (schema and
analysis queries), `tableau/` (workbook and dashboard specifications) and
`tests/` (the pytest suite).

## Start here

Reading order for someone seeing this project for the first time:

| # | Document | What it gives you |
|---|---|---|
| 1 | [`../README.md`](../README.md) | Project overview, dataset, methodology, results, reproduction commands, limitations |
| 2 | [`project-status.md`](project-status.md) | The project on one page: phases, dataset, models, tests, deployment, limitations |
| 3 | [`phase-17/final-case-study.md`](phase-17/final-case-study.md) | The whole project as a case study, in course order |
| 4 | [`phase-17/portfolio-packaging.md`](phase-17/portfolio-packaging.md) | What to show, headline results, how to reproduce |
| 5 | [`phase-17/final-presentation.md`](phase-17/final-presentation.md) | Presentation script and prepared Q&A |
| 6 | [`course-coverage.md`](course-coverage.md) | Which course topics the project demonstrates, and where |
| 7 | [`reproducibility-runbook.md`](reproducibility-runbook.md) | Command-by-command reproduction, Phase 0 → 17 |

## Phase folders

Technical phases follow a consistent pattern: a methodology document, a results
document, a quality framework and a course-content coverage record, plus a
summary. The phase-specific file names are:

| Phase | Folder | Documents |
|---|---|---|
| 0 | `phase-0/` | `project-requirements.md`, `project-plan.md`, `architecture.md`, `curriculum-mapping.md`, `environment.md`, `data-strategy.md`, `reproducibility.md`, `security.md`, `phase-0-checklist.md` |
| 1 | `phase-1/` | `business-problem.md`, `analytical-questions.md`, `stakeholder-analysis.md`, `kpi-definitions.md`, `business-requirements.md`, `requirements-traceability.md`, `decision-log.md`, `hypothesis-register.md`, `scope-and-assumptions.md`, `phase-1-checklist.md` |
| 2 | `phase-2/` | `data-acquisition.md`, `dataset-inventory.md`, `data-source-assessment.md`, `data-dictionary.md`, `initial-data-assessment.md`, `data-ethics-and-privacy.md`, `phase-2-checklist.md` |
| 3 | `phase-3/` | `spreadsheet-methodology.md`, `spreadsheet-results.md`, `spreadsheet-quality-framework.md`, `course-content-coverage.md`, `phase-3-checklist.md` |
| 4 | `phase-4/` | `database-schema.md`, `sql-analysis-plan.md`, `sql-analysis.md`, `sql-results.md`, `sql-quality-framework.md`, `course-content-coverage.md`, `phase-4-checklist.md` |
| 5 | `phase-5/` | `data-cleaning-methodology.md`, `data-quality-framework.md`, `data-quality-results.md`, `course-content-coverage.md`, `phase-5-checklist.md` |
| 6 | `phase-6/` | `integration-methodology.md`, `integration-quality-framework.md`, `integration-results.md`, `course-content-coverage.md`, `phase-6-checklist.md` |
| 7 | `phase-7/` | `eda-methodology.md`, `eda-quality-framework.md`, `eda-results.md`, `course-content-coverage.md`, `phase-7-checklist.md` |
| 8 | `phase-8/` | `statistical-methodology.md`, `statistical-quality-framework.md`, `statistical-results.md`, `course-content-coverage.md`, `phase-8-checklist.md` |
| 9 | `phase-9/` | `time-series-methodology.md`, `time-series-quality-framework.md`, `time-series-results.md`, `course-content-coverage.md`, `phase-9-checklist.md` |
| 10 | `phase-10/` | `feature-engineering-methodology.md`, `feature-engineering-quality-framework.md`, `feature-engineering-results.md`, `course-content-coverage.md`, `phase-10-checklist.md` |
| 11 | `phase-11/` | `forecasting-models-methodology.md`, `forecasting-models-quality-framework.md`, `forecasting-models-results.md`, `course-content-coverage.md`, `phase-11-checklist.md` |
| 12 | `phase-12/` | `model-evaluation-and-tuning-methodology.md`, `model-evaluation-and-tuning-quality-framework.md`, `model-evaluation-and-tuning-results.md`, `course-content-coverage.md`, `phase-12-checklist.md` |
| 13 | `phase-13/` | `forecasting-and-inventory-insights-methodology.md`, `forecasting-and-inventory-insights-quality-framework.md`, `forecasting-and-inventory-insights-results.md`, `course-content-coverage.md`, `phase-13-checklist.md` |
| 14 | `phase-14/` | `r-analysis-methodology.md`, `r-analysis-quality-framework.md`, `r-analysis-results.md`, `course-content-coverage.md`, `phase-14-checklist.md` |
| 15 | `phase-15/` | `visualization-methodology.md`, `visualization-results.md`, `visualization-quality-framework.md`, `data-storytelling.md`, `tableau-dashboard-guide.md`, `course-content-coverage.md`, `phase-15-checklist.md` |
| 16 | `phase-16/` | `application-architecture.md`, `application-development-plan.md`, `application-quality-framework.md`, `application-results.md`, `deployment-plan.md`, `deployment-validation.md`, `course-content-coverage.md`, `phase-16-checklist.md` |
| 17 | `phase-17/` | `final-case-study.md`, `portfolio-packaging.md`, `final-presentation.md`, `phase-17-checklist.md` |

Phases 0, 1, 2 and 17 have no separate `course-content-coverage.md`; their
course evidence is carried in `phase-0/curriculum-mapping.md` and
`course-coverage.md`.

The Tableau workbook's structure — its three connections and their field types,
every field's role, rename and aggregation, the five hidden fields, the six
worksheets including the `KPI Summary` row, the dashboard layout and its
filters — is recorded in `tableau/tableau-dashboard-specification.md` and
`tableau/tableau-data-dictionary.md`.

## What this repository is, and is not

**Is:** an internship-level retail demand forecasting case study — a data
analysis project that forecasts store-level demand and translates the forecasts
into conditional inventory-planning scenarios, using spreadsheets, SQL, Python,
R and Tableau, with a reproducible pipeline, an automated test suite and a
deployed Streamlit application
(<https://demand-forecasting-retail-internship.streamlit.app/>).

**Is not:** a production platform, a deep-learning research project, or a
generic machine-learning benchmark. Scope decisions and everything deliberately
left out are recorded in [`phase-0/curriculum-mapping.md`](phase-0/curriculum-mapping.md)
and in the repository [`README.md`](../README.md).

## Conventions

- **Figures** — quantitative statements identify the artifact or document they
  come from. Generated data is excluded from Git, so figures are reproducible
  from the raw dataset via [`reproducibility-runbook.md`](reproducibility-runbook.md)
  rather than committed as files.
- **Generated data is not committed** — `data/raw/`, `data/processed/`,
  `data/analysis/` and `reports/` are excluded from Git; the runbook rebuilds
  them. The one exception is the committed `deploy/artifacts/` bundle that lets
  the application start from a fresh clone.
- **Phase summaries** — each phase folder's `phase-N-checklist.md` states what
  the phase delivered.
