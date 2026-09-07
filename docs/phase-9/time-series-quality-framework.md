# Phase 9 — Time-Series Quality Framework

## Schema validation

Required columns:

- date
- item_id
- quantity
- store_id

## Key validation

The following key must be unique:

`date + item_id + store_id`

## Date validation

Dates must:

- parse successfully;
- be ordered within each item-store series;
- remain within the source temporal range.

## Demand validation

Quantity must be numeric.

The aggregate prepared quantity must reconcile with the integrated source.

## Gap validation

Temporal gaps are measured explicitly.

They are not silently converted to zero demand.

## Partition validation

The train, validation and test periods must:

- be chronological;
- have no overlapping dates;
- preserve temporal direction.

## Leakage validation

No random row shuffling is permitted.

No future observations may influence earlier partitions.

## Reproducibility

The workflow must:

- use deterministic processing;
- use fixed split proportions;
- document preprocessing decisions;
- use project-relative paths.

## Source preservation

The integrated source dataset must not be modified.

## Generated artifacts

Prepared data and analysis outputs are generated artifacts and should
remain excluded from Git where the repository's ignore rules specify them.