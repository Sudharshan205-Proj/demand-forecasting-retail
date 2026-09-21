# Project Status

**Demand Forecasting for Retail** is complete. All 18 phases (Phase 0 → Phase
17) are finished, the full automated test suite passes, and the application and
dashboard are published. This page is the one-page state of the finished
project; the detail lives in the phase folders.

## Project at a glance

| | |
|---|---|
| Project | Demand Forecasting for Retail — retail demand forecasting and inventory planning |
| Objective | Forecast daily store-level demand from historical sales and translate the forecasts into conditional inventory-planning insights |
| Lifecycle | Ask → Prepare → Process → Analyze → Share → Act |
| Dataset | Kaggle retail sales forecasting dataset (CC BY-NC-SA 4.0); 2022-08-28 → 2024-09-26; 4 stores; 7,432,685 raw sales rows |
| Models | Naive, seasonal-naive, ARIMA(1,1,1) and a deterministic feature-based gradient-boosting candidate |
| Evaluation | Chronological train/validation/test splits; RMSE and MAPE |
| Application | Streamlit decision-support app, live at <https://demand-forecasting-retail-internship.streamlit.app/> |
| Dashboard | Tableau Public, published at <https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning> |
| Tests | **532 passing across 18 modules** |
| Run-gating quality checks | **272/272** across the seven run-gating reports |

## Phase status

| Phase | Name | Delivered |
|---|---|---|
| 0 | Project Setup & Curriculum Mapping | Repository contract, environment, architecture, curriculum mapping | 
| 1 | Business Understanding & Planning | Business problem, questions, stakeholders, KPIs, requirements | 
| 2 | Data Acquisition & Data Understanding | Data inventory, dictionary, source assessment, ethics | 
| 3 | Spreadsheet-Based Analysis | Excel workbook with daily, store and item analysis | 
| 4 | SQL & Database Analysis | SQLite schema and 18 analytical queries | 
| 5 | Data Cleaning & Quality Assurance | Cleaned sales dataset and quality report | 
| 6 | Data Integration | 34-column integrated matrix across eight sources | 
| 7 | Exploratory Data Analysis | Demand patterns, concentration, correlation, figures | 
| 8 | Statistical & Analytical Analysis | Trend, promotion/price relationships, level-shift diagnosis | 
| 9 | Time-Series Preparation | Chronological train/validation/test partitions | 
| 10 | Feature Engineering | 16 leakage-safe features at store-day grain | 
| 11 | Forecasting Models | Naive, seasonal-naive and ARIMA(1,1,1) per store | 
| 12 | Model Evaluation & Tuning | Cross-validated candidate evaluation and selection | 
| 13 | Forecasting & Inventory Insights | Bias measurement and inventory scenarios | 
| 14 | R Analysis | Independent cross-language re-analysis and R Markdown report | 
| 15 | Visualization & Tableau | Four static figures and the published Tableau workbook | 
| 16 | Application Development & Deployment | Streamlit application and hosted deployment | 
| 17 | Testing, Documentation & Finalization | Consolidated test suite and project documentation | 

## Test suite

`python -m pytest -q` → **532 passed**, run from the repository root with the
virtual environment present.

| Module | Tests | Module | Tests |
|---|---:|---|---:|
| `test_phase0_project_setup.py` | 6 | `test_forecasting_models.py` | 52 |
| `test_phase1_business_understanding.py` | 5 | `test_evaluate_and_tune_models.py` | 64 |
| `test_inspect_raw_data.py` | 6 | `test_forecasting_inventory_insights.py` | 78 |
| `test_create_spreadsheet_analysis.py` | 12 | `test_r_analysis.py` | 36 |
| `test_create_sqlite_database.py` | 3 | `test_create_visualizations.py` | 34 |
| `test_sql_analysis.py` | 8 | `test_application.py` | 36 |
| `test_clean_retail_data.py` | 19 | `test_statistical_analytical_analysis.py` | 46 |
| `test_integrate_retail_data.py` | 24 | `test_prepare_time_series.py` | 37 |
| `test_exploratory_data_analysis.py` | 34 | `test_feature_engineering.py` | 32 |

Phase 4's 11 tests are split across two modules (3 database, 8 SQL). The suite
covers per-phase setup contracts, each pipeline stage, model validation
(leakage guards, fold counts, the selection rule), the R workflow as a
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

Cleaning removes 1,659 rows — the union of 1,160 negative-quantity, 67
negative-price and 1,610 negative-revenue rows, so the implemented rule is
negative quantity, price or revenue; duplicate, invalid-date, missing and
unknown-store rows are all 0. It retains 36,585 raw rows (36,580 on the cleaned
basis) without a catalog match; both are reconciled across Phases 4–6. The
2023-12 level shift is a coverage change: Store 4 enters on 2023-12-13.

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
model. It resolves them in order from the `APP_ANALYSIS_DIR` environment
variable, from `data/analysis/` when that directory is complete, or from the
committed `deploy/artifacts/` bundle — which is why a fresh clone can start the
app. `tests/test_application.py` reconciles every bundled file against pipeline
output by SHA-256 so the two cannot drift.

Per-store model evidence (selected model, configuration, fold count, validation
metrics) is derived from the Phase 12 tables rather than hardcoded.

The instance is live at
<https://demand-forecasting-retail-internship.streamlit.app/> and renders all
four sections from the committed `deploy/artifacts/` bundle. The hosted platform
issues a one-time HTTP 303 session bootstrap through `share.streamlit.io` before
serving the app, so a raw client that discards cookies appears to loop; browsers
follow it transparently, and `?embed=true` is served directly.

The Tableau Public dashboard is published and resolves. It carries six
worksheets — the five chart sheets plus `KPI Summary`, whose tiles read the
extreme values `29,711 units/day`, `0.3801` and `8.14%`.

## Security and configuration

- No secrets are committed. A scan of tracked files returns only empty
  `password=''` Tableau connection attributes and the test file's own pattern
  list; `test_application_source_contains_no_secrets` asserts the application
  source contains none, and the application requires no secrets.
- `.gitignore` excludes `.env`, key material, credentials and generated
  databases, while retaining the `data/raw/` and `data/processed/` placeholders.
- `requirements.txt` is pinned (numpy 2.5.2, pandas 3.0.5, matplotlib 3.11.1,
  scipy 1.18.1, scikit-learn 1.9.0, statsmodels 0.15.0, streamlit 1.63.0,
  openpyxl 3.1.5, jupyter 1.1.1, pytest 9.1.1); `.python-version`,
  `.streamlit/config.toml` and `pyproject.toml` pin the runtime and the pytest
  configuration.
- R, pandoc and package versions are recorded in
  `data/analysis/r/r_environment.csv`.

## Reproducibility

- Every pipeline stage is re-runnable from the documented commands and is
  deterministic; generated artifacts reconcile on rows, quantity and (where
  asserted) bytes. The integrated dataset is byte-identical on re-execution.
- Raw data is immutable; the whole pipeline re-runs without changing a raw byte.
- Random seeds are fixed where stochastic behaviour exists; the feature-based
  candidate is deterministic.
- [`reproducibility-runbook.md`](reproducibility-runbook.md) documents the
  prerequisites, acquisition, per-phase commands, expected outputs and times.

## Key decisions

- **Python is the primary implementation; R is an independent analysis and
  reporting track.** R verifies the forecasting results rather than duplicating
  the pipeline.
- **ARIMA over Prophet/LSTM.** The internship brief lists all three; Prophet and
  LSTM were assessed and deliberately not implemented, and the assessment itself
  is the recorded evidence.
- **The reserved test period stays unused.** It is reserved so it can never
  influence selection or tuning; evaluating it is future scope.
- **Generated data is excluded from Git** except the `deploy/artifacts/` bundle,
  which exists so a repository build can start the application.
- **No trained model is persisted.** Every stage is deterministic and the
  selected configurations are refit from the validated Phase 10–12 artifacts, so
  a serialised model would duplicate reproducible evidence, and the application
  never retrains.
- **No API.** The application is a single-process Streamlit interface reading
  seven committed CSVs; an API would have no consumer.

## Limitations

- No holiday field in the dataset, so holiday analysis is not applicable. The
  requirement was conditional on availability.
- No lead times, costs or stock levels, so inventory scenarios are conditional
  planning inputs rather than operational policy.
- The reserved final test-period evaluation is unevaluated: the forecasts are
  validated on the validation period only.
- Store 4 first appears on 2023-12-13, so its model rests on 60 training days and
  a single cross-validation fold.
- RMSE is scale-bound and rewards the smallest store; cross-store comparison uses
  MAPE.
- The Tableau workbook keeps an absolute local data-source path; the published
  view is insulated from it by its extract.
- Generated data is excluded from Git except the `deploy/artifacts/` bundle.

## Where the evidence lives

| Question | Document |
|---|---|
| How was a phase carried out? | `phase-N/<topic>-methodology.md` |
| What did it produce? | `phase-N/<topic>-results.md` |
| How are its outputs verified? | `phase-N/<topic>-quality-framework.md` |
| Which course topics does it cover? | `phase-N/course-content-coverage.md` |
| What did the phase deliver? | `phase-N/phase-N-checklist.md` |
| Command-by-command reproduction | [`reproducibility-runbook.md`](reproducibility-runbook.md) |
| The project as a case study | [`phase-17/final-case-study.md`](phase-17/final-case-study.md) |
