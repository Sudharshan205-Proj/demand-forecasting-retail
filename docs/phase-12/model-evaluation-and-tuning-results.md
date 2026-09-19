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

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).

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