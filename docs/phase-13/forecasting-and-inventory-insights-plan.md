# Phase 13 — Forecasting & Inventory Insights Plan

## Purpose

Translate the validated forecasting results into practical retail demand
and inventory-planning insights.

## Starting Point

Phase 12 selected a feature-based gradient-boosting configuration
(`feature_gbm`) for Stores 1, 2 and 3, and Seasonal Naive with a 7-day
seasonal period for Store 4.

All four stores have a validated Phase 12 tuned model. The Phase 12
re-audit replaced the fixed three-fold cross-validation design with an
adaptive one, so Store 4 — which previously had no tuned model because its
60 training observations could not support three 28-day folds — is now
tuned with a single fold and validated on the full 114-day period.

Phase 12's validation evidence: mean validation RMSE 3,079.4286 across the
four selected configurations, against Phase 11's 3,223.0630 for the weekly
seasonal benchmark. Stores 1 and 2 improved (11.13% and 6.38%), Store 4
reproduced Phase 11's forecast exactly, and Store 3 was 0.32% worse than
the weekly benchmark.

Phase 12 also recorded a **systematic under-forecast**: every selected
model under-forecast on average over the validation period, with the bias
widening in the second half. Phase 13 is the phase that must carry that
finding into planning quantities, and Phase 12 stores every validation
forecast in `data/analysis/model_evaluation_predictions.csv` for this phase
to use.

## Demand Basis

Historical statistics are computed on the **densified training series**,
using the same construction Phase 11 and Phase 12 apply: each store's
observed training range is reindexed onto a complete daily calendar with
absent days filled at zero.

This matters because the three phases must describe the same series. It
confines the change to Store 3, which has exactly one date (2022-10-16)
absent from the data, and the densification is measured and reconciled
rather than assumed.

## Analysis Areas

### Demand Level

Calculate:

- total historical demand;
- mean daily demand;
- median daily demand;
- minimum daily demand;
- maximum daily demand.

### Demand Variability

Calculate:

- standard deviation;
- variance;
- coefficient of variation;
- high-percentile demand.

### Inventory Planning

Produce two scenario families, because the dataset supports two defensible
uncertainty inputs and they answer different questions.

**Historical-variability family.** Uncertainty comes from the
training-period daily demand standard deviation. This is the descriptive
answer to "how variable has demand been?".

**Forecast-error family.** Uncertainty comes from the selected model's
realised validation error, and the level comes from its bias-corrected
validation demand. This is the answer to "what does the model that was
actually selected imply?".

Produce scenario calculations for:

- 7-day lead time;
- 14-day lead time;
- 28-day lead time.

Service-level scenarios:

- 90%;
- 95%;
- 99%.

### Safety Stock

Use:

Safety Stock = z × uncertainty input × sqrt(lead time)

### Reorder Point

Use:

Reorder Point = expected lead-time demand + safety stock

## Important Assumptions

The dataset does not provide verified:

- supplier lead times;
- service-level targets;
- holding costs;
- ordering costs;
- stockout costs.

Therefore the inventory calculations are planning scenarios rather than
operational recommendations.

The forecast-error family reuses the validation period's own error. That is
more optimistic than a genuinely unseen evaluation, and the reserved test
period is not read to improve on it.

## Business Insights

The phase identifies:

- highest-demand stores;
- highest-variability stores;
- the systematic forecast bias and its direction;
- relative forecast accuracy, which is the only basis on which stores of
  different size can be compared;
- inventory-risk areas;
- differences between demand level and demand volatility;
- model-supported forecasting evidence.

## Test Set

The test period is not used to select or tune models, to calibrate the
inventory scenarios, or to estimate forecast error.

## Deliverables

- Demand summary
- Variability summary
- Densification summary
- Historical-variability inventory scenarios
- Forecast-error inventory scenarios
- Forecast-error summary
- Structured insights
- Findings report
- Machine-readable quality report that gates the run
