# Phase 10 — Feature Engineering Methodology

## 1. Feature Engineering Objective

Feature engineering transforms historical retail observations into predictors
that expose temporal structure to later forecasting models.

The transformation must preserve the forecasting problem and prevent information
from the future entering historical observations.

## 2. Processing Strategy

The Phase 9 dataset (7,431,026 rows) is read in full and transformed in memory.
Unlike Phase 9 and the later model phases, feature engineering requires
whole-series group-wise operations (lags, rolling windows and series age span
each item-store series end to end), so the dataset is processed as a single
frame rather than in chunks.

Measured execution: 365.6 seconds, 2,510.3 MB peak resident memory.

The historical demand and rolling features are computed with pandas' compiled
grouped-rolling implementation (`groupby(...).rolling(...)`) rather than a
Python-level `transform` lambda. The two produce identical values, and the
compiled path is roughly an order of magnitude faster on the full dataset.

## 3. Calendar Features

Calendar variables are derived directly from the observation date.

They represent recurring temporal structure:

* day of week
* day of month
* week of year
* month
* quarter
* year
* weekend indicator

These features do not depend on the demand target.

## 4. Demand Lags

Historical demand is represented using prior observations within each item-store
series.

The implemented lag variables are:

* lag 1
* lag 7
* lag 14
* lag 28

The current observation is never used to create its own lag.

## 5. Rolling Statistics

Rolling demand statistics summarize recent historical behavior.

The implementation creates:

* seven-observation rolling mean
* seven-observation rolling standard deviation
* twenty-eight-observation rolling mean
* twenty-eight-observation rolling standard deviation

The demand series is shifted by one observation before calculating these
statistics.

Consequently, the current day's quantity is excluded.

## 6. Series Age

`series_age_days` measures the number of days elapsed since the first observed
date of the item-store series.

This allows later models to distinguish newly observed series from established
series.

Because a series' first observed date is always at or before any of its later
observations, the feature uses only information available at or before each row.
It is not forward-looking.

## 7. Price and Promotion Information

Price and promotion fields are available in the integrated dataset.

They must only be incorporated when their temporal semantics are safe.

A value representing an event that becomes known only after the forecast origin
must not be used as a predictor for that forecast.

Phase 10 therefore prioritizes leakage-safe temporal demand and calendar
features. Price and promotion variables remain subject to temporal validation in
later modeling work.

## 8. Time-Series Gaps

Phase 9 identified substantial missing intermediate dates.

This affects interpretation of demand lags.

For the implementation:

`lag_7` means the seventh previous observed demand record, not necessarily the
observation exactly seven calendar days earlier.

The same interpretation applies to the other observation-based lag and rolling
windows.

This is a deliberate and documented limitation rather than an assumption hidden
in the implementation.

## 9. Chronological Splitting

The Phase 9 partitions are preserved:

* Train: 2022-08-28 to 2024-02-10
* Validation: 2024-02-11 to 2024-06-03
* Test: 2024-06-04 to 2024-09-26

No random splitting is performed.

The output split row counts (4,315,416 / 1,548,957 / 1,566,653) and quantities
(24,038,416.097 / 8,811,477.346 / 9,099,636.467) match Phase 9 exactly.

## 10. Leakage Prevention

The following rules apply:

1. Current `quantity` cannot appear in its own historical feature.
2. Future dates cannot contribute to earlier observations.
3. Test observations are not used for feature construction of earlier periods.
4. Random shuffling is prohibited for temporal modeling.
5. Split labels are preserved from Phase 9.

The first, second and fifth rules are asserted by the quality report
(`lag_1_matches_previous_observation`, `first_observation_has_no_history`,
`rolling_excludes_current_target`, `split_preserved_vs_input`).

## 11. Reconciliation and Completeness

The engineered frame is reconciled against the Phase 9 source: rows, keys,
target values, split labels and the quantity total are compared.

A per-feature completeness artifact
(`feature_engineering_feature_summary.csv`) records the non-null and missing
count and missing share of all 16 features, exposing the missing-value structure
at each series start.

## 12. Scope Boundary

Feature engineering ends before model training, hyperparameter tuning, model
comparison, and final evaluation.

Those activities are implemented by Phases 11 and 12, which consume this
matrix.
