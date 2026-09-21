# Phase 12 — Model Evaluation & Tuning

## Purpose

Phase 12 evaluates the candidate forecasting approaches under chronological
cross-validation and selects one configuration per store, without using the test
period for model selection or tuning.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Cross-validation | Expanding-window folds with a fixed 28-day horizon on the training period; 90/90 fold evaluations completed (stores 1–3: three folds each; store 4: one affordable fold) |
| Candidate set | Nine configurations per store — naive, seasonal-naive (7/14/28), ARIMA (0,1,1)/(1,1,0)/(1,1,1)/(2,1,1) and `feature_gbm` over 16 store-day features |
| Selection | One configuration per store, chosen by mean CV RMSE with mean CV MAPE as tie-break; store 4 retained rather than skipped |
| Validation | Selected configurations evaluated on the untouched 114-day validation period (2024-02-11 to 2024-06-03) |
| Error analysis | Validation bias, mean absolute error and RMSE per store, split at the midpoint of the validation window |
| Artifacts | `model_tuning_results.csv`, `tuned_validation_results.csv`, `selected_model_configurations.csv`, `model_evaluation_predictions.csv`, `model_selection_findings.txt` |
| Pipeline | `scripts/evaluate_and_tune_models.py` |
| Tests | `tests/test_evaluate_and_tune_models.py` — 64 tests, all passing |
| Quality record | `model_evaluation_quality_report.csv` — 30 checks, all True |

## Key results

| Finding | Value |
|---|---|
| CV winners | `feature_gbm` for stores 1–3 (mean CV RMSE 3,804.0051 / 620.5061 / 599.4431); `seasonal_naive(7)` for store 4 |
| Validation RMSE | Store 1 4,233.4919 (−11.13% vs Phase 11), store 2 711.2067 (−6.38%), store 3 1,309.9600 (+0.32%), store 4 6,063.0559 (unchanged) |
| Mean validation RMSE | 3,079.4286, a 4.46% reduction on Phase 11's best single model (3,223.0630) |
| Error analysis | All selected models under-forecast on average in both halves, with growing bias in the second half |
| Test isolation | No fold or validation forecast reaches 2024-06-04 |
| Reconciliation | Store 4's classical configuration reproduces Phase 11's forecasts exactly (maximum absolute difference 0) |

## Course coverage

Phase 12 carries the **Analyze** stage's model-development half: model
evaluation, time-aware validation, analytical thinking, statistical analysis,
feature engineering, machine learning, evidence-based model selection, data
integrity and reproducibility
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`model-evaluation-and-tuning-methodology.md`](model-evaluation-and-tuning-methodology.md) — method
- [`model-evaluation-and-tuning-quality-framework.md`](model-evaluation-and-tuning-quality-framework.md) — quality practices
- [`model-evaluation-and-tuning-results.md`](model-evaluation-and-tuning-results.md) — results
