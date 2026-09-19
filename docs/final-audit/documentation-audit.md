# Documentation Audit

All 124 documentation files enumerated (see `baseline-inventory.tsv`). Key documents read in full or targeted-read: `README.md`, `docs/phase-0/project-state.md` (1,206 lines — the master phase-by-phase record), all phase plans/results/checklists, `deploy/README.md`, Tableau documents, `docs/project-file-update-register.md`.

## Documented command map (the "Expected" side for execution)

| Phase | Documented command (repo root) | Expected outcome (documented) |
|---|---|---|
| 0 | no script — setup contract | `tests/test_phase0_project_setup.py` — 6 tests |
| 1 | no script — planning documents | `tests/test_phase1_business_understanding.py` — 5 tests |
| 2 | `python scripts/inspect_raw_data.py` | completes over full raw dataset; 8 raw files recorded |
| 3 | `python scripts/create_spreadsheet_analysis.py` | workbook with 761 daily / 4 store / 28,182 item records |
| 4 | `python scripts/create_sqlite_database.py`, then `python scripts/run_sql_analysis.py` | 1.06 GB DB; 18 queries executed; stores 4, catalog 219,810, sales 7,432,685, markdowns 8,979, price_history 698,626 |
| 5 | `python scripts/clean_retail_data.py` | 7,432,685 read → 7,431,026 written; ~113 s |
| 6 | `python scripts/integrate_retail_data.py` | 7,431,026 rows, 34 cols; ~350 s; total demand 41,949,529.910; revenue 5,659,219,309.90 |
| 7 | `python scripts/exploratory_data_analysis.py` | exact correlation (price coeff -0.04442); ~61 s |
| 8 | `python scripts/statistical_analytical_analysis.py` | streaming accumulators; promotion comparison presence-based; HAC trend; ~41 s |
| 9 | `python scripts/prepare_time_series.py` | quality report 15 checks; splits train→2024-02-10 / val→2024-06-03 / test→2024-09-26; ~232 s |
| 10 | `python scripts/feature_engineering.py` | quality report 14 checks; 16 features; lag_1 missing 58,022 |
| 11 | `python scripts/forecasting_models.py` | quality report 24 checks; naive/seasonal-naive/ARIMA(1,1,1) per store; predictions 1,368 rows 2024-02-11→2024-06-03 |
| 12 | `python scripts/evaluate_and_tune_models.py` | quality report 30 checks; 9 candidates × 4 stores; CV-only selection; predictions 2,976 rows max date 2024-06-03 |
| 13 | `python scripts/forecasting_inventory_insights.py` | quality report 43 checks; densified 1,656 synthetic 1; mean bias 1,409.941; test_period_excluded = 2024-02-10 |
| 14 | `Rscript r/r_analysis.R`; `Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(),'data','analysis','r'))"` | 91/91 quality checks; findings + environment CSV + plots + HTML report |
| 15 | `python scripts/create_visualizations.py`; `python scripts/sync_tableau_workbook_schema.py --check` | 55/55 checks; 4 figures; manifest digests; "Workbook schema already matches its sources." |
| 16 | `python -m streamlit run app/streamlit_app.py --server.port 8523 --server.headless true` | HTTP 200; artifact resolution env → data/analysis → deploy/artifacts |
| 17 | full suite `python -m pytest -q` | 530 passed (self-audit claim) |

Per-phase pytest counts as the phase results documents state them: P0 6, P1 5, P2 6, P3 10, P4 11, P5 19, P6 22, P7 34, P8 46, P9 37, P10 32, P11 52, P12 64, P13 78, P14 36, P15 32, P16 36 — documented sum **526** against an executed **530**. **Corrected 2026-09-19:** the four-test difference is two stale counts — Phase 3 (10 documented, 12 executed) and Phase 6 (22 documented, 24 executed). The master record additionally carried Phase 9 as 36 (executes 37) and Phase 10 as 31 (executes 32), making its own sum 524. The first pass reported this as a single stale figure (528 vs 530); that was incorrect. See `docs-file-review-2026-09-19.md`.

## Claims requiring execution evidence (extracted from docs)

1. Pipeline determinism: P6 output "byte-identical on re-execution"; P11 "byte-identical to the pre-audit run" — re-execution must reproduce or the drift must be quantified.
2. Quality gates: P9 15, P10 14, P11 24, P12 30, P13 43, P14 91, P15 55 checks, all `passed=True`.
3. Cross-phase reconciliation constants (row counts, demand, revenue, dates) repeat consistently across P2/P4/P5/P6/P7/P8/P9/P10 docs.
4. No leakage: selection uses training-period CV only; test period (2024-06-04→2024-09-26) never read by tuning; P13 `test_period_excluded` check.
5. Raw data immutability: all phase docs claim raw data never modified — verified via baseline vs post-execution SHA-256.
6. Application resolves artifacts env → `data/analysis/` → `deploy/artifacts/` without retraining.
7. Tableau Public dashboard URL resolves (HTTP 200 claimed on 2026-09-19 — re-verified in the link audit).

## Documentation findings (updated as phases execute)

- DOC-01 (Informational, resolved): per-phase test-count sum (526) vs executed suite total (530) — two stale counts (Phase 3, Phase 6) plus two in the master record (Phase 9, Phase 10). All corrected 2026-09-19; see `docs-file-review-2026-09-19.md`.
- (further findings appended per phase)
