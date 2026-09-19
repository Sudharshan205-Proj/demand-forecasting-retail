# Phase 11 — Forecasting Models Checklist

## Objective

Develop and evaluate classical forecasting models using the Phase 10 feature-engineered retail demand data.

Status: COMPLETE — verified during the Phase 17 re-audit.

## Models

* [x] Naive baseline
* [x] Seasonal-naive baseline
* [x] ARIMA

## Data

* [x] Use physical retail quantity as the target.
* [x] Preserve chronological partitions.
* [x] Do not randomly shuffle temporal observations.
* [x] Do not use the test period for model selection.
* [x] Reconcile the store-day aggregate against the Phase 10 source (41,949,529.910 quantity).
* [x] Measure and record the store-day densification (1 zero-filled store-day).

## Evaluation

* [x] RMSE
* [x] MAPE
* [x] Document zero-demand handling for MAPE.
* [x] Record model configurations.
* [x] Record forecast horizons.
* [x] Record validation dates.

## Validation

* [x] Input schema validation
* [x] Forecast-length validation
* [x] Chronological validation
* [x] Metric validation
* [x] Model configuration validation
* [x] Automated tests (52 passing)

## Documentation

* [x] Forecasting plan
* [x] Methodology
* [x] Quality framework
* [x] Results
* [x] Course-content mapping
* [x] README
* [x] Project state
* [x] File-update register

## Git

* [x] Create Phase 11 branch (at implementation time).
* [x] Review changes.
* [x] Stage correct files.
* [x] Commit once at phase completion.
* [x] Push branch.
* [x] Verify clean working tree.

The Git items above are the original Phase 11 implementation record. The Phase 17 audit performs no Git operations, so they are retained as the phase record rather than re-asserted by the audit.

## Phase 17 Re-Audit Status

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
