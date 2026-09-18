# Phase 9 — Time-Series Quality Framework

## Schema validation

Required columns:

- date
- item_id
- quantity
- store_id

`validate_columns` rejects a source missing any required column, and the
aggregation rejects unparsable dates and non-numeric quantities. The quality
report records `quantity_numeric_and_complete` (verified True).

## Key validation

The following key must be unique:

`date + item_id + store_id`

Evidenced by `duplicate_date_item_store_keys` (verified 0) and
`within_chunk_duplicate_source_keys` (verified 0). The row-reduction metric
`prepared_rows_do_not_exceed_source_rows` (verified 7,431,026 ≤ 7,431,026)
exposes any cross-chunk merge that a chunk-local scan cannot see.

## Date validation

Dates must:

- parse successfully;
- be ordered within each item-store series;
- remain within the source temporal range.

Evidenced by `chronological_within_item_store_series` (verified True) and
`prepared_dates_within_source_range` (verified True).

## Demand validation

Quantity must be numeric.

The aggregate prepared quantity must reconcile with the integrated source.

Evidenced by `quantity_numeric_and_complete` (verified True) and
`source_quantity_equals_prepared_quantity` (verified 41,949,529.910 on both
sides).

## Gap validation

Temporal gaps are measured explicitly.

They are not silently converted to zero demand.

Evidenced by `maximum_gap_within_observed_span` (verified 757 ≤ 760 days) and
`missing_intermediate_days_within_span` (verified 756 ≤ 760 days). Every gap is
bounded by the observed series span, and the overall totals are recorded in
the summary and findings.

## Partition validation

The train, validation and test periods must:

- be chronological;
- have no overlapping dates;
- preserve temporal direction.

Evidenced by `all_partitions_present`,
`partitions_chronological_without_overlap`,
`split_quantity_reconciles_with_prepared` and
`split_rows_reconcile_with_prepared`, all verified True. The split row counts
(4,315,416 + 1,548,957 + 1,566,653) reconcile exactly with 7,431,026 prepared
rows.

## Leakage validation

No random row shuffling is permitted.

No future observations may influence earlier partitions.

Asserted structurally — the partitions are contiguous date ranges and the
workflow contains no shuffle operation — and verified by
`partitions_chronological_without_overlap`.

## Reproducibility

The workflow must:

- use deterministic processing;
- use fixed split proportions;
- document preprocessing decisions;
- use project-relative paths.

Proportions are fixed constants (0.70 / 0.85), the final sort is stable, the
processing is deterministic, and paths are project-relative.

## Source preservation

The integrated source dataset must not be modified.

Evidenced by `source_file_not_modified`, which compares the file size and
modification time before and after the run (verified True).

## Generated artifacts

Prepared data and analysis outputs are generated artifacts and remain excluded
from Git where the repository's ignore rules specify them.

## Verification summary

`data/analysis/time_series_quality_report.csv` records 15 checks, all True:

| Check | Result |
|---|---|
| `source_quantity_equals_prepared_quantity` | True (41,949,529.910) |
| `prepared_rows_do_not_exceed_source_rows` | True (7,431,026 ≤ 7,431,026) |
| `within_chunk_duplicate_source_keys` | True (0) |
| `duplicate_date_item_store_keys` | True (0) |
| `chronological_within_item_store_series` | True |
| `prepared_rows_positive` | True (7,431,026) |
| `quantity_numeric_and_complete` | True |
| `prepared_dates_within_source_range` | True |
| `all_partitions_present` | True |
| `partitions_chronological_without_overlap` | True |
| `split_quantity_reconciles_with_prepared` | True |
| `split_rows_reconcile_with_prepared` | True |
| `maximum_gap_within_observed_span` | True (757 ≤ 760) |
| `missing_intermediate_days_within_span` | True (756 ≤ 760) |
| `source_file_not_modified` | True |

## Phase 17 re-audit record

The framework was written before the workflow existed and no artifact
evidenced it. During the Phase 17 re-audit:

- `time_series_quality_report.csv` was rebuilt and now evidences every check
  listed above (15 metrics, all True);
- the two gap checks that could never fail (`>= 0`) were replaced with
  span-bounded checks;
- partition, date-range, leakage and source-preservation checks were added;
- the source is no longer re-read for reconciliation, closing the gap between
  the documented chunked strategy and the implementation.
