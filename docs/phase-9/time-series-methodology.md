# Phase 9 — Time-Series Preparation Methodology

## Source

The integrated retail dataset from Phase 6 is the source:

`data/processed/integrated_retail_data.csv` (approximately 1.28 GB).

## Processing strategy

The source is read once, in chunks of 250,000 rows. Inside the same pass the
workflow accumulates the source row count, source quantity, source date range
and a within-chunk duplicate-key count, re-aggregates each chunk to the
forecasting grain and appends the reduced chunk. The source is therefore never
loaded as a whole and is never read a second time. The prepared frame
(7,431,026 rows) is retained only to write the output dataset.

Measured execution: 231.6 seconds, 1,405.5 MB peak resident memory.

## Aggregation

Sales records are aggregated to:

`date + item_id + store_id`

with:

`quantity = sum(quantity)`

The integrated source already carries a unique date-item-store grain, so the
aggregation preserves all 7,431,026 rows and total quantity 41,949,529.910
exactly. The workflow records the row reduction
(`source_rows - prepared_rows`, measured 0), which would expose any cross-chunk
merge of repeated keys.

## Chronology

Dates are explicitly parsed as datetime values.

The final grain is sorted by item, store and date with a stable sort, so each
item-store series is chronologically ordered.

## Duplicate handling

The date-item-store key is unique by construction after aggregation. A
within-chunk duplicate scan is recorded (`within_chunk_duplicate_keys`,
measured 0). Because chunks are read sequentially, a duplicate key split across
a chunk boundary would not be detected by that scan — the same chunk-local
limitation documented in Phase 5. It cannot change the result: the final
groupby merges any repeated key and the recorded row reduction exposes the
merge. A non-zero duplicate count stops the workflow.

## Temporal gaps

The difference between consecutive observed dates is calculated within each
item-store series.

A gap greater than one day indicates one or more missing intermediate calendar
dates, counted as `difference - 1`.

Measured: 58,022 item-store series, of which 55,122 contain at least one gap,
totalling 12,553,017 missing intermediate days; the largest single gap is 757
days and the largest per-series missing-day total is 756.

The workflow reports these gaps instead of silently filling them. Missing
observations are never converted to zero demand.

## Train/validation/test split

The complete observed date range is ordered chronologically.

The first approximately 70% of unique dates forms training data, the next
approximately 15% forms validation data and the final approximately 15% forms
test data. The boundary indices are `floor(n * 0.70) - 1` and
`floor(n * 0.85) - 1`, clamped so that each of the three partitions holds at
least one date. The clamping preserves the documented three-date minimum.

Measured boundaries for the 761-date history: train ends 2024-02-10 (532
dates), validation ends 2024-06-03 (114 dates), and test runs from 2024-06-04
to 2024-09-26 (115 dates).

## Leakage control

No random sampling is performed.

Partitions are contiguous date ranges, so no future date can be assigned to
training or validation when it belongs to a later chronological partition. The
quality report asserts that all three partitions are present, that they are
ordered and non-overlapping, and that their rows and quantities reconcile with
the prepared frame.

## Online channel

Online demand remains separate from physical-store demand.

It is not added to the physical demand target. The integrated source used in
this phase is the physical-sales grain.

## Forecasting boundary

This phase prepares the temporal dataset only.

Feature engineering and model development are subsequent stages.
