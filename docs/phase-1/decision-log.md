# Decision Log

## Purpose

Record important project decisions and the reasoning behind them.

## Decision D001

### Decision

Use retail demand forecasting as the central business problem.

### Reason

The project requirement explicitly defines the goal as forecasting product demand to optimize inventory.

### Status

APPROVED

---

## Decision D002

### Decision

Use the six-stage analytical lifecycle:

Ask → Prepare → Process → Analyze → Share → Act

### Reason

This is the course's core analytical methodology and provides a structured end-to-end workflow.

### Status

APPROVED

---

## Decision D003

### Decision

ARIMA is mandatory.

### Reason

The retail project requirement explicitly allows and requires a forecasting approach such as ARIMA, Prophet or LSTM, and ARIMA has been selected as a mandatory project component.

### Status

APPROVED

---

## Decision D004

### Decision

Evaluate whether Prophet or LSTM should be added as the second major forecasting approach.

### Reason

The project should demonstrate the permitted forecasting approaches without introducing unnecessary dependencies or complexity before dataset characteristics are known.

### Status

RESOLVED

### Resolution

The dataset and technical suitability were reviewed during the forecasting phases. Phase 11 records that Prophet and LSTM were not artificially added: the implemented models are the naive baseline, the seasonal-naive baseline and ARIMA(1,1,1). The decision to retain these approaches is documented in `docs/phase-11/course-content-coverage.md` and `data/analysis/forecasting_findings.txt`.

---

## Decision D005

### Decision

Use RMSE and MAPE for forecast evaluation where appropriate.

### Reason

These are explicitly required by the project guideline.

### Status

APPROVED

---

## Decision D006

### Decision

Do not define the final forecast horizon until the dataset is inspected.

### Reason

Forecast frequency and historical coverage determine a sensible forecast horizon.

### Status

APPROVED

---

## Decision D007

### Decision

Do not claim promotion or holiday effects as causal effects without appropriate evidence.

### Reason

Observed relationships do not automatically establish causality.

### Status

APPROVED

---

## Decision D008

### Decision

Do not select the final forecasting model before evaluation.

### Reason

Model superiority must be demonstrated using consistent evaluation rather than assumed in advance.

### Status

APPROVED

---

## Future Decisions

Major decisions concerning:

- Dataset
- Forecast frequency
- Forecast horizon
- Model selection
- Feature engineering
- Deployment platform

will be recorded here as they are made.

### Phase 17 Re-Audit Note

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
