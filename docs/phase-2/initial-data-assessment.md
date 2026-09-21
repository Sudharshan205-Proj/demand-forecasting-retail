# Initial Data Assessment

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Assessment rule

This document records the state of the raw dataset before cleaning. No cleaning
or transformation is performed during this assessment.

## Dataset files

- `sales.csv`
- `online.csv`
- `markdowns.csv`
- `price_history.csv`
- `stores.csv`
- `catalog.csv`
- `discounts_history.csv`
- `actual_matrix.csv`

## Dimensions

Produced by the inspection script:

| File | Rows | Columns |
|---|---:|---:|
| `sales.csv` | 7,432,685 | 6 |
| `online.csv` | 1,123,412 | 6 |
| `markdowns.csv` | 8,979 | 6 |
| `price_history.csv` | 698,626 | 5 |
| `stores.csv` | 4 | 5 |
| `catalog.csv` | 219,810 (all physical lines read; 27,571 ragged) | 8 |
| `discounts_history.csv` | 3,746,744 | 8 |
| `actual_matrix.csv` | 35,202 | 3 |

## Data types

- `quantity`, `price_base`, `sum_total`, `normal_price`, `price`, `sale_price_*`, `weight_*`, `fatness` are numeric (`float64`/`int64`).
- `date` and `item_id` are string; `store_id` is integer.
- Catalog attributes are string; catalog weight/fatness fields are numeric with
  substantial missing values.

## Missing values

- `sales.csv`, `online.csv`, `markdowns.csv`, `price_history.csv`, `stores.csv`,
  `actual_matrix.csv`: no missing values.
- `catalog.csv`: substantial missing values, e.g. fatness 185,408; item_type
  155,271; weight_netto 150,033; weight_volume 120,805.
- `discounts_history.csv`: `promo_type_code` missing for 317,846 rows.

Missing values are measured here; their treatment belongs to Phase 5.

## Duplicate records

- `markdowns.csv`: 268 duplicate rows.
- `price_history.csv`: 18,641 duplicate rows.
- All other files: 0 duplicate rows.

Duplicates are investigated and handled in Phase 5.

## Temporal coverage

| File | Date minimum | Date maximum |
|---|---|---|
| `sales.csv` | 2022-08-28 | 2024-09-26 |
| `online.csv` | 2022-08-28 | 2024-09-26 |
| `markdowns.csv` | 2022-08-28 | 2024-09-26 |
| `price_history.csv` | 2022-08-28 | 2024-09-26 |
| `discounts_history.csv` | 2022-08-28 | 2045-12-31 (future-dated rows) |
| `actual_matrix.csv` | 2019-10-17 | 2024-09-26 |

## Chronological ordering

The time-based files are not sorted chronologically in the raw files. The raw
files are not modified; ordering is handled during later processing.

## Target

Candidate demand variable: `quantity`, confirmed as the forecasting target in
later phases (daily store-level quantity, per the Phase 9 and Phase 11 records).

## Time-series granularity

Daily.

## Forecasting unit

`store_id + item_id`, confirmed in the Phase 9 and Phase 11 records, with the
forecasting phases operating at the store-day grain.

## Promotions / markdowns

The dataset contains markdown information (`markdowns.csv`) and
promotion/discount activity (`discounts_history.csv`). These are treated as
markdown/promotion/pricing information; no causal promotional effect is assumed.

## Holidays

No explicit holiday variable exists in the source description or in any of the
eight raw files. The absence is documented as a dataset limitation rather than
filled with an invented holiday feature.

## Holdout

The source describes a one-month holdout intended for the Kaggle leaderboard; it
is not present in the public training files.

## Initial quality observations

Passed to later phases:

- `sales.csv` contains 1,160 rows with negative quantities.
- `markdowns.csv` has 268 duplicate rows; `price_history.csv` has 18,641
  duplicate rows.
- `discounts_history.csv` contains 233,374 rows dated after 2024-12-31
  (future-dated promotional records, up to 2045-12-31).
- `catalog.csv` has 27,571 lines with unquoted commas within text fields and
  substantial missing attribute values.
- All raw files include a leading unnamed index column (`Unnamed: 0`), a
  file-format artifact.
- Time-based files are not chronologically sorted.
- Overlapping information across tables (sales/online/markdowns/discounts)
  requires integration care.

## Assessment status

Complete. The assessment covers all eight raw files, and its results are used by
the cleaning, integration and analysis phases.
