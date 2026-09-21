# Phase 13 — Forecasting & Inventory Insights Methodology

## 1. Demand Basis

Historical demand statistics are calculated from the **training period only**,
on the densified store-day series.

Aggregation proceeds in two steps. First, the 7,431,026-row engineered matrix is
streamed in chunks and reduced to observed store-day demand; second, each store's
observed training range is reindexed onto a complete daily calendar with
`pd.date_range(..., freq="D")` and absent days filled at zero. This is the same
construction Phase 11's `to_regular_daily_series` and Phase 12's series loader
use, so all three phases describe an identical store-day series.

At this grain an absent date means no quantity was recorded for that store that
day, so zero-filling is the correct interpretation. The result is 1,656 training
store-days (532 / 532 / 532 / 60), of which exactly one — Store 3, 2022-10-16 —
is zero-filled. Total training quantity is unchanged at 24,038,416.097, because
the added day contributes zero.

Densification is measured per store, and the measurement is written to
`inventory_densification_summary.csv` rather than being asserted.

The target remains physical sales quantity. Online demand is not combined with
the physical-store demand target.

## 2. Forecasting Evidence

Phase 12 selected forecasting configurations using training-period time-series
cross-validation, and stored every fold and validation forecast in
`data/analysis/model_evaluation_predictions.csv`.

Phase 13 loads the selection (`selected_model_configurations.csv`) and the
recorded validation metrics (`tuned_validation_results.csv`), and then
**independently recomputes** each store's error statistics from the stored
predictions. The recomputed RMSE and MAPE are compared against Phase 12's
recorded values by the quality report, so the two phases are reconciled rather
than one being trusted.

## 3. Demand Level

Average daily demand represents the typical observed daily demand during the
training period.

Median demand provides a robust comparison with the mean.

Maximum and percentile demand provide information about high-demand periods.

## 4. Demand Variability

Standard deviation measures absolute variability.

Coefficient of variation is calculated as:

CV = standard deviation / mean demand

CV helps compare relative variability between stores with different demand
levels. It is derived inside a single grouped aggregation, so no column depends
on positional alignment with a separately computed series.

## 5. Safety Stock

Safety stock is estimated using:

SS = z × sigma × sqrt(L)

where:

- z is the service-level normal quantile;
- sigma is the uncertainty input for the scenario family;
- L is lead time.

The uncertainty input is the **historical daily demand standard deviation** for
the historical-variability family and the **standard deviation of the selected
model's validation error** for the forecast-error family.

## 6. Reorder Point

The reorder point is:

ROP = expected lead-time demand + SS

This represents the estimated inventory position at which replenishment would be
triggered under the scenario assumptions.

The identity is verified numerically for both families by the quality report, not
merely documented.

## 7. Scenario Analysis

Because operational inventory parameters are unavailable, the project uses
explicit scenarios rather than pretending that assumed values are business
requirements.

Lead-time scenarios:

- 7 days
- 14 days
- 28 days

Service-level scenarios:

- 90%
- 95%
- 99%

### Historical-variability family

The level is the densified training-period mean daily demand and the uncertainty
input is the training-period standard deviation.

### Forecast-error family

The level is the selected model's mean validation prediction plus its measured
bias, and the uncertainty input is the standard deviation of its validation
residuals.

The bias is `mean(actual − predicted)` over the 114 validation days, so a
positive value means the model under-forecasts. In the delivered run every
selected model under-forecast, by 694.31 / 224.65 / 849.77 / 3,871.04 units per
day.

Two levels are carried in the artifact — `model_daily_demand` (what the model
predicts) and `bias_adjusted_daily_demand` (that prediction plus the bias) — so
the correction is visible rather than baked in. Adding the bias back recovers the
demand actually realised over the validation period, so
`bias_adjusted_daily_demand` equals the validation mean by construction. The
quality report asserts that identity, because it determines how the number must
be described: it is a **recovered validation-period demand level, not a forecast
of future demand**. The only genuinely unseen period is the reserved test set,
which neither family reads.

## 8. Interpretation

Higher demand does not necessarily mean higher relative inventory risk.

A store may have:

- high demand and low variability;
- low demand and high variability;
- high demand and high variability;
- low demand and low variability.

Inventory planning should consider both demand level and uncertainty.

Cross-store comparisons of forecast accuracy use relative error (MAPE). Raw RMSE
is reported as well, but it is measured in demand units and is therefore
scale-bound: the smallest store tends to win on scale alone, and RMSE is only
meaningful within a store.

## 9. Store 4

Store 4 is assigned a tuned Phase 12 forecasting configuration: Seasonal Naive
with a 7-day seasonal period, selected on its single available cross-validation
fold (its 60 training observations cannot support three 28-day folds).

That evidence is weaker than Stores 1–3, which each use three folds. Its
validated forecast should therefore be read with more caution than the
three-fold evidence behind the other stores, and the single-fold basis is
recorded rather than hidden.

Store 4 also has the shortest demand history of the four stores, so its
coefficient of variation — the highest of the four — is estimated on 60
observations rather than 532. This is recorded as a caveat wherever the finding
is reported.

## 10. Leakage Prevention

The test period is never read. The loader filters on `split == "train"` and the
quality report verifies the boundary rather than trusting the filter: the
densified series must span exactly 2022-08-28 to 2024-02-10, and the validation
and test partitions must exist in the source with their recorded row counts while
contributing no rows to the analysis.

Forecast evidence comes only from predictions whose `scope` is `validation`, and
the recorded validation window must equal 2024-02-11 to 2024-06-03 for every
store.

## 11. Limitations

The analysis does not model:

- supplier reliability;
- lead-time uncertainty;
- stockout costs;
- holding costs;
- ordering costs;
- existing inventory;
- purchase orders;
- warehouse constraints;
- shelf-life constraints.

Operational deployment would require these inputs.

The forecast-error family additionally reuses the validation period's own error,
which is more optimistic than a truly unseen evaluation.

## 12. Reproducibility

The phase records:

- the source matrix's row and quantity totals, and the train, validation and
  test row counts, all reconciled against the Phase 9/10 contract;
- the densified store-day count and every zero-filled day;
- the selected configuration per store, with typed `season_length` and `order`
  fields rather than a display string;
- the forecast-error statistics recomputed from the stored predictions;
- both scenario families in full, with their level and uncertainty inputs;
- the formulas and the assumption sets;
- a machine-readable quality report.

The scripts are deterministic: the quality report is rebuilt on every run, the
analysis reads no clock or random source, and re-running the workflow twice over
the same inputs reproduces every artifact.

## 13. Quality Verification

`data/analysis/forecasting_inventory_quality_report.csv` records 43 checks and
the run is gated on all of them passing. The checks cover source reconciliation,
partition and leakage integrity, densification, store coverage, typed
configuration, forecast-evidence reconciliation against Phase 12, error-analysis
reconciliation, scenario coverage and formula identity, monotonicity, insight
completeness, and findings consistency with the loaded evidence.

`main()` writes the report first and raises before writing any data artifact if a
check fails, so a failing run cannot leave partially updated outputs behind.
