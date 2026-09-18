# KPI Definitions

## Purpose

This document defines the measurements that will be used throughout the project.

Numerical KPI values are not reported here; they belong to the phase results documents where each analysis is actually performed (for example the Phase 8 statistical results, Phase 11–12 model results, and Phase 13 inventory insights).

## 1. Historical Demand

### Definition

The quantity of product sold during the selected time period.

### Usage

Used to understand historical demand and construct the forecasting target.

---

## 2. Forecast Demand

### Definition

The model-generated estimate of future demand for the selected forecasting period.

### Usage

Used to support inventory-planning analysis.

---

## 3. RMSE

### Full Name

Root Mean Squared Error

### Definition

RMSE measures the square root of the average squared difference between actual and predicted demand.

### Interpretation

Lower RMSE indicates smaller prediction errors under the metric's scale.

### Usage

Primary forecasting accuracy metric.

Phase 11 reports RMSE per store and model on the validation period. Phase 12
applies it as the primary configuration-selection criterion during
training-period cross-validation, then reports it again for the selected
configuration on the untouched validation period. The numerical values
belong to those phase result documents.

---

## 4. MAPE

### Full Name

Mean Absolute Percentage Error

### Definition

MAPE measures average absolute forecast error as a percentage of actual demand.

### Interpretation

Lower MAPE generally indicates better forecasting accuracy.

### Important Limitation

MAPE can behave poorly when actual demand is zero or very close to zero.

The project will therefore document how zero-demand observations are handled before reporting MAPE. Phase 11 does so: it excludes zero-actual observations from MAPE and records that the validation store-days contain none (the minimum validation store-day demand is 3152.575), so the rule is a verified safety guarantee rather than a value-changing adjustment. See `docs/phase-11/forecasting-models-methodology.md`.

---

## 5. Forecast Bias

### Definition

The tendency of forecasts to systematically overestimate or underestimate actual demand.

### Usage

Used as a diagnostic rather than as the sole model-selection metric.

Phase 11 reports the bias by comparing model errors, and Phase 12 confirmed a
systematic under-forecast on the validation period. Phase 13 quantifies it per
store as `mean(actual − predicted)` over the 114 validation days and applies it
as an explicit level correction in its forecast-driven inventory scenarios,
where a positive value means the model under-forecasts. The measured correction
is large enough to matter: 694.31 to 3,871.04 units per day, a mean of
1,409.941. The correction is carried as a named column so it is visible rather
than folded silently into a quantity.

---

## 6. Demand Volatility

### Definition

A measure of variation in demand over time.

### Usage

Used to identify products or periods with unstable demand and investigate forecasting difficulty.

---

## 7. Promotional Demand Difference

### Definition

Difference in demand between promotional and non-promotional observations, where the selected dataset supports this comparison.

### Important Limitation

This metric measures association and does not automatically establish causal impact.

---

## 8. Holiday Demand Difference

### Definition

Difference in demand between holiday and non-holiday observations, where applicable.

---

## 9. Inventory-Oriented Indicator

The project may construct indicators such as:

- Expected demand ranking
- Forecast increase
- Forecast decrease
- High-demand period indicator
- Forecast uncertainty/error indicator

These are decision-support indicators, not direct inventory optimization outputs.

### Implemented in Phase 13

Phase 13 realises this KPI as two scenario families rather than a single
number, because the uncertainty input is an assumption the reader should be
able to see and change.

- **Safety stock** — `z × uncertainty × sqrt(lead time)`, where the
  uncertainty input is the training-period daily demand standard deviation in
  the historical-variability family and the selected model's realised
  validation error in the forecast-error family.
- **Reorder point** — expected lead-time demand plus safety stock, with the
  identity verified numerically for every scenario.
- **Coefficient of variation** — standard deviation divided by mean demand,
  which is the basis on which stores are compared, since absolute spread and
  demand level are not comparable across stores of different size.

The phases deliberately do not report a single recommended inventory quantity.
The dataset has no verified lead times, service-level targets or costs, so any
such number would present an assumption as a finding. Every quantity is a
labelled planning scenario across 7/14/28-day lead times and 90/95/99% service
levels.

## KPI Selection Principle

No metric will be used merely because it is available.

Every KPI must have a clear relationship to:

- The business problem
- The analytical question
- The forecasting objective
- The stakeholder decision