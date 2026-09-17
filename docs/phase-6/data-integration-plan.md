# Phase 6 — Data Integration Plan

## Purpose

Phase 6 integrates the validated retail datasets into a single analytical dataset suitable for subsequent exploratory analysis, feature engineering, and demand forecasting.

The primary fact source is:

`data/processed/sales_clean.csv`

The integration preserves the sales fact at the canonical grain:

**date + item_id + store_id**

## Source datasets

| Dataset               | Role                          |
| --------------------- | ----------------------------- |
| sales_clean.csv       | Primary sales fact            |
| stores.csv            | Store attributes              |
| catalog.csv           | Product attributes            |
| price_history.csv     | Price-change events           |
| markdowns.csv         | Markdown activity             |
| discounts_history.csv | Promotion/discount activity   |
| online.csv            | Online-channel sales          |
| actual_matrix.csv     | Product/store matrix coverage |

## Integration strategy

The sales dataset is treated as the left/base dataset.

One-to-many auxiliary datasets are aggregated to the canonical grain before joining.

All joins are validated using many-to-one constraints where applicable.

## Why the canonical grain matters

The forecasting problem concerns demand by product and store over time.

The canonical key:

`date + item_id + store_id`

therefore provides a stable analytical unit.

The integration must not create additional rows for a single sales observation.

## Online sales

Online sales are retained as separate features.

Online quantity is not added to physical sales quantity because the two sources represent different sales channels.

This prevents double-counting and preserves the meaning of the primary demand target.

## Price history

Price history records price-change events.

Phase 6 records those events at the canonical grain rather than forward-filling prices into future dates.

Chronological price propagation will be handled during later feature engineering.

## Catalog matching

Catalog information is joined using a left join.

Sales without a catalog match are retained because missing product metadata does not make the underlying sales record invalid.

## Expected output

`data/processed/integrated_retail_data.csv`

`data/processed/integration_quality_report.csv`

## Quality requirements

The integration must satisfy:

1. Output row count equals cleaned-sales row count.
2. Canonical grain is unique.
3. No many-to-many join multiplication occurs.
4. Store references remain valid.
5. Missing catalog matches are reported rather than silently discarded.
6. Online sales remain separate from physical sales.
7. Raw data are never modified.
8. Generated processed data remain excluded from Git.

## Phase 17 Re-Audit Record

AUDITED — COMPLETE

All eight quality requirements were verified against a fresh full execution
(350 seconds):

1. Output row count equals cleaned-sales row count — 7,431,026.
2. Canonical grain is unique — 0 duplicates.
3. No many-to-many multiplication — every join validated many-to-one.
4. Store references remain valid — 0 unknown store rows.
5. Missing catalog matches reported, not discarded — 36,580 rows retained.
6. Online sales remain separate from physical sales.
7. Raw data unchanged.
8. Generated processed data remain excluded from Git.

No grain, join key, policy or output schema was changed by this audit. The
quality report gained six additional validation metrics (date coverage, unique
items/stores, total demand and revenue) that were previously held in a stale,
unreproducible JSON artifact; that file was removed. See
`integration-results.md`.
