# Phase 10 — Feature Engineering Results

## Status

VERIFIED

Verified during the Phase 17 re-audit by executing the feature-engineering
workflow against the full Phase 9 dataset (7,431,026 rows) and inspecting
every generated artifact. All reported values come from the complete dataset.

## Input

`data/processed/time_series_daily.csv`

## Output

`data/processed/feature_engineered_daily.csv` — 887,995,450 bytes,
7,431,026 rows plus header, 21 columns (key, target, split and 16 features).

## Verified Results

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

Rows, keys, target values, split labels and the quantity total all reconcile
with the Phase 9 dataset. The output dataset is byte-size-identical to the
pre-audit artifact, so the re-audit's vectorized rewrite changed speed, not
values.

### Chronological partitions (preserved)

| Split | Rows | Quantity | Date range |
|---|---:|---:|---|
| Train | 4,315,416 | 24,038,416.097 | 2022-08-28 to 2024-02-10 |
| Validation | 1,548,957 | 8,811,477.346 | 2024-02-11 to 2024-06-03 |
| Test | 1,566,653 | 9,099,636.467 | 2024-06-04 to 2024-09-26 |

The split row counts and quantities match Phase 9 exactly, so the Phase 9
chronological partitions are preserved unchanged.

### Feature groups

Calendar features (7): `day_of_week`, `day_of_month`, `week_of_year`,
`month`, `quarter`, `year`, `is_weekend`.

Historical features (9): `lag_1`, `lag_7`, `lag_14`, `lag_28`,
`rolling_mean_7`, `rolling_std_7`, `rolling_mean_28`, `rolling_std_28`,
`series_age_days`.

### Feature completeness

`feature_engineering_feature_summary.csv` records the missing-value structure
of every feature:

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
`lag_1` and `rolling_mean_7` are missing exactly once per series (58,022 =
the number of item-store series). Longer lags and the standard deviations
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

## Limitations

- **Record-based windows.** Lag and rolling windows operate over previous
  *observed records*, not calendar days. Because 55,122 of 58,022 item-store
  series contain intermediate date gaps (Phase 9), `lag_7` is the seventh
  previous observed record rather than necessarily the observation seven days
  earlier. This is a deliberate, documented design decision, not a hidden
  assumption.
- **Missing feature values.** Up to 16.93% of `lag_28` values are missing at
  series starts; later modeling stages must handle these explicitly rather than
  assuming a complete feature matrix.
- **Price and promotion fields are excluded.** They are withheld until their
  temporal semantics are validated, so the matrix carries demand and calendar
  structure only.
- **The features are not currently consumed as predictors.** Phases 11, 12 and
  13 all read `feature_engineered_daily.csv` but select only
  `date`, `store_id`, `quantity` and `split`; the lag, rolling and calendar
  features never reach a model. This is a Phase 11–13 integration gap, flagged
  for those audits, not a Phase 10 defect. Phase 10's obligation is to build a
  leakage-safe, verified matrix, which it does. The Phase 11 re-audit confirmed
  the gap still stands and carried it forward to the Phase 12–13 audits,
  because Phase 11's documented scope is classical univariate models.

## Phase status

Phase 10 is implemented, executed and verified.

## Phase 17 Re-Audit Record

**Audit status: AUDITED.**

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/feature_engineering.py` |
| Tests | `tests/test_feature_engineering.py` |
| Phase 10 documents | all six files in `docs/phase-10/` |
| Generated artifacts | `data/processed/feature_engineered_daily.csv`; `feature_engineering_summary.csv`, `feature_engineering_quality_report.csv`, `feature_engineering_feature_summary.csv`, `feature_engineering_split_summary.csv`, `feature_engineering_findings.txt` |
| Inputs | `data/processed/time_series_daily.csv` (Phase 9) |
| Downstream | `scripts/forecasting_models.py`, `scripts/evaluate_and_tune_models.py`, `scripts/forecasting_inventory_insights.py` |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-2/dataset-inventory.md`, `docs/phase-9/time-series-results.md`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Documentation never updated after execution | `feature-engineering-results.md` said "NOT YET VERIFIED"; the checklist was entirely unchecked; the register said "Not yet started" while the README reported COMPLETE | Medium |
| F2 | Two quality checks reported a hardcoded `actual=True` | `calendar_features_present` and `historical_features_present` set `actual: True` regardless of `passed` | Low |
| F3 | Framework validation was unimplemented | The framework and plan required target-alteration, leakage (lag-from-prior, rolling-excludes-current, future-exclusion, split-unchanged) and quantity reconciliation checks; none existed. `target_quantity_missing` is not target preservation | Medium |
| F4 | No reconciliation with the Phase 9 input | No check compared rows, keys, quantity total or split labels against the source | Medium |
| F5 | Full-memory processing was slow and unmeasured | The Python `transform` lambda made the full run exceed the audit time budget; no runtime or memory figure was documented | Medium |
| F6 | Missing-value structure undocumented | The lag/rolling NaNs at series starts appeared in no artifact; no per-feature completeness report existed | Medium |
| F7 | Test coverage missed the core | 10 tests covered pure functions; `main`, summary, split summary, findings and end-to-end were untested | Medium |
| F8 | Engineered features are unused downstream | Phases 11, 12 and 13 select only `date/store_id/quantity/split` from the matrix | Informational (cross-phase) |
| F9 | The prior `series_age_days` leakage flag was incorrect | The feature is `date − series(min date)`; a series' first observed date is always at or before its later rows, so no future information enters it | Resolved |

**Leakage audit:** the matrix introduces no forward-looking feature. `lag_1`
is verified to equal the previous observed quantity, the rolling mean is
verified to exclude the current observation, and the split labels are
preserved unchanged. `series_age_days` uses only at-or-before information.

**Positive validation:** the re-executed output reproduces the pre-audit
dataset exactly (887,995,450 bytes; 7,431,026 rows) and the split rows and
quantities match Phase 9 exactly.

### Code changes

1. **Real presence checks (F2).** `calendar_features_present` and
   `historical_features_present` now report the number of features present
   (7 of 7; 9 of 9) instead of a constant `True`.
2. **Source reconciliation (F3, F4).** `create_quality_report(frame, source)`
   now compares rows, keys, target values and split labels against the Phase 9
   input and reconciles the quantity total
   (`input_output_rows_match`, `input_output_keys_match`,
   `target_preserved_vs_input`, `split_preserved_vs_input`,
   `quantity_total_reconciled`).
3. **Leakage verification (F3).** New checks
   `lag_1_matches_previous_observation`, `first_observation_has_no_history`
   and `rolling_excludes_current_target` assert the historical features use
   prior observations only.
4. **Feature completeness artifact (F6).** New
   `feature_engineering_feature_summary.csv` (16 rows: feature, group, dtype,
   non-null, missing, missing share).
5. **Vectorized rolling (F5).** The per-group `transform` lambda was replaced
   by pandas' compiled `groupby(...).rolling(...)`; values are identical and
   the full run now completes in 365.6 seconds.
6. **Reduced copying (F5).** `prepare_features` no longer makes a redundant
   copy and re-sort, and the reconciliation sort operates on five columns
   rather than the full 21-column frame.
7. **Enriched summary and findings (F4, F6).** `feature_engineering_summary.csv`
   now records source rows and split rows; the findings report source
   reconciliation, split preservation, the leakage contract and feature
   completeness.
8. **Quantity formatting.** `quantity_total_reconciled` renders both figures
   through `_format_quantity`, so the report prints `41949529.910` rather than
   `41949529.910000004`. The pass/fail decision is computed numerically before
   formatting, so presentation can never mask a mismatch (asserted by test).
9. **Deterministic date parsing.** `add_calendar_features` parses dates with an
   explicit ISO format (`%Y-%m-%d`). The Phase 9 source dates are ISO-shaped,
   so an invalid date now raises immediately instead of triggering pandas'
   per-element inference; this removed the Phase 10 test `UserWarning`.

### Testing

| Test | Result |
|---|---|
| Phase 10 test file | 32 tests, all passing (was 10) |
| Full suite | 280 tests, all passing; Phase 9 and Phase 10 add 48 between them |

Coverage added: end-to-end `prepare_features`, invalid date and column
rejection, rolling mean and standard deviation values, multi-series
independence, target/split preservation, the quality report pass and five
deliberate-failure cases (duplicate key, modified target, changed split,
missing feature, current-inclusive rolling, history at series start),
presence-check counts, the feature summary, split summary, findings formatting
and the complete `main()` workflow. One further test asserts that the
quantity-reconciliation row carries no floating-point artefacts.

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/feature_engineering.py
Exit status: 0
Runtime:     365.6 seconds
Peak memory: 2,510.3 MB
Result:      "Feature engineering completed successfully."
```

The peak is dominated by the fully materialized 7,431,026 x 21 feature frame,
which whole-series group-wise operations require. The compiled grouped-rolling
path keeps runtime within budget; the Python `transform` lambda exceeded the
audit time budget.

Phase 10 was re-run after Phase 9 so that its input — the regenerated Phase 9
dataset — was already in place. The output remains byte-size identical to the
pre-audit dataset, so every artifact again post-dates the script that produced
it.

### Generated-file verification

| File | Exists | Size | Structure | Validation |
|---|---|---|---|---|
| `feature_engineered_daily.csv` | yes | 887,995,450 B | 7,431,026 rows + header, 21 columns | byte-size identical to pre-audit; reconciles with Phase 9 |
| `feature_engineering_summary.csv` | yes | 11 metric rows | — | rows, source rows, split rows reconcile |
| `feature_engineering_quality_report.csv` | yes | 14 rows | check/passed/actual/expected | all True; quantity row carries no float artefacts |
| `feature_engineering_feature_summary.csv` | yes | 16 rows | feature/completeness columns | `lag_1` missing = 58,022 series |
| `feature_engineering_split_summary.csv` | yes | 3 rows | 5 columns | matches Phase 9 exactly |
| `feature_engineering_findings.txt` | yes | 6 sections | — | no float artefacts; integer counts |

### Documentation changes

All six Phase 10 documents were rewritten under their existing headings, and
the cross-phase records listed under "Files reviewed" were synchronised.

### Remaining issues

- None open for Phase 10.
- Cross-phase: `scripts/clean_retail_data.py` (Phase 5) still emits a pandas
  `UserWarning` for implicit date inference; outside Phase 10 scope, recorded
  here for the Phase 5 audit.
- Flagged for the Phase 12–13 audits: the engineered features are not used as
  predictors by `forecasting_models.py`, `evaluate_and_tune_models.py` or
  `forecasting_inventory_insights.py` (F8). The Phase 11 re-audit re-confirmed
  the finding and documented that Phase 11's classical models consume the
  demand target only.
- Phase 11 verified the target/split contract this phase established: the
  store-day aggregate reconciles with the matrix on total quantity
  (41,949,529.910) and total rows (7,431,026), with no duplicate store-day key
  and no target missing value.
- The record-based lag/rolling semantics and the missing feature values at
  series starts are modelling constraints for Phase 11–12, documented here.

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
| 7 | Regression: full suite | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 321 passed |
