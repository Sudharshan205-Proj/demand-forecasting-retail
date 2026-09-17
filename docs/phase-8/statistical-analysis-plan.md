# Phase 8 — Statistical Analysis Plan

## Purpose

Phase 8 extends the descriptive findings from Exploratory Data Analysis
by quantifying demand variability, relationships, trends and statistical
evidence.

The phase does not train the final forecasting models.

## Primary analytical variable

The primary demand variable is:

`quantity`

The physical-store demand measure is kept separate from online demand.

## Questions

1. What is the distribution and variability of daily demand?
2. Is aggregate demand associated with a systematic temporal trend?
3. How different are stores in total demand?
4. How different are product departments?
5. Is price associated with quantity demanded?
6. Is promotional activity associated with demand?
7. Does recent demand predict or correlate with current demand through
   temporal autocorrelation?
8. Which relationships are statistically significant?

## Statistical methods

### Descriptive statistics

- Mean
- Median
- Standard deviation
- Minimum
- Maximum
- Coefficient of variation

### Relationship analysis

- Pearson correlation
- Covariance
- Simple linear regression for price-demand analysis

### Temporal analysis

- Daily demand trend, with ordinary least squares and Newey-West (HAC)
  robust inference
- Lagged autocorrelation for 14 daily lags

### Group comparison

- Store-level demand comparison (descriptive, with share of demand)
- Department-level demand comparison (descriptive)
- Promotion versus non-promotion comparison: presence of a discount record,
  with a secondary breakdown of promoted records by discount-rate sign

### Statistical significance

Where assumptions permit, significance tests are calculated and reported
using p-values: a two-sided Mann-Whitney U test for each promotion
comparison, and a trend test with autocorrelation-robust standard errors.

Store and department comparisons are reported descriptively rather than
tested, because the store groups contain only four units and department rows
are far from independent; a significance test on millions of non-independent
observations would add no information beyond the reported magnitudes.

Statistical significance is not treated as evidence of causation.

### Data integrity and validation

- Row, quantity, revenue, date and monthly reconciliation
- Per-variable observation and exclusion counts
- Correlation-range, p-value, regression and output finiteness checks
- Recorded in `data/analysis/statistical_quality_report.csv`

## Reproducibility

The analysis:

- uses deterministic processing;
- uses fixed analytical definitions;
- processes the source dataset in chunks of 100,000 rows without retaining it;
- computes every reported statistic from the complete dataset;
- uses a deterministic systematic sample only for the price/demand figure;
- preserves chronological ordering;
- does not modify source data.

## Phase 17 re-audit record

The plan was reviewed against the implementation during the Phase 17 re-audit.
Two clarifications were needed and are recorded above:

1. **Covariance** was listed as "where applicable" but was never produced; it
   is now reported in `statistical_correlations.csv`.
2. **"Promotion versus non-promotion"** was implemented as a comparison of
   promoted rows by discount-rate sign, which excluded the 5,912,426 rows with
   no discount record. The comparison is now presence-based as specified, with
   the rate-sign breakdown retained as a labelled secondary comparison.

The plan's store and department "group comparison" requirement is satisfied by
descriptive magnitude reporting, and the reason significance testing is not
applied is stated rather than left implicit.

An addition beyond the original plan was made deliberately: a monthly activity
diagnostic (`statistical_monthly_activity.csv`) that distinguishes a coverage
or assortment change from a demand change before a level shift is modelled as
trend.
