# Phase 11 — Forecasting Models Methodology

## 1. Forecasting Problem

The project forecasts physical retail demand represented by `quantity`.

The forecasting problem is temporal, so historical observations must precede the
observations being predicted. Every model is fitted on data up to `2024-02-10`
and evaluated on `2024-02-11` through `2024-06-03`; the test partition beginning
`2024-06-04` is never read for fitting or selection.

## 2. Chronological Data Separation

The project uses the Phase 9 chronological partitions:

* Train: 2022-08-28 to 2024-02-10 (4,315,416 observed records)
* Validation: 2024-02-11 to 2024-06-03 (1,548,957 observed records)
* Test: 2024-06-04 to 2024-09-26 (1,566,653 observed records)

The test partition is not used to select or tune models.

At the forecasting grain the same boundaries produce a training window ending
`2024-02-10` for every store and a single, identical 114-day validation window
(`2024-02-11` to `2024-06-03`) for every store. The quality report verifies this
window contract rather than trusting it.

## 3. Aggregation to the Store-Day Grain

The Phase 10 source is read with four columns only (`date`, `store_id`,
`quantity`, `split`) and aggregated to daily store-level demand. The aggregation
is reconciled against the source on total quantity (`41,949,529.910`), so no
demand is lost in the transition from item-store rows to store-days.

Each store series is then densified onto a complete daily calendar. Phase 9
preserves missing dates as missing rather than assuming zero demand at the
item-store grain; at the store level an absent date means no quantity was
recorded for that store that day, so zero-filling is the correct interpretation.
This also gives the series the regular frequency that ARIMA's out-of-sample
forecasting requires.

The densification adds exactly one store-day across the whole dataset — store 3
on `2022-10-16` — and the count is recorded in the findings report.
Densification is therefore measured, not assumed.

## 4. Naive Forecast

The naive forecast uses the most recent observed training demand as the forecast
for every validation point.

This establishes the minimum benchmark for model performance. The predictions
artifact is verified to contain exactly the repeated last training value for
every store.

## 5. Seasonal-Naive Forecast

The seasonal-naive model repeats the latest seven-observation training pattern
across the horizon, tiling the pattern when the horizon is not an exact multiple
of seven.

This provides a simple benchmark for weekly recurring behavior. The predictions
artifact is verified to reproduce the documented seven-day pattern exactly.

## 6. ARIMA

ARIMA models temporal dependence through autoregressive, differencing, and
moving-average components.

The configuration is:

`ARIMA(1, 1, 1)`

fitted with `enforce_stationarity=False` and `enforce_invertibility=False`. The
order is recorded explicitly for every store in the configurations artifact, and
the quality report verifies that record. The model is intentionally
conservative rather than extensively tuned in this phase.

## 7. Modeling Scope

The daily physical demand is aggregated by store for classical ARIMA
experimentation.

This decision addresses two characteristics identified during time-series
preparation:

1. The dataset contains substantial intermediate-date gaps (55,122 of 58,022
   item-store series).
2. There are many item-store series.

Fitting an independent ARIMA model to every item-store series would introduce
unnecessary computational complexity and unreliable modeling for sparse series.

One consequence is documented: store 4 first appears on `2023-12-13`, so its
ARIMA model is fitted on 60 training observations rather than the 531 available
to stores 1–3.

## 8. Evaluation Metrics

RMSE and MAPE are calculated on the validation period.

RMSE penalizes large errors more strongly because errors are squared.

MAPE is expressed as a percentage.

Observations with zero actual demand are excluded from MAPE. The validation
store-days contain no zero-demand observations, so the rule is a safety
guarantee rather than a change to the reported values.

The summary records both across-store statistics (mean and median) and pooled
statistics computed over every store-day validation observation. The two differ
because pooling weights larger stores more heavily.

## 9. Metric Verification

The per-store forecasts are written to `forecasting_predictions.csv`. The
quality report recomputes RMSE and MAPE from those stored predictions and
reconciles them against `forecasting_model_results.csv`, so the reported metrics
cannot drift from the forecasts that produced them.

## 10. Leakage Prevention

No validation observation is used to fit the initial training forecast. Each
model is fitted on the training window only, and its configuration records that
window.

The test period remains isolated: the quality report verifies that no prediction
date reaches `2024-06-04` and that every configuration's training window ends at
or before `2024-02-10`.

No random temporal shuffle is performed.

## 11. Position in the Forecasting Workflow

Phase 11 delivers the classical univariate model set: two benchmarks and
ARIMA(1,1,1). The feature-based candidate that uses the Phase 10 engineered
matrix, the comparison and selection across the full candidate set, and the
final held-out evaluation are delivered by Phase 12.

Deep-learning approaches such as LSTM are outside the scope of the delivered
project.
