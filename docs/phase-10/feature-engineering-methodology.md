# Phase 10 — Feature Engineering Methodology

## 1. Feature Engineering Objective

Feature engineering transforms historical retail observations into predictors that expose temporal structure to later forecasting models.

The transformation must preserve the forecasting problem and prevent information from the future entering historical observations.

## 2. Calendar Features

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

## 3. Demand Lags

Historical demand is represented using prior observations within each item-store series.

The implemented lag variables are:

* lag 1
* lag 7
* lag 14
* lag 28

The current observation is never used to create its own lag.

## 4. Rolling Statistics

Rolling demand statistics summarize recent historical behavior.

The implementation creates:

* seven-observation rolling mean
* seven-observation rolling standard deviation
* twenty-eight-observation rolling mean
* twenty-eight-observation rolling standard deviation

The demand series is shifted by one observation before calculating these statistics.

Consequently, the current day's quantity is excluded.

## 5. Series Age

`series_age_days` measures the number of days elapsed since the first observed date of the item-store series.

This allows later models to distinguish newly observed series from established series.

## 6. Price and Promotion Information

Price and promotion fields are available in the integrated dataset.

They must only be incorporated when their temporal semantics are safe.

A value representing an event that becomes known only after the forecast origin must not be used as a predictor for that forecast.

Therefore, Phase 10 prioritizes leakage-safe temporal demand and calendar features. Price and promotion variables remain subject to temporal validation in later modeling work.

## 7. Time-Series Gaps

Phase 9 identified substantial missing intermediate dates.

This affects interpretation of demand lags.

For the initial implementation:

`lag_7` means the seventh previous observed demand record, not necessarily the observation exactly seven calendar days earlier.

The same interpretation applies to the other observation-based lag and rolling windows.

This is a deliberate and documented limitation rather than an assumption hidden in the implementation.

## 8. Chronological Splitting

The Phase 9 partitions are preserved:

* Train: 2022-08-28 to 2024-02-10
* Validation: 2024-02-11 to 2024-06-03
* Test: 2024-06-04 to 2024-09-26

No random splitting is performed.

## 9. Leakage Prevention

The following rules apply:

1. Current `quantity` cannot appear in its own historical feature.
2. Future dates cannot contribute to earlier observations.
3. Test observations are not used for feature construction of earlier periods.
4. Random shuffling is prohibited for temporal modeling.
5. Split labels are preserved from Phase 9.

## 10. Scope Boundary

Feature engineering ends before model training, hyperparameter tuning, model comparison, and final evaluation.
