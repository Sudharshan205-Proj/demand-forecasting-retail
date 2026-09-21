# Phase 11 — Course Content Coverage

| Course concept | Phase 11 implementation | Evidence |
| --- | --- | --- |
| Time-series analysis | Forecast physical retail demand over time | `scripts/forecasting_models.py` |
| Predictive modeling | Forecast future demand from historical demand | Forecasting script |
| Model evaluation | RMSE and MAPE on the validation period | Forecasting script, `forecasting_model_results.csv` |
| Baseline modeling | Naive and seasonal-naive benchmarks | Forecasting script, verified element-wise against their definitions |
| Advanced data science | ARIMA(1,1,1) forecasting | Forecasting script, `forecasting_model_configurations.csv` |
| Data preparation | Phase 10 feature-engineered dataset | Phase 10 output, reconciled to 7,431,026 rows and 41,949,529.910 quantity |
| Train/test separation | Chronological partitions | Phase 9 split; test period excluded and verified |
| Validation | Dedicated 114-day validation period | Forecasting script, `forecasting_quality_report.csv` |
| Data quality | Forecast and metric validation | 24-check quality report, all passing |
| Reproducibility | Explicit model configuration and dates | `forecasting_model_configurations.csv` |
| Pattern identification | Seasonal-naive weekly pattern | Forecasting model, verified against the seven-observation cycle |
| Analytical reasoning | Model performance compared against baselines | Results and `forecasting_findings.txt` |
| Data visualization | Forecast-versus-actual diagnostic | Delivered by Phase 15 (forecast-evidence figure and Tableau worksheet) |

## Course Requirement

The internship material specifically identifies ARIMA, Prophet, or LSTM for the
retail demand forecasting project and RMSE or MAPE for evaluation.

Phase 11 implements ARIMA(1,1,1) and both required evaluation metrics (RMSE and
MAPE). ARIMA is fitted independently per store on the training window and
evaluated on the 114-day validation period, with the test period excluded from
selection.

Outcome: the seasonal-naive benchmark achieves the lowest mean (3,223.0630) and
pooled (3,928.6186) validation RMSE. ARIMA(1,1,1) records a mean RMSE of
5,193.2159, improving on the naive baseline (5,725.4922) but not on the weekly
benchmark. No model is claimed to be superior beyond what these validation
results support.

## Model Scope

The delivered project uses ARIMA(1,1,1) as its statistical forecasting model and
adds the feature-based gradient-boosting candidate evaluated in Phase 12.
Prophet and LSTM are not part of the delivered implementation.

The evaluation metrics and the chronological validation discipline are applied
consistently across the Phase 11 and Phase 12 model set, so no curriculum claim
rests on an unimplemented model.
