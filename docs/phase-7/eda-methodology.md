# Phase 7 — Exploratory Data Analysis Methodology

## 1. Data source

The Phase 6 integrated dataset is used as the analytical source.

Raw datasets are not modified.

## 2. Large-data processing

The integrated dataset contains millions of rows.

Chunked processing is therefore used for aggregate calculations.

This avoids requiring the complete dataset to be loaded into memory for every
analysis.

## 3. Structural analysis

The analysis verifies:

* required columns
* date representation
* numerical measures
* missing values
* temporal coverage
* number of stores
* number of products

## 4. Univariate analysis

Demand, revenue, and product-level demand are examined using descriptive
statistics and distributions.

## 5. Temporal analysis

Demand is aggregated by month to identify:

* trend
* recurring patterns
* high-demand periods
* low-demand periods

## 6. Store analysis

Demand and revenue are aggregated by store.

This identifies differences in store-level demand contribution.

## 7. Product analysis

Demand is aggregated by item and department.

The highest-demand products and departments are identified descriptively.

## 8. Relationship analysis

Numeric variables are sampled deterministically and examined using correlation
matrices.

Correlation is interpreted as association rather than causation.

## 9. Outlier analysis

The EDA stage identifies unusual demand behaviour for investigation.

An observation is not removed merely because it is statistically unusual.

The Phase 5 quality process already distinguishes potential outliers from
records that violate documented validity rules.

## 10. Visualization

Charts are produced for:

* demand over time
* monthly demand
* store demand
* department demand
* item-level demand distribution

## 11. Forecasting relevance

EDA findings are used to inform later feature engineering and model design.

Potential considerations include:

* temporal structure
* demand concentration
* store heterogeneity
* product heterogeneity
* price relationships
* promotion effects

## 12. Leakage prevention

No future information is used to create predictive features during Phase 7.

This phase is descriptive rather than predictive.
