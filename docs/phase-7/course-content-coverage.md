# Phase 7 — Course Content Coverage

## Purpose

This document records the internship-course concepts demonstrated through
exploratory data analysis.

## Analyze

### Concept: Analyse data to answer questions

**Application:** Phase 7 converts the project questions into descriptive
analyses of demand, stores, products, time, prices, and promotional activity.
Each planned question is answered by a generated artifact: overall demand,
temporal behaviour, store behaviour, product behaviour, concentration, price
association, promotion frequency, and markdown frequency.

### Concept: Sorting and filtering

**Application:** Aggregated outputs are sorted to identify high-demand stores,
departments, and products, and to rank items by aggregate demand for the
concentration metrics.

### Concept: Aggregation

**Application:** Millions of sales observations are aggregated by month, store,
department, and item. The complete 7,431,026-row dataset is aggregated; no
sample is used.

### Concept: Patterns

**Application:** Temporal and product-level summaries are used to identify
demand patterns. Month-level record counts accompany quantity so that a change
in coverage can be distinguished from a change in demand; a level shift between
2023-11 and 2023-12 is identified this way. In 2024 demand peaks from March to
August.

### Concept: Relationships

**Application:** Numeric variables are examined through pairwise-complete
Pearson correlation over the complete dataset. All associations are weak to
moderate; the strongest is demand against markdown quantity (0.6979 over the
8,709 marked-down rows) and demand against sales value (0.4074). Correlation is
reported as association.

### Concept: Outliers

**Application:** Unusual demand is identified at item level using the
interquartile-range upper fence on total item demand (Q1 21.0, median 122.974,
Q3 699.0, fence 1,716.0). 4,007 items lie above the fence and together hold
85.27% of demand. The observations are flagged for investigation and none are
removed, which matches the Phase 5 record-level outlier screening.

## Data quality

### Concept: Validate data before analysis

**Application:** The EDA pipeline verifies that the integrated dataset exists
and that the required integrated schema is present before performing analysis,
and fails with an actionable message naming the expected file and the phase
that produces it.

### Concept: Data completeness

**Application:** Missing values are quantified across the analytical columns.
Promotion and markdown presence is additionally counted from the record-count
columns, because a left join leaves a value missing when no auxiliary record
exists.

### Concept: Invalid and extreme values

**Application:** Non-finite values are quantified per numeric column (6,760 in
`promo_discount_rate` when the audit was performed). They are excluded from the
correlation calculation and reported, and the cause is documented for the phase
that produces the column. The Phase 8 re-audit then guarded the two Phase 6
divisions at source, so both columns now contain 0 infinite values.

## Visualization

### Concept: Visual analysis

**Application:** Demand trends, store differences, department contributions,
and demand distributions are visualized in five charts. Categories without a
catalog match are shown with an explicit "(unmatched)" label instead of being
dropped or causing an error.

### Concept: Communicating findings

**Application:** A findings file accompanies the numerical summaries and
charts, and presents headline metrics without floating-point artefacts.

## Analytical thinking

The analysis separates:

* descriptive observation
* association
* interpretation
* forecasting implications

Causal claims are not made solely from EDA results. The promotion comparison is
explicitly described as an association because promotion targeting is not
random.

## Concepts deferred to later phases

### Forecasting models

Not performed during EDA.

### Feature engineering

Only implications are identified. Predictive features are created later.

### Model evaluation

Not applicable because no forecasting model is trained in Phase 7.

### Final dashboard

Visualization artifacts produced here support later visualization and dashboard
work but do not constitute the final dashboard.

## Evidence

Implementation:

`scripts/exploratory_data_analysis.py`

Tests:

`tests/test_exploratory_data_analysis.py` (34 tests)

Outputs:

`data/analysis/eda_*.csv`

Figures:

`reports/figures/eda_*.png`

## Phase 17 Re-Audit Record

**Audit status:** AUDITED — COMPLETE

The "Concept: Outliers" application previously described identification of
unusual demand that was not implemented anywhere in the script, and the
"Relationships" application claimed sampling that was not documented in the
coverage record. During the re-audit:

* item-level outlier identification was implemented (interquartile-range
  upper fence, item count above the fence, and the share of demand they hold),
  so the Outliers claim is now backed by output;
* correlation was moved from a deterministic 4% sample to an exact
  full-dataset calculation, so the Relationships claim now holds without
  qualification;
* promotion and markdown record frequency was added, completing the
  question-driven coverage;
* non-finite quantification was added to the data-quality coverage.

No course-content evidence was removed or reduced. The phase still
demonstrates aggregation, sorting, pattern identification, relationship
analysis, outlier identification, data completeness, invalid-value handling,
visual analysis and findings communication using Python.
