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

## KPI Selection Principle

No metric will be used merely because it is available.

Every KPI must have a clear relationship to:

- The business problem
- The analytical question
- The forecasting objective
- The stakeholder decision