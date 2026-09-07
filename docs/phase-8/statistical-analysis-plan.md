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
- Covariance where applicable
- Simple linear regression for price-demand analysis

### Temporal analysis

- Daily demand trend
- Lagged autocorrelation

### Group comparison

- Store-level demand comparison
- Department-level demand comparison
- Promotion versus non-promotion comparison

### Statistical significance

Where assumptions permit, significance tests are calculated and reported
using p-values.

Statistical significance is not treated as evidence of causation.

## Reproducibility

The analysis:

- uses deterministic processing;
- uses fixed analytical definitions;
- processes the source dataset in chunks;
- preserves chronological ordering;
- does not modify source data.