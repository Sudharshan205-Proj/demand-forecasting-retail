# Phase 8 — Course Content Coverage

## Analysis and statistical thinking

| Course concept | Phase 8 evidence |
|---|---|
| Analytical questions | Statistical analysis plan (8 questions) |
| Identifying relationships | Pearson correlation and sample covariance for 9 variables in `statistical_correlations.csv` |
| Identifying patterns | Daily trend with Newey-West robust inference and 14-lag autocorrelation showing weekly periodicity |
| Descriptive statistics | `statistical_summary.csv` (mean, median, standard deviation, minimum, maximum, coefficient of variation) |
| Statistical significance | Mann-Whitney U tests for both promotion comparisons, trend p-values, p-value underflow rule |
| Data-driven interpretation | `statistical_findings.txt` |
| Validation | `statistical_quality_report.csv` (56 metrics) evidencing the quality framework |
| Reproducibility | Deterministic chunked Python workflow with pinned dependencies |

## R programming curriculum

R is part of the internship curriculum and is implemented as a separate
analytical track in Phase 14. Phase 8 does not claim R coverage for statistical
work performed in Python.

## Visualization curriculum

Statistical relationships are supported with appropriate static charts:

- line chart (`statistical_demand_trend.png`) — daily demand over time;
- bar chart (`statistical_store_variability.png`) — total demand by store;
- scatter plot (`statistical_price_demand.png`) — price against quantity, on a
  documented deterministic systematic sample that spans the whole date range;
- autocorrelation chart (`statistical_demand_autocorrelation.png`) — demand
  autocorrelation by lag.

The final dashboard and storytelling work belong to Phase 15.

## Forecasting curriculum

Phase 8 provides statistical evidence for the later forecasting work:

- weekly seasonality (lag 7 and lag 14 autocorrelation of 0.874 and 0.885)
  establishes that forecasting models need weekly terms;
- strong short-run autocorrelation (lag 1: 0.882) rules out random train/test
  splits and motivates temporal validation;
- the trend, measured with robust standard errors, is partly explained by a
  documented coverage change, which is handled explicitly before it is modelled;
- price and promotions explain very little row-level variation, so the main
  forecasting signal comes from temporal structure rather than these covariates.

Phase 8 does not claim forecasting-model performance before models are trained
and evaluated.

## Course-content principle

Every course concept claimed as implemented has corresponding project evidence.
