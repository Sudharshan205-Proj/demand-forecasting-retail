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

Safety Stock = z × daily demand standard deviation × sqrt(lead time)

### Reorder Point

Use:

Reorder Point = average daily demand × lead time + safety stock

## Important Assumptions

The dataset does not provide verified:

- supplier lead times;
- service-level targets;
- holding costs;
- ordering costs;
- stockout costs.

Therefore the inventory calculations are planning scenarios rather than
operational recommendations.

## Business Insights

The phase identifies:

- highest-demand stores;
- highest-variability stores;
- inventory-risk areas;
- differences between demand level and demand volatility;
- model-supported forecasting evidence.

## Test Set

The test period is not used to select or tune models.

## Deliverables

- Demand summary
- Variability summary
- Inventory scenarios
- Structured insights
- Findings report