# Phase 6 — Integration Methodology

## 1. Primary fact

The cleaned sales dataset is the integration anchor.

Each record represents daily sales for an item at a store.

## 2. Canonical integration grain

All integration operations use:

`date + item_id + store_id`

as the canonical key.

## 3. Dimension integration

### Stores

Store attributes are one row per store and are joined using:

`store_id`

The join is validated as many-to-one.

### Catalog

Product attributes are one row per item and are joined using:

`item_id`

A left join is used so sales records without catalog metadata remain available.

## 4. Event-data integration

Price history, markdowns, and discounts can contain multiple records for the same analytical key.

They are therefore aggregated before integration.

When several price-change events share the same date/item/store key, the
representative price and code are resolved by file order (``last``). The raw
source files are not chronologically sorted, so such a same-day tie is
file-order dependent. This is a tie-break inside a single key that already
contains the date; it is not a temporal-ordering or leakage issue.

Examples include:

* number of price changes
* markdown quantity
* markdown price
* promotion record count
* promotion discount rate

## 5. Online channel

Online sales are aggregated separately and attached as online-channel features.

They are not added to the primary physical-sales demand measure.

## 6. Actual matrix

Actual-matrix records are converted into an exact-key indicator.

A missing indicator does not automatically imply that the product was unavailable because the source only records represented matrix observations.

## 7. Join validation

Pandas merge validation is used to enforce expected cardinality.

The integration rejects a join when an auxiliary table violates its expected uniqueness.

## 8. Row preservation

The number of integrated records must equal the number of cleaned sales records.

Any difference is treated as a pipeline failure.

## 9. Temporal integrity

Phase 6 does not propagate future price information backwards through time.

Any future-looking feature construction belongs to chronological feature engineering and must be performed without temporal leakage.

## 10. Reproducibility

The integration is implemented in a deterministic Python script using project-relative paths and existing project dependencies.

## 11. Chunked aggregation correctness

Discounts and online sales are read in fixed-size chunks and aggregated before
integration. Where a chunk-level mean is combined across chunks, the result
would differ from the true mean if a single canonical key spanned more than one
chunk.

The Phase 17 re-audit measured this directly. Both sources carry a unique
canonical key — `discounts_history` has 3,746,744 rows and 3,746,744 distinct
keys, and `online` has 1,123,412 rows and 1,123,412 distinct keys — and no key
spans more than one chunk. Comparing the pipeline output with an exact
sum/count reconstruction gives a maximum absolute difference of 0.0 for every
averaged field. The chunked aggregation is therefore numerically exact for this
dataset; the accumulation is kept as-is and the reason is recorded rather than
changed.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
