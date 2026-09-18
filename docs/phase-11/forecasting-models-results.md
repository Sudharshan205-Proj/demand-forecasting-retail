# Phase 11 — Forecasting Models Results

## Status

VERIFIED.

Every figure below was produced by `scripts/forecasting_models.py` during the Phase 17 re-audit and inspected directly in the generated artifacts. The model results are byte-identical to the pre-audit run, so the re-audit changed verification machinery rather than model output.

## Models

* Naive baseline — last observed training value
* Seasonal-naive baseline — `season_length = 7`
* ARIMA(1,1,1) — `enforce_stationarity=False; enforce_invertibility=False`

## Input Reconciliation

| Metric | Value |
|---|---|
| Source rows (Phase 10) | 7,431,026 |
| Unique stores | 4 |
| Date range | 2022-08-28 to 2024-09-26 |
| Total quantity | 41,949,529.910 |
| Train / validation / test rows | 4,315,416 / 1,548,957 / 1,566,653 |
| Observed store-days | 2,571 |
| Zero-filled store-days | 1 (store 3, 2022-10-16) |

The store-day total quantity equals the source total exactly, so the aggregation to the forecasting grain is lossless.

## Validation Period

2024-02-11 through 2024-06-03 — 114 daily observations for every store.

Training ends 2024-02-10. Store 1–3 train from 2022-08-28; store 4 trains from 2023-12-13 (60 observations).

## Evaluation Metrics

* RMSE — root mean squared error, lower is better
* MAPE — mean absolute percentage error, zero-actual observations excluded

### Per-store validation results

| Store | Model | RMSE | MAPE (%) |
|---:|---|---:|---:|
| 1 | naive | 6,941.4807 | 20.9340 |
| 1 | seasonal_naive | 4,763.7639 | 10.1038 |
| 1 | arima | 6,282.6325 | 18.5960 |
| 2 | naive | 1,296.3913 | 15.8597 |
| 2 | seasonal_naive | 759.6968 | 8.5978 |
| 2 | arima | 1,112.2110 | 14.3755 |
| 3 | naive | 3,122.4588 | 35.1611 |
| 3 | seasonal_naive | 1,305.7352 | 15.2432 |
| 3 | arima | 2,008.3482 | 28.5553 |
| 4 | naive | 11,541.6380 | 36.3830 |
| 4 | seasonal_naive | 6,063.0559 | 14.0605 |
| 4 | arima | 11,369.6719 | 35.8095 |

### Summary across stores

| Model | Stores | Mean RMSE | Median RMSE | Mean MAPE (%) | Pooled RMSE | Pooled MAPE (%) |
|---|---:|---:|---:|---:|---:|---:|
| seasonal_naive | 4 | 3,223.0630 | 3,034.7496 | 12.0013 | 3,928.6186 | 12.0013 |
| arima | 4 | 5,193.2159 | 4,145.4904 | 24.3341 | 6,595.6688 | 24.3341 |
| naive | 4 | 5,725.4922 | 5,031.9697 | 27.0845 | 6,943.0530 | 27.0845 |

Pooled metrics are computed over all 456 store-day validation observations per model (4 stores × 114 days).

The seasonal-naive benchmark is the best model on both the across-store mean and the pooled metric. ARIMA(1,1,1) improves on naive but does not beat the weekly benchmark. The validation store-days contain no zero-demand observations, so no observation was excluded from MAPE.

## Test Isolation

The test period beginning 2024-06-04 was not used. The quality report verifies that the latest prediction date is 2024-06-03 and that every configuration's training window ends at 2024-02-10. One month of test data (1,566,653 rows) exists and was deliberately excluded.

## Expected Artifacts

* `data/analysis/forecasting_model_results.csv`
* `data/analysis/forecasting_model_configurations.csv`
* `data/analysis/forecasting_summary.csv`
* `data/analysis/forecasting_predictions.csv`
* `data/analysis/forecasting_quality_report.csv`
* `data/analysis/forecasting_findings.txt`

## Actual Results

All six artifacts were generated and inspected. The quality report contains 24 checks, all passing.

| File | Rows | Columns | Size |
|---|---:|---:|---:|
| `forecasting_model_results.csv` | 12 | 7 | 872 B |
| `forecasting_model_configurations.csv` | 12 | 8 | 1,271 B |
| `forecasting_summary.csv` | 3 | 9 | 431 B |
| `forecasting_predictions.csv` | 1,368 | 5 | 58,997 B |
| `forecasting_quality_report.csv` | 24 | 4 | 1,125 B |
| `forecasting_findings.txt` | 63 lines | — | 2,551 B |

No model performance result is claimed beyond these verified outputs.

## Phase 17 Re-Audit Record

**Audit status: AUDITED.**

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/forecasting_models.py` |
| Tests | `tests/test_forecasting_models.py` |
| Phase 11 documents | all six files in `docs/phase-11/` |
| Generated artifacts | `forecasting_model_results.csv`, `forecasting_model_configurations.csv`, `forecasting_summary.csv`, `forecasting_predictions.csv`, `forecasting_quality_report.csv`, `forecasting_findings.txt` |
| Inputs | `data/processed/feature_engineered_daily.csv` (Phase 10) |
| Downstream | `scripts/evaluate_and_tune_models.py` (Phase 12), `scripts/forecasting_inventory_insights.py` (Phase 13) |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-1/kpi-definitions.md`, `docs/phase-2/dataset-inventory.md`, `docs/phase-9/time-series-results.md`, `docs/phase-10/feature-engineering-results.md`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Documentation never updated after execution | `forecasting-models-results.md` said "NOT YET VERIFIED"; the checklist was entirely unchecked; the register said "Not yet started" while the README reported COMPLETE | Medium |
| F2 | The findings report mislabelled the validation start | It printed `Validation period: 2024-02-10 to 2024-06-03` — the training end, not the validation start (2024-02-11) | Medium |
| F3 | No machine-readable validation artifact | The quality framework required schema, temporal, model, metric and leakage validation; none was recorded and no run gated on it | High |
| F4 | No source reconciliation | Nothing compared the store-day aggregate against the Phase 10 input, so a lossy aggregation could pass unnoticed | Medium |
| F5 | No stored predictions | Metrics could not be independently recomputed, so the reported RMSE/MAPE were unverifiable | Medium |
| F6 | Reproducibility record was incomplete | The configurations artifact recorded only `model, store_id, configuration`; the training window, validation window and horizon required by the framework were absent | Low |
| F7 | Baseline definitions were unverified | Nothing confirmed that the naive forecast equals the last training value or that the seasonal-naive pattern is the documented one | Low |
| F8 | Test coverage missed the core | 11 tests covered pure functions only; loading, densification, per-store runs, summary, quality report, findings and `main` were untested | Medium |
| F9 | Densification was undocumented and unmeasured | Store-level zero-filling of missing dates was a correctness-critical modelling decision with no recorded count | Medium |
| F10 | Engineered features are unused downstream (cross-phase) | Phase 11 reads the Phase 10 matrix but selects only `date`, `store_id`, `quantity` and `split` | Informational (cross-phase) |

**Leakage audit:** no future information enters any forecast. Every model is fitted on the training window only; the naive and seasonal-naive definitions are recomputed from the training window and compared element-wise with the stored predictions; the configurations record a training end of 2024-02-10; and the latest prediction date is 2024-06-03, before the test start.

**Positive validation:** the re-executed `forecasting_model_results.csv` is byte-identical to the pre-audit file (MD5 `af5220f90d9f889b8758022a7bf78809`), so every correction is verification-only with respect to the reported model metrics.

### Code changes

1. **Machine-readable quality report (F3).** `create_quality_report(...)` writes `forecasting_quality_report.csv` with 24 checks spanning input, temporal, model, metric, leakage and reproducibility validation. `main()` raises when any check fails, so results cannot be written from an invalid run.
2. **Stored predictions (F5).** Every store-day forecast is now written to `forecasting_predictions.csv` (1,368 rows: 4 stores × 3 models × 114 days), and RMSE/MAPE are recomputed from it and reconciled against the results.
3. **Source reconciliation (F4).** `store_day_demand_reconciled` compares the store-day total quantity with the Phase 10 source total; `store_day_keys_unique`, `store_count_preserved` and `input_target_complete` close the remaining input requirements.
4. **Baseline verification (F7).** `naive_matches_last_observation` and `seasonal_naive_matches_weekly_pattern` recompute each baseline from the training window and compare it with the stored predictions. A length mismatch is reported as a failed comparison rather than an exception (`_arrays_agree`).
5. **Temporal contract checks (F3).** `training_window_ends_at_train_end`, `validation_window_matches_contract`, `validation_horizon_consistent`, `test_period_excluded_from_evaluation` and `test_partition_present_but_unused` verify the boundaries rather than trusting the constants.
6. **Reproducibility record (F6).** The configurations artifact now carries `training_start`, `training_end`, `validation_start`, `validation_end` and `forecast_horizon` alongside the configuration string.
7. **Findings correction (F2).** `write_findings` reports `validation period: 2024-02-11 to 2024-06-03`, the training end separately, the excluded test period, the zero-filled store-day count, both best-model criteria, the input reconciliation and the quality-check status.
8. **Measured densification (F9).** `to_regular_daily_series` validates the input index (non-empty, datetime, chronological) and the findings report records that exactly one store-day was zero-filled (store 3, 2022-10-16).
9. **Metric guards (F5).** `rmse` and `mape` now reject mismatched or empty inputs instead of broadcasting silently.
10. **Pooled metrics (F3).** `create_summary` adds pooled RMSE and MAPE across all store-day validation observations alongside the across-store mean and median.

### Testing

| Test | Result |
|---|---|
| Phase 11 test file | 52 tests, all passing (was 11) |
| Full suite | 321 tests, all passing; Phase 11 adds 41 tests |

Coverage added: loader schema and sorting, missing-input handling, input summarisation, store-day aggregation, densification of gaps and its input-index validation, per-store model runs (configuration, horizon, baseline reproduction), summary pooled-metric reconciliation and ordering, the quality report pass case on a full synthetic workflow, thirteen deliberate-failure cases (duplicate store-day key, unreconciled demand, missing target value, wrong validation window, inconsistent horizon, test-period leakage, incomplete model coverage, wrong naive and seasonal predictions, RMSE and MAPE mismatch, missing ARIMA configuration, missing prediction rows), findings content (including the corrected validation period) and the complete `main()` workflow plus its failure paths.

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/forecasting_models.py
Exit status: 0
Runtime:     21.4 seconds
Peak memory: 1,279.6 MB
Result:      "Forecasting models completed successfully."
```

The peak is dominated by reading the 888 MB Phase 10 matrix (four columns) and its store-day aggregation.

### Generated-file verification

| File | Exists | Structure | Validation |
|---|---|---|---|
| `forecasting_model_results.csv` | yes | 12 rows, 7 columns | byte-identical to the pre-audit artifact; metrics reproduced from predictions |
| `forecasting_model_configurations.csv` | yes | 12 rows, 8 columns | training end 2024-02-10; ARIMA order explicit |
| `forecasting_summary.csv` | yes | 3 rows, 9 columns | reconciles with results and predictions |
| `forecasting_predictions.csv` | yes | 1,368 rows, 5 columns | no missing values; dates 2024-02-11 to 2024-06-03 |
| `forecasting_quality_report.csv` | yes | 24 rows, 4 columns | all passing |
| `forecasting_findings.txt` | yes | 63 lines | validation period, reconciliation and quality status present |

### Documentation changes

All six Phase 11 documents were rewritten under their existing headings, and the cross-phase records listed under "Files reviewed" were synchronised.

### Remaining issues

- None open for Phase 11.
- Cross-phase (F10): the Phase 10 engineered features are still not used as predictors by `forecasting_models.py`, `evaluate_and_tune_models.py` or `forecasting_inventory_insights.py`. Phase 11's documented scope is classical univariate models, so this is not a Phase 11 verification failure, but the gap remains open for the Phase 12 and 13 audits.
- Store 4 has only 60 ARIMA training observations because it first appears on 2023-12-13; Phase 12 should treat that store's ARIMA result with corresponding caution.

## Reproduction runbook

Run from the project root with the virtual environment present, after Phase 10 has produced `data/processed/feature_engineered_daily.csv`.

| # | Purpose | Command | Expected result |
|---|---|---|---|
| 1 | Run the Phase 11 tests | `.venv\Scripts\python.exe -m pytest tests/test_forecasting_models.py -q -p no:cacheprovider` | 52 passed |
| 2 | Execute the forecasting workflow | `.venv\Scripts\python.exe scripts/forecasting_models.py` | "Forecasting models completed successfully." |
| 3 | Verify the quality report | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/forecasting_quality_report.csv'); print(len(r), bool(r['passed'].all()))"` | `24 True` |
| 4 | Verify the summary | `.venv\Scripts\python.exe -c "import pandas as pd; print(pd.read_csv('data/analysis/forecasting_summary.csv').to_string(index=False))"` | seasonal_naive best on mean and pooled RMSE |
| 5 | Verify test isolation | `.venv\Scripts\python.exe -c "import pandas as pd; p=pd.read_csv('data/analysis/forecasting_predictions.csv', parse_dates=['date']); print(p['date'].min().date(), p['date'].max().date(), len(p))"` | `2024-02-11 2024-06-03 1368` |
| 6 | Regression: producing phase | `.venv\Scripts\python.exe -m pytest tests/test_feature_engineering.py -q -p no:cacheprovider` | 32 passed |
