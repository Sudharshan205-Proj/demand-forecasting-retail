# Business Requirements

## 1. Objective

Build a system that forecasts future retail product demand and communicates the results in a way that supports inventory planning.

## 2. Functional Requirements

### BR-001 — Historical Demand

The system shall use historical retail sales/demand data.

### BR-002 — Promotions

The analysis shall incorporate promotional information when reliable promotional data is available.

### BR-003 — Holidays

The analysis shall incorporate holiday information when reliable holiday data is available.

**Outcome (Phase 17 final audit): NOT APPLICABLE.** The requirement is
conditional on reliable holiday data being available. Phase 2 established that
no holiday field exists in the selected dataset ("VERIFIED ABSENT"), so the
condition was never satisfied and no holiday analysis is claimed. If an external
holiday calendar is introduced later, this requirement becomes applicable again;
the pilot hypotheses and analytical questions are already drafted for it.

### BR-004 — Time-Series Forecasting

The system shall produce forecasts of future demand.

### BR-005 — Baseline

The project shall establish at least one simple baseline forecast.

### BR-006 — ARIMA

The project shall implement ARIMA as a required forecasting approach.

### BR-007 — Additional Forecasting Approach

The project shall evaluate whether Prophet or LSTM should be implemented as an additional forecasting approach.

The decision will be based on:

- Dataset characteristics
- Course/project requirements
- Technical suitability
- Reproducibility
- Complexity
- Evaluation results

### BR-008 — Forecast Evaluation

The project shall evaluate forecasts using RMSE and MAPE where appropriate.

### BR-009 — Model Comparison

Forecasting approaches shall be compared using consistent evaluation procedures.

### BR-010 — Inventory Insights

The system shall translate forecasts into inventory-planning insights.

### BR-011 — Visualization

The project shall provide clear visualizations of historical demand and forecasts.

### BR-012 — Dashboard

The project shall provide an interactive Tableau dashboard.

### BR-013 — Application

The project shall provide a user-facing forecasting application.

### BR-014 — Reproducibility

Important analysis and model results shall be reproducible.

### BR-015 — Documentation

The project shall document methodology, assumptions, data, models, evaluation and limitations.

## 3. Non-Functional Requirements

### NFR-001 — Maintainability

Code shall be modular and understandable.

### NFR-002 — Security

Secrets must not be committed.

### NFR-003 — Validation

Data and model outputs shall be validated.

### NFR-004 — Testing

Appropriate automated and manual testing shall be performed.

### NFR-005 — Documentation

Documentation shall reflect actual implementation.

### NFR-006 — Reproducibility

Important experiments shall record relevant configuration and preprocessing decisions.

### NFR-007 — Time-Series Integrity

Temporal ordering shall be preserved.

### NFR-008 — Leakage Prevention

Future information shall not be used to train models that are evaluated on that future period.

## 4. Business Success Criteria

The project will be considered successful when it:

1. Produces reproducible demand forecasts.
2. Provides quantitative forecast evaluation.
3. Identifies meaningful demand patterns.
4. Investigates promotion and holiday relationships where data supports them.
5. Provides actionable inventory-planning insights.
6. Communicates results clearly to non-technical stakeholders.
7. Provides a working application.
8. Provides complete documentation.

## 5. Important Limitation

These requirements define intended functionality.

They do not constitute evidence that the functionality has already been implemented.