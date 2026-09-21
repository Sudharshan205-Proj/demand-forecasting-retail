# Phase 8 — Statistical Analysis Methodology

## Data source

The analysis uses `data/processed/integrated_retail_data.csv`, which contains the
cleaned physical-store sales data and associated store, catalog, pricing,
markdown, promotion and online-channel information.

## Processing strategy

The integrated dataset is approximately 1.28 GB and is processed with pandas
chunked CSV reading at a chunk size of 100,000 rows. The complete dataset is
never loaded into memory, and no reported statistic is computed from a sample.

Chunked statistics are combined rather than averaged across chunks. Each chunk
contributes its own centered sums, which are merged with the parallel-
accumulation formula:

```text
mean      = mean_a + delta * n_b / (n_a + n_b)
cov_sum   = cov_a + cov_b + delta_x * delta_y * n_a * n_b / (n_a + n_b)
var_x_sum = var_x_a + var_x_b + delta_x^2 * n_a * n_b / (n_a + n_b)
```

Centering inside the chunk keeps floating-point cancellation negligible, so the
chunked result agrees with a whole-array calculation to about 13 significant
figures while memory stays proportional to the chunk size. The chunk size is a
documented constant: 100,000 rows was measured to use about 24% less memory than
250,000 rows at the same runtime.

## Demand

Physical demand is represented by `quantity`. Online quantity is retained as a
separate variable and is not added to physical-store demand.

## Missing and non-finite values

Each analytical column is coerced to numeric; values that cannot be coerced
become missing rather than silently dropping the variable. Pairwise statistics
use only rows where both variables are finite, so missing and infinite values are
excluded per pair instead of being imputed or sampled. Every exclusion is counted
in `statistical_quality_report.csv` as `observations_<variable>` and
`excluded_<variable>`.

A variable whose variance is indistinguishable from zero relative to its own
scale (relative tolerance 1e-12) is treated as having no usable variation, so its
correlation is undefined rather than a meaningless coefficient produced by
rounding in the estimated mean.

## Descriptive statistics

Daily aggregate demand is summarized using mean, median, standard deviation,
minimum, maximum and coefficient of variation. The coefficient of variation is
`standard deviation / mean` and is used to compare relative demand variability.

## Correlation and covariance

Pearson correlation quantifies linear association between numeric variables, and
the sample covariance is reported alongside it. Correlation values range from -1
to +1 and do not establish causation.

## Price-demand analysis

Price and quantity are evaluated using Pearson correlation, a p-value, simple
linear regression, the regression slope and R-squared. Quantity is the response
and price is the explanatory variable, so the slope is expressed in quantity
units per price unit. This is an analytical relationship, not a causal elasticity
estimate.

## Promotion analysis

Two comparisons are reported, each with a Mann-Whitney U test, and they are
labelled separately in the artifacts:

1. **Presence (primary).** `promotion_record_present` groups records with a
   discount record (`discount_record_count > 0`); `promotion_record_absent`
   groups records without one. These two groups partition the rows with a finite
   demand value.
2. **Rate sign (secondary).** Within the promoted rows, records with a positive
   finite discount rate are compared with records whose finite rate is zero or
   negative.

Rows with a missing or non-finite discount rate stay in the presence comparison
and are excluded from the rate-sign comparison, and both exclusions are counted
(`promotion_rate_missing_excluded`, `promotion_rate_infinite_excluded`).

Group differences are observational. Promotion selection is not random, so a
difference between promoted and unpromoted rows is not evidence of a promotional
effect.

## Trend analysis

Aggregate daily demand is regressed against the chronological observation index.
The resulting slope indicates the estimated linear change per day.

Because daily demand is strongly autocorrelated, the ordinary least squares
standard error understates the uncertainty of the slope. A Newey-West (HAC)
standard error and p-value with 14 lags are therefore reported next to the OLS
values, and the robust values are the defensible measure of trend uncertainty.
The trend remains a descriptive linear summary, not a forecasting model.

## Autocorrelation

Demand autocorrelation is calculated for the 14 most recent daily lags, providing
evidence about temporal dependence and whether previous demand contains
information about current demand. Autocorrelation that peaks at lag 7 and lag 14
indicates weekly periodicity.

## Monthly activity

`statistical_monthly_activity.csv` records row count, distinct items, distinct
stores, quantity and revenue for every month. It separates a change in data
coverage or assortment from a change in demand before any level shift is
modelled. Distinct items and distinct stores are accumulated as sets during the
same chunked pass.

## Sampling policy

Every reported statistic uses the complete dataset. The only sampled artifact is
the price/demand scatter figure, which takes a deterministic systematic sample of
one in every 37 eligible rows (200,839 points) so that the figure spans the whole
date range instead of a contiguous block of the file. The sample step and size
are recorded in the quality report, and the figure title states the sampling.

## Statistical interpretation

Results are interpreted using both statistical significance and practical
magnitude; a small p-value alone does not establish business importance.

With millions of observations, p-values underflow double precision. Values below
1e-300 are reported as `< 1e-300` in the findings file and in the documentation,
because a probability of exactly zero is not a valid statistical statement.

## Forecasting boundary

No forecasting model is trained in Phase 8. The statistical findings inform the
forecasting methodology of Phases 9–13.
