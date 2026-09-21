# Phase 6 — Data Integration Results

## Input

| Metric | Result |
|---|---:|
| Clean sales rows | 7,431,026 |
| Stores rows | 4 |
| Catalog rows | 219,810 (219,810 unique item_ids) |
| Price history rows | 698,626 |
| Markdown rows | 8,979 |
| Discount rows | 3,746,744 |
| Online rows | 1,123,412 |
| Actual matrix rows | 35,202 |

## Output

| Metric | Result |
|---|---:|
| Integrated rows | 7,431,026 |
| Row-count difference | 0 |
| Duplicate canonical-grain rows | 0 |
| Unknown store rows | 0 |
| Unmatched catalog rows | 36,580 |
| Date coverage | 2022-08-28 to 2024-09-26 |
| Unique items | 28,180 |
| Unique stores | 4 |
| Total demand quantity | 41,949,529.91 |
| Total sales revenue | 5,659,219,309.90 |
| Integrated columns | 34 |
| Integrated file size | 1,283,859,491 bytes |

The integrated dataset is byte-identical on re-execution.

## Validation

- **Row preservation:** 7,431,026 integrated rows equals 7,431,026 cleaned sales
  rows.
- **Canonical-grain uniqueness:** 0 duplicate `date + item_id + store_id` keys,
  confirmed independently by streaming the 1.28 GB output file.
- **Referential integrity:** unknown store rows = 0; catalog references are
  reported rather than enforced.
- **Join cardinality:** every auxiliary join is validated as many-to-one, and a
  non-unique auxiliary key raises an error (regression-tested).
- **Online-channel separation:** online demand is carried in `online_quantity`,
  `online_sales_value` and `online_average_price`, and is never added to the
  physical `quantity` measure.
- **Raw-data preservation:** no raw file is modified.
- **Catalog-unmatched retained:** 36,580 sales rows (948 distinct items) have no
  catalog match and are retained with null product attributes.

## Discount-rate guard

The two derived rate columns guard their denominators, so the integrated dataset
contains no infinite rate. The undefined counts are reported explicitly in the
quality report:

| Metric | Result |
|---|---:|
| `undefined_markdown_discount_records` | 2 |
| `undefined_promo_discount_rate_records` | 21,419 |
| `promoted_rows_with_undefined_discount_rate` | 6,782 |

The counts reconcile: 6,760 rows that carry a discount record with no usable rate
plus 22 promoted rows with no discount record make 6,782 promoted rows with an
undefined rate.

## Chunked aggregation

Discounts and online sales are aggregated in fixed-size chunks. Both sources
carry a unique canonical key, and no key spans more than one chunk; comparing the
pipeline output with an exact sum/count reconstruction gives a maximum absolute
difference of 0.0 for every averaged field ([`integration-methodology.md`](integration-methodology.md) §11).

## Test results

Phase 6's test module holds **24 tests, all passing**; the full project suite
passes 532.

## Carried-forward characteristics

- 36,580 sales rows (948 distinct items) carry null catalog attributes. This is
  the data-coverage gap first reported by Phase 4 Query 17 and reported by
  Phase 5; it is retained rather than dropped.
- The Phase 5 revenue mismatches (1,041,252 rows) are carried into the integrated
  dataset unchanged.
- Same-day price-change ties in `price_history` are resolved by file order
  ([`integration-methodology.md`](integration-methodology.md) §4); the raw files
  are not chronologically sorted.
