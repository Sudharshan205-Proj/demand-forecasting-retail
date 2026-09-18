# Phase 9 — Time-Series Preparation Plan

## Purpose

Prepare historical retail demand data for forecasting while preserving
temporal ordering and preventing information leakage.

## Status

COMPLETE — implemented, executed and verified during the Phase 17 re-audit.

## Forecasting target

The primary forecasting target is:

`quantity`

## Forecasting grain

The fundamental forecasting key is:

`date + item_id + store_id`

This preserves product-specific and store-specific demand.

## Data source

`data/processed/integrated_retail_data.csv`

## Preparation

The integrated dataset is aggregated to one observation per:

- date;
- item;
- store.

Duplicate keys are rejected.

Verified: the integrated source already carries a unique date-item-store grain
(established in Phase 6), so aggregation preserves all 7,431,026 source rows
(0 rows reduced) and total quantity 41,949,529.910 exactly. A within-chunk
duplicate scan is recorded and any non-zero count fails the workflow.

## Temporal gaps

The preparation process identifies missing dates within observed item-store
series.

Missing observations are not automatically interpreted as zero demand.

Verified: 55,122 of 58,022 item-store series contain at least one intermediate
gap, totalling 12,553,017 missing intermediate days (largest single gap 757
days). Gaps are reported, never filled.

## Chronological partitioning

The historical period is divided chronologically into:

- 70% training;
- 15% validation;
- 15% test.

The boundaries are calculated from the unique chronological dates.

Verified boundaries for the 761-date history:

| Partition | Dates | Date range | Share |
|---|---|---:|---:|
| Train | 532 | 2022-08-28 to 2024-02-10 | 69.9% |
| Validation | 114 | 2024-02-11 to 2024-06-03 | 15.0% |
| Test | 115 | 2024-06-04 to 2024-09-26 | 15.1% |

## Leakage prevention

No future observations may appear in an earlier partition.

Random shuffling is prohibited for the forecasting dataset.

Verified by contiguous date partitions and an explicit
non-overlapping-partition quality check; no shuffle operation exists anywhere
in the workflow.

## Outputs

- Prepared daily time-series dataset.
- Gap summary.
- Split summary.
- Quality report.
- Preparation findings.

## Phase boundary

No lag features, rolling features, forecasting models or model evaluation
are created in this phase.

## Phase 17 re-audit record

The plan was reviewed against the implementation and the re-executed
artifacts. The plan's requirements were confirmed as implemented. The re-audit
clarified two points without changing scope:

1. The integrated source is already at the target grain, so the aggregation is
   a type-conversion and chronological-ordering pass rather than a
   row-reducing step.
2. The gap magnitudes are now recorded precisely in the quality report and
   findings rather than left implicit.
