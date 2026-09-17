# Phase 8 — Course Content Coverage

## Analysis and statistical thinking

| Course concept | Phase 8 evidence |
|---|---|
| Analytical questions | Statistical analysis plan (8 questions) |
| Identifying relationships | Pearson correlation and sample covariance for 9 variables in `statistical_correlations.csv` |
| Identifying patterns | Daily trend with Newey-West robust inference and 14-lag autocorrelation showing weekly periodicity |
| Descriptive statistics | `statistical_summary.csv` (mean, median, standard deviation, minimum, maximum, coefficient of variation) |
| Statistical significance | Mann-Whitney U tests for both promotion comparisons, trend p-values, p-value underflow rule |
| Data-driven interpretation | `statistical_findings.txt` and the verified results document |
| Validation | `statistical_quality_report.csv` (56 metrics) evidencing the quality framework |
| Reproducibility | Deterministic chunked Python workflow with pinned dependencies |

## R programming curriculum

R is part of the internship curriculum and is planned as a separate
analytical implementation where appropriate.

Phase 8 does not falsely claim R coverage merely because statistical
analysis is being performed in Python.

## Visualization curriculum

Statistical relationships are supported with appropriate static charts:

- line chart (`statistical_demand_trend.png`) — daily demand over time;
- bar chart (`statistical_store_variability.png`) — total demand by store;
- scatter plot (`statistical_price_demand.png`) — price against quantity, on a
  documented deterministic systematic sample that spans the whole date range;
- autocorrelation chart (`statistical_demand_autocorrelation.png`) — demand
  autocorrelation by lag.

Final dashboard and storytelling work remain separate project stages.

## Forecasting curriculum

Phase 8 provides statistical evidence for later forecasting work:

- weekly seasonality (lag 7 and lag 14 autocorrelation of 0.874 and 0.885)
  establishes that forecasting models need weekly terms;
- strong short-run autocorrelation (lag 1: 0.882) rules out random
  train/test splits and motivates temporal validation;
- the trend, measured with robust standard errors, is partly explained by a
  documented coverage change, which must be handled before it is modelled;
- price and promotions explain very little row-level variation, so the main
  forecasting signal must come from temporal structure rather than these
  covariates.

It does not claim forecasting-model performance before models are trained
and evaluated.

## Course-content principle

Every course concept claimed as implemented must have corresponding
project evidence.

## Phase 17 re-audit record

| Change | Reason |
|---|---|
| Covariance and significance testing rows added | The plan listed covariance and significance tests; both now exist as evidence |
| Scatter row qualified as a systematic sample | The figure previously plotted the first 200,000 rows, a contiguous 2.7% block, without any note |
| Forecasting row expanded | The level shift, weekly periodicity and the weak row-level covariates are now evidential findings rather than generic statements |
| Validation row re-pointed at the quality report | The framework previously had no artifact to evidence it |
