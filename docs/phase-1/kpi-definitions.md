# KPI Definitions

## Purpose

This document defines the measurements used throughout the project.

Numerical KPI values are not reported here; they belong to the phase results
documents where each analysis is performed (Phase 8 statistical results,
Phase 11–12 model results, Phase 13 inventory insights).

## 1. Historical demand

### Definition

The quantity of product sold during the selected time period.

### Usage

Characterizes historical demand and constructs the forecasting target.

---

## 2. Forecast demand

### Definition

The model-generated estimate of demand for the selected forecasting period.

### Usage

Supports the inventory-planning analysis.

---

## 3. RMSE

### Full name

Root Mean Squared Error

### Definition

RMSE is the square root of the average squared difference between actual and
predicted demand.

### Interpretation

Lower RMSE indicates smaller prediction errors under the metric's scale. RMSE is
in demand units, so it is scale-bound and not directly comparable across stores
of different size.

### Usage

Primary forecasting accuracy metric. Phase 11 reports RMSE per store and model
on the validation period. Phase 12 applies it as the primary
configuration-selection criterion during training-period cross-validation, then
reports it again for the selected configuration on the untouched validation
period. The numerical values belong to those phase result documents.

---

## 4. MAPE

### Full name

Mean Absolute Percentage Error

### Definition

MAPE is average absolute forecast error as a percentage of actual demand.

### Interpretation

Lower MAPE generally indicates better forecasting accuracy, and it is the metric
used for cross-store comparison because it is scale-free.

### Limitation

MAPE behaves poorly when actual demand is zero or very close to zero. Phase 11
excludes zero-actual observations from MAPE and records that the validation
store-days contain none (the minimum validation store-day demand is
3152.575), so the rule is a safety guarantee rather than a value-changing
adjustment. See
[`../phase-11/forecasting-models-methodology.md`](../phase-11/forecasting-models-methodology.md).

---

## 5. Forecast bias

### Definition

The tendency of forecasts to systematically overestimate or underestimate
actual demand.

### Usage

A diagnostic rather than a sole model-selection metric. Phase 11 reports bias by
comparing model errors, and Phase 12 confirmed a systematic under-forecast on
the validation period. Phase 13 quantifies it per store as
`mean(actual − predicted)` over the 114 validation days and applies it as an
explicit level correction in its forecast-driven inventory scenarios, where a
positive value means the model under-forecasts. The measured correction is large
enough to matter: 694.31 to 3,871.04 units per day, a mean of 1,409.941. The
correction is carried as a named column so it is visible rather than folded
silently into a quantity.

---

## 6. Demand volatility

### Definition

A measure of variation in demand over time.

### Usage

Identifies products or stores with unstable demand and informs the forecasting
difficulty question. The coefficient of variation (standard deviation divided by
mean demand) is the basis for comparing stores, because absolute spread and
demand level are not comparable across stores of different size.

---

## 7. Promotional demand difference

### Definition

Difference in demand between promotional and non-promotional observations.

### Limitation

This metric measures association and does not establish causal impact.

---

## 8. Holiday demand difference

Not applicable: the dataset has no holiday field, so no holiday demand
comparison exists.

---

## 9. Inventory-oriented indicator

The project realizes the inventory-oriented indicator as two scenario families
in Phase 13 rather than a single number, because the uncertainty input is an
assumption the reader should be able to see and change:

- **Safety stock** — `z × uncertainty × sqrt(lead time)`, where the uncertainty
  input is the training-period daily demand standard deviation in the
  historical-variability family and the selected model's realised validation
  error in the forecast-error family.
- **Reorder point** — expected lead-time demand plus safety stock, with the
  identity verified numerically for every scenario.
- **Coefficient of variation** — standard deviation divided by mean demand.

The phase deliberately does not report a single recommended inventory quantity:
the dataset has no verified lead times, service-level targets or costs, so any
such number would present an assumption as a finding. Every quantity is a
labelled planning scenario across 7/14/28-day lead times and 90/95/99 % service
levels.

## KPI selection principle

Every KPI has a clear relationship to the business problem, the analytical
question, the forecasting objective and the stakeholder decision.
