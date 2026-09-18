# Phase 12 — Model Evaluation & Tuning Results

## Status

VERIFIED.

Every figure below was produced by `scripts/evaluate_and_tune_models.py`
during the Phase 17 re-audit and inspected directly in the generated
artifacts. The stale pre-audit artifacts (dated 8 Sep, before the Phase 10
input was regenerated) reproduced byte-identically when the original script
was re-run, so the audit's comparison point was sound; the results below
come from the re-audited pipeline, which additionally covers store 4 and
the feature-based candidate.

## Evaluation Design

The phase uses:

- training-period expanding-window cross-validation;
- three requested cross-validation folds, adapted down to the largest
  affordable count for stores with shorter histories;
- 28-day forecast horizons (fixed);
- a minimum initial training sample of 28 observations;
- RMSE as the primary selection metric;
- MAPE as a complementary metric and tie-break.

Nine candidate configurations are evaluated for every store: nine
configurations x ten folds (three stores x three folds, plus store 4's
single fold) = 90 cross-validation evaluations, all of which completed
successfully.

| Store | Folds | Fold training windows (end) | Fold test windows |
|---:|---:|---|---|
| 1 | 3 | 2023-11-18, 2023-12-16, 2024-01-13 | 2023-11-19–2023-12-16, 2023-12-17–2024-01-13, 2024-01-14–2024-02-10 |
| 2 | 3 | 2023-11-18, 2023-12-16, 2024-01-13 | 2023-11-19–2023-12-16, 2023-12-17–2024-01-13, 2024-01-14–2024-02-10 |
| 3 | 3 | 2023-11-18, 2023-12-16, 2024-01-13 | 2023-11-19–2023-12-16, 2023-12-17–2024-01-13, 2024-01-14–2024-02-10 |
| 4 | 1 | 2024-01-13 (from 2023-12-13) | 2024-01-14–2024-02-10 |

Store 4 first appears on 2023-12-13, so its 60 training observations support
exactly one 28-day fold. It is tuned and validated rather than excluded.

## Candidate Models

### Naive

Last observed value.

### Seasonal Naive

Candidate season lengths:

- 7
- 14
- 28

### ARIMA

Candidate orders:

- (0,1,1)
- (1,1,0)
- (1,1,1)
- (2,1,1)

### Feature-Based Model

`feature_gbm` — `HistGradientBoostingRegressor(learning_rate=0.1,
max_iter=200, max_depth=3, min_samples_leaf=5, l2_regularization=1.0,
early_stopping=False, random_state=0)`, fitted on the 16 store-day lag,
rolling and calendar features that mirror the Phase 10 families, with
recursive multi-step forecasting.

## Test-Set Protection

The test period is not used during Phase 12 tuning. The quality report
verifies that the latest cross-validation and validation forecast date is
2024-06-03, before the test period begins on 2024-06-04.

## Results

### Store coverage

All four stores were tuned and validated. No store was skipped.

### Cross-validation leaderboard (mean CV RMSE)

| Store | Winner | Mean CV RMSE | Mean CV MAPE | Runner-up | Runner-up RMSE |
|---:|---|---:|---:|---|---:|
| 1 | feature_gbm | 3,804.0051 | 8.6164% | seasonal_naive (7) | 4,413.7272 |
| 2 | feature_gbm | 620.5061 | 8.3563% | seasonal_naive (7) | 1,049.5830 |
| 3 | feature_gbm | 599.4431 | 9.2610% | seasonal_naive (7) | 1,280.8110 |
| 4 | seasonal_naive (7) | 3,908.9523 | 12.1233% | seasonal_naive (14) | 7,565.6522 |

The feature model wins the training-period cross-validation on RMSE for
stores 1–3. Store 1 is the one case where the winner does not also win on
MAPE: the feature model's 8.6164% is higher than seasonal_naive(7)'s
7.7988%, because selection is by RMSE and RMSE penalises the large errors
more strongly.

Store 4's single fold favours the seven-day seasonal benchmark, which is
unsurprising with 60 training observations and a 28-day seasonal cycle.

### Selected configurations

| Store | Model | Configuration |
|---:|---|---|
| 1 | feature_gbm | HistGradientBoostingRegressor (recursive, 16 store-day features) |
| 2 | feature_gbm | HistGradientBoostingRegressor (recursive, 16 store-day features) |
| 3 | feature_gbm | HistGradientBoostingRegressor (recursive, 16 store-day features) |
| 4 | seasonal_naive | season_length=7 |

### Validation results (untouched 114-day period)

| Store | Selected model | RMSE | MAPE | Phase 11 RMSE | Change |
|---:|---|---:|---:|---:|---:|
| 1 | feature_gbm | 4,233.4919 | 9.0715% | 4,763.7639 | −11.13% |
| 2 | feature_gbm | 711.2067 | 8.1414% | 759.6968 | −6.38% |
| 3 | feature_gbm | 1,309.9600 | 16.2833% | 1,305.7352 | +0.32% |
| 4 | seasonal_naive (7) | 6,063.0559 | 14.0605% | 6,063.0559 | 0.00% |

Mean validation RMSE across the four selected configurations: **3,079.4286**,
against **3,223.0630** for Phase 11's best single model (seasonal-naive,
all four stores) — a 4.46% reduction in the mean.

The result is deliberately not oversold. The tuned portfolio improves
stores 1 and 2 clearly, is essentially unchanged for store 4 (the same
configuration, reproduced exactly), and is marginally worse for store 3,
where the cross-validation winner does not beat the phase's own benchmark
on the validation period. Cross-validation selection is evidence, not a
guarantee.

### Error analysis

| Store | Segment | Mean error | Mean absolute error | RMSE |
|---:|---|---:|---:|---:|
| 1 | first half | 245.66 | 2,877.80 | 4,421.58 |
| 1 | second half | 1,142.96 | 3,219.33 | 4,036.64 |
| 2 | first half | 171.80 | 500.74 | 686.54 |
| 2 | second half | 277.49 | 576.15 | 735.05 |
| 3 | first half | 672.96 | 814.84 | 982.44 |
| 3 | second half | 1,026.59 | 1,388.19 | 1,570.61 |
| 4 | first half | 2,800.11 | 3,784.12 | 5,444.02 |
| 4 | second half | 4,941.96 | 5,349.58 | 6,624.50 |

Every selected model under-forecasts on average in both halves, and the
bias grows in the second half for stores 1, 3 and 4. This is a systematic
under-forecast rather than random error, and it is the strongest signal in
the error analysis.

### Phase 11 reconciliation

Store 4's selected `seasonal_naive(7)` configuration reproduces Phase 11's
validation forecasts exactly (maximum absolute difference 0), confirming
that the two phases compute the same forecast for the same configuration.

## Interpretation Rule

No model is declared superior beyond what the validation results support.
The selected configurations improved the mean validation RMSE over Phase
11, but store 3's cross-validation winner did not beat the weekly benchmark
on validation and store 4 used the same configuration as Phase 11. Test
performance remains unknown and reserved.

## Phase 17 Re-Audit Record

**Audit status: AUDITED.**

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/evaluate_and_tune_models.py` |
| Tests | `tests/test_evaluate_and_tune_models.py` |
| Phase 12 documents | all six files in `docs/phase-12/` |
| Generated artifacts | `model_tuning_results.csv`, `model_tuning_summary.csv`, `selected_model_configurations.csv`, `tuned_validation_results.csv`, `model_error_analysis.csv`, `model_evaluation_predictions.csv`, `model_evaluation_quality_report.csv`, `model_evaluation_findings.txt` |
| Inputs | `data/processed/feature_engineered_daily.csv` (Phase 10) |
| Upstream | `data/analysis/forecasting_predictions.csv` (Phase 11, reconciliation reference) |
| Downstream | `scripts/forecasting_inventory_insights.py` (Phase 13) |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-1/kpi-definitions.md`, `docs/phase-2/dataset-inventory.md`, `docs/phase-11/forecasting-models-results.md`, `docs/phase-13/*`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Artifacts predated the current input | All six artifacts were dated 8 Sep; the Phase 10 matrix was regenerated on 18–19 Sep, so the phase had not run against the data it consumes | High |
| F2 | Documentation never updated after execution | `model-evaluation-and-tuning-results.md` said "NOT YET EXECUTED"; the checklist was entirely unchecked; the register said "Not yet started" while the README reported COMPLETE | Medium |
| F3 | Store 4 was silently excluded | The fixed three-fold design requires 84 training days and store 4 has 60, so `run_cross_validation` skipped it; `selected_model_configurations.csv` held three rows and no artifact recorded why | High |
| F4 | Configuration strings were parsed back into parameters | `evaluate_selected_on_validation` and `create_error_analysis` re-derived `season_length`/`order` by splitting the display string, and the model dispatch was duplicated three times | Medium |
| F5 | No machine-readable validation artifact | The quality framework required data-integrity, leakage, fold, model, selection and validation checks; none was recorded and no run gated on it | High |
| F6 | No stored predictions | Metrics could not be independently recomputed, and `create_error_analysis` re-fitted every model instead of reusing the validation forecasts | Medium |
| F7 | The engineered features were unused (cross-phase) | The Phase 10–11 audits flagged that no model consumed the 16 engineered features | High (cross-phase, now resolved) |
| F8 | Fold identifiers carried no window dates | The framework requires every fold to be recorded; only a fold number was stored | Low |
| F9 | Test coverage missed the core | 12 tests covered pure functions only; loading, folds, per-store runs, selection, quality, findings and `main` were untested | Medium |
| F10 | Skipped stores were unrecorded | A skip was printed to the console only, so a partial model set could be reported as a complete comparison | Medium |

**Leakage audit:** no test observation enters tuning. Every fold trains
strictly before its test window; fold windows end at 2024-02-10; the
validation evaluation uses the complete training period only; and the
latest stored forecast date is 2024-06-03. The feature model's lags and
rolling statistics are verified to use prior observations only, and its
recursive forecasting folds earlier predictions back in rather than any
actual value.

**Positive validation:** the pre-audit script was re-executed before any
change and reproduced all six stale artifacts byte-for-byte, so the
differences below come from the audit's own changes rather than from input
drift.

### Code changes

1. **Adaptive fold count (F3).** `create_cv_folds` now uses the requested
   three folds when the series can afford them and otherwise the largest
   affordable count, keeping the 28-day horizon fixed and enforcing a
   28-observation minimum training sample. Stores 1–3 keep exactly their
   previous folds and values; store 4 gains its single fold.
2. **Explicit store-coverage contract (F3, F10).** `run_cross_validation`
   returns a skipped-store frame with the reason and training length, and
   the quality report fails if any store is neither tuned nor recorded.
3. **Typed configurations (F4).** `ModelConfiguration` carries
   `season_length` and `order`; the artifacts record them as explicit
   columns; validation and error analysis resolve the typed object from a
   registry. Every string parse was removed, and the three duplicated
   dispatch blocks collapsed into one `forecast_configuration`.
4. **Feature-based candidate (F7).** `build_feature_frame` and
   `feature_forecast` add a deterministic gradient-boosting candidate that
   consumes the Phase 10 feature families at the store-day grain, with
   recursive multi-step forecasting.
5. **Stored predictions (F6).** `model_evaluation_predictions.csv` records
   all 2,976 fold and validation forecasts; metrics and error-analysis
   segments are now recomputed from them, and `create_error_analysis` no
   longer re-fits any model.
6. **Machine-readable quality report (F5).** 30 checks gating the run,
   covering input reconciliation, split boundaries, coverage, fold
   structure, leakage, the selection rule, feature leakage, metric
   reproduction and error-analysis reconciliation.
7. **Fold windows recorded (F8).** Each fold now stores training/test start
   and end dates.
8. **Metric guards.** `rmse`/`mape` reject mismatched or empty inputs, the
   forecast primitives validate their horizon, and `validate_splits`
   rejects duplicate store-day rows.
9. **Findings rewrite.** The report now records input reconciliation, the
   fold rule, store coverage, both CV and validation tables, the feature
   candidate's outcome, the Phase 11 reconciliation and the quality status.

### Testing

| Test | Result |
|---|---|
| Phase 12 test file | 64 tests, all passing (was 12) |
| Full suite | 373 tests, all passing; Phase 12 adds 52 |

Coverage added: metric guards, forecast primitives, the feature builder
(all 16 features, lag identity, rolling exclusion, target preservation,
series age, determinism, horizon and argument validation), the typed
dispatcher and configuration fields, adaptive fold creation (requested
count, adapted count, reduced count, chronology, expansion, rejection),
split validation including duplicate keys, cross-validation coverage and
skip recording, summary aggregation, the selection rule and its MAPE
tie-break, validation and error-analysis reproduction, the quality report's
pass case and eleven deliberate-failure cases, and the full `main()`
workflow with its missing-input and failed-quality-check paths.

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/evaluate_and_tune_models.py
Exit status: 0
Runtime:     70.9 seconds
Peak memory: 236.6 MB
Result:      "Model evaluation and tuning completed successfully."
```

The chunked loader keeps the peak low relative to Phase 11's fully
materialised frame. Runtime rose from 29 seconds because the evaluation now
covers four stores instead of three and includes the feature candidate.
Repeat runs of the final script completed in 63–71 seconds with byte-identical
artifacts, so the figures above are a representative sample rather than a
fixed runtime.

### Generated-file verification

| File | Rows | Columns | Size | Validation |
|---|---:|---:|---:|---|
| `model_tuning_results.csv` | 90 | 14 | 15,695 B | all successful; fold windows recorded |
| `model_tuning_summary.csv` | 36 | 10 | 5,690 B | reconciles with the fold results |
| `selected_model_configurations.csv` | 4 | 11 | 1,247 B | one row per store; explicit parameters |
| `tuned_validation_results.csv` | 4 | 10 | 932 B | metrics reproduced from predictions |
| `model_error_analysis.csv` | 8 | 7 | 1,727 B | recomputed from predictions |
| `model_evaluation_predictions.csv` | 2,976 | 8 | 370,431 B | 2,520 fold + 456 validation forecasts; dates 2023-11-19 to 2024-06-03 |
| `model_evaluation_quality_report.csv` | 30 | 4 | 1,354 B | all passing |
| `model_evaluation_findings.txt` | 47 lines | — | 2,850 B | coverage, reconciliation and quality status present |

### Documentation changes

All six Phase 12 documents were rewritten under their existing headings,
and the cross-phase records listed under "Files reviewed" were synchronised.

### Remaining issues

- None open for Phase 12.
- RESOLVED by the Phase 13 re-audit: Phase 13's documentation and generated
  artifacts asserted that store 4 had no tuned model and that seasonal-naive
  was selected for stores 1–3. Both claims were corrected, and the phase's
  artifacts were re-executed against this phase's evidence. Phase 13 now
  recomputes every forecast-error statistic from this phase's stored
  predictions and reconciles RMSE, MAPE and the segment error analysis
  exactly, and it confirms and quantifies the systematic under-forecast this
  phase recorded (694.31 / 224.65 / 849.77 / 3,871.04 units per day).
- The systematic under-forecast identified in the error analysis is a
  modelling limitation that Phase 13's inventory scenarios should treat as
  a known bias.
- The reserved final test evaluation still has no owning phase; it remains
  deferred and is recorded as an open item for the final project audit.

## Reproduction runbook

Run from the project root with the virtual environment present, after
Phase 10 has produced `data/processed/feature_engineered_daily.csv`.

| # | Purpose | Command | Expected result |
|---|---|---|---|
| 1 | Run the Phase 12 tests | `.venv\Scripts\python.exe -m pytest tests/test_evaluate_and_tune_models.py -q -p no:cacheprovider` | 64 passed |
| 2 | Execute the evaluation workflow | `.venv\Scripts\python.exe scripts/evaluate_and_tune_models.py` | "Model evaluation and tuning completed successfully." |
| 3 | Verify the quality report | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/model_evaluation_quality_report.csv'); print(len(r), bool(r['passed'].all()))"` | `30 True` |
| 4 | Verify store coverage | `.venv\Scripts\python.exe -c "import pandas as pd; print(sorted(pd.read_csv('data/analysis/selected_model_configurations.csv')['store_id']))"` | `[1, 2, 3, 4]` |
| 5 | Verify test isolation | `.venv\Scripts\python.exe -c "import pandas as pd; p=pd.read_csv('data/analysis/model_evaluation_predictions.csv', parse_dates=['date']); print(p['date'].max().date(), len(p))"` | `2024-06-03 2976` |
| 6 | Regression: upstream phase | `.venv\Scripts\python.exe -m pytest tests/test_forecasting_models.py -q -p no:cacheprovider` | 52 passed |
| 7 | Regression: full suite | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 373 passed |