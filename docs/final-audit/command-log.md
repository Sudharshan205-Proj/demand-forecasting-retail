# Command Log

All commands run from the repository root (Git Bash) on 2026-09-19 unless stated. Evidence paths are relative to `docs/final-audit/`.

| ID | Phase | Command | Purpose | Result | Evidence |
|---|---|---|---|---|---|
| CMD-B01 | Base | `.venv/Scripts/python.exe -m pip list --format=freeze` | Installed package verification | exit 0; all 10 pins match `requirements.txt` | `execution/baseline-pip-freeze.txt` |
| CMD-B02 | Base | `python -m py_compile scripts/*.py app/*.py` | Static compile check | exit 0 (20 modules) | `execution/baseline-evidence.md` |
| CMD-B03 | Base | `python scripts/sync_tableau_workbook_schema.py --check` | Workbook schema drift check | exit 0; "already matches its sources" | `execution/Baseline-evidence.md` |
| CMD-B04 | Base | `audit_baseline_helper.py` | File inventory + baseline SHA-256 manifest | exit 0; 124 artifacts hashed, 308 files classified | `execution/baseline-{checksums,inventory}.tsv` |
| CMD-B05 | Base | `pytest -q` | Baseline full suite | exit 0; **530 passed**, 1 warning, 223.58 s | `execution/baseline-pytest-full.txt` |
| CMD-P0-01 | 0 | `pytest tests/test_phase0_project_setup.py` | Setup contract | exit 0 (6 tests) | `execution/phase-00/command-001.txt` |
| CMD-P1-01 | 1 | `pytest tests/test_phase1_business_understanding.py` | Planning docs | exit 0 (5 tests) | `execution/phase-01/command-001.txt` |
| CMD-P2-01 | 2 | `python scripts/inspect_raw_data.py` | Raw dataset inspection | exit 0; 210 output lines; empty stderr | `execution/phase-02/command-001-*` |
| CMD-P2-02 | 2 | `pytest tests/test_inspect_raw_data.py` | Phase 2 tests | exit 0; 6 passed | `execution/phase-02/command-002.txt` |
| CMD-P3-01 | 3 | `python scripts/create_spreadsheet_analysis.py` | Regenerate workbook | exit 0; 761/4/28,182 records | `execution/phase-03/command-001-*` |
| CMD-P3-02 | 3 | `pytest tests/test_create_spreadsheet_analysis.py` | Phase 3 tests | exit 0; 12 passed | `execution/phase-03/command-002.txt` |
| CMD-P4-01 | 4 | `python scripts/create_sqlite_database.py` | Rebuild DB | exit 0; counts as documented | `execution/phase-04/command-001-*` |
| CMD-P4-02 | 4 | `python scripts/run_sql_analysis.py` | Execute 18 queries | exit 0 after 22 m 06 s; 18/18 result files | `execution/phase-04/command-002-*` |
| CMD-P4-03 | 4 | `pytest tests/test_sql_analysis.py` | Phase 4 tests | exit 0; 8 passed | `execution/phase-04/command-003.txt` |
| CMD-P4-04 | 4 | sqlite3 spot-check (rows/dates/totals/stores) | Independent data verification | exit 0; 7,432,685 rows; dates correct; raw totals below cleaned totals (negative rows removed) | `execution/phase-04/command-004-spotcheck.txt` |
| CMD-P5-01 | 5 | `python scripts/clean_retail_data.py` | Cleaning | exit 0; 7,432,685→7,431,026; 141.6 s | `execution/phase-05/command-001-*` |
| CMD-P5-02 | 5 | `pytest tests/test_clean_retail_data.py` | Phase 5 tests | exit 0; 19 passed | `execution/phase-05/command-002.txt` |
| CMD-P5-03 | 5 | SHA-256 `sales_clean.csv` | Determinism | identical to baseline | `execution/baseline-checksums.tsv` |
| CMD-P6-01 | 6 | `python scripts/integrate_retail_data.py` | Integration | exit 0; 7,431,026 rows; 295.2 s | `execution/phase-06/command-001-*` |
| CMD-P6-02 | 6 | `pytest tests/test_integrate_retail_data.py` | Phase 6 tests | exit 0; 24 passed | `execution/phase-06/command-002.txt` |
| CMD-P6-03 | 6 | SHA-256 `integrated_retail_data.csv` | Determinism | identical to baseline (1,283,859,491 B) | `execution/baseline-checksums.tsv` |
| CMD-P7-01 | 7 | `python scripts/exploratory_data_analysis.py` | EDA | exit 0; 82.2 s | `execution/phase-07/command-001-*` |
| CMD-P7-02 | 7 | `pytest tests/test_exploratory_data_analysis.py` | Phase 7 tests | exit 0; 34 passed | `execution/phase-07/command-002.txt` |
| CMD-P8-01 | 8 | `python scripts/statistical_analytical_analysis.py` | Statistics | exit 0; 56.3 s | `execution/phase-08/command-001-*` |
| CMD-P8-02 | 8 | `pytest tests/test_statistical_analytical_analysis.py` | Phase 8 tests | exit 0; 46 passed | `execution/phase-08/command-002.txt` |
| CMD-P9-01 | 9 | `python scripts/prepare_time_series.py` | Time-series prep | exit 0; 219.8 s | `execution/phase-09/command-001-*` |
| CMD-P9-02 | 9 | `pytest tests/test_prepare_time_series.py` | Phase 9 tests | exit 0; 37 passed | `execution/phase-09/command-002.txt` |
| CMD-P9-03 | 9 | quality report + SHA-256 | Gate + determinism | 15/15 passed; byte-identical | `execution/phase-09/` |
| CMD-P10-01 | 10 | `python scripts/feature_engineering.py` | Features | exit 0; 429.8 s | `execution/phase-10/command-001-*` |
| CMD-P10-02 | 10 | `pytest tests/test_feature_engineering.py` | Phase 10 tests | exit 0; 32 passed | `execution/phase-10/command-002.txt` |
| CMD-P11-01 | 11 | `python scripts/forecasting_models.py` | Forecasting | exit 0; 51.6 s | `execution/phase-11/command-001-*` |
| CMD-P11-02 | 11 | `pytest tests/test_forecasting_models.py` | Phase 11 tests | exit 0; 52 passed | `execution/phase-11/command-002.txt` |
| CMD-P12-01 | 12 | `python scripts/evaluate_and_tune_models.py` | Evaluation/tuning | exit 0; 58.6 s | `execution/phase-12/command-001-*` |
| CMD-P12-02 | 12 | `pytest tests/test_evaluate_and_tune_models.py` | Phase 12 tests | exit 0; 64 passed | `execution/phase-12/command-002.txt` |
| CMD-P13-01 | 13 | `python scripts/forecasting_inventory_insights.py` | Inventory insights | exit 0; 21.5 s | `execution/phase-13/command-001-*` |
| CMD-P13-02 | 13 | `pytest tests/test_forecasting_inventory_insights.py` | Phase 13 tests | exit 0; 78 passed | `execution/phase-13/command-002.txt` |
| CMD-P14-01 | 14 | `Rscript r/r_analysis.R` | R analysis | exit 0; 91/91 checks | `execution/phase-14/command-001-*` |
| CMD-P14-02 | 14 | `Rscript -e "rmarkdown::render(...)"` | R Markdown report | exit 0; 43 chunks; HTML created | `execution/phase-14/command-002-*` |
| CMD-P14-03 | 14 | `pytest tests/test_r_analysis.py` | Phase 14 tests | exit 0; 36 passed; 246.95 s | `execution/phase-14/command-003.txt` |
| CMD-P15-01 | 15 | `python scripts/create_visualizations.py` | Figures + gate | exit 0; 55/55 checks; 8.9 s | `execution/phase-15/command-001-*` |
| CMD-P15-02 | 15 | `sync_tableau_workbook_schema.py --check` | Schema | exit 0; matches | `execution/phase-15/command-002-stdout.txt` |
| CMD-P15-03 | 15 | `pytest tests/test_create_visualizations.py` | Phase 15 tests | exit 0; 32 passed | `execution/phase-15/command-003.txt` |
| CMD-P15-04 | 15 | manifest re-hash (auditor) | Independent verification | 4/4 figures byte+digest match | `execution/phase-15/command-004-manifest-check.txt` |
| CMD-P16-01 | 16 | `streamlit run app/streamlit_app.py --server.port 8523 --server.headless true` | App startup | listening on 8523; PID 21852 | `execution/phase-16/command-001-*` |
| CMD-P16-02 | 16 | `curl http://127.0.0.1:8523` + `/_stcore/health` | HTTP verification | both **HTTP 200** | `execution/phase-16/command-002-http-check.txt`, `homepage.html` |
| CMD-P16-03 | 16 | `pytest tests/test_application.py` | Phase 16 tests | exit 0; 36 passed | `execution/phase-16/command-003.txt` |
| CMD-P17-01 | 17 | `pytest -q` | Final full suite | exit 0; **530 passed**, 281.66 s | `execution/phase-17/command-001-pytest-full.txt` |
| CMD-P17-02 | 17 | `compare_checksums.py` | Artifact drift vs baseline | 120/124 identical; 4 timestamp-only differences | `execution/phase-17/artifact-drift-*` |
| CMD-L01 | Link | `curl -sL -o /dev/null -w "%{http_code}"` × 4 URLs | Link audit | all **200** | `execution/link-checks.txt` |

## Audit-tooling mishaps (recorded for transparency, not project defects)

1. `audit_baseline_helper.py` first run failed (exit 1) on a wrong `dirname` depth (wrote to `docs/docs/...`); fixed in the helper, re-run.
2. `run_sql_analysis.py` first attempt was killed by the audit harness's 600 s limit (queries 1–9 had completed; no corruption — each CSV is fully rewritten per query). A `nohup` background retry died with its shell (Git Bash child kill). The successful run used an unbounded blocking timeout.
3. Manifest re-hash first attempt used the `figure` basename column instead of `path` (FileNotFoundError); corrected and re-run.
4. Streamlit launch first attempt failed on bash/`$p.Id` quoting; replaced with `start_app.ps1`.
5. `code_search` (ripgrep) became unavailable mid-audit; link/command extraction fell back to `grep`.
