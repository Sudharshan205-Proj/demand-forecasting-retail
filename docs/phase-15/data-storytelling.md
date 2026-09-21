# Phase 15 — Data Storytelling

## 1. Audience

The primary audience is a retail operations or inventory-planning stakeholder who
needs concise evidence about demand and planning risk.

The audience should not need to understand the implementation details of ARIMA,
seasonal-naive forecasting or R programming to interpret the dashboard.

## 2. Context

The project analyses historical retail demand to support forecasting and
inventory-planning decisions.

## 3. Problem

Retail demand varies across stores and over time.

Planning must therefore account for:

- demand level;
- demand variability;
- forecast evidence;
- lead-time assumptions;
- service-level assumptions.

## 4. Evidence

The project establishes the following reconciled values:

| Evidence | Value |
|---|---|
| Highest average demand | Store 1 — 29,711.253352 demand units/day over 532 training days |
| Highest relative variability | Store 4 — CV 0.380098 over 60 training days |
| Lowest validation RMSE | Store 2 — 711.206677 demand units (scale-bound) |
| Lowest relative validation error | Store 2 — 8.141356 % MAPE |
| Scenario reorder point, 14 days / 95 % | Store 1 — 448,302.491763; Store 2 — 95,240.141608; Store 3 — 91,617.640793; Store 4 — 476,010.139796 |

## 5. Key Insights

The visualization narrative emphasizes:

1. Where demand is concentrated — Store 1 and Store 4 together carry the two
   largest average demand levels.
2. Which stores have greater relative variability — Store 4 is the most variable
   relative to its own mean, and its history is much shorter than the others, so
   that estimate rests on fewer observations.
3. Which validated result provides the strongest evidence under the project's
   metric — Store 2 records both the lowest validation RMSE and the lowest MAPE,
   but RMSE rewards the smallest store, so the MAPE comparison is the one worth
   acting on.
4. How reorder-point scenarios change with assumed lead time and service level —
   they rise monotonically in both, and the choice of assumption moves the number
   by roughly the width of the store's demand.

## 6. Recommendations

Recommendations remain conditional.

Examples include:

- prioritize high-demand stores for demand-monitoring attention;
- investigate highly variable stores for additional operational context;
- use validated forecasting evidence as an input to planning;
- calibrate scenario reorder points using actual supplier and inventory data.

## 7. Limitations

The dataset does not provide all operational information required for production
inventory decisions.

Therefore the dashboard must not present scenario reorder points as mandatory
inventory policies.

Two further limitations belong in the narrative:

- RMSE is measured in demand units and cannot be compared across stores of
  different size.
- The published dashboard carries a publish-time extract; the static figures in
  this repository are regenerated from the analytical CSVs by their workflow. A
  pipeline re-run does not re-publish the dashboard — that needs Tableau Desktop —
  so the two can drift between releases.

## 8. Narrative Flow

The flow is:

**What is happening?**
→ demand distribution

**Where is it happening?**
→ store comparison

**How predictable/variable is it?**
→ variability and forecast evidence

**What could this mean for planning?**
→ inventory scenarios

**What should be done next?**
→ conditional recommendations and operational-data requirements

## Final Case Study

The narrative arc described above is carried into the project's final portfolio
artifact, [`../phase-17/final-case-study.md`](../phase-17/final-case-study.md),
which presents the same evidence in the course case-study order (problem → future
scope). The delivery script and anticipated questions are in
[`../phase-17/final-presentation.md`](../phase-17/final-presentation.md). This
document remains the storytelling design; the final case study is the written
narrative, so the two are cross-referenced rather than duplicated.
