# Hypothesis Register

## Purpose

Hypotheses provide testable expectations that guide the analysis. They are not
conclusions.

Each hypothesis carries a verdict supported by the evidence produced in Phases
7–13. A verdict records what that evidence supports; it does not by itself
promote a hypothesis to a finding.

## H1 — Historical demand pattern

### Hypothesis

Retail demand contains identifiable patterns over time.

### Expected evidence

- Time-series visualization
- Aggregated demand
- Trend analysis
- Seasonal analysis

### Status

**SUPPORTED.** Phase 7 established trend, recurring seasonal structure and
demand concentration from the complete integrated dataset
(`docs/phase-7/eda-results.md`).

---

## H2 — Seasonality

### Hypothesis

Demand varies systematically across recurring time periods.

### Expected evidence

- Time-series decomposition or appropriate seasonal analysis
- Periodic demand comparisons
- Forecasting diagnostics

### Status

**SUPPORTED.** Phase 8 measured weekly seasonality in demand
(`docs/phase-8/statistical-results.md`), and the Phase 11 seasonal-naive
benchmark reproduces the seven-day cycle exactly
(`docs/phase-11/forecasting-models-results.md`).

---

## H3 — Promotions

### Hypothesis

Promotional periods are associated with different demand levels compared with
non-promotional periods.

### Expected evidence

- Promotional vs non-promotional comparison
- Product-level comparison
- Statistical analysis where appropriate

### Important limitation

Association is not interpreted as causation.

### Status

**SUPPORTED as an association only.** Phase 8 measured promotional and markdown
demand against non-promotional periods
(`docs/phase-8/statistical-results.md`). The limitation still applies: no causal
claim is made, and the data carries no control group.

---

## H4 — Holidays

### Hypothesis

Holiday periods are associated with changes in retail demand.

### Expected evidence

- Holiday vs non-holiday comparison
- Product-level analysis
- Time-based analysis

### Status

**NOT ASSESSABLE.** The dataset contains no explicit holiday field — Phase 2
records its absence (`docs/phase-2/initial-data-assessment.md`). The hypothesis
is left unevaluated rather than tested against a fabricated calendar, and the
absence is documented as a dataset limitation.

---

## H5 — Product differences

### Hypothesis

Different products have different demand levels and volatility.

### Expected evidence

- Product aggregation
- Distribution analysis
- Time-series comparison

### Status

**SUPPORTED.** Phase 7's item- and category-level distribution and concentration
analysis shows demand levels and dispersion differ materially across products
(`docs/phase-7/eda-results.md`), and Phase 8's store analysis shows the same at
store level.

---

## H6 — Forecasting difficulty

### Hypothesis

Products with more volatile or irregular demand are generally more difficult to
forecast accurately.

### Expected evidence

- Demand variability
- Forecast errors
- Product-level RMSE/MAPE

### Status

**PARTIALLY SUPPORTED.** Phases 12–13 show forecast error varies by store and is
concentrated at the most variable, shortest-history store (Store 4)
(`docs/phase-12/model-evaluation-and-tuning-results.md`,
`docs/phase-13/forecasting-and-inventory-insights-results.md`). The project did
not run a per-item volatility-versus-error test, so the general claim is not
fully evidenced.

---

## H7 — Model performance

### Hypothesis

At least one forecasting approach outperforms the baseline according to the
selected evaluation metrics.

### Expected evidence

- Baseline metrics
- ARIMA metrics
- Additional model metrics
- RMSE/MAPE comparison

### Status

**SUPPORTED.** Phase 11's seasonal-naive benchmark outperforms the naive
baseline on every store (`docs/phase-11/forecasting-models-results.md`), and the
Phase 12 tuned portfolio lowers mean validation RMSE from 3,223.0630 to
3,079.4286 (`docs/phase-12/model-evaluation-and-tuning-results.md`). Improvement
is partial — one store is not bettered — and is reported as such.

---

## H8 — Inventory relevance

### Hypothesis

Forecast outputs can identify future periods or products that deserve greater
inventory-planning attention.

### Expected evidence

- Forecasts
- Demand ranking
- Forecast change analysis
- Business interpretation

### Status

**SUPPORTED.** Phase 13 derives demand rankings and lead-time/service-level
reorder-point scenarios that identify which stores warrant planning attention
(`docs/phase-13/forecasting-and-inventory-insights-results.md`). They are
presented as conditional scenarios, not inventory policy.

---

## Hypothesis governance

Rules:

1. Hypotheses must be testable.
2. Hypotheses must not be presented as findings.
3. Contradictory evidence must be reported.
4. Correlation must not automatically be described as causation.
5. Model superiority must be demonstrated through evaluation.
