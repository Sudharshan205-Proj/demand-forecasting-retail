# Phase 11 — Forecasting Models Methodology

## 1. Forecasting Problem

The project forecasts physical retail demand represented by `quantity`.

The forecasting problem is temporal, so historical observations must precede the observations being predicted.

## 2. Chronological Data Separation

The project uses the Phase 9 chronological partitions:

* Train: 2022-08-28 to 2024-02-10
* Validation: 2024-02-11 to 2024-06-03
* Test: 2024-06-04 to 2024-09-26

The test partition is not used to select or tune models.

## 3. Naive Forecast

The naive forecast uses the most recent observed demand as the forecast for every future point.

This establishes the minimum benchmark for model performance.

## 4. Seasonal-Naive Forecast

The seasonal-naive model repeats the latest seven-observation demand pattern.

This provides a simple benchmark for weekly recurring behavior.

## 5. ARIMA

ARIMA models temporal dependence through autoregressive, differencing, and moving-average components.

The initial configuration is:

`ARIMA(1,1,1)`

The model is intentionally conservative rather than extensively tuned in this phase.

## 6. Modeling Scope

The daily physical demand is aggregated by store for classical ARIMA experimentation.

This decision addresses two characteristics identified during time-series preparation:

1. The dataset contains substantial intermediate-date gaps.
2. There are many item-store series.

Fitting an independent ARIMA model to every item-store series would introduce unnecessary computational complexity and unreliable modeling for sparse series.

## 7. Evaluation Metrics

RMSE and MAPE are calculated on the validation period.

RMSE penalizes large errors more strongly because errors are squared.

MAPE is expressed as a percentage.

Observations with zero actual demand are excluded from MAPE.

## 8. Leakage Prevention

No validation observation is used to fit the initial training forecast.

The test period remains isolated.

No random temporal shuffle is performed.

## 9. Future Modeling

Later phases may evaluate feature-based machine-learning models and deep-learning approaches such as LSTM.

Those models must use the same chronological principles.
