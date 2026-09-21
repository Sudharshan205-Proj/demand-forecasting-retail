# Phase 6 — Integration Methodology

## 1. Primary fact

The cleaned sales dataset is the integration anchor. Each record represents
daily sales for an item at a store.

## 2. Canonical integration grain

All integration operations use `date + item_id + store_id` as the canonical key.

## 3. Dimension integration

### Stores

Store attributes are one row per store and are joined using `store_id`. The join
is validated as many-to-one.

### Catalog

Product attributes are one row per item and are joined using `item_id`. A left
join is used so sales records without catalog metadata remain available.

## 4. Event-data integration

Price history, markdowns and discounts can contain multiple records for the same
analytical key, so they are aggregated before integration. The aggregated
measures include number of price changes, markdown quantity, markdown price,
promotion record count and promotion discount rate.

When several price-change events share the same date/item/store key, the
representative price and code are resolved by file order. The raw source files
are not chronologically sorted, so such a same-day tie is file-order dependent.
This is a tie-break inside a single key that already contains the date; it is not
a temporal-ordering or leakage issue.

### Discount-rate guard

Two derived rate columns divide by a raw price:
`discount_rate = 1 - sale_price_time_promo / sale_price_before_promo` and
`markdown_discount = 1 - price / normal_price`. Each denominator is replaced by a
missing value when it is zero, negative or missing, so a derived rate is never
infinite. The affected counts are reported explicitly in the quality report:

| Metric | Result |
|---|---:|
| `undefined_markdown_discount_records` | 2 |
| `undefined_promo_discount_rate_records` | 21,419 |
| `promoted_rows_with_undefined_discount_rate` | 6,782 |

The counts reconcile exactly: the 21,419 raw records with a zero base price
include the 28 records whose promotional price is also zero, so 6,760 rows that
carry a discount record with no usable rate plus 22 promoted rows with no
discount record make 6,782 promoted rows with an undefined rate.

## 5. Online channel

Online sales are aggregated separately and attached as online-channel features.
They are not added to the primary physical-sales demand measure.

## 6. Actual matrix

Actual-matrix records are converted into an exact-key indicator. A missing
indicator does not imply that a product was unavailable, because the source only
records represented matrix observations.

## 7. Join validation

Pandas merge validation enforces the expected cardinality. The integration
rejects a join when an auxiliary table violates its expected uniqueness.

## 8. Row preservation

The number of integrated records equals the number of cleaned sales records; any
difference is treated as a pipeline failure.

## 9. Temporal integrity

Phase 6 does not propagate future price information backwards through time.
Future-looking feature construction belongs to chronological feature engineering,
which is performed without temporal leakage in Phase 10.

## 10. Reproducibility

The integration is a deterministic Python script using project-relative paths and
existing project dependencies. Re-execution over the same inputs produces a
byte-identical integrated dataset.

## 11. Chunked aggregation correctness

Discounts and online sales are read in fixed-size chunks and aggregated before
integration. Where a chunk-level mean is combined across chunks, the result would
differ from the true mean if a single canonical key spanned more than one chunk.

Both sources carry a unique canonical key — `discounts_history` has 3,746,744
rows and 3,746,744 distinct keys, and `online` has 1,123,412 rows and 1,123,412
distinct keys — and no key spans more than one chunk. Comparing the pipeline
output with an exact sum/count reconstruction gives a maximum absolute difference
of 0.0 for every averaged field, so the chunked aggregation is numerically exact
for this dataset.
