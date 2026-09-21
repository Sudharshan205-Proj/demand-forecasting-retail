# Phase 10 — Feature Engineering

## Purpose

Phase 10 converts the prepared time-series dataset into a leakage-safe feature
matrix for retail demand forecasting, keeping the Phase 9 grain, target and
chronological partitions unchanged.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Feature matrix | `data/processed/feature_engineered_daily.csv` — 7,431,026 rows, 21 columns (key, target, split, 16 features) |
| Feature groups | 7 calendar features and 9 historical features (lags 1/7/14/28, 7- and 28-observation rolling mean and standard deviation, series age) |
| Analysis tables | `feature_engineering_summary.csv`, `feature_engineering_feature_summary.csv` (per-feature completeness), `feature_engineering_quality_report.csv`, `feature_engineering_findings.txt` |
| Pipeline | `scripts/feature_engineering.py` |
| Tests | `tests/test_feature_engineering.py` — 32 tests, all passing |
| Quality record | `feature_engineering_quality_report.csv` — 14 checks, all True |

## Key results

| Finding | Value |
|---|---|
| Rows / quantity | 7,431,026 / 41,949,529.910, both unchanged from Phase 9 |
| Split row counts | 4,315,416 train / 1,548,957 validation / 1,566,653 test, matching Phase 9 |
| Feature schema | 7 of 7 calendar present; 9 of 9 historical present |
| Largest missing share | `lag_28` — 1,258,301 values (16.93%) at series starts |
| Leakage checks | `lag_1_matches_previous_observation`, `rolling_excludes_current_target`, `first_observation_has_no_history`, `split_preserved_vs_input` — all True |
| Duplicate keys | 0 |

## Course coverage

Phase 10 carries the **Process → Analyze** stage's feature-construction half:
data preparation, transformation, pattern representation, time-series thinking,
data integrity and validation, leakage awareness and reproducibility
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`feature-engineering-methodology.md`](feature-engineering-methodology.md) — method
- [`feature-engineering-quality-framework.md`](feature-engineering-quality-framework.md) — quality practices
- [`feature-engineering-results.md`](feature-engineering-results.md) — results
