# Final Audit Report — Retail Demand Forecasting (Phases 0–17)

Independent, evidence-based audit, validation and from-scratch re-execution performed 2026-09-19. Every statement below is tied to an executed command, a test result, an artifact inspection or a checksum, all preserved under `docs/final-audit/`.

## Executive Summary

The project is **correct, complete, consistent, reproducible, executable, tested, documented, structurally sound and appropriate for an internship/portfolio deliverable**. The entire Phase 0→17 pipeline was re-executed from the preserved raw inputs and reproduced its documented results exactly.

- 18/18 phases audited and executed; **530/530 tests passed** (baseline and after full re-execution).
- All six machine-checked quality gates passed: **272/272 checks** (15+14+24+30+43+91+55).
- **Raw data unmodified** (9/9 checksums unchanged); **all processed datasets byte-identical** (8/8); 90/94 analysis outputs byte-identical, the other 4 differing only by embedded generation timestamps.
- The Streamlit application started headless and answered **HTTP 200**; the R workflow produced **91/91 checks** and rendered its report.
- **No project file was modified by the audit.** A follow-up per-file review of all 220 files under `docs/` (2026-09-19) found documentation drift that this report originally under-reported: four stale per-phase test counts, an artifact byte-size error, Phase 9's full-suite total, missing master-record entries and two stale Git/structural figures. All are now corrected — see `docs-file-review-2026-09-19.md` and `findings.md` DOC-01/DOC-02/DOC-06–DOC-12.
- Remaining open items are pre-existing, honestly documented limitations (hosted deployment, Tableau refresh, reserved test-period evaluation) — none are defects.

## Project Objective

Forecast daily store-item retail demand from historical sales with promotions, prices and catalog data, then translate forecasts into inventory-oriented insights; demonstrate the full analytical lifecycle (Ask → Prepare → Process → Analyze → Share → Act) with Python as the primary implementation and SQL, spreadsheets, R and Tableau as supporting tracks.

## Project Scope

In scope: raw-data understanding; cleaning and integration; EDA and statistics; time-series preparation and feature engineering; classical forecasting (naive, seasonal-naive, ARIMA) plus a feature-based gradient-boosting candidate with cross-validated selection; validation metrics (RMSE, MAPE); inventory scenarios; R cross-verification; static visualizations and a Tableau workbook; a local Streamlit application; a pytest suite. Out of scope (correctly): production infrastructure, hosted orchestration, monitoring, feature stores, distributed processing.

## Internship Scope Assessment

**Appropriate.** The technology set (pandas, scikit-learn/statsmodels, SQLite, openpyxl, R/knitr, Tableau, Streamlit, pytest) is proportionate and educational. No Kubernetes, microservices, cloud infrastructure, MLOps or enterprise patterns were introduced. Complexity present is justified by the dataset (7.43 M rows → chunked streaming in Phases 5/6/9/10; streaming accumulators in Phase 8). Methodological rigour (time-aware splits, CV-only selection, leakage guards, zero-safe MAPE, quality gates) is professional without being over-engineered. The project is **credible and technically defensible for an internship**, with breadth (SQL/R/spreadsheets/Tableau) supported by real evidence rather than decorative duplication.

## Architecture Summary

Single coherent repository: `scripts/` (15 phase-owned pipeline scripts) → `data/{raw,processed,analysis}` → `app/` (Streamlit) reading seven compact artifacts; parallel evidence tracks `sql/`, `r/`, `tableau/`, plus committed `deploy/artifacts/` so a repository build can start the app; `tests/` (18 modules); `docs/phase-0…17/`. Each script is runnable from the repository root with no hardcoded absolute paths (asserted by tests).

## Data Lineage Summary

Raw (8 CSVs, 824 MB) → inspect (P2) → clean `sales_clean.csv` (P5, 7,431,026 rows) → integrate `integrated_retail_data.csv` (P6, 34 cols, 1,283,859,491 B) → EDA (P7) / statistics (P8) → prepare `time_series_daily.csv` (P9, chronological train/val/test) → features `feature_engineered_daily.csv` (P10, 16 features) → forecast (P11) → tune/select (P12, CV-only) → inventory insights (P13) → R verification (P14) / visualizations + Tableau (P15) → application (P16) → suite (P17). Every transformation is script-owned and each output reconciles with its input (rows, quantity 41,949,529.910, revenue 5,659,219,309.90, dates 2022-08-28 → 2024-09-26).

## Phase Summary

See `phase-status.md` for the full table. Highlights with verified figures: P5 7,432,685→7,431,026; P6 7,431,026 rows/28,180 items; P9 splits 4,315,416 / 1,548,957 / 1,566,653; P11 seasonal-naive mean RMSE 3,223.063; P12 mean validation RMSE 3,079.4286 with stores 1–3 `feature_gbm`, store 4 `seasonal_naive`; P13 densified 1,656 / synthetic 1, mean bias 1,409.941; P14 91/91; P15 55/55; P16 HTTP 200; P17 530/530.

## Documentation Findings

Documentation is extensive (220 files under `docs/`), evidence-tied, and — after the 2026-09-19 per-file review and its corrections — internally consistent. The review found four stale per-phase test counts (Phase 3 10→12, Phase 6 22→24, master-record Phase 9 36→37 and Phase 10 31→32), an artifact byte-size error (1,283,886,539 → 1,283,859,491), Phase 9's full-suite total (280 → the arithmetically verified 258), four missing master-record test entries, the tracked-file count (178 → 183) and a stale HEAD record. All are corrected. Phase 4's documented 11 was confirmed correct, and documentation-vs-implementation otherwise agrees, including honest disclosure of limitations. The two owner reference documents remain intentionally untracked (recorded, not a project dependency).

## Code Findings

All 15 scripts, 5 app modules, both R sources and 18 test modules were inspected/executed. No correctness defect was found: no path bugs, no join/cardinality faults (P6 byte-identical re-execution proves row-multiplication-free integration), no aggregation error (totals reconcile across phases), no metric error (P11/P12/P13 reconcile and R reproduces them with `yardstick`). No dead code or unsupported functionality was identified. Code is readable, modular and documented.

## Data Findings

Raw data is immutable (9/9 checksums unchanged). Cleaning removes 1,659 rows (negative quantity/price, invalid dates, duplicates) and retains 36,585 rows without a catalog match — reconciled across P4/P5/P6. The 2023-12 level shift is diagnosed as a coverage/assortment change (store 4 enters 2023-12-13). No impossible or corrupt values were found in the analysis artifacts.

## Artifact Findings

124 artifacts reconciled against baseline: 120 identical, 4 differ only by generation timestamps (XLSX ZIP metadata; R findings/environment/report timestamps) — see `artifact-validation.md`. All documented artifacts exist; none missing; no orphaned artifacts. The `deploy/artifacts/` bundle is a deliberate, SHA-256-reconciled duplicate of seven analysis CSVs.

## Testing Findings

530 tests pass at baseline and after full re-execution. Coverage is meaningful: setup contracts, each pipeline stage, model validation (leakage guards, folds, selection rule), the R workflow as a subprocess with twelve deliberate-failure paths, the visualization workflow with six failure paths, and application behaviour including a headless HTTP startup test. No test was removed or altered. Test-cost is dominated by the R subprocess suite (~4 min), which is proportionate to its coverage.

## Performance Findings

Full re-execution ≈55 minutes of pipeline compute. Observed vs documented: P6 295 s (documented 350 s), P9 220 s (~232 s), P5 142 s (~113 s) — all same-order. One anomaly: `run_sql_analysis.py` took 22 m 06 s versus ~2 min historically, with correct outputs and passing tests; cause unproven (cold cache/load) and recorded as PERF-01. No memory or disk pressure. No low-risk optimization would materially improve correctness — none proposed (internship scope).

## Reproducibility Findings

**Verified by reconstruction.** Running every documented command from Phase 0 onward reproduced the documented results, with processed datasets byte-identical and raw data untouched. The runbook (`runbook.md`) documents prerequisites, dataset acquisition, commands, expected outputs/times, verification and common issues. Residual caveats: generated data is Git-excluded (the committed deploy bundle covers application startup); the two reference documents are untracked by owner decision; and hosted deployment requires owner authorisation.

## Link Audit

Four documented external links, all HTTP 200 on 2026-09-19: the Tableau Public dashboard (and its canonical author URL) and the Kaggle dataset source/download endpoints. No dead or undocumented links. See `link-audit.md`.

## Missing Components

None on the documented critical path. Everything the documentation names exists and executed.

## Incorrect Components

None in code, tests, configuration or data. The documentation inaccuracies found by the follow-up review — four stale test counts, one artifact byte size, Phase 9's full-suite total, four missing master-record entries, the tracked-file count and the HEAD record — are listed in `findings.md` and are all corrected.

## Unused Components

None identified among tracked files.

## Duplicate Components

Only the intentional `deploy/artifacts/` bundle (SHA-256-reconciled by test) — justified, not accidental duplication.

## Documentation vs Implementation Discrepancies

| ID | Documentation | Implementation | Impact | Resolution | Status |
|---|---|---|---|---|---|
| DOC-01/02 | Phase 3 "10 tests", Phase 6 "22 tests" | 12 and 24 execute | Low (understates coverage) | Corrected in the phase records and the master record | Resolved 2026-09-19 |
| DOC-03 | Phase 4 "11 tests" | 11 (3+8) execute | None | Documentation verified correct | Retracted |
| DOC-06 | Integrated dataset "1,283,886,539 bytes" | 1,283,859,491 bytes on disk | Low (wrong figure) | Corrected in both documents | Resolved 2026-09-19 |
| DOC-07 | Phase 9 full suite "280 tests", phases add "48" | Verified 258 and 49 | Low (internally contradictory) | Corrected with an at-the-time label | Resolved 2026-09-19 |
| DOC-08/09/10/12 | Master-record Tests section, tracked file count, HEAD record, register status token | 4 missing entries; 183 tracked files; HEAD `e5a750f` | Low/Medium (master record) | All corrected | Resolved 2026-09-19 |

## Data Integrity Findings

Strong: raw immutability proven; deterministic byte-identical processing; cross-phase totals reconcile exactly; catalog gaps and coverage shifts explicitly documented rather than hidden.

## Leakage Findings

**No leakage found.** Time-aware chronological splits with non-overlap; Phase 12 selection uses training-period cross-validation only; predictions stop at the validation boundary (2024-06-03); Phase 13 asserts `test_period_excluded` (2024-02-10); lag/rolling features respect temporal boundaries (test-asserted). The reserved final test-period evaluation is *unused* rather than misused.

## Regression Findings

No code changed, so no change-driven regression was required. Reconstruction regression is green: each downstream phase reconciled to its upstream output, and both full-suite runs passed 530/530. See `regression-log.md`.

## Internship-Scope Findings

Scope is proportionate; no enterprise complexity was added; breadth is genuinely evidenced (SQL 18 queries, R 91 checks, spreadsheets, Tableau, Streamlit). Recommendations that would exceed internship scope are listed below as future work rather than implemented.

## Changes Made

**None to project code, tests, configuration or data.** Audit-only additions live under `docs/final-audit/` and cannot affect the project (`testpaths=["tests"]`; not importable from project code). The final 530-test run post-dates those additions.

## Changes Not Made and Why

- **Documentation corrections were originally deferred** (Phase 3/Phase 6 test counts) — reconsidered and applied on 2026-09-19 together with the further findings from the per-file review.
- **Explicit date format in Phase 5 parsing** — removes a benign pandas warning but risks changing parsing behaviour for no correctness gain; not applied.
- **Tableau absolute-path parameterisation / dashboard refresh** — requires Tableau Desktop; out of command-line scope.
- **Reserved test-period evaluation** — a new phase beyond the current internship scope; recommended as future work.
- **Production infrastructure (hosting, monitoring, CI/CD, MLOps)** — deliberately avoided per internship scope.

## Remaining Issues

1. Hosted Streamlit deployment unexecuted (owner authorisation; no public URL claimed).
2. Tableau Public dashboard reflects the 8 September 2026 extract; refresh needs Tableau Desktop.
3. No human usability/accessibility review of the rendered interface.
4. Reserved final test-period evaluation has no owning phase.
5. RStudio installed but unevidenced (workflow runs via `Rscript`).
6. Tableau workbook uses an absolute local data-source path; one worksheet's fixed axis starts slightly below zero.
7. Documentation drift (DOC-01/02, DOC-06–DOC-12) — **all corrected 2026-09-19** (see `docs-file-review-2026-09-19.md`).
8. `run_sql_analysis.py` one-off 22-minute runtime (PERF-01), outputs correct.

All eight are recorded, not hidden; none is a correctness or integrity defect.

## Final Execution Results

18/18 phases executed with exit 0; 6/6 quality gates fully passed; application HTTP 200; complete stdout/stderr preserved under `docs/final-audit/execution/phase-00…17/`. Raw data unmodified; 120/124 artifacts byte-identical, 4 timestamp-only.

## Final Test Results

| Run | Result |
|---|---|
| Baseline full suite | 530 passed, 1 warning, 223.58 s |
| Final full suite (after re-execution) | 530 passed, 1 warning, 281.66 s |
| Per-phase modules | all passed (module totals sum to 530) |
| Failures / skips | 0 / 0 |

## Final Project Status

**PASSED — complete and audit-safe as an internship/portfolio deliverable.** The project is correct, reproducible (verified by from-scratch re-execution), leaki-free, internally consistent, well tested and honestly documented. Recommended follow-ups (outside internship scope): the reserved test-period evaluation; a Tableau dashboard refresh and connection parameterisation; a human usability/accessibility pass; and optional hosted deployment. The documentation corrections this report originally deferred were applied on 2026-09-19.
