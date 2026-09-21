# Reproducibility Runbook — Phase 0 → 17

Audience: a developer reproducing the project. Follow the phases in order; each
phase's expected result must hold before proceeding. All commands run from the
repository root.

## 0. Prerequisites

| Requirement | Version verified | Check command |
|---|---|---|
| Operating system | Windows x86-64 (Linux/macOS also work; only path separators differ) | — |
| Python | 3.12.10 | `.venv/Scripts/python.exe --version` (`python3` on POSIX) |
| R | 4.6.1 | `Rscript --version` |
| pandoc | 3.11 | `pandoc --version` (used by R Markdown) |
| SQLite | 3.53.4 | `sqlite3 --version` |
| Git | any | `git --version` |

### Environment setup

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` is pinned (numpy 2.5.2, pandas 3.0.5, matplotlib 3.11.1, scipy
1.18.1, scikit-learn 1.9.0, statsmodels 0.15.0, streamlit 1.63.0, openpyxl 3.1.5,
jupyter 1.1.1, pytest 9.1.1). Analysis output depends on these versions.

### Dataset acquisition

The raw dataset is **not** in Git (data policy). Obtain it from Kaggle:

```bash
curl -L "https://www.kaggle.com/api/v1/datasets/download/svizor/retail-sales-forecasting-data" -o data/raw/retail-sales-forecasting-data.zip
# unzip into data/raw/ so that these 8 files exist:
# sales.csv, stores.csv, catalog.csv, markdowns.csv, price_history.csv,
# discounts_history.csv, online.csv, actual_matrix.csv
```

License: CC BY-NC-SA 4.0 (non-commercial). The raw files are treated as immutable;
never edit them.

Total expected raw size ≈ 824 MB (sales.csv ≈ 379 MB, discounts_history.csv ≈
341 MB).

## Phase execution

Each phase: run the command, confirm the stated expected result, then continue.

### Phase 0 — Project Setup & Curriculum Mapping

- **Prereqs**: repository checked out; virtual environment prepared.
- **Command**: `.venv\Scripts\python.exe -m pytest tests/test_phase0_project_setup.py -q`
- **Expected**: 6 passed.
- **Completion**: repository contract (files, data placeholders, .gitignore, pins,
  pytest config, docs) intact.

### Phase 1 — Business Understanding & Planning

- **Command**: `.venv\Scripts\python.exe -m pytest tests/test_phase1_business_understanding.py -q`
- **Expected**: 5 passed.
- **Completion**: business problem, scope, KPI and forecasting-target documents
  present and consistent.

### Phase 2 — Data Acquisition & Data Understanding

- **Command**: `.venv\Scripts\python.exe scripts/inspect_raw_data.py`
- **Expected**: per-file structure report; dates 2022-08-28 → 2024-09-26; 4 stores;
  0 invalid dates; ~1–2 min.
- **Test**: `.venv\Scripts\python.exe -m pytest tests/test_inspect_raw_data.py -q` → 6 passed.

### Phase 3 — Spreadsheet-Based Analysis

- **Command**: `.venv\Scripts\python.exe scripts/create_spreadsheet_analysis.py`
- **Expected**: "Spreadsheet analysis workbook created successfully."; 761 daily /
  4 store / 28,182 item records → `data/analysis/retail_spreadsheet_analysis.xlsx`.
- **Test**: `.venv\Scripts\python.exe -m pytest tests/test_create_spreadsheet_analysis.py -q` → 12 passed.

### Phase 4 — SQL & Database Analysis

- **Commands**:
  - `.venv\Scripts\python.exe scripts/create_sqlite_database.py` → published row
    counts (stores 4, catalog 219,810, sales 7,432,685, markdowns 8,979,
    price_history 698,626) → `data/analysis/retail_demand.db` (~1.06 GB).
  - `.venv\Scripts\python.exe scripts/run_sql_analysis.py` → "Generated 18 result
    files" → `data/analysis/sql_results/query_1..18.csv`. **Allow up to ~25
    minutes** (observed 22 m 06 s; do not interrupt a slow run).
- **Tests**: `tests/test_create_sqlite_database.py` (3) + `tests/test_sql_analysis.py` (8) → 11 passed.
- **Completion**: row counts match Phase 2 facts; 18 result files present.

### Phase 5 — Data Cleaning & Quality Assurance

- **Command**: `.venv\Scripts\python.exe scripts/clean_retail_data.py`
- **Expected** (~2–3 min): Rows read 7,432,685 → Rows written 7,431,026; Unmatched
  catalog rows 36,585; dates 2022-08-28 → 2024-09-26.
- **Test**: `tests/test_clean_retail_data.py` → 19 passed.

### Phase 6 — Data Integration

- **Command**: `.venv\Scripts\python.exe scripts/integrate_retail_data.py`
- **Expected** (~5–6 min): Rows integrated 7,431,026; coverage 2022-08-28 →
  2024-09-26; unique items 28,180; output 1,283,859,491 bytes.
- **Test**: `tests/test_integrate_retail_data.py` → 24 passed.

### Phase 7 — Exploratory Data Analysis

- **Command**: `.venv\Scripts\python.exe scripts/exploratory_data_analysis.py`
- **Expected** (~1–2 min): findings header rows 7,431,026; total quantity
  41,949,529.910; revenue 5,659,219,309.900; price/quantity correlation
  −0.0444219121; figures in `reports/figures/`.
- **Test**: `tests/test_exploratory_data_analysis.py` → 34 passed.

### Phase 8 — Statistical & Analytical Analysis

- **Command**: `.venv\Scripts\python.exe scripts/statistical_analytical_analysis.py`
- **Expected** (~1 min): summary, findings and quality report plus the statistical
  figures.
- **Test**: `tests/test_statistical_analytical_analysis.py` → 46 passed.

### Phase 9 — Time-Series Preparation

- **Command**: `.venv\Scripts\python.exe scripts/prepare_time_series.py`
- **Expected** (~4 min): `time_series_summary.csv` rows 7,431,026, quantity
  41,949,529.910; splits train 4,315,416 (→2024-02-10), validation 1,548,957
  (→2024-06-03), test 1,566,653 (→2024-09-26); **quality report 15/15 passed** (a
  failing check stops the run).
- **Test**: `tests/test_prepare_time_series.py` → 37 passed.

### Phase 10 — Feature Engineering

- **Command**: `.venv\Scripts\python.exe scripts/feature_engineering.py`
- **Expected** (~7 min): 16 features; **quality report 14/14 passed**;
  `feature_engineered_daily.csv` (887,995,450 bytes, SHA-256
  `7fbe2f8155887b7cd2218237663763b4631a33721b109d162bbc0cad7c58c0e3`).
- **Test**: `tests/test_feature_engineering.py` → 32 passed.

### Phase 11 — Forecasting Models

- **Command**: `.venv\Scripts\python.exe scripts/forecasting_models.py`
- **Expected** (~1 min): naive / seasonal-naive / ARIMA(1,1,1) per store; **quality
  report 24/24 passed**; 1,368 predictions 2024-02-11 → 2024-06-03; seasonal-naive
  best (mean validation RMSE 3,223.063).
- **Test**: `tests/test_forecasting_models.py` → 52 passed.

### Phase 12 — Model Evaluation & Tuning

- **Command**: `.venv\Scripts\python.exe scripts/evaluate_and_tune_models.py`
- **Expected** (~1 min): **quality report 30/30 passed**; selected stores
  [1,2,3,4] with `feature_gbm` ×3 + `seasonal_naive`; mean validation RMSE
  3,079.4286; 2,976 predictions ending 2024-06-03.
- **Test**: `tests/test_evaluate_and_tune_models.py` → 64 passed.

### Phase 13 — Forecasting & Inventory Insights

- **Command**: `.venv\Scripts\python.exe scripts/forecasting_inventory_insights.py`
- **Expected** (~30 s): **quality report 43/43 passed**; densified 1,656 / synthetic
  1; mean bias 1,409.941; `test_period_excluded` actual 2024-02-10.
- **Test**: `tests/test_forecasting_inventory_insights.py` → 78 passed.

### Phase 14 — R Analysis

- **Commands**:
  - `Rscript r/r_analysis.R` → "Quality checks passed: 91 of 91".
  - `Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(), 'data', 'analysis', 'r'))"`
    → HTML report created (21 code chunks; the report refuses to render if the
    gate fails).
- **Expected outputs** in `data/analysis/r/`: quality report, findings, environment
  CSV, scenario CSVs, `plots/`, `r_analysis_report.html`.
- **Test**: `.venv\Scripts\python.exe -m pytest tests/test_r_analysis.py -q` → 36 passed (≈4 min).

### Phase 15 — Visualization & Tableau

- **Commands**:
  - `.venv\Scripts\python.exe scripts/create_visualizations.py` → "55 of 55
    checks"; 4 figures plus the manifest.
  - `.venv\Scripts\python.exe scripts/sync_tableau_workbook_schema.py --check` →
    "Workbook schema already matches its sources." (omit `--check` to repair). Run
    this **after any Tableau save or publish**, because saving rewrites the cached
    schema blocks. The reconciliation is hidden-aware: the workbook's five hidden
    fields are omitted from each source's extract metadata by design, and it never
    re-introduces them.
- **Test**: `tests/test_create_visualizations.py` → 34 passed.
- **Expected**: 4 figure PNGs; `visualization_manifest.csv` digests match the files.
- **Manual step, not scriptable**: the Tableau workbook build and the
  publish-with-extract step, which require Tableau Desktop. The workbook is built
  and published — six worksheets (five chart sheets plus `KPI Summary`), one
  dashboard and the publication stamp — so the dashboard specification is met.

### Phase 16 — Application Development & Deployment

- **Command**: `.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py --server.port 8523 --server.headless true`
- **Expected**: "Local URL: http://localhost:8523"; `curl http://127.0.0.1:8523` →
  HTTP 200; health `/_stcore/health` → HTTP 200. Stop with Ctrl-C.
- **Test**: `tests/test_application.py` → 36 passed.
- **Note**: artifact resolution order is `APP_ANALYSIS_DIR` → `data/analysis/` →
  committed `deploy/artifacts/`. The hosted instance serves the committed bundle.

### Phase 17 — Testing, Documentation & Finalization

- **Command**: `.venv\Scripts\python.exe -m pytest -q`
- **Expected**: **532 passed** (~4–6 min), warning-free.

## Full-pipeline verification checklist

1. Raw filenames, dates and counts match Phase 2.
2. Phase 5/6/9/10 datasets reconcile (rows, quantity, revenue, dates, store/item
   counts).
3. Every run-gating quality report passes all its checks (15, 14, 24, 30, 43, 91,
   55).
4. Phase 11 → Phase 12 mean validation RMSE improves 3,223.0630 → 3,079.4286, and
   the test period is never read (maximum prediction date 2024-06-03).
5. Phase 16 answers HTTP 200 and the deployment bundle reconciles by SHA-256.
6. The full suite passes 532 tests.

## What is verified where

| Report | Checks | Gate |
|---|---|---|
| Phase 9 `time_series_quality_report.csv` | 15 | Yes |
| Phase 10 `feature_engineering_quality_report.csv` | 14 | Yes |
| Phase 11 `forecasting_quality_report.csv` | 24 | Yes |
| Phase 12 `model_evaluation_quality_report.csv` | 30 | Yes |
| Phase 13 `forecasting_inventory_quality_report.csv` | 43 | Yes |
| Phase 14 `r_analysis_quality_report.csv` | 91 | Yes |
| Phase 15 `visualization_quality_report.csv` | 55 | Yes |

Seven run-gating reports, **272 checks** in total.

Phase 8's `statistical_quality_report.csv` is a 56-metric validation report rather
than a run gate, and the Phase 5 and Phase 6 reports are metric/value tables with
no pass/fail column — their checks are asserted by the test suite — so neither is
part of the 272 total.

## Common issues

| Symptom | Cause | Remedy |
|---|---|---|
| `run_sql_analysis.py` appears hung | large full-table scans; observed 22 min | wait; do not interrupt; results are written per query |
| R Markdown render fails at the quality gate | missing or incomplete upstream inputs | run `Rscript r/r_analysis.R` first; the gate is intentional |
| Streamlit port in use | another server on 8523 | use `--server.port <free>` |
| `data/analysis` empty | Git excludes generated data | run Phases 3–15, or use the committed `deploy/artifacts/` bundle |
| Tableau workbook paths broken | absolute local path in `.twb` | re-point the connection (documented limitation) |

## Completion criteria

All 18 phases executed; 532/532 tests pass; the seven run-gating quality reports
pass 272/272 checks; the application answers HTTP 200; artifacts reconcile to the
documented values; no raw file is modified.
