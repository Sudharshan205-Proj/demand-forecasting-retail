# Decision Log

## Purpose

Record the important business and analytical decisions made during Phase 1 and
the reasoning behind them.

## Decision D001

### Decision

Use retail demand forecasting as the central business problem.

### Reason

The project requirement defines the goal as forecasting product demand to
optimize inventory.

### Status

APPROVED

---

## Decision D002

### Decision

Use the six-stage analytical lifecycle:

Ask → Prepare → Process → Analyze → Share → Act

### Reason

This is the course's core analytical methodology and provides a structured
end-to-end workflow.

### Status

APPROVED

---

## Decision D003

### Decision

Implement ARIMA as a mandatory forecasting model.

### Reason

The retail project requirement requires a forecasting approach such as ARIMA,
Prophet or LSTM, and ARIMA is the selected mandatory component.

### Status

APPROVED

---

## Decision D004

### Decision

Assess whether Prophet or LSTM should be added as a second major forecasting
approach.

### Reason

The project should demonstrate the permitted forecasting approaches without
introducing unnecessary dependencies or complexity before the dataset
characteristics are known.

### Status

RESOLVED

### Resolution

The dataset and technical suitability were reviewed during the forecasting
phases. Prophet and LSTM were assessed and deliberately not implemented; the
additional permitted approach is the deterministic feature-based
gradient-boosting candidate (`feature_gbm`) over the engineered features, which
competes against the naive, seasonal-naive and ARIMA(1,1,1) models. The
assessment is recorded in `docs/phase-11/course-content-coverage.md` and
`docs/phase-12/model-evaluation-and-tuning-results.md`.

---

## Decision D005

### Decision

Use RMSE and MAPE for forecast evaluation.

### Reason

These are explicitly required by the project guideline.

### Status

APPROVED

---

## Decision D006

### Decision

Define the forecast horizon after the dataset is inspected.

### Reason

Forecast frequency and historical coverage determine a sensible forecast
horizon.

### Status

APPROVED

### Resolution

The dataset supports daily forecasting at the date × item × store grain, with a
114-day validation period (2024-02-11 → 2024-06-03) and lead-time scenarios of 7,
14 and 28 days. Recorded in `docs/phase-9/time-series-methodology.md` and
`docs/phase-13/forecasting-and-inventory-insights-methodology.md`.

---

## Decision D007

### Decision

Do not claim promotion or holiday effects as causal effects without appropriate
evidence.

### Reason

Observed relationships do not automatically establish causality.

### Status

APPROVED

---

## Decision D008

### Decision

Select the final forecasting model through evaluation rather than in advance.

### Reason

Model superiority is demonstrated using consistent evaluation rather than
assumed.

### Status

APPROVED

---

## Decisions recorded in later phases

Decisions made after Phase 1 are recorded in the phase that owns them:

| Decision | Recorded in |
|---|---|
| Dataset selection | `docs/phase-2/data-acquisition.md` |
| Forecast frequency and horizon | `docs/phase-9/time-series-methodology.md` |
| Feature engineering | `docs/phase-10/feature-engineering-methodology.md` |
| Model selection | `docs/phase-12/model-evaluation-and-tuning-results.md` |
| Deployment platform | `docs/phase-16/deployment-plan.md` |
