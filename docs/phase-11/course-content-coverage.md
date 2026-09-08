# Phase 11 — Course Content Coverage

| Course concept         | Phase 11 implementation                       | Evidence                        |
| ---------------------- | --------------------------------------------- | ------------------------------- |
| Time-series analysis   | Forecast physical retail demand over time     | `scripts/forecasting_models.py` |
| Predictive modeling    | Forecast future demand from historical demand | Forecasting script              |
| Model evaluation       | RMSE and MAPE                                 | Forecasting script              |
| Baseline modeling      | Naive and seasonal-naive benchmarks           | Forecasting script              |
| Advanced data science  | ARIMA forecasting                             | Forecasting script              |
| Data preparation       | Phase 10 feature-engineered dataset           | Phase 10 output                 |
| Train/test separation  | Chronological partitions                      | Phase 9 split                   |
| Validation             | Dedicated validation period                   | Forecasting script              |
| Data quality           | Forecast and metric validation                | Tests                           |
| Reproducibility        | Explicit model configuration and dates        | Configuration output            |
| Pattern identification | Seasonal-naive weekly pattern                 | Forecasting model               |
| Analytical reasoning   | Model performance compared against baselines  | Results                         |

## Course Requirement

The internship material specifically identifies ARIMA, Prophet, or LSTM for the retail demand forecasting project and RMSE or MAPE for evaluation.

Phase 11 implements ARIMA and both required evaluation metrics.

## Deferred Concepts

Prophet and LSTM are not artificially added to this phase.

LSTM belongs to a later deep-learning stage, while Prophet may be considered later if a specific forecasting experiment benefits from it.

The project will document rather than falsely claim these implementations in Phase 11.
