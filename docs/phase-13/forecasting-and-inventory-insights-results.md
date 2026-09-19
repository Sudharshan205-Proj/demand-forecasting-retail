# Phase 13 — Forecasting & Inventory Insights Results

## Status

VERIFIED.

Every figure below was produced by `scripts/forecasting_inventory_insights.py`
during the Phase 17 re-audit and inspected directly in the generated
artifacts.

## Objective

Translate validated forecasting results into demand and inventory-planning
insights.

## Data Basis

Historical demand calculations use the **densified training series**, which
is the same construction Phase 11 and Phase 12 apply. The phase reports
1,656 training store-days, of which 1,655 are observed and exactly one is
zero-filled.

| Store | Observed days | Densified days | Zero-filled days | Window |
|---:|---:|---:|---:|---|
| 1 | 532 | 532 | 0 | 2022-08-28 to 2024-02-10 |
| 2 | 532 | 532 | 0 | 2022-08-28 to 2024-02-10 |
| 3 | 531 | 532 | 1 | 2022-08-28 to 2024-02-10 |
| 4 | 60 | 60 | 0 | 2023-12-13 to 2024-02-10 |

The single zero-filled day is **Store 3, 2022-10-16** — the same day Phase
11 measured. Total training quantity is 24,038,416.097 both before and
after densification, because the added day contributes zero, and it
reconciles exactly with the Phase 10 source.

The basis change therefore affects **Store 3 only**:

| Metric | Observed (531 days) | Densified (532 days) |
|---|---:|---:|
| Mean daily demand | 5,843.874970 | 5,832.890242 |
| Median daily demand | 6,531.5260 | 6,530.1280 |
| Minimum daily demand | 173.898 | 0.000 |
| Maximum daily demand | 8,712.819 | 8,712.819 |
| Standard deviation | 1,599.419835 | 1,617.875022 |
| Coefficient of variation | 0.273692 | 0.277371 |

Stores 1, 2 and 4 are unaffected, and the two headline findings the
downstream R analysis reproduces — highest average demand (Store 1) and
highest relative variability (Store 4) — are unchanged.

## Demand Level

| Store | Training days | Total quantity | Mean | Median | Minimum | Maximum | CV |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 532 | 15,806,386.783 | 29,711.253352 | 27,946.1695 | 14,053.423 | 68,811.417 | 0.176886 |
| 2 | 532 | 3,380,962.296 | 6,355.192286 | 6,536.3150 | 2,405.134 | 10,172.994 | 0.160240 |
| 3 | 532 | 3,103,097.609 | 5,832.890242 | 6,530.1280 | 0.000 | 8,712.819 | 0.277371 |
| 4 | 60 | 1,747,969.409 | 29,132.823483 | 25,336.9450 | 36.000 | 73,203.762 | 0.380098 |

Store 1 carries the highest average daily demand. Store 4 carries the
highest relative variability, but its estimate rests on 60 observations
rather than 532, so it is reported with that caveat rather than as a
like-for-like comparison.

## Demand Variability

| Store | Mean | Std | Variance | P90 | P95 | P99 | CV |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 29,711.253352 | 5,255.513309 | 27,620,420.142 | 36,141.7616 | 37,832.8189 | 48,632.5605 | 0.176886 |
| 2 | 6,355.192286 | 1,018.355882 | 1,037,048.702 | 7,506.4196 | 7,762.6311 | 8,436.6552 | 0.160240 |
| 3 | 5,832.890242 | 1,617.875022 | 2,617,519.586 | 7,435.8229 | 7,649.8254 | 8,049.2960 | 0.277371 |
| 4 | 29,132.823483 | 11,073.336036 | 122,618,770.960 | 41,508.7895 | 51,477.1110 | 60,837.1927 | 0.380098 |

Demand level and demand volatility do not move together: Store 2 has both
the lowest mean and the lowest relative variability, while Store 4 has the
second-highest mean and by far the highest relative variability.

## Forecast Evidence (from Phase 12)

Each store's error statistics are recomputed from the stored Phase 12
validation forecasts and reconciled with Phase 12's recorded RMSE and MAPE.

| Store | Model | Observations | Mean predicted | Mean actual | Bias | Residual std | RMSE | MAPE |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | feature_gbm | 114 | 31,392.922520 | 32,087.230526 | 694.308007 | 4,194.607194 | 4,233.491867 | 9.071513% |
| 2 | feature_gbm | 114 | 6,480.096035 | 6,704.743544 | 224.647509 | 677.774347 | 711.206677 | 8.141356% |
| 3 | feature_gbm | 114 | 5,837.958610 | 6,687.732711 | 849.774101 | 1,001.336437 | 1,309.960034 | 16.283339% |
| 4 | seasonal_naive (7) | 114 | 27,942.918746 | 31,813.954149 | 3,871.035404 | 4,687.049969 | 6,063.055906 | 14.060535% |

**The systematic under-forecast is confirmed and quantified.** Every
selected model under-forecast on average, by 694.31, 224.65, 849.77 and
3,871.04 units per day respectively — a mean of 1,409.941 units per day
across the four stores. The bias is largest at Store 4, which is also the
store with the weakest selection evidence.

The recomputed RMSE and MAPE equal Phase 12's recorded values exactly for
all four stores, and Phase 12's half-period error segments reproduce the
same bias and RMSE (the mean of the two segment biases, and the root mean
of the two squared segment RMSEs). The two phases therefore present
consistent error evidence.

Store 2 records both the lowest absolute error and the lowest relative
error. That agreement is coincidental to the metric choice: Store 2 is also
the smallest store, and raw RMSE is measured in demand units, so it is
reported as scale-bound and the cross-store comparison rests on MAPE.

## Inventory Scenarios

Both families are reported at every combination of 7, 14 and 28-day lead
times and 90%, 95% and 99% service levels — 36 scenarios each.

### 14-day lead time, 95% service level

| Store | Historical-variability ROP | Forecast-error ROP | Change |
|---:|---:|---:|---:|
| 1 | 448,302.4918 | 475,036.8481 | +5.96% |
| 2 | 95,240.1416 | 98,037.7574 | +2.94% |
| 3 | 91,617.6408 | 99,790.9617 | +8.92% |
| 4 | 476,010.1398 | 474,241.7074 | −0.37% |

### Why the two families disagree, and in which direction

The families differ in both of their inputs, and the two differences push
in opposite directions.

**Level.** The forecast family's level is higher, because the validation
period's demand exceeded the training-period mean: +8.00% for Store 1,
+5.50% for Store 2, +14.66% for Store 3 and +9.20% for Store 4.

**Uncertainty.** The forecast family's uncertainty is lower everywhere,
because the selected models capture structure that the raw spread includes:
Store 1 −20.19%, Store 2 −33.44%, Store 3 −38.11%, Store 4 −57.67%.

For Stores 1–3 the level correction dominates and the reorder point rises.
For Store 4 the uncertainty reduction dominates and the reorder point falls
slightly. The safety-stock column separates the two effects cleanly:

| Store | Historical safety stock | Forecast safety stock | Change |
|---:|---:|---:|---:|
| 1 | 32,344.9448 | 25,815.6207 | −20.19% |
| 2 | 6,267.4496 | 4,171.3478 | −33.44% |
| 3 | 9,957.1774 | 6,162.7038 | −38.11% |
| 4 | 68,150.6110 | 28,846.3493 | −57.67% |

The direction of the disagreement is the substantive finding: a buffer
sized from raw historical spread is materially larger than one sized from
the error the selected model actually makes, at every store.

### What the forecast-family level is, and is not

Adding the measured bias back to the model's own prediction recovers the
mean demand actually realised over the validation period, so
`bias_adjusted_daily_demand` equals the validation mean by construction.
Both levels are carried in the artifact — `model_daily_demand` and
`bias_adjusted_daily_demand` — and the quality report asserts the identity.

The consequence must be stated plainly: the forecast family's level is a
**recovered validation-period demand level, not a forecast of future
demand**. The only genuinely unseen period is the reserved test set, which
neither family reads. The numbers above are therefore conditional planning
scenarios on two stated assumption sets, not demand predictions.

## Scenario Assumptions

Lead times:

- 7 days
- 14 days
- 28 days

Service levels:

- 90%
- 95%
- 99%

Safety stock uses a normal-demand variability approximation, and reorder
point equals expected lead-time demand plus safety stock. These are
scenario assumptions and are not verified operational parameters.

## Structured Insights

Thirteen insight rows are produced:

| Insight | Store | Metric | Value |
|---|---:|---|---:|
| highest_average_demand | 1 | mean_daily_demand | 29,711.253352 |
| highest_relative_variability | 4 | coefficient_of_variation | 0.380098 |
| lowest_validation_rmse | 2 | validation_rmse | 711.206677 |
| lowest_relative_validation_error | 2 | validation_mape_percent | 8.141356 |
| systematic_bias | 4 | mean_forecast_bias | 3,871.035404 |
| inventory_scenario | 1–4 | reorder_point | per store |
| forecast_inventory_scenario | 1–4 | reorder_point | per store |

The two demand findings (Store 1 highest demand, Store 4 highest relative
variability) preserve the definitions the downstream R analysis reproduces.

## Known Phase 12 Limitation

Store 4 **does** receive a tuned Phase 12 model (Seasonal Naive,
`season_length=7`). The Phase 12 re-audit replaced the fixed three-fold
design with an adaptive one, so Store 4 is tuned on its single affordable
28-day fold and validated on the full 114-day period.

The residual limitation is the evidence behind that selection: one fold
instead of three, and 60 training observations instead of 532. The Phase 13
interpretation preserves that caveat rather than the earlier claim that
Store 4 had no tuned model.

## Interpretation Rule

No business recommendation will be presented as an operational requirement
unless the required business parameters are actually available and verified.

## Phase 17 Re-Audit Record

**Audit status: AUDITED.**

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/forecasting_inventory_insights.py` |
| Tests | `tests/test_forecasting_inventory_insights.py` |
| Phase 13 documents | all six files in `docs/phase-13/` |
| Generated artifacts | `inventory_demand_summary.csv`, `inventory_variability_summary.csv`, `inventory_densification_summary.csv`, `inventory_scenarios.csv`, `inventory_forecast_scenarios.csv`, `inventory_forecast_error_summary.csv`, `forecast_inventory_insights.csv`, `forecasting_inventory_findings.txt`, `forecasting_inventory_quality_report.csv` |
| Inputs | `data/processed/feature_engineered_daily.csv` (Phase 10) |
| Upstream | `selected_model_configurations.csv`, `tuned_validation_results.csv`, `model_evaluation_predictions.csv`, `model_error_analysis.csv` (Phase 12) |
| Downstream | `r/r_analysis.R`, `r/r_analysis_report.Rmd` (Phase 14) |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-1/kpi-definitions.md`, `docs/phase-2/dataset-inventory.md`, `docs/phase-12/*`, `docs/phase-16/*`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Generated findings asserted Store 4 had no tuned Phase 12 configuration | `forecasting_inventory_findings.txt` ended with "Store 4 has no Phase 12 tuned forecasting configuration." The sentence was hardcoded and **survived re-execution** while the phase's own data contradicted it | High |
| F2 | Artifacts predated the Phase 12 inputs they consume | All five artifacts were dated 8 Sep; Phase 12's selection and validation files were rewritten on 19 Sep, so the phase had never run against the evidence it depends on | High |
| F3 | The forecasts were loaded and never used | The phase's stated purpose is translating validated forecasting into inventory insight, yet every calculation used historical spread only; the verified under-forecast was not carried in | High |
| F4 | The demand basis silently differed from Phases 11–12 | Phase 13 aggregated observed store-days (531 for Store 3) while the models were fitted on a densified 532-day series | Medium |
| F5 | No machine-readable validation artifact | The quality framework listed data, evidence, inventory, leakage, reproducibility and interpretation requirements with no artifact and no gate | High |
| F6 | No source reconciliation | Rows, quantity and key uniqueness were never reconciled against the Phase 10 matrix | Medium |
| F7 | `lowest_validation_rmse` compared raw RMSE across stores | Stores differ roughly fivefold in demand level, so the comparison rewarded scale — the failure mode Phase 8 warned against | Medium |
| F8 | Positional alignment between separate aggregations | `calculate_demand_summary` grafted a separately computed grouped standard deviation onto the summary via `.to_numpy()`, relying on identical ordering | Medium |
| F9 | Test isolation assumed, not verified | The `split == "train"` filter was trusted; no boundary check existed | Medium |
| F10 | No check that each store had exactly one selection | A partial or duplicated selection could have passed unnoticed | Low |
| F11 | Configuration displayed as a string | The Phase 12 typed `season_length` and `order` fields were ignored in favour of the display string | Low |
| F12 | Phase 16 asserted Store 4 was descriptive-only | `docs/phase-16/*` claims "a validated tuned forecasting configuration does not exist" for Store 4, which Phase 12 falsified | Medium (downstream) |
| F13 | Tests covered 3 of 8 functions | 10 tests touched validation, the service-level table and one scenario builder; loading, densification, summaries, insights, findings and `main` were untested | Medium |

**Leakage audit:** the test period is never read. The loader filters on
`split == "train"`, the densified series is verified to span exactly
2022-08-28 to 2024-02-10, and forecast evidence is restricted to
predictions whose `scope` is `validation` with a verified
2024-02-11 to 2024-06-03 window. The source's validation and test
partitions are still reconciled on row count, so an accidentally truncated
input would fail rather than pass quietly.

**Positive validation:** the pre-audit script was re-executed before any
change (16.1 seconds, 148.0 MB peak, exit 0). Two artifacts changed because
they read the rewritten Phase 12 files, but `forecasting_inventory_findings.txt`
reproduced **byte-for-byte — including the false Store 4 claim**, which is
the direct evidence that F1 was a correctness defect rather than staleness
that re-running would have cleared.

### Code changes

1. **Densified demand basis (F4).** `densify_store_days` reindexes each
   store's training range with `pd.date_range(..., freq="D")` and
   `fill_value=0.0`, mirroring Phase 11's construction, and flags every
   filled day. `summarize_densification` records observed, densified and
   synthetic day counts plus the synthetic dates.
2. **Forecast-driven scenario family (F3).** `load_phase12_forecast_errors`
   recomputes each store's bias, residual standard deviation, mean
   prediction, mean actual, RMSE and MAPE from the stored Phase 12
   predictions; `calculate_forecast_scenarios` builds a second family whose
   level is bias-corrected and whose uncertainty input is realised error.
3. **Bias-correction identity asserted (F3).** Because the bias-adjusted
   level equals the validation mean by construction, the artifact carries
   both `model_daily_demand` and `bias_adjusted_daily_demand`, and the
   quality report asserts the identity so the number cannot be described as
   a forward forecast.
4. **Machine-readable quality report (F5).** 43 checks gating the run,
   covering source reconciliation, partition and leakage integrity,
   densification, coverage, typed configuration, Phase 12 reconciliation,
   error-analysis reconciliation, scenario coverage and formula identity,
   monotonicity, insight completeness and findings consistency.
5. **Source reconciliation (F6).** The loader records the source matrix's
   row and quantity totals and the train, validation and test row counts,
   and the findings report states the densified and observed store-day
   counts.
6. **Interpretation fixes (F7).** A new `lowest_relative_validation_error`
   insight compares stores on MAPE, the `lowest_validation_rmse`
   interpretation states explicitly that RMSE is scale-bound, and a new
   `systematic_bias` insight records the directional under-forecast.
7. **Robustness (F8, F10, F11).** The coefficient of variation is derived
   inside a single grouped aggregation; typed `season_length` and `order`
   fields flow into both families; the loader rejects duplicate or
   mismatched selections and missing typed columns; insights are validated
   against the selection.
8. **Findings rewrite (F1).** The report is now derived from the loaded
   evidence — one line per selected configuration with its validated RMSE
   and MAPE, the densification counts, the bias, and both scenario families
   — and the quality report fails if a store's model line is missing or if
   the stale claim reappears. The false sentence cannot be reintroduced
   silently.

### Testing

| Test | Result |
|---|---|
| Phase 13 test file | 78 tests, all passing (was 10) |
| Full suite | 441 tests, all passing; Phase 13 adds 68 |

Coverage added: validation (including the expected-store contract),
densification (gap filling, per-store bounds, quantity preservation,
duplicate and empty rejection), both descriptive summaries and their CV
agreement, model-evidence loading and its four rejection paths,
forecast-error recomputation against Phase 12, both scenario families
including the bias-adjusted level and the recovered-mean identity, typed
configuration propagation, insight selection and its relative-error
reframing, findings generation, the quality report (one pass case and
eighteen deliberate-failure cases covering source mismatch, leakage into
the test period, densification drift, RMSE disagreement, bias sign,
formula and monotonicity violations, coverage gaps, insight gaps, findings
inconsistency and scope drift), and the full `main()` workflow including
the missing-input, determinism and failed-gate paths.

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/forecasting_inventory_insights.py
Exit status: 0
Runtime:     16.7 seconds
Peak memory: 149.6 MB
Result:      "Forecasting and inventory insights completed successfully."
```

The chunked loader keeps peak memory low because only the store-day
aggregate is densified, not the 7.4-million-row source.

### Generated-file verification

| File | Rows | Columns | Size | Validation |
|---|---:|---:|---:|---|
| `inventory_demand_summary.csv` | 4 | 8 | 479 B | one row per store; CV derived in-aggregation |
| `inventory_variability_summary.csv` | 4 | 8 | 629 B | percentiles ordered; CV equals std/mean |
| `inventory_densification_summary.csv` | 4 | 7 | 243 B | 1,655 observed, 1,656 densified, one synthetic day |
| `inventory_scenarios.csv` | 36 | 13 | 9,547 B | historical-variability family; typed configuration carried |
| `inventory_forecast_scenarios.csv` | 36 | 16 | 11,511 B | forecast-error family; both levels carried |
| `inventory_forecast_error_summary.csv` | 4 | 12 | 1,236 B | RMSE and MAPE reproduced from stored predictions |
| `forecast_inventory_insights.csv` | 13 | 5 | 4,174 B | seven insight types; store mapping verified |
| `forecasting_inventory_quality_report.csv` | 43 | 4 | 2,878 B | all passing |
| `forecasting_inventory_findings.txt` | 50 lines | — | 3,194 B | derived from evidence; no stale claim |

Every generated file post-dates both the script and the Phase 12 evidence
it consumes.

### Documentation changes

All six Phase 13 documents were rewritten under their existing headings,
and the cross-phase records listed under "Files reviewed" were
synchronised.

### Remaining issues

- None open for Phase 13.
- Downstream: Phase 14's plan named four Phase 13 artifacts as its inputs
  and reproduced the two demand findings. Both remained valid — the four
  filenames were preserved, and the density basis change left highest
  average demand at Store 1 and highest relative variability at Store 4.
  **Resolved by the Phase 14 re-audit:** the three additional artifacts this
  note identified — `inventory_forecast_scenarios.csv`,
  `inventory_forecast_error_summary.csv` and
  `inventory_densification_summary.csv` — are now consumed, and the R
  workflow reconciles all 13 published insight rows on store, metric name
  and value rather than the two store labels alone. Phase 14 is executed
  and verified; its record is in `docs/phase-14/r-analysis-results.md`.
- Downstream: Phase 16's documentation still asserts that Store 4 is
  descriptive-only. That is now false and was corrected during this audit;
  Phase 16's generated artifacts must be re-executed during its own audit.
- The forecast-error family reuses the validation period's own error. A
  genuinely unseen estimate requires the reserved test evaluation, which
  still has no owning phase.
- Store 4's coefficient of variation rests on 60 observations and its
  model on a single cross-validation fold. Both caveats are recorded in the
  artifacts rather than only in prose.
- The dataset has no lead times, service-level targets or costs, so no
  quantity in this phase is an operational recommendation.

## Reproduction runbook

Run from the project root with the virtual environment present, after
Phase 12 has produced `selected_model_configurations.csv`,
`tuned_validation_results.csv`, `model_evaluation_predictions.csv` and
`model_error_analysis.csv`.

| # | Purpose | Command | Expected result |
|---|---|---|---|
| 1 | Run the Phase 13 tests | `.venv\Scripts\python.exe -m pytest tests/test_forecasting_inventory_insights.py -q -p no:cacheprovider` | 78 passed |
| 2 | Execute the insights workflow | `.venv\Scripts\python.exe scripts/forecasting_inventory_insights.py` | "Forecasting and inventory insights completed successfully." |
| 3 | Verify the quality report | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/forecasting_inventory_quality_report.csv'); print(len(r), bool(r['passed'].all()))"` | `43 True` |
| 4 | Verify densification | `.venv\Scripts\python.exe -c "import pandas as pd; d=pd.read_csv('data/analysis/inventory_densification_summary.csv'); print(int(d['densified_days'].sum()), int(d['synthetic_days'].sum()))"` | `1656 1` |
| 5 | Verify the bias correction | `.venv\Scripts\python.exe -c "import pandas as pd; e=pd.read_csv('data/analysis/inventory_forecast_error_summary.csv'); print((e['bias']>0).all(), round(e['bias'].mean(),3))"` | `True 1409.941` |
| 6 | Verify test isolation | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/forecasting_inventory_quality_report.csv').set_index('check'); print(r.loc['test_period_excluded','actual'], bool(r.loc['test_period_excluded','passed']))"` | `2024-02-10 True` |
| 7 | Regression: upstream phase | `.venv\Scripts\python.exe -m pytest tests/test_evaluate_and_tune_models.py -q -p no:cacheprovider` | 64 passed |
| 8 | Regression: full suite | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 441 passed |
