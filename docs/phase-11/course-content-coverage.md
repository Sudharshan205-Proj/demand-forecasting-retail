# Phase 11 — Course Content Coverage

| Course concept         | Phase 11 implementation                       | Evidence                        | Status |
| ---------------------- | --------------------------------------------- | ------------------------------- | ------ |
| Time-series analysis   | Forecast physical retail demand over time     | `scripts/forecasting_models.py` | VERIFIED |
| Predictive modeling    | Forecast future demand from historical demand | Forecasting script | VERIFIED |
| Model evaluation       | RMSE and MAPE on the validation period        | Forecasting script, `forecasting_model_results.csv` | VERIFIED |
| Baseline modeling      | Naive and seasonal-naive benchmarks           | Forecasting script, verified element-wise against their definitions | VERIFIED |
| Advanced data science  | ARIMA(1,1,1) forecasting                      | Forecasting script, `forecasting_model_configurations.csv` | VERIFIED |
| Data preparation       | Phase 10 feature-engineered dataset           | Phase 10 output, reconciled to 7,431,026 rows and 41,949,529.910 quantity | VERIFIED |
| Train/test separation  | Chronological partitions                      | Phase 9 split; test period excluded and verified | VERIFIED |
| Validation             | Dedicated 114-day validation period           | Forecasting script, `forecasting_quality_report.csv` | VERIFIED |
| Data quality           | Forecast and metric validation                | 24-check quality report, all passing | VERIFIED |
| Reproducibility        | Explicit model configuration and dates        | `forecasting_model_configurations.csv` | VERIFIED |
| Pattern identification | Seasonal-naive weekly pattern                 | Forecasting model, verified against the seven-observation cycle | VERIFIED |
| Analytical reasoning   | Model performance compared against baselines  | Results and `forecasting_findings.txt` | VERIFIED |
| Data visualization     | Forecast-versus-actual diagnostic             | Not implemented in Phase 11 — delivered by Phase 15 (forecast-evidence figure and Tableau worksheet) | DEFERRED — LANDED IN PHASE 15 |

## Course Requirement

The internship material specifically identifies ARIMA, Prophet, or LSTM for the retail demand forecasting project and RMSE or MAPE for evaluation.

Phase 11 implements ARIMA(1,1,1) and both required evaluation metrics (RMSE and MAPE). ARIMA is fitted independently per store on the training window and evaluated on the 114-day validation period, with the test period excluded from selection.

Verified outcome: the seasonal-naive benchmark achieves the lowest mean (3,223.0630) and pooled (3,928.6186) validation RMSE. ARIMA(1,1,1) records a mean RMSE of 5,193.2159, improving on the naive baseline (5,725.4922) but not on the weekly benchmark. No model is claimed to be superior beyond what these validation results support.

## Deferred Concepts

Prophet and LSTM are not artificially added to this phase.

LSTM belongs to a later deep-learning stage, while Prophet may be considered later if a specific forecasting experiment benefits from it.

The project documents rather than falsely claims these implementations in Phase 11. The Phase 11 plan, methodology and coverage documents all state that final selection, tuning and machine-learning or deep-learning forecasting belong to later phases.

## Phase 17 Re-Audit Note

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
