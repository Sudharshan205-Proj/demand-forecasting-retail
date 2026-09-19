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

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).

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
