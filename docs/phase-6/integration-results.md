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

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
