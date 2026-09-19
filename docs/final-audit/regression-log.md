# Regression Log

Because the re-execution regenerated every pipeline artifact in dependency order, regression evidence consists of (a) per-phase test modules, (b) downstream reconciliation, and (c) the full-suite runs at baseline and after all changes.

## Change-driven regressions

**No project code files were modified by this audit.** Consequently no change→downstream regression chain was triggered. The regression evidence below is the *reconstruction* regression: each phase's output was validated against the next phase's inputs.

| Step | Change | Upstream | Downstream | Verification | Result |
|---|---|---|---|---|---|
| — | none (no modifications) | — | — | — | NOT APPLICABLE |

## Reconstruction regression chain (Phase 5 → 13)

| Producing phase | Upstream artifact | Downstream phase | Downstream check | Result |
|---|---|---|---|---|
| 5 cleaning | `sales_clean.csv` (byte-identical) | 6 integration | 7,431,026 rows consumed; integration byte-identical | PASS |
| 6 integration | `integrated_retail_data.csv` (byte-identical) | 7 EDA, 8 stats, 9 prep | rows/demand/revenue reconciled exactly (7,431,026 / 41,949,529.910 / 5,659,219,309.900) | PASS |
| 9 preparation | `time_series_daily.csv` (byte-identical) | 10 features | split totals reconcile exactly (4,315,416 / 1,548,957 / 1,566,653) | PASS |
| 10 features | `feature_engineered_daily.csv` (byte-identical) | 11 forecasting, 12 tuning | demand target and features consumed; 16 features; splits preserved | PASS |
| 11 forecasting | metrics + predictions | 12 tuning | Phase 11 mean validation RMSE 3,223.0630 is the Phase 12 baseline; store 4 forecast reproduced exactly (6,063.055906) | PASS |
| 12 tuning | selected configs + `tuned_validation_results.csv` | 13 insights, 14 R, 15 viz, 16 app | store selection [1,2,3,4]; mean 3,079.4286; bias 1,409.941; figures' source rows 4/4/36/13 match | PASS |
| 13 insights | inventory CSVs | 14 R, 15 viz, 16 app | R 91/91 checks reconcile metrics; viz consumes scenarios (36 rows) and insights (13 rows) | PASS |
| 14 R | quality report | 16 app (deploy bundle) | deploy bundle SHA-256 reconciliation test passes | PASS |
| 15 viz | manifest | 16 app | manifest digests re-verified against files | PASS |
| 16 app | runtime | 17 suite | `test_application.py` 36 passed | PASS |

## Test-suite regression runs

| Run | Command | Result |
|---|---|---|
| Baseline (before any execution) | `pytest -q` | 530 passed, 1 warning, 223.58 s |
| Phase 17 final (after full re-execution) | `pytest -q` | 530 passed, 1 warning, 281.66 s |

No test regressed: zero failures at every per-phase module run and at both full-suite runs. Per-module totals are recorded in `phase-status.md`; their sum (530) matches the two full-suite runs.

## Artifact regression

| Artifact class | Regression result |
|---|---|
| raw data (9) | 9/9 byte-identical (never modified) |
| processed datasets (8) | 8/8 byte-identical |
| analysis outputs (94) | 90/94 byte-identical; 4 differ only by embedded generation timestamp (see `artifact-validation.md`) |
| deployment bundle (8), Tableau (3), R sources (2) | all byte-identical |
