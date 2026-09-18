# Phase 10 — Feature Engineering Checklist

## Objective

Create a leakage-safe feature matrix for retail demand forecasting using the Phase 9 time-series dataset.

## Data Grain

`date + item_id + store_id`

## Target

`quantity`

## Checklist

* [x] Use Phase 9 time-series data as the input.
* [x] Preserve the physical-sales demand target (`target_preserved_vs_input`).
* [x] Do not use online quantity as the forecasting target.
* [x] Create calendar features (7 features, all present).
* [x] Create lag 1.
* [x] Create lag 7.
* [x] Create lag 14.
* [x] Create lag 28.
* [x] Create shifted 7-period rolling mean.
* [x] Create shifted 7-period rolling standard deviation.
* [x] Create shifted 28-period rolling mean.
* [x] Create shifted 28-period rolling standard deviation.
* [x] Create series age.
* [x] Preserve chronological split labels (`split_preserved_vs_input`; rows and
      quantities match Phase 9).
* [x] Prevent target leakage (`lag_1_matches_previous_observation`,
      `rolling_excludes_current_target`, `first_observation_has_no_history`).
* [x] Validate uniqueness (`duplicate_date_item_store_keys`, verified 0).
* [x] Validate chronology.
* [x] Validate target preservation.
* [x] Validate feature schema (7 of 7 calendar, 9 of 9 historical).
* [x] Run automated tests (32 tests, all passing).
* [x] Generate quality reports (`feature_engineering_quality_report.csv`, 14
      checks; `feature_engineering_feature_summary.csv`, 16 features).
* [x] Document limitations caused by missing intermediate dates.
* [x] Update README (reviewed; already correct).
* [x] Update project state.
* [x] Update file-update register.
* [ ] Review Git changes.
* [ ] Commit Phase 10.
* [ ] Push Phase 10 branch.
* [ ] Verify Git state.

The Git items are not exercised by the Phase 17 audit workflow: this repository
is audited in place and the audit runs no Git commands, so no branch, commit or
push is created for the re-audit. The items are left unticked deliberately
rather than claimed.

## Phase 17 re-audit record

**Audit status: AUDITED.**

Every checklist item above was verified against the re-executed workflow. The
re-audit added source reconciliation, leakage verification and a per-feature
completeness artifact, replaced two constant presence checks, vectorized the
rolling statistics, formatted the quantity figure and made date parsing
explicitly ISO. The Git items remain intentionally unticked because the Phase 17
audit runs no Git commands.
