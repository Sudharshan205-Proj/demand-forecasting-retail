# Business Requirements

## 1. Objective

Build a system that forecasts future retail product demand and communicates the
results in a way that supports inventory planning.

## 2. Functional requirements

### BR-001 — Historical demand

The system uses historical retail sales/demand data.

### BR-002 — Promotions

The analysis incorporates promotional information from the dataset's markdown
and discount records.

### BR-003 — Holidays

The analysis incorporates holiday information when reliable holiday data is
available.

**Outcome: not applicable.** The requirement is conditional on reliable holiday
data being available. Phase 2 established that no holiday field exists in the
selected dataset, so the condition is never satisfied and no holiday analysis is
claimed. If an external holiday calendar is introduced later, this requirement
becomes applicable again; the hypotheses and analytical questions are already
drafted for it.

### BR-004 — Time-series forecasting

The system produces forecasts of future demand.

### BR-005 — Baseline

The project establishes simple baseline forecasts (naive and seasonal-naive).

### BR-006 — ARIMA

The project implements ARIMA as the mandatory forecasting approach.

### BR-007 — Additional forecasting approach

The project assesses whether Prophet or LSTM should be implemented as an
additional forecasting approach.

**Outcome:** assessed and deliberately not implemented. The additional permitted
approach is the deterministic feature-based gradient-boosting candidate
(`feature_gbm`), selected on technical suitability, reproducibility and
complexity. Recorded in
[`../phase-11/course-content-coverage.md`](../phase-11/course-content-coverage.md).

### BR-008 — Forecast evaluation

The project evaluates forecasts using RMSE and MAPE.

### BR-009 — Model comparison

Forecasting approaches are compared using consistent evaluation procedures.

### BR-010 — Inventory insights

The system translates forecasts into inventory-planning insights.

### BR-011 — Visualization

The project provides visualizations of historical demand and forecasts.

### BR-012 — Dashboard

The project provides an interactive Tableau dashboard.

### BR-013 — Application

The project provides a user-facing forecasting application.

### BR-014 — Reproducibility

Important analysis and model results are reproducible.

### BR-015 — Documentation

The project documents methodology, assumptions, data, models, evaluation and
limitations.

## 3. Non-functional requirements

- **NFR-001 Maintainability** — code is modular and understandable.
- **NFR-002 Security** — secrets are not committed.
- **NFR-003 Validation** — data and model outputs are validated.
- **NFR-004 Testing** — automated and manual testing is performed.
- **NFR-005 Documentation** — documentation reflects the implementation.
- **NFR-006 Reproducibility** — experiments record their configuration and
  preprocessing decisions.
- **NFR-007 Time-series integrity** — temporal ordering is preserved.
- **NFR-008 Leakage prevention** — future information is not used to train
  models evaluated on that future period.

## 4. Business success criteria

The project is successful because it:

1. Produces reproducible demand forecasts.
2. Provides quantitative forecast evaluation.
3. Identifies meaningful demand patterns.
4. Investigates promotion relationships and records the holiday question as not
   applicable.
5. Provides actionable inventory-planning insights.
6. Communicates results clearly to non-technical stakeholders.
7. Provides a working application.
8. Provides complete documentation.

## 5. Requirement traceability

Requirement-by-requirement status is recorded in
[`requirements-traceability.md`](requirements-traceability.md).
