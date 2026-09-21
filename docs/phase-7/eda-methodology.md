# Phase 7 — Exploratory Data Analysis Methodology

## 1. Data source

The Phase 6 integrated dataset is the analytical source. Raw datasets are not
modified.

## 2. Large-data processing

The integrated dataset contains millions of rows, so chunked processing is used
for aggregate calculations rather than loading the complete dataset into memory
for every analysis.

The pipeline makes three passes over the integrated dataset: one aggregation
pass over the 16 analytical columns, and two correlation passes over the 7
numeric columns (one to determine a per-column centering constant and one to
accumulate the pairwise moments). Peak memory stays at one chunk, so the
complete dataset is analysed without ever being held in memory.

## 3. Structural analysis

The analysis verifies required columns, date representation, numerical measures,
missing values, non-finite values, temporal coverage, store count and product
count.

Non-finite values are counted per numeric column and reported as
`infinite_<column>` metrics in `data/analysis/eda_summary.csv`. Missing promotion
and markdown values are reported as the absence of a matching auxiliary record
rather than as a defect, and record frequency is additionally reported from
`discount_record_count` and `markdown_record_count` so that presence is measured
independently of value usability.

## 4. Univariate analysis

Demand, revenue and product-level demand are examined using descriptive
statistics and distributions.

Item-level demand is summarised by quartiles, the interquartile range and the
upper fence (Q3 + 1.5 × IQR), together with the number of items above the fence
and their share of total demand. Demand concentration is summarised by the share
of total demand held by the top 1% of items and by the top 10 items.

## 5. Temporal analysis

Demand is aggregated by month to identify trend, recurring patterns, and high-
and low-demand periods.

Month-level record counts are reported alongside quantity so that a change in
coverage can be distinguished from a change in demand. The partial first month
(2022-08, which covers only 2022-08-28 onward) is identified as such.

## 6. Store analysis

Demand and revenue are aggregated by store, identifying differences in
store-level demand contribution. Store shares of total demand and total revenue
are reported together, because a store can hold a different share of each.

## 7. Product analysis

Demand is aggregated by item and department, and the highest-demand products and
departments are identified descriptively.

Rows with no catalog match are retained and reported as an explicit "(unmatched)"
group in the department summary and chart rather than dropped. Average demand per
record is reported for the leading item and department so that bulk or aggregated
product lines can be distinguished from typical consumer products.

## 8. Relationship analysis

Numeric variables are examined using pairwise-complete Pearson correlation
coefficients calculated from the complete integrated dataset. The coefficients
are accumulated in chunks as pairwise counts, centered sums, centered products
and centered squares. Values are centered on the mean of the finite values of
each column before accumulation, which keeps the calculation numerically stable
for sparse columns. Each pairwise coefficient uses only the rows where both
variables are finite, and a variable correlates with itself as exactly 1.

Non-finite values (missing or infinite) are excluded pairwise and quantified in
the summary. No sampling is used, and no random seed is required. Correlation is
interpreted as association rather than causation.

## 9. Outlier analysis

Unusual demand is identified at item level using the interquartile-range upper
fence on total item demand. The number of items above the fence and their share
of total demand are recorded, together with the quartiles and the fence value. An
observation is not removed merely because it is statistically unusual.

The Phase 5 quality process distinguishes potential outliers from records that
violate documented validity rules; record-level validity outliers therefore
remain Phase 5's responsibility and are not recomputed here.

## 10. Visualization

Charts are produced for demand over time, monthly demand, store demand,
department demand and item-level demand distribution.

Categorical chart axes are rendered through a label helper that replaces missing
labels with an explicit name, so a category without a catalog match is shown as
"(unmatched)" instead of aborting the chart. Label handling does not alter the
underlying values.

## 11. Forecasting relevance

EDA findings inform the later feature engineering and model design.
Considerations include temporal structure, demand concentration, store and
product heterogeneity, price relationships, promotion effects, and the apparent
level shift between 2023-11 and 2023-12. Phase 8 established that the shift is a
coverage and assortment change (store 4 first appears on 2023-12-13) rather than
demand growth.

## 12. Leakage prevention

No future information is used to create predictive features during Phase 7. This
phase is descriptive rather than predictive.
