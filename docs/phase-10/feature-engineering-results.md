# Phase 10 — Feature Engineering Results

## Input

`data/processed/time_series_daily.csv`

## Output

`data/processed/feature_engineered_daily.csv` — 887,995,450 bytes, 7,431,026
rows plus header, 21 columns (key, target, split and 16 features), SHA-256
`7fbe2f8155887b7cd2218237663763b4631a33721b109d162bbc0cad7c58c0e3`.

## Results

### Dataset and reconciliation

| Metric | Result |
|---|---:|
| Rows | 7,431,026 |
| Source rows | 7,431,026 |
| Unique items | 28,180 |
| Unique stores | 4 |
| Date range | 2022-08-28 to 2024-09-26 |
| Features | 16 |
| Target | `quantity` |
| Total quantity | 41,949,529.910 |
| Source quantity | 41,949,529.910 |

Rows, keys, target values, split labels and the quantity total all reconcile with
the Phase 9 dataset.

### Chronological partitions (preserved)

| Split | Rows | Quantity | Date range |
|---|---:|---:|---|
| Train | 4,315,416 | 24,038,416.097 | 2022-08-28 to 2024-02-10 |
| Validation | 1,548,957 | 8,811,477.346 | 2024-02-11 to 2024-06-03 |
| Test | 1,566,653 | 9,099,636.467 | 2024-06-04 to 2024-09-26 |

The split row counts and quantities match Phase 9 exactly, so the Phase 9
chronological partitions are preserved unchanged.

### Feature groups

Calendar features (7): `day_of_week`, `day_of_month`, `week_of_year`, `month`,
`quarter`, `year`, `is_weekend`.

Historical features (9): `lag_1`, `lag_7`, `lag_14`, `lag_28`,
`rolling_mean_7`, `rolling_std_7`, `rolling_mean_28`, `rolling_std_28`,
`series_age_days`.

### Feature completeness

`feature_engineering_feature_summary.csv` records the missing-value structure of
every feature:

| Feature | Missing | Missing share |
|---|---:|---:|
| `lag_1` | 58,022 | 0.78% |
| `lag_7` | 374,137 | 5.03% |
| `lag_14` | 697,526 | 9.39% |
| `lag_28` | 1,258,301 | 16.93% |
| `rolling_mean_7` | 58,022 | 0.78% |
| `rolling_std_7` | 114,064 | 1.54% |
| `rolling_mean_28` | 58,022 | 0.78% |
| `rolling_std_28` | 114,064 | 1.54% |
| `series_age_days` | 0 | 0.00% |
| Calendar features (7) | 0 | 0.00% |

The pattern is expected: each series' first observation has no history, so
`lag_1` and `rolling_mean_7` are missing exactly once per series (58,022 = the
number of item-store series). Longer lags and the standard deviations
(`min_periods=2`) accumulate more missing values at each series start. Calendar
features and `series_age_days` are always present.

### Leakage contract

| Rule | Result |
|---|---|
| `lag_1` equals the previous observed quantity | True |
| The first observation of every series has no history (`lag_1` and `rolling_mean_7` missing) | True |
| `rolling_mean_7` excludes the current observation | True |
| Split labels unchanged from Phase 9 | True |
| No random shuffling | Verified by design |

## Interpretation

The matrix exposes recurring temporal structure (calendar fields) and recent
demand history (lags and rolling statistics) without using the current or any
future observation. `series_age_days` distinguishes established series from
newly observed ones using only information available at each row.

The matrix is consumed downstream at different grains. Phase 12's
`feature_gbm` candidate uses all 16 feature families, recomputed at the
store-day grain with recursive prediction. Phase 11's classical univariate
models and Phase 13's inventory-insight workflow consume the demand target and
the chronological split from the same file, because those methods are defined on
the demand series itself.

## Limitations

- **Record-based windows.** Lag and rolling windows operate over previous
  *observed records*, not calendar days. Because 55,122 of 58,022 item-store
  series contain intermediate date gaps (Phase 9), `lag_7` is the seventh
  previous observed record rather than necessarily the observation seven days
  earlier. This is a deliberate, documented design decision, not a hidden
  assumption.
- **Missing feature values.** Up to 16.93% of `lag_28` values are missing at
  series starts, so any consumer of the feature matrix must handle them
  explicitly rather than assuming a complete matrix.
- **Price and promotion fields are excluded.** They are withheld until their
  temporal semantics are validated, so the matrix carries demand and calendar
  structure only.

## Reproduction runbook

Run from the project root with the virtual environment present, after Phase 9
has produced `data/processed/time_series_daily.csv`.

| # | Purpose | Command | Expected result |
|---|---|---|---|
| 1 | Run the Phase 10 tests | `.venv\Scripts\python.exe -m pytest tests/test_feature_engineering.py -q -p no:cacheprovider` | 32 passed |
| 2 | Execute the feature workflow | `.venv\Scripts\python.exe scripts/feature_engineering.py` | "Feature engineering completed successfully." |
| 3 | Verify the quality report | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/feature_engineering_quality_report.csv'); print(len(r), bool(r['passed'].all()))"` | `14 True` |
| 4 | Verify reconciliation | `.venv\Scripts\python.exe -c "import pandas as pd; print(pd.read_csv('data/analysis/feature_engineering_summary.csv').to_string(index=False))"` | 7,431,026 rows; 4,315,416 / 1,548,957 / 1,566,653 split rows |
| 5 | Verify feature completeness | `.venv\Scripts\python.exe -c "import pandas as pd; print(pd.read_csv('data/analysis/feature_engineering_feature_summary.csv').to_string(index=False))"` | 16 features; `lag_1` missing = 58,022 |
| 6 | Regression: producing phase | `.venv\Scripts\python.exe -m pytest tests/test_prepare_time_series.py -q -p no:cacheprovider` | 37 passed |
| 7 | Regression: full suite | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 532 passed |
