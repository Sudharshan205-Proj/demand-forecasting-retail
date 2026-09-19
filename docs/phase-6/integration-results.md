# Phase 6 — Data Integration Results

## Status

VERIFIED

The Phase 6 integration pipeline was re-executed over the complete cleaned sales
dataset and all seven auxiliary sources during the Phase 17 re-audit, and its
outputs were inspected and independently validated.

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

## Validation

- Row preservation: PASS — 7,431,026 integrated rows equals 7,431,026 cleaned
  sales rows.
- Canonical-grain uniqueness: PASS — 0 duplicate `date + item_id + store_id`
  keys, re-verified independently by streaming the 1.28 GB output file.
- Referential integrity: PASS — unknown store rows = 0; catalog references are
  reported rather than enforced (see below).
- Join cardinality: PASS — every auxiliary join is validated as many-to-one;
  a non-unique auxiliary key raises an error (regression-tested).
- Online-channel separation: PASS — online demand is carried in
  `online_quantity`/`online_sales_value`/`online_average_price` and is never
  added to the physical `quantity` measure.
- Raw-data preservation: PASS — no raw file was modified (sizes and timestamps
  unchanged).
- Catalog-unmatched retained: PASS — 36,580 sales rows (948 distinct items)
  have no catalog match and are retained with null product attributes.

## Test results

22 passed (Phase 6 test module); 169 passed (full project suite). The 22 was the
count at the completion of this phase's audit; the Phase 8 re-audit added two
tests when the discount-rate zero-denominator guard was fixed at source, so the
module now holds **24 tests, all passing**.

## Known issues

- 36,580 sales rows (948 distinct items) carry null catalog attributes. This is
  the data-coverage gap first reported by Phase 4 Query 17 and reported by
  Phase 5; it is retained rather than dropped, and its magnitude is unchanged
  from the original phase run.
- The inherited Phase 5 revenue mismatches (1,041,252 rows) are carried into the
  integrated dataset unchanged.
- Same-day price-change ties in `price_history` are resolved by file order
  (documented in the integration methodology); the raw files are not
  chronologically sorted.
- Historical: an earlier implementation wrote
  `data/processed/integration_quality_report.json`. The current pipeline writes a
  single CSV quality report. The JSON was not referenced by any code or
  documentation, could not be regenerated, and predated the CSV by several
  hours. During the Phase 17 audit its validation metrics were folded into the
  CSV report and the stale JSON was removed.

## Phase status

COMPLETE — VERIFIED

The implementation, tests, validation, documentation and artifact checks have
all succeeded. Git state is managed by the project owner; verified 2026-09-19:
the branch `phase-6-data-integration` exists locally and on `origin`, its tip
`f8aee8b` is merged into `main`, and `main` matches `origin/main`.

## Phase 17 Re-Audit Record

AUDITED — COMPLETE

The pipeline was re-executed over the full dataset during the Phase 17 re-audit
(350 seconds) and produced a byte-identical integrated dataset (1,283,859,491
bytes, 7,431,026 rows). Verified findings:

1. The end-to-end run reproduces the original phase result exactly: row count,
   canonical-grain uniqueness (0 duplicates), unknown stores (0) and unmatched
   catalog rows (36,580) are unchanged.
2. The quality report was extended with the validation metrics that were
   previously only present in the orphan JSON: `date_min`, `date_max`,
   `unique_items`, `unique_stores`, `total_demand_quantity` and
   `total_sales_revenue`.
3. The chunked aggregation strategy was audited for the mean-of-means bias:
   `discounts_history` has 3,746,744 rows and 3,746,744 distinct canonical keys,
   and `online` has 1,123,412 rows and 1,123,412 distinct keys, with **0 keys
   spanning more than one 250,000-row chunk**. Comparing the pipeline's chunked
   output with an exact sum/count reconstruction gives a maximum absolute
   difference of 0.0 for every averaged field, so the chunking is numerically
   exact for this dataset.
4. Test coverage of the integration core was added: the previously untested
   `aggregate_*` functions and `build_integration` are now covered (13 → 22
   tests; 24 after the Phase 8 re-audit), replacing a pre-existing test whose
   assertion was vacuous.

Date coverage (2022-08-28 to 2024-09-26) and the unmatched catalog count
(36,580) reconcile with the Phase 5 cleaned-basis figures, and the raw-basis
36,585 count reconciles with Phase 4 Query 17.

### Resolved in the Phase 8 re-audit: non-finite discount values

The discount aggregation derives `discount_rate = 1 - sale_price_time_promo /
sale_price_before_promo` without guarding a zero denominator. 21,419 of the
3,746,744 raw discount records have `sale_price_before_promo == 0`, which
produces 21,391 infinite rates and leaves 6,760 infinite `promo_discount_rate`
values in the integrated dataset; a further 28 records have both prices equal
to zero, so `1 - 0/0` is NaN and 22 integrated rows carry a missing rate
despite having a discount record. Two `markdown_discount` values are also
infinite.

**Resolved.** The Phase 8 re-audit guarded both divisions at source: each
denominator is replaced by a missing value when it is zero, negative or
missing, so a derived rate is never infinite. The affected counts are now
reported explicitly instead of silently:

| Metric | Result |
|---|---:|
| `undefined_markdown_discount_records` | 2 |
| `undefined_promo_discount_rate_records` | 21,419 |
| `promoted_rows_with_undefined_discount_rate` | 6,782 |

The counts reconcile exactly: the 21,419 raw records with a zero base price
include the 28 records whose promotional price is also zero, so 6,760 rows
that previously carried an infinite rate plus 22 rows that already carried a
missing rate now make 6,782 promoted rows with an undefined rate.

The dataset was regenerated (244 seconds) and independently re-scanned: rows
read and written are unchanged at 7,431,026, the canonical grain is still
unique, all other quality metrics are unchanged, and both rate columns contain
**0 infinite values**. Phase 7's `infinite_promo_discount_rate` metric moved
from 6,760 to 0 and its `missing_promo_discount_rate` metric from 5,912,426 to
5,919,186, which is the only analytical change; every Phase 7 and Phase 8
statistic is otherwise unchanged (see the Phase 7 and Phase 8 re-audit
records).