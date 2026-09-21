# Dataset Inventory

## Purpose

This document records the files used by the project and their characteristics.

## Source

Kaggle — Retail Sales Forecasting Data

<https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data>

## Source files

| File | Purpose | Rows (parsed) | Columns |
|---|---|---:|---:|
| `sales.csv` | Physical/store sales | 7,432,685 | 6 |
| `online.csv` | Online sales | 1,123,412 | 6 |
| `markdowns.csv` | Markdown sales | 8,979 | 6 |
| `price_history.csv` | Price changes | 698,626 | 5 |
| `stores.csv` | Store lookup | 4 | 5 |
| `catalog.csv` | Product catalog | 219,810 | 8 |
| `discounts_history.csv` | Promotion/discount activity | 3,746,744 | 8 |
| `actual_matrix.csv` | Product/store coverage matrix | 35,202 | 3 |

Note: `catalog.csv` contains 219,810 physical data lines. On 27,571 of them an
unquoted comma inside a text field makes the line ragged, shifting the trailing
attribute columns (`item_type`, `weight_*`, `fatness`) on those rows. No rows are
skipped: the parser reads all 219,810 lines, and `item_id` remains correct and
usable as the join key.

## Dataset-level characteristics

| Characteristic | Value |
|---|---|
| Stores | 4 |
| Historical period (sales) | 2022-08-28 to 2024-09-26 — approximately 25 elapsed months (26 calendar months, because 2022-08 is partial) |
| Time granularity | Daily |
| Product identifier | `item_id` |
| Store identifier | `store_id` |
| Demand target | `quantity` |
| Pricing information | Yes |
| Markdown information | Yes |
| Promotion/discount information | Yes (`discounts_history.csv`) |
| Holiday data | No holiday field exists in `sales.csv` or any supporting file |
| Holdout period | One month described by the source; not present in the public raw files |

## File statistics

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
  2023-12-13, which explains the monthly level shift between 2023-11 and 2023-12
  as a coverage change rather than demand growth

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

- Rows: 219,810 (all physical data lines are read; 27,571 are ragged)
- Columns: 8 (item_id, dept_name, class_name, subclass_name, item_type, weight_volume, weight_netto, fatness)
- Missing values (largest): fatness 185,408; item_type 155,271; weight_netto 150,033; weight_volume 120,805
- Duplicate rows: 0
- Unique products: 219,810

### `discounts_history.csv`

- Rows: 3,746,744
- Columns: 8 (date, item_id, sale_price_before_promo, sale_price_time_promo, promo_type_code, doc_id, number_disc_day, store_id)
- Date minimum: 2022-08-28
- Date maximum: 2045-12-31 (contains future-dated records; see
  [`initial-data-assessment.md`](initial-data-assessment.md))
- Missing values: promo_type_code 317,846
- Duplicate rows: 0
- Unique products: 16,081
- Unique stores: 4
- Records with a zero `sale_price_before_promo`: 21,419, of which 28 also have a
  zero promotional price (the derived discount rate is undefined for all 21,419)

### `actual_matrix.csv`

- Rows: 35,202
- Columns: 3 (item_id, date, store_id)
- Date minimum: 2019-10-17
- Date maximum: 2024-09-26
- Missing values: 0
- Duplicate rows: 0
- Unique products: 15,398
- Unique stores: 4

## Derived datasets

| Dataset | Source | Grain | Rows | Dates |
|---|---|---|---:|---|
| `data/processed/time_series_daily.csv` | Phase 6 integrated dataset | `date + item_id + store_id` | 7,431,026 | 2022-08-28 to 2024-09-26 |
| `data/processed/feature_engineered_daily.csv` | Phase 9 time-series dataset | `date + item_id + store_id` | 7,431,026 | 2022-08-28 to 2024-09-26 |

The prepared time-series dataset carries `quantity` and the chronological
`split` label (`train` / `validation` / `test`). It contains observed records
only: the daily grain covers all 761 calendar dates, but 55,122 of 58,022
item-store series have intermediate date gaps and are not zero-filled. It is a
reproducible generated artifact and is excluded from Git.

### Phase 11 forecasting view

Phase 11 reads `data/processed/feature_engineered_daily.csv` (four columns) and
aggregates it to a daily store-level forecasting grain (`date + store_id`),
producing 2,571 observed store-days from the 7,431,026 item-store records. The
aggregate reconciles with the source on total quantity (41,949,529.910).
Densifying each store series onto a complete daily calendar adds exactly one
zero-demand store-day (store 3, 2022-10-16); every other store-day is an observed
record.

### Phase 12 feature view

Phase 12 rebuilds the same 16 feature families Phase 10 defines (four lags, four
rolling statistics, seven calendar features and `series_age_days`) on the
store-day series rather than aggregating the item-store matrix: summing item-level
lags is not a leakage-safe store-level lag, and the forecasting phases operate at
the store-day grain. The recomputed matrix feeds the `feature_gbm` candidate,
whose per-fold and validation forecasts are stored in
`data/analysis/model_evaluation_predictions.csv`.

### Phase 13 demand basis

Phase 13 reads the same four columns over the training partition and reduces
them to 1,655 observed store-days, then densifies each store onto a complete
daily calendar with the identical construction Phases 11–12 use, giving 1,656
store-days (532 / 532 / 532 / 60). Exactly one day is zero-filled — store 3,
2022-10-16 — matching Phase 11's measured densification, and total training
quantity is unchanged at 24,038,416.097 because the added day contributes zero.

The observed-versus-densified distinction is recorded because it moves store 3's
descriptive statistics: 531 to 532 days, mean 5,843.874970 to 5,832.890242,
minimum 173.898 to 0.000, standard deviation 1,599.419835 to 1,617.875022 and
coefficient of variation 0.273692 to 0.277371. Stores 1, 2 and 4 are unaffected.
The per-store measurement is written to
`data/analysis/inventory_densification_summary.csv`.

## Data relationships

The relationship is `store_id + item_id + date`. It holds at the Phase 5
cleaned-sales key normalisation and at the Phase 6 canonical-grain check, where
the integrated dataset contains 7,431,026 rows with 7,431,026 unique
`date + item_id + store_id` keys and 0 duplicates.

## Holdout

The source describes a one-month holdout sample intended for the internal Kaggle
leaderboard. It is held out by Kaggle, so it is not present in the public
training files.

## Structural characteristics

- Every raw CSV leads with an unnamed index column (`Unnamed: 0`), a file-format
  artifact excluded from later processing.
- `catalog.csv` is UTF-8 with a byte-order mark.
- `catalog.csv` has 27,571 ragged lines (unquoted commas in text fields); the
  inspection tool reports them and the parser retains every line, shifting only
  the trailing attribute columns.
- Two derived rate columns divide by a raw price:
  `1 - sale_price_time_promo / sale_price_before_promo` and
  `1 - price / normal_price`. The denominators are zero for 21,419 discount
  records and 2 markdown records. Phase 6 guards both divisions, so the derived
  rate is left missing rather than infinite, and the affected counts are recorded
  in the integration quality report (`undefined_promo_discount_rate_records`,
  `undefined_markdown_discount_records`).

## Raw data policy

Raw files are not committed to Git. Only metadata, documentation, scripts,
validation logic and reproducible project code are committed.
