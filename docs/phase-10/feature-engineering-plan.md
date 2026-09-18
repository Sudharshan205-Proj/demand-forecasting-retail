# Phase 10 — Feature Engineering Plan

## Purpose

Phase 10 converts the prepared Phase 9 retail time series into a feature matrix suitable for subsequent forecasting and machine-learning development.

No forecasting model is trained during this phase.

## Status

COMPLETE — implemented, executed and verified during the Phase 17 re-audit.

## Input

`data/processed/time_series_daily.csv`

## Output

`data/processed/feature_engineered_daily.csv`

## Forecasting Grain

The modeling grain is:

`date + item_id + store_id`

Each observation represents physical retail demand for an item at a store on a given date.

## Target

The forecasting target is:

`quantity`

Online demand is retained as a separate business-data concept and is not used as the physical-sales target.

## Feature Groups

### Calendar

* `day_of_week`
* `day_of_month`
* `week_of_year`
* `month`
* `quarter`
* `year`
* `is_weekend`

### Historical Demand

* `lag_1`
* `lag_7`
* `lag_14`
* `lag_28`

### Historical Rolling Statistics

* `rolling_mean_7`
* `rolling_std_7`
* `rolling_mean_28`
* `rolling_std_28`

Rolling statistics are shifted so that the current target does not contribute to its own predictors.

### Series Metadata

* `series_age_days`

## Leakage Policy

No feature may use the current target or future observations.

The Phase 9 chronological train/validation/test partitions are preserved.

Random shuffling is not used.

## Missing-Date Consideration

Phase 9 identified substantial gaps in item-store series. Therefore, the initial feature implementation defines lag and rolling windows over previous observed records rather than claiming that every lag represents an exact calendar-day offset.

This limitation is explicitly documented for later modeling decisions.

## Reproducibility

The transformation is deterministic and uses the same Phase 9 input dataset and split labels.

## Phase 17 re-audit record

**Audit status: AUDITED.**

The plan was reviewed against the implementation and the re-executed artifacts.
Requirements were confirmed as implemented. The re-audit added three
deliverables that the plan implied but had no artifact to evidence:

1. source reconciliation against the Phase 9 input (rows, keys, target, split,
   quantity total);
2. explicit leakage verification (`lag_1` equals the previous observed
   quantity, the first observation of each series has no history, and the
   rolling mean excludes the current observation);
3. a per-feature completeness artifact
   (`feature_engineering_feature_summary.csv`).

The record-based lag/rolling semantics and the Phase 9 split are unchanged.
