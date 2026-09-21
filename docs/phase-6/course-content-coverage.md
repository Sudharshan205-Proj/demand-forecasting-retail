# Phase 6 — Course Content Coverage

## Purpose

This document records how Phase 6 applies relevant internship-course concepts to
the retail demand forecasting project.

## Data preparation

| Concept | Application |
|---|---|
| Data from multiple sources | Phase 6 combines sales, store, product, price, markdown, promotion, online-channel and product-matrix data |
| Data types | Integration keys are normalised into consistent date, item and store representations before joining |
| Data quality | Row counts, uniqueness, referential integrity and join cardinality are validated |

## SQL and relational concepts

| Concept | Application |
|---|---|
| Joins | Store and catalog dimensions are joined to the sales fact using appropriate keys |
| Join cardinality | Many-to-one validation prevents accidental row multiplication |
| Aggregation | Price, markdown, promotion and online records are aggregated to the canonical analytical grain before integration |
| Data validation | The pipeline checks row preservation, duplicate keys and referential integrity |

## Analytical reasoning

| Concept | Application |
|---|---|
| Tool selection | pandas is used for the large-file integration because the datasets are CSV-based and the primary sales file contains millions of rows |
| Documentation | Integration decisions, assumptions, validation rules and results are recorded in the project documentation |

## Concepts delivered by other phases

- **Feature engineering** — chronological feature creation, including lagged
  variables and forward-filled prices, belongs to Phases 9–10.
- **Modelling** — no forecasting model is trained in Phase 6.
- **Visualization** — no dashboard is produced in Phase 6.

## Evidence

- Implementation: `scripts/integrate_retail_data.py`
- Tests: `tests/test_integrate_retail_data.py`
- Output: `data/processed/integrated_retail_data.csv`
- Quality report: `data/processed/integration_quality_report.csv`
