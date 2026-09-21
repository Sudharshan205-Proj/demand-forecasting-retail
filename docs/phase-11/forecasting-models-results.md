# Phase 11 — Forecasting Models Results

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

The store-day total quantity equals the source total exactly, so the aggregation
to the forecasting grain is lossless.

## Validation Period

2024-02-11 through 2024-06-03 — 114 daily observations for every store.

Training ends 2024-02-10. Stores 1–3 train from 2022-08-28; store 4 trains from
2023-12-13 (60 observations).

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

Pooled metrics are computed over all 456 store-day validation observations per
model (4 stores × 114 days).

The seasonal-naive benchmark is the best model on both the across-store mean and
the pooled metric. ARIMA(1,1,1) improves on naive but does not beat the weekly
benchmark. The validation store-days contain no zero-demand observations, so no
observation was excluded from MAPE.

## Test Isolation

The test period beginning 2024-06-04 was not used. The quality report verifies
that the latest prediction date is 2024-06-03 and that every configuration's
training window ends at 2024-02-10. One month of test data (1,566,653 rows)
exists and was deliberately excluded.

## Artifacts

* `data/analysis/forecasting_model_results.csv`
* `data/analysis/forecasting_model_configurations.csv`
* `data/analysis/forecasting_summary.csv`
* `data/analysis/forecasting_predictions.csv`
* `data/analysis/forecasting_quality_report.csv`
* `data/analysis/forecasting_findings.txt`

| File | Rows | Columns | Size |
|---|---:|---:|---:|
| `forecasting_model_results.csv` | 12 | 7 | 872 B |
| `forecasting_model_configurations.csv` | 12 | 8 | 1,271 B |
| `forecasting_summary.csv` | 3 | 9 | 431 B |
| `forecasting_predictions.csv` | 1,368 | 5 | 58,997 B |
| `forecasting_quality_report.csv` | 24 | 4 | 1,125 B |
| `forecasting_findings.txt` | 63 lines | — | 2,551 B |

The quality report contains 24 checks, all passing.

## Interpretation

At the validation stage the weekly seasonal pattern carries more predictive
information than the ARIMA(1,1,1) specification: demand for these stores is
dominated by day-of-week structure, which a seasonal-naive benchmark reproduces
directly. Phase 12 uses these benchmarks as the reference against which every
further candidate, including the feature-based gradient-boosting model, is
compared.

## Reproduction runbook

Run from the project root with the virtual environment present, after Phase 10
has produced `data/processed/feature_engineered_daily.csv`.

| # | Purpose | Command | Expected result |
|---|---|---|---|
| 1 | Run the Phase 11 tests | `.venv\Scripts\python.exe -m pytest tests/test_forecasting_models.py -q -p no:cacheprovider` | 52 passed |
| 2 | Execute the forecasting workflow | `.venv\Scripts\python.exe scripts/forecasting_models.py` | "Forecasting models completed successfully." |
| 3 | Verify the quality report | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/forecasting_quality_report.csv'); print(len(r), bool(r['passed'].all()))"` | `24 True` |
| 4 | Verify the summary | `.venv\Scripts\python.exe -c "import pandas as pd; print(pd.read_csv('data/analysis/forecasting_summary.csv').to_string(index=False))"` | seasonal_naive best on mean and pooled RMSE |
| 5 | Verify test isolation | `.venv\Scripts\python.exe -c "import pandas as pd; p=pd.read_csv('data/analysis/forecasting_predictions.csv', parse_dates=['date']); print(p['date'].min().date(), p['date'].max().date(), len(p))"` | `2024-02-11 2024-06-03 1368` |
| 6 | Regression: producing phase | `.venv\Scripts\python.exe -m pytest tests/test_feature_engineering.py -q -p no:cacheprovider` | 32 passed |
| 7 | Regression: full suite | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 532 passed |
