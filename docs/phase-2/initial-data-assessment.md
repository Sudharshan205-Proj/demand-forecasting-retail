# Initial Data Assessment

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Assessment Rule

This document records the state of the raw dataset before cleaning.

No cleaning or transformation should be performed during this assessment.

## Dataset Files

Verified raw files:

- `sales.csv`
- `online.csv`
- `markdowns.csv`
- `price_history.csv`
- `stores.csv`
- `catalog.csv`
- `discounts_history.csv`
- `actual_matrix.csv`

## Dimensions

Verified via the inspection script (Phase 17 re-audit):

| File | Rows | Columns |
|---|---:|---:|
| `sales.csv` | 7,432,685 | 6 |
| `online.csv` | 1,123,412 | 6 |
| `markdowns.csv` | 8,979 | 6 |
| `price_history.csv` | 698,626 | 5 |
| `stores.csv` | 4 | 5 |
| `catalog.csv` | 192,239 (parsed of 219,810 physical) | 8 |
| `discounts_history.csv` | 3,746,744 | 8 |
| `actual_matrix.csv` | 35,202 | 3 |

## Data Types

Verified via the inspection script:

- `quantity`, `price_base`, `sum_total`, `normal_price`, `price`, `sale_price_*`, `weight_*`, `fatness` are numeric (`float64`/`int64`).
- `date` and `item_id` are string; `store_id` is integer.
- Catalog attributes are string; catalog weight/fatness fields are numeric with substantial missing values.

Status:

VERIFIED

## Missing Values

Verified via the inspection script:

- `sales.csv`, `online.csv`, `markdowns.csv`, `price_history.csv`, `stores.csv`, `actual_matrix.csv`: no missing values.
- `catalog.csv`: substantial missing values, e.g. fatness 185,408; item_type 155,271; weight_netto 150,033; weight_volume 120,805.
- `discounts_history.csv`: promo_type_code missing for 317,846 rows.

Status:

VERIFIED

Important:

Missing values are being measured only at this stage.

No missing-value treatment is performed in Phase 2.

## Duplicate Records

Verified via the inspection script:

- `markdowns.csv`: 268 duplicate rows.
- `price_history.csv`: 18,641 duplicate rows.
- All other files: 0 duplicate rows.

Status:

VERIFIED

Duplicates will be investigated and handled in the appropriate cleaning phase.

## Temporal Coverage

Verified date coverage:

| File | Date Minimum | Date Maximum |
|---|---|---|
| `sales.csv` | 2022-08-28 | 2024-09-26 |
| `online.csv` | 2022-08-28 | 2024-09-26 |
| `markdowns.csv` | 2022-08-28 | 2024-09-26 |
| `price_history.csv` | 2022-08-28 | 2024-09-26 |
| `discounts_history.csv` | 2022-08-28 | 2045-12-31 (future-dated rows) |
| `actual_matrix.csv` | 2019-10-17 | 2024-09-26 |

Status:

VERIFIED

## Chronological Ordering

The inspection determined that the time-based files are not sorted chronologically in the raw files.

The raw files were not modified.

Ordering will be handled during later processing.

## Target Candidate

Candidate demand variable:

`quantity`

Final target definition:

CONFIRMED IN LATER PHASES (daily store-level quantity, per the Phase 9 and Phase 11 records)

## Time-Series Granularity

Expected:

Daily

Actual:

VERIFIED — DAILY

## Forecasting Unit

Potential unit:

`store_id + item_id`

Status:

CONFIRMED IN LATER PHASES — the implemented forecasting unit is documented in the Phase 9 and Phase 11 records.

## Promotions / Markdowns

The dataset contains markdown information (`markdowns.csv`) and promotion/discount activity (`discounts_history.csv`).

These will initially be treated as markdown/promotion/pricing information.

No causal promotional effect will be assumed.

## Holidays

An explicit holiday variable has not been identified from the source description or the raw files.

Status:

NOT VERIFIED

The project will document the absence of an explicit holiday field as a dataset limitation rather than inventing a holiday feature.

## Holdout

The source describes a one-month holdout intended for the Kaggle leaderboard; it is not present in the public training files.

Status:

NOT IDENTIFIED IN RAW FILES

## Initial Quality Concerns

Potential issues identified from inspection:

- `sales.csv` contains 1,160 rows with negative quantities.
- `markdowns.csv` has 268 duplicate rows; `price_history.csv` has 18,641 duplicate rows.
- `discounts_history.csv` contains 233,374 rows dated after 2024-12-31 (future-dated promotional records, up to 2045-12-31).
- `catalog.csv` has 27,571 lines with unquoted commas within text fields and substantial missing attribute values.
- All raw files include a leading unnamed index column (`Unnamed: 0`), a file-format artifact.
- Time-based files are not chronologically sorted.
- Overlapping information across tables (sales/online/markdowns/discounts) requires integration care.

These are observations passed to later phases, not cleaning performed here.

## Phase 2 Assessment Status

COMPLETE

The assessment was completed during the Phase 17 re-audit after the local raw data was inspected.