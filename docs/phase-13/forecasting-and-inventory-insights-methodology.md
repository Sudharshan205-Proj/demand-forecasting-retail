# Phase 13 — Forecasting & Inventory Insights Methodology

## 1. Demand Basis

Historical demand statistics are calculated from the training period.

The target remains physical sales quantity.

Online demand is not combined with the physical-store demand target.

## 2. Forecasting Evidence

Phase 12 selected forecasting configurations using training-period
time-series cross-validation.

The Phase 12 validation results are used as model-performance evidence.

## 3. Demand Level

Average daily demand represents the typical observed daily demand during
the training period.

Median demand provides a robust comparison with the mean.

Maximum and percentile demand provide information about high-demand periods.

## 4. Demand Variability

Standard deviation measures absolute variability.

Coefficient of variation is calculated as:

CV = standard deviation / mean demand

CV helps compare relative variability between stores with different demand
levels.

## 5. Safety Stock

Safety stock is estimated using:

SS = z × sigma × sqrt(L)

where:

- z is the service-level normal quantile;
- sigma is daily demand standard deviation;
- L is lead time.

## 6. Reorder Point

The reorder point is:

ROP = mean daily demand × L + SS

This represents the estimated inventory position at which replenishment
would be triggered under the scenario assumptions.

## 7. Scenario Analysis

Because operational inventory parameters are unavailable, the project
uses explicit scenarios rather than pretending that assumed values are
business requirements.

Lead-time scenarios:

- 7 days
- 14 days
- 28 days

Service-level scenarios:

- 90%
- 95%
- 99%

## 8. Interpretation

Higher demand does not necessarily mean higher relative inventory risk.

A store may have:

- high demand and low variability;
- low demand and high variability;
- high demand and high variability;
- low demand and low variability.

Inventory planning should consider both demand level and uncertainty.

## 9. Store 4

Store 4 is not assigned a tuned Phase 12 forecasting configuration because
its training series was too short for the configured cross-validation
procedure.

Store 4 therefore receives descriptive inventory analysis rather than a
claim of validated forecasting superiority.

## 10. Limitations

The analysis does not model:

- supplier reliability;
- lead-time uncertainty;
- stockout costs;
- holding costs;
- ordering costs;
- existing inventory;
- purchase orders;
- warehouse constraints;
- shelf-life constraints.

Operational deployment would require these inputs.