# Phase 12 — Model Evaluation & Tuning

## Purpose
Evaluate nine candidate configurations per store across expanding-window cross-validation (CV), select the winner on training-period CV only, then reproduce validation metrics from stored predictions.

## Starting State
Phase 11 PASSED with forecasting baseline metrics (mean validation RMSE 3,223.0630).

## Inputs
`data/processed/feature_engineered_daily.csv` (byte-identical); Phase 11 predictions/results for comparison.

## Commands Executed
- CMD-P12-01: `.venv/Scripts/python.exe scripts/evaluate_and_tune_models.py` — exit 0, **58.6 s**, empty stderr. Evidence: `command-001-stdout.txt`.
- CMD-P12-02: `pytest tests/test_evaluate_and_tune_models.py -q -p no:cacheprovider` — exit 0, **64 passed**, 53.70 s. Evidence: `command-002.txt`.
- Verification: quality report = **30 checks, all passed**.

## Tests
64/64 PASSED (matches documented 64). Covers metric guards, feature builder leakage guards (lag identity, rolling exclusion), adaptive folds, chronology/expansion, selection rule with MAPE tie-break, quality-report deliberate-failure paths.

## Artifacts
`data/analysis/{model_tuning_results,model_tuning_summary,selected_model_configurations,tuned_validation_results,model_error_analysis,model_evaluation_predictions,model_evaluation_quality_report}.csv`, `model_evaluation_findings.txt` regenerated.

## Expected Results
Per docs: 9 candidates/store, 90 CV folds; selection stores 1–3 `feature_gbm`, store 4 `seasonal_naive` (single affordable fold); mean validation RMSE 3,079.4286; store 3 0.32 % worse than the weekly benchmark; predictions 2,976 rows max 2024-06-03; test period never read.

## Actual Results
- Selected stores **[1, 2, 3, 4]**; configurations `feature_gbm`, `feature_gbm`, `feature_gbm`, `seasonal_naive` — exact match.
- Predictions **2,976 rows, max date 2024-06-03** — test period untouched (leakage guard holds).
- Validation RMSE: store1 4,233.491867; store2 711.206677; store3 1,309.960034; store4 6,063.055906 → **mean 3,079.428621**, matching the documented 3,079.4286.
- Store 3 vs seasonal-naive 1,305.735241: (1,309.960034−1,305.735241)/1,305.735241 = **0.3235 % worse** — reproduces the documented 0.32 % regression exactly (recorded, not smoothed).
- Quality report 30/30 passed.

## Discrepancies
None.

## Changes
None.

## Regression Checks
Improves on the Phase 11 mean validation RMSE (3,223.0630 → 3,079.4286); store 4 reproduces its Phase 11 seasonal-naive forecast exactly (6,063.055906 both phases).

## Final Status
PASSED
