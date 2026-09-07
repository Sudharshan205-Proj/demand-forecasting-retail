# Phase 7 — Course Content Coverage

## Purpose

This document records the internship-course concepts demonstrated through
exploratory data analysis.

## Analyze

### Concept: Analyse data to answer questions

**Application:** Phase 7 converts the project questions into descriptive
analyses of demand, stores, products, time, prices, and promotional activity.

### Concept: Sorting and filtering

**Application:** Aggregated outputs are sorted to identify high-demand stores,
departments, and products.

### Concept: Aggregation

**Application:** Millions of sales observations are aggregated by month, store,
department, and item.

### Concept: Patterns

**Application:** Temporal and product-level summaries are used to identify
demand patterns.

### Concept: Relationships

**Application:** Numeric variables are examined through correlation analysis.

### Concept: Outliers

**Application:** Unusual demand observations are identified for investigation
rather than automatically deleted.

## Data quality

### Concept: Validate data before analysis

**Application:** The EDA pipeline verifies the required integrated schema before
performing analysis.

### Concept: Data completeness

**Application:** Missing values are quantified across the analytical columns.

## Visualization

### Concept: Visual analysis

**Application:** Demand trends, store differences, department contributions,
and demand distributions are visualized.

### Concept: Communicating findings

**Application:** A findings file accompanies the numerical summaries and charts.

## Analytical thinking

The analysis separates:

* descriptive observation
* association
* interpretation
* forecasting implications

Causal claims are not made solely from EDA results.

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

`tests/test_exploratory_data_analysis.py`

Outputs:

`data/analysis/eda_*.csv`

Figures:

`reports/figures/eda_*.png`
