# Project Status

Single-page state of the project. This file consolidates two earlier
bookkeeping records — the running phase state log (`docs/phase-0/project-state.md`)
and the file update register (`docs/project-file-update-register.md`) — which were
removed during the 2026-09-19 documentation cleanup. Both recorded the
development process rather than the project; the durable record of what changed
is Git history plus each phase's own folder.

## Current status

**All 18 phases (Phase 0 → Phase 17) are complete.** The application is verified
running locally. One item is outstanding and requires the project owner: the
hosted Streamlit deployment.

| | |
|---|---|
| Current phase | None — Phase 17 closed |
| Automated tests | **530 collected, 530 passing** across 18 modules |
| Machine-checked quality gates | **272/272** (15 + 14 + 24 + 30 + 43 + 91 + 55) |
| Application | Verified locally (headless start, HTTP 200) |
| Hosted deployment | **Pending** — requires one-time owner authorisation |
| Test-period evaluation | Reserved and unused; no owning phase |

## Phase status

| Phase | Name | Status | Primary evidence | Tests |
|---|---|---|---|---|
| 0 | Project Setup & Curriculum Audit | COMPLETE | `phase-0/` | 6 |
| 1 | Business Understanding & Planning | COMPLETE | `phase-1/` | 5 |
| 2 | Data Acquisition & Data Understanding | COMPLETE | `phase-2/` | 6 |
| 3 | Spreadsheet-Based Analysis | COMPLETE | `phase-3/` | 12 |
| 4 | SQL & Database Analysis | COMPLETE | `phase-4/` | 11 |
| 5 | Data Cleaning & Quality Assurance | COMPLETE | `phase-5/` | 19 |
| 6 | Data Integration | COMPLETE | `phase-6/` | 24 |
| 7 | Exploratory Data Analysis | COMPLETE | `phase-7/` | 34 |
| 8 | Statistical & Analytical Analysis | COMPLETE | `phase-8/` | 46 |
| 9 | Time-Series Preparation | COMPLETE | `phase-9/` | 37 |
| 10 | Feature Engineering | COMPLETE | `phase-10/` | 32 |
| 11 | Forecasting Models | COMPLETE | `phase-11/` | 52 |
| 12 | Model Evaluation & Tuning | COMPLETE | `phase-12/` | 64 |
| 13 | Forecasting & Inventory Insights | COMPLETE | `phase-13/` | 78 |
| 14 | R Analysis | COMPLETE | `phase-14/`, `r/` | 36 |
| 15 | Visualization & Tableau | COMPLETE | `phase-15/`, `tableau/` | 32 |
| 16 | Application Development & Deployment | COMPLETE (local); hosted deployment pending | `phase-16/`, `app/`, `deploy/` | 36 |
| 17 | Testing, Documentation & Final Audit | COMPLETE | `phase-17/` | — (full suite) |

Phase 4's 11 tests are split across two modules (3 database, 8 SQL). Phase 17
contributes no module of its own; its validation is the full-suite run.

## Test suite

`python -m pytest -q` → **530 passed**, run from the repository root with the
virtual environment present. Module counts, as collected:

| Module | Tests | Module | Tests |
|---|---|---|---|
| `test_phase0_project_setup.py` | 6 | `test_forecasting_models.py` | 52 |
| `test_phase1_business_understanding.py` | 5 | `test_evaluate_and_tune_models.py` | 64 |
| `test_inspect_raw_data.py` | 6 | `test_forecasting_inventory_insights.py` | 78 |
| `test_create_spreadsheet_analysis.py` | 12 | `test_r_analysis.py` | 36 |
| `test_create_sqlite_database.py` | 3 | `test_create_visualizations.py` | 32 |
| `test_sql_analysis.py` | 8 | `test_application.py` | 36 |
| `test_clean_retail_data.py` | 19 | `test_statistical_analytical_analysis.py` | 46 |
| `test_integrate_retail_data.py` | 24 | `test_prepare_time_series.py` | 37 |
| `test_exploratory_data_analysis.py` | 34 | `test_feature_engineering.py` | 32 |

The suite covers per-phase setup contracts, each pipeline stage, model
validation (leakage guards, fold counts, the selection rule), the R workflow as a
subprocess with deliberate-failure paths, the visualization workflow with
failure paths, and application behaviour including a headless HTTP startup test.

## Dataset

| Property | Value |
|---|---|
| Raw files | 8 CSVs, ≈824 MB (not committed — data policy) |
| Source | Kaggle retail sales forecasting dataset (CC BY-NC-SA 4.0) |
| Coverage | 2022-08-28 → 2024-09-26 |
| Stores | 4 |
| Sales rows (raw → cleaned) | 7,432,685 → 7,431,026 |
| Integrated dataset | 34 columns, 1,283,859,491 bytes |
| Total demand | 41,949,529.910 |
| Total revenue | 5,659,219,309.90 |
| Known gaps | No holiday field; no lead times, costs or stock levels |

Cleaning removes 1,659 rows (negative quantity or price, invalid dates,
duplicates) and retains 36,585 rows without a catalog match; both are reconciled
across Phases 4–6. The 2023-12 level shift is diagnosed as a coverage change
(Store 4 enters 2023-12-13).

## Models and results

Chronological splits: train → 2024-02-10 (4,315,416 rows), validation → 2024-06-03
(1,548,957), test → 2024-09-26 (1,566,653, unused). Model selection uses
training-period cross-validation only; the test period is never read.

| Item | Result |
|---|---|
| Candidates evaluated | Naive, seasonal-naive, ARIMA(1,1,1), feature-based gradient boosting, plus tuning variants |
| Seasonal-naive mean validation RMSE | 3,223.0630 |
| Tuned mean validation RMSE | 3,079.4286 |
| Selected models | `feature_gbm` for Stores 1–3; `seasonal_naive(7)` for Store 4 |
| Store 4 caveat | Selected on a single cross-validation fold — disclosed in the application |
| Highest average daily demand | Store 1 — 29,711.253352 |
| Highest relative variability | Store 4 — CV 0.380098 |
| Lowest relative validation error | Store 2 — MAPE 8.141356 % |
| Systematic under-forecast | Mean 1,409.941 units/day across stores |
| 14-day / 95 % reorder points | 448,302 / 95,240 / 91,618 / 476,010 |

R independently reproduces the Python results with `yardstick`, alongside its own
ggplot2 figures and a rendered R Markdown report.

## Application and deployment

The Streamlit application reads seven compact CSV artifacts and never retrains a
model. It resolves them in order from `APP_ANALYSIS_DIR`, from `data/analysis/`
when complete, or from the committed `deploy/artifacts/` bundle — which is why a
fresh clone can start the app. `tests/test_application.py` reconciles every
bundled file against pipeline output by SHA-256 so the two cannot drift.

Per-store model evidence (selected model, configuration, fold count, validation
metrics) is derived from the Phase 12 tables rather than hardcoded.

The Tableau Public dashboard is published and resolves, but reflects the extract
built on 2026-09-08; refreshing it requires Tableau Desktop.

## Key decisions

- **Python is the primary implementation; R is an independent analysis and
  reporting track.** R verifies the forecasting results rather than duplicating
  the pipeline.
- **ARIMA over Prophet/LSTM.** The internship brief lists all three; Prophet and
  LSTM were assessed and deliberately not implemented, and the assessment itself
  is recorded as evidence.
- **The reserved test period stays unused.** It is reserved so it can never
  influence selection or tuning; evaluating it is future work, not a defect.
- **Generated data is excluded from Git** except the `deploy/artifacts/` bundle,
  which exists so a repository build can start the application.
- **Phase branches.** Each phase was developed on its own `phase-N-…` branch and
  merged to `main`; all 17 phase branches exist on the remote.

## Known limitations

Recorded, not hidden. The full register is `phase-17/final-audit-report.md` §15.

1. Hosted Streamlit deployment requires one-time owner authorisation; no public
   URL is claimed. The application is verified locally.
2. The Tableau Public dashboard reflects the 2026-09-08 extract.
3. No human usability or accessibility review of the rendered interface.
4. The reserved final test-period evaluation has no owning phase.
5. No holiday field in the data, so holiday analysis is Not Applicable.
6. No lead times, costs or stock levels, so inventory scenarios are conditional.
7. RStudio is installed but unevidenced; the R workflow runs through `Rscript`.
8. The Tableau workbook uses an absolute local data-source path.
9. One-off 22-minute `run_sql_analysis.py` runtime (PERF-01), outputs correct.

## Where the evidence lives

| Question | Document |
|---|---|
| How was a phase carried out? | `phase-N/<topic>-methodology.md` |
| What did it produce? | `phase-N/<topic>-results.md` |
| How are its outputs verified? | `phase-N/<topic>-quality-framework.md` |
| Which course topics does it cover? | `phase-N/course-content-coverage.md` |
| Is the phase finished? | `phase-N/phase-N-checklist.md` |
| Verdicts on open and closed items | `phase-17/audit-findings.md` |
| What the Phase 17 pass found in each phase | `phase-17/re-audit-record.md` |
| Independent re-execution | `phase-17/independent-verification.md` |
| Command-by-command reproduction | `reproducibility-runbook.md` |

## Git state

- `main` is the integration branch; all 17 phase branches exist locally and on
  `origin`.
- Phase 17 closed at `e5a750f` (*Final Audit*). A later commit, `80aca45`
  (*Verification and Checks*), committed the audit working files and the
  documentation corrections and is the current tip of `main`.
- The 2026-09-19 documentation cleanup (removing superseded plan documents, the
  audit's working files and the two bookkeeping records it replaced with this
  page) is a working-tree change on top of `80aca45`.
- The two root reference documents (the curriculum authority and the AI
  development instructions) remain untracked by the project owner's decision,
  and `.freebuff/` is gitignored. The project does not depend on either to run,
  and a fresh clone is complete without them.

## Repository corrections

Two corrections were applied on 2026-09-19 alongside the documentation cleanup.
They are recorded here so the repository state is never inferred from a clean
working tree alone.

- **Missing data placeholders (resolved).** `data/interim/.gitkeep` and
  `data/external/.gitkeep` were absent from the repository, so
  `tests/test_phase0_project_setup.py::test_data_directory_placeholders_exist`
  failed at `HEAD` even though `README.md`, `.gitignore` and the test itself all
  declare those directories tracked. Both placeholders were restored and the
  suite is green. Recorded as **ENV-03** in `phase-17/audit-findings.md`.
- **Documentation consolidation (no project code affected).** The running phase
  state log and the file update register were replaced by this page; 11
  superseded per-phase plan documents, 12 audit process records and 88 raw
  command captures were removed; the retained audit material moved to
  `phase-17/independent-verification.md`, `phase-17/audit-findings.md` and
  `reproducibility-runbook.md`; and the per-phase re-audit records were
  consolidated into `phase-17/re-audit-record.md`. The findings that mattered
  were carried into `audit-findings.md`; the per-file documentation review that
  produced them survives only in Git history, as its own Provenance section
  states.
