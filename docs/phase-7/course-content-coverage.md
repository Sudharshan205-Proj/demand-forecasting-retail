# Phase 7 — Course Content Coverage

## Purpose

This document records the internship-course concepts demonstrated through
exploratory data analysis.

## Analyze

### Concept: Analyse data to answer questions

**Application:** Phase 7 converts the project questions into descriptive analyses
of demand, stores, products, time, prices and promotional activity. Each planned
question is answered by a generated artifact: overall demand, temporal behaviour,
store behaviour, product behaviour, concentration, price association, promotion
frequency and markdown frequency.

### Concept: Sorting and filtering

**Application:** Aggregated outputs are sorted to identify high-demand stores,
departments and products, and to rank items by aggregate demand for the
concentration metrics.

### Concept: Aggregation

**Application:** Millions of sales observations are aggregated by month, store,
department and item. The complete 7,431,026-row dataset is aggregated; no sample
is used.

### Concept: Patterns

**Application:** Temporal and product-level summaries identify demand patterns.
Month-level record counts accompany quantity so that a change in coverage can be
distinguished from a change in demand; a level shift between 2023-11 and 2023-12
is identified this way. In 2024 demand peaks from March to August.

### Concept: Relationships

**Application:** Numeric variables are examined through pairwise-complete Pearson
correlation over the complete dataset. All associations are weak to moderate; the
strongest is demand against markdown quantity (0.6979 over the 8,709 marked-down
rows) and demand against sales value (0.4074). Correlation is reported as
association.

### Concept: Outliers

**Application:** Unusual demand is identified at item level using the
interquartile-range upper fence on total item demand (Q1 21.0, median 122.974,
Q3 699.0, fence 1,716.0). 4,007 items lie above the fence and together hold
85.27% of demand. The observations are flagged for investigation and none are
removed, matching the Phase 5 record-level outlier screening.

## Data quality

### Concept: Validate data before analysis

**Application:** The EDA pipeline verifies that the integrated dataset exists and
that the required integrated schema is present before performing analysis, and
fails with an actionable message naming the expected file and the phase that
produces it.

### Concept: Data completeness

**Application:** Missing values are quantified across the analytical columns.
Promotion and markdown presence is additionally counted from the record-count
columns, because a left join leaves a value missing when no auxiliary record
exists.

### Concept: Invalid and extreme values

**Application:** Non-finite values are quantified per numeric column and excluded
from the correlation calculation. The two Phase 6 divisions guard their
denominators, so `promo_discount_rate` and `markdown_discount` contain 0 infinite
values and the affected rows are left missing instead.

## Visualization

### Concept: Visual analysis

**Application:** Demand trends, store differences, department contributions and
demand distributions are visualized in five charts. Categories without a catalog
match are shown with an explicit "(unmatched)" label instead of being dropped or
causing an error.

### Concept: Communicating findings

**Application:** A findings file accompanies the numerical summaries and charts
and presents headline metrics without floating-point artefacts.

## Analytical thinking

The analysis separates descriptive observation, association, interpretation and
forecasting implications. Causal claims are not made solely from EDA results. The
promotion comparison is described as an association because promotion targeting
is not random.

## Concepts delivered by later phases

- **Feature engineering** — only implications are identified; predictive features
  are created in Phases 9–10.
- **Forecasting and model evaluation** — no model is trained in Phase 7.
- **Final dashboard** — the Phase 7 figures support the later visualization work
  but are not the final dashboard.

## Evidence

- Implementation: `scripts/exploratory_data_analysis.py`
- Tests: `tests/test_exploratory_data_analysis.py` (34 tests)
- Outputs: `data/analysis/eda_*.csv`
- Figures: `reports/figures/eda_*.png`
