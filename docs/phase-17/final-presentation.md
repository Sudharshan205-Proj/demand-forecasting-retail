# Final Presentation — Demand Forecasting for Retail

## Purpose

This document is the presentation script and anticipated Q&A for the project. It
is the `Presentation` and `Q&A` element of Course 6 / Course 8 coverage and pairs
with [`../phase-15/data-storytelling.md`](../phase-15/data-storytelling.md) and
[`final-case-study.md`](final-case-study.md).

Each slide names the document behind its claim so nothing on a slide is
unsupported.

---

## Slide 1 — Title

**Demand Forecasting for Retail**

A reproducible, end-to-end data project: Ask → Prepare → Process → Analyze →
Share → Act.

## Slide 2 — The Problem

- Demand varies by store and over time; inventory must be committed before
  demand is known.
- Too little stock → stock-outs. Too much → tied-up capital.
- Question: how accurately can we forecast demand, and how reliably can those
  forecasts support planning?

*Source:* [`../phase-1/business-problem.md`](../phase-1/business-problem.md).

## Slide 3 — The Data

- 8 raw files; 7,432,685 raw sales rows; 4 stores; 28,180 items after cleaning.
- Coverage 2022-08-28 → 2024-09-26; promotions and price history present.
- License CC BY-NC-SA 4.0.
- **Gaps:** no holiday field, and no lead times, costs or stock data.

*Source:* [`../phase-2/`](../phase-2/).

## Slide 4 — The Pipeline

Raw → clean (7,431,026 rows) → integrate (34 columns, byte-identical on
re-run) → time-series split:

| Split | To |
|---|---|
| Train | 2024-02-10 |
| Validation | 2024-06-03 |
| Test | 2024-09-26 |

Every stage reconciles on rows and on 41,949,529.910 total quantity.

*Source:* Phases 5, 6, 9.

## Slide 5 — The Analysis

- EDA: concentration, outliers, exact correlation matrix.
- Statistics: Newey–West trend, price/demand, the 2023-12 level shift explained
  by Store 4 first appearing on 2023-12-13.
- R: independent cross-language verification of all 13 insight rows.

*Source:* Phases 7, 8, 14.

## Slide 6 — The Models

Naive, seasonal-naive, ARIMA(1,1,1) and a deterministic `feature_gbm` candidate.

- Nine candidates per store across 10 cross-validation folds (90 evaluations):
  stores 1-3 use three folds each, store 4 its single affordable fold.
- Selection on training-period cross-validation only; the test period is never
  read.
- **Tuned portfolio: mean validation RMSE 3,223.0630 → 3,079.4286.**

*Source:* Phases 11, 12.

## Slide 7 — The Results

- Store 1 highest average demand: **29,711.253352/day**.
- Store 4 highest relative variability: **CV 0.380098** (60 observations —
  caveat).
- Store 2 lowest MAPE: **8.141356 %** — the cross-store metric that matters.
- Every model under-forecasts: mean bias **1,409.941/day**.

*Source:* Phase 13.

## Slide 8 — Planning Insight

- Buffers from realised error are smaller at every store than buffers from raw
  spread (−20.19 % to −57.67 %).
- 14-day / 95 % scenario reorder points: **448,302 / 95,240 / 91,618 / 476,010**.
- **They are scenarios, not policies** — no costs or lead times in the data.

*Source:* Phase 13.

## Slide 9 — Share It

- Static figures with direct labels; Tableau dashboard; interactive Streamlit
  app.
- Dashboard:
  <https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning>
- Application:
  <https://demand-forecasting-retail-internship.streamlit.app/>

*Source:* Phases 15, 16.

## Slide 10 — Quality

- 532 automated tests pass.
- Each run-gating phase writes a machine-readable quality report (15–91 checks
  per phase; 272 checks in total).
- The pipeline is deterministic: raw data is immutable, the integrated dataset
  is byte-identical on re-execution, and every transformation reconciles on rows
  and totals.

*Source:* [`../project-status.md`](../project-status.md).

## Slide 11 — What I Would Do Next

Reserved test-period evaluation → operational inputs (lead times, costs,
targets) → holiday calendar → monitoring/re-tuning loop.

## Slide 12 — Close

A complete, reproducible, tested and documented project that forecasts demand
and communicates the uncertainty around it.

---

## Anticipated Q&A

**Q: Why MAPE and not just RMSE?**
A: RMSE is in demand units and rewards the smallest store. Store 2 wins on both,
but the comparison that is valid across stores is MAPE. Recorded in Phase 13.

**Q: Why is there no holiday analysis?**
A: No holiday field exists in the dataset. Phase 2 records the absence, and the
requirement was conditional on availability, so it is marked not applicable
rather than fabricated.

**Q: Why isn't the tuned model better everywhere?**
A: It improves stores 1 and 2, is 0.32 % worse than the weekly benchmark at
store 3, and reproduces Phase 11 at store 4. The project reports that rather
than smoothing it over.

**Q: Did you use the test data anywhere?**
A: No. Selection uses training-period cross-validation; the test period from
2024-06-04 is never read. Evaluating the reserved test period is future scope.

**Q: Why is Store 4 treated cautiously?**
A: It first appears on 2023-12-13 — 60 training days and one affordable
cross-validation fold. Its estimates carry that caveat.

**Q: Are the reorder points operational recommendations?**
A: No. They are scenario estimates under stated lead-time and service-level
assumptions; the data has no costs or lead-time evidence to make them policy.

**Q: Is the app deployed publicly?**
A: Yes. It runs from the repository (verified locally, HTTP 200) and the hosted
Streamlit Community Cloud deployment is live at
<https://demand-forecasting-retail-internship.streamlit.app/>, where all four
sections render. Evidence is in
[`../phase-16/deployment-validation.md`](../phase-16/deployment-validation.md).

**Q: Why Python *and* R?**
A: R is an independent re-analysis that reconciles the Python results —
cross-language verification, not a second source of truth.

**Q: How do you know the pipeline is reproducible?**
A: Byte-identical re-execution at the integration stage, reconciled totals at
every stage, pinned dependencies and recorded environment versions.

**Q: What would break first in production?**
A: The missing operational inputs and the systematic under-forecast — both are
stated in the limitations rather than hidden.

---

## Delivery Notes

- Target length: 10–12 minutes.
- Lead with the problem and the gaps, not the model names.
- Keep every number to the ones on these slides so the talk and the repository
  cannot drift.
