# Phase 7 — Exploratory Data Analysis Methodology

## 1. Data source

The Phase 6 integrated dataset is used as the analytical source.

Raw datasets are not modified.

## 2. Large-data processing

The integrated dataset contains millions of rows.

Chunked processing is therefore used for aggregate calculations.

This avoids requiring the complete dataset to be loaded into memory for every
analysis.

The pipeline makes three passes over the integrated dataset: one aggregation
pass over the 16 analytical columns, and two correlation passes over the 7
numeric columns (one to determine a per-column centering constant and one to
accumulate the pairwise moments). Peak memory stays at one chunk, so the
complete dataset is analysed without ever being held in memory.

## 3. Structural analysis

The analysis verifies:

* required columns
* date representation
* numerical measures
* missing values
* non-finite values
* temporal coverage
* number of stores
* number of products

Non-finite values are counted per numeric column and reported as
`infinite_<column>` metrics in `data/analysis/eda_summary.csv`. Missing
promotion and markdown values are reported as the absence of a matching
auxiliary record rather than as a defect, and record frequency is additionally
reported from `discount_record_count` and `markdown_record_count` so that
presence is measured independently of value usability.

## 4. Univariate analysis

Demand, revenue, and product-level demand are examined using descriptive
statistics and distributions.

Item-level demand is summarised by quartiles, the interquartile range and the
upper fence (Q3 + 1.5 x IQR), together with the number of items above the
fence and their share of total demand. Demand concentration is summarised by
the share of total demand held by the top 1% of items and by the top 10
items.

## 5. Temporal analysis

Demand is aggregated by month to identify:

* trend
* recurring patterns
* high-demand periods
* low-demand periods

Month-level record counts are reported alongside quantity so that a change in
coverage can be distinguished from a change in demand. The partial first
month (2022-08, which covers only 2022-08-28 onward) is identified as such.

## 6. Store analysis

Demand and revenue are aggregated by store.

This identifies differences in store-level demand contribution.

Store shares of total demand and total revenue are reported together, because
a store can hold a different share of each.

## 7. Product analysis

Demand is aggregated by item and department.

The highest-demand products and departments are identified descriptively.

Rows with no catalog match are retained and reported as an explicit
"(unmatched)" group in the department summary and in the department chart,
rather than being dropped.

Average demand per record is reported for the leading item and department so
that bulk or aggregated product lines can be distinguished from typical
consumer products.

## 8. Relationship analysis

Numeric variables are examined using pairwise-complete Pearson correlation
coefficients calculated from the complete integrated dataset.The coefficients are accumulated in chunks as pairwise counts, centered sums,
centered products and centered squares. Values are centered on the mean of the
finite values of each column before accumulation, which keeps the calculation
numerically stable for sparse columns. Each pairwise coefficient uses only the
rows where both variables are finite, and a variable correlates with itself as
exactly 1.

Non-finite values (missing or infinite) are excluded pairwise and quantified
in the summary. No sampling is used, and no random seed is required.

Correlation is interpreted as association rather than causation.

## 9. Outlier analysis

The EDA stage identifies unusual demand behaviour for investigation.

Unusual demand is identified at item level using the interquartile-range
upper fence on total item demand. The number of items above the fence and
their share of total demand are recorded, together with the quartiles and the
fence value.

An observation is not removed merely because it is statistically unusual.

The Phase 5 quality process already distinguishes potential outliers from
records that violate documented validity rules; record-level validity
outliers therefore remain Phase 5's responsibility and are not recomputed
here.

## 10. Visualization

Charts are produced for:

* demand over time
* monthly demand
* store demand
* department demand
* item-level demand distribution

Categorical chart axes are rendered through a label helper that replaces
missing labels with an explicit name, so a category without a catalog match
is shown as "(unmatched)" instead of aborting the chart. Label handling does
not alter the underlying values.

## 11. Forecasting relevance

EDA findings are used to inform later feature engineering and model design.

Potential considerations include:

* temporal structure
* demand concentration
* store heterogeneity
* product heterogeneity
* price relationships
* promotion effects
* the apparent level shift between 2023-11 and 2023-12, which must be
  distinguished from demand growth before it is modelled as trend; the Phase 8
  re-audit later established that it is a coverage and assortment change
  (store 4 first appears on 2023-12-13) rather than demand growth

## 12. Leakage prevention

No future information is used to create predictive features during Phase 7.

This phase is descriptive rather than predictive.

## Phase 17 Re-Audit Record

**Audit status:** AUDITED — COMPLETE

The Phase 17 re-audit applied the following methodological changes, all of
which are reflected under the headings above:

| Section | Change |
|---|---|
| 2 | Documented the three-pass chunked execution and constant-memory behaviour |
| 3 | Added non-finite quantification and record-frequency reporting |
| 4 | Added item-level quartiles, IQR fence and concentration metrics |
| 5 | Added month-level record counts and the partial-month note |
| 6 | Added revenue share alongside demand share |
| 7 | Added the explicit unmatched-department group and per-record averages |
| 8 | Replaced the deterministic sample with exact full-dataset pairwise-complete correlation; documented centering and non-finite exclusion |
| 9 | Implemented the previously documented outlier identification at item level |
| 10 | Documented categorical label handling |
| 11 | Added the level shift to the forecasting considerations |

Justification: the previous correlation sample gave equal weight to every
chunk irrespective of size and reused one seed per chunk, producing
coefficients that differed from the exact full-dataset values by up to 0.179
(including a sign change) while appearing in the results documentation as
authoritative. Sections 4, 5, 6, 7 and 9 close requirements that the phase
purpose, the EDA questions, this methodology and the course-content coverage
already claimed but that had no implementation.

Verification: the exact correlation procedure was validated against two
independent calculations (a direct pairwise-complete computation and a
centered accumulator prototype) for all 21 coefficient pairs; the model
reproduced every one to four decimal places, and the diagonal is reported as
exactly 1. Phase 7 tests were extended from 10 to 34 and the full suite passes
with 193 tests. The pipeline completed in 61-63 seconds and every artifact was
inspected against the summaries it derives from.
