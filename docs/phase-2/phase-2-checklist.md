# Phase 2 — Data Acquisition & Data Understanding

## Purpose

Phase 2 acquires the retail dataset, characterises it and records what it
contains and what it lacks, before any cleaning or modelling.

## What the phase delivered

| Area | Delivered |
|---|---|
| Acquisition | The eight raw CSV files under `data/raw/` (≈824 MB, Git-excluded), with source URL, acquisition date, version and license recorded ([`data-acquisition.md`](data-acquisition.md)) |
| Inventory | File dimensions, columns and dataset-level characteristics ([`dataset-inventory.md`](dataset-inventory.md)) |
| Source assessment | ROCCC assessment and requirement-by-requirement relevance ([`data-source-assessment.md`](data-source-assessment.md)) |
| Data dictionary | A field-level dictionary for all eight files ([`data-dictionary.md`](data-dictionary.md)) |
| Initial assessment | Missing values, duplicates, temporal coverage, ordering, granularity, target and quality observations ([`initial-data-assessment.md`](initial-data-assessment.md)) |
| Ethics and privacy | Privacy assessment, ownership, licensing, responsible use and bias ([`data-ethics-and-privacy.md`](data-ethics-and-privacy.md)) |
| Inspection script | `scripts/inspect_raw_data.py` with its test module (`tests/test_inspect_raw_data.py`, 6 tests) |

## Key findings

| Finding | Value |
|---|---|
| Stores | 4 |
| Sales rows | 7,432,685 |
| Coverage | 2022-08-28 → 2024-09-26 (daily) |
| Demand target | `quantity` |
| Canonical grain | `date + item_id + store_id` |
| Duplicates | 268 in `markdowns.csv`, 18,641 in `price_history.csv`; none elsewhere |
| Missing values | `catalog.csv` attribute fields; `promo_type_code` in 317,846 discount rows |
| Holiday field | None — recorded as a dataset limitation |
| Holdout | Described by the source; not present in the public files |
| Structural notes | Leading unnamed index column; `catalog.csv` BOM and 27,571 ragged lines; 233,374 future-dated discount records |

## Course coverage

Phase 2 carries the **Prepare** stage: data sources, structures, types,
credibility, relevance, ROCCC, metadata, ethics, privacy and security.

## Related documents

- [`../phase-0/data-strategy.md`](../phase-0/data-strategy.md) — the data strategy
- [`../project-status.md`](../project-status.md) — dataset facts in context
