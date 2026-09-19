# Phase 11 — Forecasting Models

## Purpose
Train and evaluate the three documented classical models per store — naive, seasonal-naive(7) and ARIMA(1,1,1) — on the training window, evaluated over the 114-day validation period.

## Starting State
Phase 10 PASSED with byte-identical feature-engineered output.

## Inputs
`data/processed/feature_engineered_daily.csv` (byte-identical to baseline); demand target at store-day grain.

## Commands Executed
- CMD-P11-01: `.venv/Scripts/python.exe scripts/forecasting_models.py` — exit 0, **51.6 s**, empty stderr. Evidence: `command-001-stdout.txt`.
- CMD-P11-02: `pytest tests/test_forecasting_models.py -q -p no:cacheprovider` — exit 0, **52 passed**, 6.58 s. Evidence: `command-002.txt`.
- Verification: quality report = **24 checks, all passed**.

## Tests
52/52 PASSED (matches documented 52). Tests cover configuration, training/validation windows, horizon, baseline reproduction, pooled reconciliation and 13 deliberate-failure paths.

## Artifacts
`data/analysis/forecasting_{model_results,model_configurations,summary,predictions,quality_report}.csv`, `forecasting_findings.txt` regenerated.

## Expected Results
Per docs: seasonal-naive best on mean and pooled RMSE; predictions 1,368 rows 2024-02-11→2024-06-03; horizon 114; RMSE/MAPE per store; no test-period access.

## Actual Results
- Predictions: **1,368 rows, 2024-02-11 → 2024-06-03** — exact match; test period (2024-06-04+) untouched.
- Summary (mean RMSE): seasonal_naive **3,223.063**, arima 5,193.216, naive 5,725.492 → seasonal-naive best, matching the documented 3,223.0630.
- Mean MAPE: seasonal_naive 12.00 %, arima 24.33 %, naive 27.08 %. Horizon 114 per store. All four stores evaluated.

## Discrepancies
None.

## Changes
None.

## Regression Checks
Consumes Phase 10 output; metric values reconcile with the Phase 12 re-evaluation baseline (mean validation RMSE 3,223.0630 cited there).

## Final Status
PASSED
