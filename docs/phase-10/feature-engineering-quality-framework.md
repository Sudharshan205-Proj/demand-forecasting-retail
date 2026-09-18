# Phase 10 — Feature Engineering Quality Framework

## Quality Objectives

The feature-engineering pipeline must produce a reproducible, structurally valid, leakage-safe feature matrix.

## Validation Categories

### Schema

Verify:

* required source columns exist
* required engineered features exist
* target exists
* split exists

Evidenced by `calendar_features_present` (actual 7 of 7) and
`historical_features_present` (actual 9 of 9). A missing feature reduces the
reported count and fails the check.

### Key Integrity

Verify:

`date + item_id + store_id`

contains no duplicates.

Evidenced by `duplicate_date_item_store_keys` (verified 0).

### Chronology

Verify that each item-store series is ordered chronologically.

Evidenced by `chronological_within_item_store_series` (verified True).

### Target Integrity

Verify that feature engineering does not alter the physical demand target.

Evidenced by `target_preserved_vs_input` (verified True, compared row by row
against the Phase 9 source) and `target_quantity_missing` (verified 0).

### Feature Integrity

Verify the presence of:

* calendar features
* lag features
* rolling features
* series age

Evidenced by the two presence checks above and
`first_observation_has_no_history`.

### Leakage

Verify that:

* lag values come from prior observations
* rolling features exclude the current target
* future observations do not enter earlier records
* chronological split labels remain unchanged

Evidenced by `lag_1_matches_previous_observation`,
`rolling_excludes_current_target`, `first_observation_has_no_history` and
`split_preserved_vs_input`, all verified True.

### Reconciliation

Compare the quantity total before and after feature engineering.

Evidenced by `quantity_total_reconciled` (verified 41,949,529.910 on both
sides), `input_output_rows_match` (7,431,026) and `input_output_keys_match`.

### Reproducibility

The same input and implementation should produce the same feature values.

The transformation is deterministic; the re-executed output dataset is
byte-size-identical to the pre-audit artifact (887,995,450 bytes).

## Quality Status

A Phase 10 run is valid only when all mandatory quality checks pass.

`data/analysis/feature_engineering_quality_report.csv` records 14 checks, all
True:

| Check | Result |
|---|---|
| `duplicate_date_item_store_keys` | True (0) |
| `chronological_within_item_store_series` | True |
| `rows_positive` | True (7,431,026) |
| `target_quantity_missing` | True (0) |
| `input_output_rows_match` | True (7,431,026 = 7,431,026) |
| `input_output_keys_match` | True |
| `target_preserved_vs_input` | True |
| `split_preserved_vs_input` | True |
| `quantity_total_reconciled` | True (41,949,529.910) |
| `calendar_features_present` | True (7 of 7) |
| `historical_features_present` | True (9 of 9) |
| `first_observation_has_no_history` | True |
| `lag_1_matches_previous_observation` | True |
| `rolling_excludes_current_target` | True |

A separate `feature_engineering_feature_summary.csv` records the completeness
of all 16 features.

## Phase 17 re-audit record

**Audit status: AUDITED.**

The framework was written before the workflow existed. During the Phase 17
re-audit:

- `feature_engineering_quality_report.csv` was rebuilt and now evidences every
  requirement above (14 checks, all True);
- two checks that reported a hardcoded `actual=True` now report real counts;
- source reconciliation and leakage verification were implemented for the
  first time;
- the per-feature completeness artifact was added.
