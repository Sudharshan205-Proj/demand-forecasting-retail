# Final Case Study — Retail Demand Forecasting for Inventory Planning

## Preface

This is the project's final portfolio case study, produced during Phase 17 from
evidence verified in Phases 0–16. It follows the case-study order the course
requires. Every figure is a reconciled project artifact; none is estimated here.

This case study is the `Findings`, `Limitations`, `Future scope` and
`Communication` element of Course 8 coverage. It does not replace the phase
documentation, which carries the full method and audit trail.

---

## 1. Problem

Retail demand varies across stores and over time, and inventory decisions must
be made before demand is known. Planning too little stock risks stock-outs;
planning too much ties up working capital and risks obsolescence.

The business problem is therefore:

> Given historical retail sales, promotions and product data, how accurately can
> future demand be forecast, and how reliably can those forecasts support
> store-level inventory planning?

The project answers this as a complete analytical lifecycle:
**Ask → Prepare → Process → Analyze → Share → Act.**

## 2. Context

- The subject is a multi-store retail operation selling a broad product catalog.
- Demand is observed at the **date × item × store** grain.
- Planning is store-level and short-horizon: lead times of 7, 14 and 28 days and
  service levels of 90 %, 95 % and 99 % are the scenario assumptions.
- The dataset contains sales, markdown/discount records, price history and an
  online channel, but **no lead times, costs, stock levels or holiday field**.
  Those absences bound what the project can honestly recommend.

## 3. Stakeholders

| Stakeholder | Interest |
|---|---|
| Inventory planners | Store-level demand level, variability and reorder-point scenarios |
| Retail operations managers | Which stores need monitoring attention |
| Analysts / data team | A reproducible forecasting and evaluation pipeline |
| Project owner / internship evaluator | A portfolio-quality demonstration of the full lifecycle |

## 4. Questions

The primary SMART question:

> How accurately can future retail product demand be forecast from historical
> sales data, with promotions and holidays incorporated where available, over a
> defined forecasting horizon supported by the selected dataset?

Supporting questions span historical demand patterns, promotion effects, store
and product variation, forecast accuracy (RMSE/MAPE), forecast reliability
(bias, hardest periods) and inventory implications.

**Holidays were not available.** Phase 2 recorded an explicit holiday variable as
"VERIFIED ABSENT", so the holiday sub-questions are answered as *not applicable*
rather than fabricated.

## 5. Data

| File | Role |
|---|---|
| `sales.csv` | 7,432,685 raw sales rows |
| `online.csv` | Online-channel sales |
| `markdowns.csv`, `discounts_history.csv` | Promotional / markdown records |
| `price_history.csv` | Price history (698,626 rows) |
| `catalog.csv` | Item directory (219,810 rows) |
| `stores.csv` | Store directory (4 stores) |
| `actual_matrix.csv` | Actual-matrix reference |

- Coverage: **2022-08-28 to 2024-09-26**, 4 stores and 28,180 items after
  cleaning.
- License: **CC BY-NC-SA 4.0** (confirmed by the project owner in the Phase 3 audit).
- Raw data and generated artifacts are excluded from Git under the project's
  data policy; directory placeholders are tracked.

**Known data-quality issues carried into processing:** negative quantities in
sales, duplicate rows in markdowns/price_history, future-dated discount records,
36,585 sales rows without a catalog match (948 distinct items), and 21,419
discount records with a zero base price.

## 6. Preparation

Phase 2 established the schema, data dictionary and source assessment. Phase 3
demonstrated spreadsheet-based analysis in a regenerable workbook (761 daily
records, 4-store and 28,182-item summaries). Phase 4 built the SQLite database
and ran 18 analytical SQL queries.

## 7. Processing

Phase 5 cleaned the raw data (7,431,026 rows retained; the catalog gap and
invalid-date coverage reconciled) and Phase 6 integrated the eight sources into a
34-column matrix that is byte-identical on re-execution. Phase 9 produced the
chronological partitions used by every later phase:

| Split | Boundary |
|---|---|
| Train | to 2024-02-10 |
| Validation | to 2024-06-03 |
| Test | to 2024-09-26 |

Phases 7–10 added exploratory, statistical and engineered-feature views
(7,431,026 rows × 16 features), with leakage-safe lags and an explicit decision
that intermediate date gaps are reported rather than silently zero-filled.

## 8. Analysis

- **Phase 7 (EDA):** demand concentration, item-level outliers, monthly and
  store-level patterns, and an exact full-dataset correlation matrix.
- **Phase 8 (statistical):** trend with Newey–West inference, price/demand and
  promotion/demand relationships, store and category differences, and a
  diagnosis of the 2023-12 level shift as a coverage/assortment change (Store 4
  first appears on 2023-12-13).
- **Phase 14 (R):** an independent cross-language re-analysis that reconciles
  all 13 Phase 13 insight rows and recomputes RMSE/MAE/MAPE with `yardstick`.

## 9. Forecasting / Modeling

| Model | Role |
|---|---|
| Naive | Documented baseline |
| Seasonal-naive (7/30/365) | Weekly/periodic baseline; strongest Phase 11 benchmark |
| ARIMA(1,1,1) | Mandatory classical time-series model |
| `feature_gbm` | Deterministic gradient-boosting candidate over 16 store-day features |

Phase 11 fitted and evaluated the three classical models per store over the
114-day validation period. Phase 12 evaluated nine candidates per store over 90
expanding-window cross-validation folds, with selection on training-period
cross-validation only and the test period never read.

**Result:** the tuned portfolio reduced mean validation RMSE from **3,223.0630 to
3,079.4286**. Stores 1 and 2 improved (11.13 % and 6.38 %); store 3 was 0.32 %
worse than the weekly benchmark (recorded, not hidden); store 4 reproduced its
Phase 11 forecast exactly on a single affordable fold.

The evaluation deliberately rejects the naive conclusion RMSE invites: because
RMSE is in demand units, cross-store comparison uses MAPE.

## 10. Visualization

- **Python (Phase 15):** four static figures with direct value labels and units,
  gated by a 55-check quality report and recorded in a digest manifest.
- **R (Phase 14):** four exported ggplot2 figures plus inline report figures.
- **Tableau (Phase 15):** a committed workbook (5 worksheets, 1 dashboard, 6
  filters) and a published dashboard that resolves (HTTP 200).
- **Application (Phase 16):** an interactive Streamlit decision-support tool.

Published dashboard:
<https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning>

## 11. Findings

1. **Where demand is concentrated.** Store 1 carries the highest average daily
   demand — **29,711.253352 units/day** over 532 training days. Stores 1 and 4
   together carry the two largest average demand levels.
2. **Where demand is least predictable.** Store 4 has the highest relative
   variability (**CV 0.380098**), but on only 60 observations, so it is reported
   with that caveat rather than as a like-for-like comparison.
3. **Which store forecasts best under the project's metric.** Store 2 records
   both the lowest validation RMSE (**711.206677**) and the lowest MAPE
   (**8.141356 %**). Because RMSE rewards the smallest store, the MAPE result is
   the one worth acting on.
4. **Forecasts are systematically biased low.** Every selected model
   under-forecast on average — by **694.31 / 224.65 / 849.77 / 3,871.04** units
   per day (mean **1,409.941**). This is a directional warning, not noise.
5. **Buffers sized from raw spread overstate risk.** Sizing safety stock from
   realised forecast error rather than raw historical variability reduced safety
   stock at **every** store (−20.19 % / −33.44 % / −38.11 % / −57.67 %).
6. **Reorder-point scenarios move with both assumptions.** At a 14-day lead time
   and 95 % service level the historical family gives reorder points of
   **448,302 / 95,240 / 91,618 / 476,010**, and reorder points rise monotonically
   in both lead time and service level.

## 12. Recommendations

All recommendations are **conditional planning inputs**, not operational
requirements — the dataset lacks the lead times, costs and stock positions a
mandatory policy would need.

- Prioritise high-demand stores (Store 1, Store 4) for demand-monitoring attention.
- Investigate Store 4's variability with additional operational context before
  relying on its short-history estimates.
- Use the MAPE-based comparison, not raw RMSE, when ranking stores.
- Treat the systematic under-forecast as a directional adjustment when sizing
  buffers.
- Calibrate scenario reorder points using actual supplier lead times, service
  targets and inventory costs.
- Re-run the reserved test-period evaluation before any production use.

## 13. Limitations

- No holiday data; holiday questions are not applicable.
- No lead times, service-level targets, costs or stock levels in the dataset.
- The forecast-error scenario family's level is a **recovered validation-period
  demand level, not a forecast of future demand** — the only genuinely unseen
  period is the reserved test set, which no phase reads.
- Store 4's selection rests on a single cross-validation fold and 60
  observations.
- RMSE is scale-bound and not comparable across stores.
- The published Tableau dashboard reflects the extract built on 2026-09-08; the
  repository figures were regenerated on 2026-09-19.
- The hosted application deployment has not been executed (owner authorisation
  pending), and no human usability/accessibility review has been performed.
- RStudio is installed but unevidenced; the R workflow runs through `Rscript`.

## 14. Future Scope

- Reserved test-period evaluation for a genuinely unseen accuracy estimate.
- Refresh and re-publish the Tableau dashboard against post-audit extracts.
- Introduce an external holiday calendar and re-test the holiday hypothesis H4.
- Add operational inputs (lead times, costs, service targets) to convert
  scenarios into policies.
- A monitoring loop that tracks realised vs. forecast demand and re-tunes.
- Extend the model set with Prophet or LSTM if a specific experiment justifies it.

## 15. Communication

- **Static:** the README, phase documentation and this case study.
- **Visual:** `reports/figures/` (EDA and statistical figures), the Phase 14/15
  figures, the Tableau dashboard and the Streamlit application.
- **Narrative:** `docs/phase-15/data-storytelling.md` and
  `docs/phase-17/final-presentation.md`.
- **Reproducible:** every command to rebuild the artifacts is documented and
  project-root-relative.
