# Phase 6 — Course Content Coverage

## Purpose

This document records how Phase 6 applies relevant internship-course concepts to
the retail demand forecasting project.

## Data preparation

### Concept: Data from multiple sources

**Application:** Phase 6 combines sales, store, product, price, markdown,
promotion, online-channel, and product-matrix data.

### Concept: Data types

**Application:** Integration keys are normalised into consistent date, item,
and store representations before joining.

### Concept: Data quality

**Application:** Row counts, uniqueness, referential integrity, and join
cardinality are validated.

## SQL and relational concepts

### Concept: Joins

**Application:** Store and catalog dimensions are joined to the sales fact using
appropriate keys.

### Concept: Join cardinality

**Application:** Many-to-one validation is used to prevent accidental row
multiplication.

### Concept: Aggregation

**Application:** Price, markdown, promotion, and online records are aggregated
to the canonical analytical grain before integration.

### Concept: Data validation

**Application:** The pipeline checks row preservation, duplicate keys, and
referential integrity.

## Analytical reasoning

### Concept: Tool selection

The project uses pandas for the large file integration because the datasets are
CSV-based and the primary sales file contains millions of rows.

### Concept: Documentation

Integration decisions, assumptions, validation rules, and results are recorded
in project documentation.

## Concepts intentionally deferred

### Feature engineering

Not performed as a primary Phase 6 objective. Chronological feature creation,
including lagged variables and forward-filled prices, belongs to the later
forecasting preparation stages.

### Modeling

No forecasting model is trained in Phase 6.

### Visualization

No dashboard is produced in Phase 6.

## Evidence

Implementation:

`scripts/integrate_retail_data.py`

Tests:

`tests/test_integrate_retail_data.py`

Output:

`data/processed/integrated_retail_data.csv`

Quality report:

`data/processed/integration_quality_report.csv`

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
