# Dataset Inventory

## Purpose

This document records the actual files obtained for the project and their verified characteristics.

## Source

Kaggle — Retail Sales Forecasting Data

https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data

## Expected Files

| File | Expected Purpose | Exists Locally | Rows (Parsed) | Columns | Status |
|---|---:|---:|---:|---|
| `sales.csv` | Physical/store sales | YES | 7,432,685 | 6 | VERIFIED |
| `online.csv` | Online sales | YES | 1,123,412 | 6 | VERIFIED |
| `markdowns.csv` | Markdown sales | YES | 8,979 | 6 | VERIFIED |
| `price_history.csv` | Price changes | YES | 698,626 | 5 | VERIFIED |
| `stores.csv` | Store lookup | YES | 4 | 5 | VERIFIED |
| `catalog.csv` | Product catalog | YES | 192,239 | 8 | VERIFIED |
| `discounts_history.csv` | Promotion/discount activity | YES | 3,746,744 | 8 | VERIFIED |
| `actual_matrix.csv` | Product/store coverage matrix | YES | 35,202 | 3 | VERIFIED |

Note: `catalog.csv` contains 219,810 physical data lines; 27,571 lines contain unquoted commas inside text fields and are skipped by the parser because those attributes would otherwise be misaligned. The parsed row count above reflects the clean lines.

## Dataset-Level Characteristics

| Characteristic | Value | Status |
|---|---|---|
| Stores | 4 | VERIFIED |
| Historical period (sales) | 2022-08-28 to 2024-09-26 (≈25 months) | VERIFIED |
| Time granularity | Daily | VERIFIED |
| Product identifier | `item_id` | VERIFIED |
| Store identifier | `store_id` | VERIFIED |
| Candidate demand target | `quantity` | VERIFIED |
| Pricing information | Yes | VERIFIED |
| Markdown information | Yes | VERIFIED |
| Promotion/discount information | Yes (`discounts_history.csv`) | VERIFIED |
| Explicit holiday data | Not established | Requires inspection |
| Holdout period | One month according to source | NOT IDENTIFIED IN RAW FILES |

## Verified File Statistics

The values below were produced by the Phase 2 inspection script during the Phase 17 re-audit.

### `sales.csv`

- Rows: 7,432,685
- Columns: 6 (date, item_id, quantity, price_base, sum_total, store_id)
- Date minimum: 2022-08-28
- Date maximum: 2024-09-26
- Missing values: 0
- Duplicate rows: 0
- Unique products: 28,182
- Unique stores: 4
- Store coverage: stores 1-3 span the full range; store 4 first appears on
  2023-12-13 (established in the Phase 8 re-audit), which explains the monthly
  level shift between 2023-11 and 2023-12 as a coverage change

### `online.csv`

- Rows: 1,123,412
- Columns: 6 (date, item_id, quantity, price_base, sum_total, store_id)
- Date minimum: 2022-08-28
- Date maximum: 2024-09-26
- Missing values: 0
- Duplicate rows: 0
- Unique products: 18,405
- Unique stores: 2

### `markdowns.csv`

- Rows: 8,979
- Columns: 6 (date, item_id, normal_price, price, quantity, store_id)
- Date minimum: 2022-08-28
- Date maximum: 2024-09-26
- Missing values: 0
- Duplicate rows: 268
- Unique products: 313
- Unique stores: 3
- Records with a zero `normal_price`: 2 (the derived markdown discount is
  undefined for these records)

### `price_history.csv`

- Rows: 698,626
- Columns: 5 (date, item_id, price, code, store_id)
- Date minimum: 2022-08-28
- Date maximum: 2024-09-26
- Missing values: 0
- Duplicate rows: 18,641
- Unique products: 37,624
- Unique stores: 4

### `stores.csv`

- Rows: 4
- Columns: 5 (store_id, division, format, city, area)
- Duplicate rows: 0
- Unique stores: 4

### `catalog.csv`

- Rows (parsed): 192,239
- Columns: 8 (item_id, dept_name, class_name, subclass_name, item_type, weight_volume, weight_netto, fatness)
- Missing values (largest): fatness 185,408; item_type 155,271; weight_netto 150,033; weight_volume 120,805
- Duplicate rows: 0
- Unique products: 192,239

### `discounts_history.csv`

- Rows: 3,746,744
- Columns: 8 (date, item_id, sale_price_before_promo, sale_price_time_promo, promo_type_code, doc_id, number_disc_day, store_id)
- Date minimum: 2022-08-28
- Date maximum: 2045-12-31 (contains future-dated records; see Initial Data Assessment)
- Missing values: promo_type_code 317,846
- Duplicate rows: 0
- Unique products: 16,081
- Unique stores: 4
- Records with a zero `sale_price_before_promo`: 21,419, of which 28 also have
  a zero promotional price (the derived discount rate is undefined for all
  21,419)

### `actual_matrix.csv`

- Rows: 35,202
- Columns: 3 (item_id, date, store_id)
- Date minimum: 2019-10-17
- Date maximum: 2024-09-26
- Missing values: 0
- Duplicate rows: 0
- Unique products: 15,398
- Unique stores: 4

## Data Relationships

The expected relationship is:

`store_id + item_id + date`

Verified during the Phase 17 audit: the relationship holds at the Phase 5
cleaned-sales key normalisation and at the Phase 6 canonical-grain check, where
the integrated dataset contains 7,431,026 rows with 7,431,026 unique
`date + item_id + store_id` keys and 0 duplicates.

## Holdout

The source describes a one-month holdout sample intended for the internal Kaggle leaderboard. It is expected to be held out by Kaggle, so it is not present in the public training files.

Status: NOT IDENTIFIED in the local raw files.

## Structural Characteristics

- Every raw CSV leads with an unnamed index column (`Unnamed: 0`), a file-format artifact excluded from later processing.
- `catalog.csv` is UTF-8 with a byte-order mark.
- `catalog.csv` has 27,571 ragged lines (unquoted commas in text fields) reported and skipped by the inspection tool.
- Two derived rate columns divide by a raw price: `1 - sale_price_time_promo /
  sale_price_before_promo` and `1 - price / normal_price`. The denominators are
  zero for 21,419 discount records and 2 markdown records. The Phase 8 re-audit
  guarded both divisions in Phase 6, so the derived rate is left missing rather
  than infinite and the affected counts are recorded in the integration quality
  report (`undefined_promo_discount_rate_records`,
  `undefined_markdown_discount_records`).

## Raw Data Policy

Raw files are not committed to Git.

Only metadata, documentation, scripts, validation logic, and reproducible project code should be committed.