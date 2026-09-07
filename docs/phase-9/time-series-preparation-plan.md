# Phase 9 — Time-Series Preparation Plan

## Purpose

Prepare historical retail demand data for forecasting while preserving
temporal ordering and preventing information leakage.

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

The integrated dataset will be aggregated to one observation per:

- date;
- item;
- store.

Duplicate keys will be rejected.

## Temporal gaps

The preparation process will identify missing dates within observed
item-store series.

Missing observations will not automatically be interpreted as zero demand.

## Chronological partitioning

The historical period will be divided chronologically into:

- 70% training;
- 15% validation;
- 15% test.

The boundaries are calculated from the unique chronological dates.

## Leakage prevention

No future observations may appear in an earlier partition.

Random shuffling is prohibited for the forecasting dataset.

## Outputs

- Prepared daily time-series dataset.
- Gap summary.
- Split summary.
- Quality report.
- Preparation findings.

## Phase boundary

No lag features, rolling features, forecasting models or model evaluation
are created in this phase.