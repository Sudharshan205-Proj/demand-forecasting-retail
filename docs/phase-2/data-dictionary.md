# Data Dictionary

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Source

Kaggle — Retail Sales Forecasting Data

https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data

## Important Rule

The dictionary distinguishes between:

1. Fields documented by the source.
2. Fields verified from the actual downloaded files.
3. Fields whose meaning still requires investigation.

No field should be assigned a business meaning that has not been supported by the source documentation or data inspection.

## `sales.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `date` | Sales date | Time variable | Source documented; local verification required |
| `item_id` | Unique product identifier | Time-series grouping variable | Source documented; local verification required |
| `quantity` | Total quantity sold per day | Candidate demand target | Source documented; local verification required |
| `price_base` | Average sales price per day | Explanatory variable | Source documented; local verification required |
| `sum_total` | Total daily sales amount | Revenue/value measure | Source documented; local verification required |
| `store_id` | Store number | Time-series grouping variable | Source documented; local verification required |

## `online.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `date` | Sales date | Time variable | Source documented; local verification required |
| `item_id` | Unique product identifier | Time-series grouping variable | Source documented; local verification required |
| `quantity` | Total quantity sold per day online | Candidate online-demand target | Source documented; local verification required |
| `price_base` | Average sales price per day | Explanatory variable | Source documented; local verification required |
| `sum_total` | Total daily sales amount | Revenue/value measure | Source documented; local verification required |
| `store_id` | Store number | Grouping variable | Source documented; local verification required |

## `markdowns.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `date` | Markdown date | Time variable | Source documented; local verification required |
| `item_id` | Product identifier | Product key | Source documented; local verification required |
| `normal_price` | Regular price | Pricing variable | Source documented; local verification required |
| `price` | Markdown price | Pricing/promotional variable | Source documented; local verification required |
| `quantity` | Quantity sold at markdown | Markdown-demand measure | Source documented; local verification required |
| `store_id` | Store number | Store key | Source documented; local verification required |

## `price_history.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `date` | Price-change date | Time variable | VERIFIED |
| `item_id` | Product identifier | Product key | VERIFIED |
| `price` | New item price | Pricing variable | VERIFIED |
| `code` | Price-change code | Price-change metadata | VERIFIED |
| `store_id` | Store number | Store key | VERIFIED |

## `stores.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `store_id` | Store number | Store key | VERIFIED |
| `division` | Store division | Store attribute | VERIFIED |
| `format` | Store format | Store attribute | VERIFIED |
| `city` | Store city | Geographic attribute | VERIFIED |
| `area` | Store area | Store attribute | VERIFIED |

## `catalog.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `item_id` | Product identifier | Product key | VERIFIED |
| `dept_name` | Department name | Product attribute | VERIFIED |
| `class_name` | Class name | Product attribute | VERIFIED |
| `subclass_name` | Subclass name | Product attribute | VERIFIED |
| `item_type` | Item type | Product attribute | VERIFIED (large proportion missing) |
| `weight_volume` | Weight/volume | Product attribute | VERIFIED (large proportion missing) |
| `weight_netto` | Net weight | Product attribute | VERIFIED (large proportion missing) |
| `fatness` | Fatness | Product attribute | VERIFIED (large proportion missing) |

## `discounts_history.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `date` | Discount date | Time variable | VERIFIED |
| `item_id` | Product identifier | Product key | VERIFIED |
| `sale_price_before_promo` | Price before promotion | Pricing variable | VERIFIED |
| `sale_price_time_promo` | Price during promotion | Promotional variable | VERIFIED |
| `promo_type_code` | Promotion type code | Promotional variable | VERIFIED (some missing) |
| `doc_id` | Promotion document identifier | Promotional metadata | VERIFIED |
| `number_disc_day` | Number of discount days | Promotional variable | VERIFIED |
| `store_id` | Store number | Store key | VERIFIED |

## `actual_matrix.csv`

| Column | Source Description | Expected Role | Verification |
|---|---|---|---|
| `item_id` | Product identifier | Product key | VERIFIED |
| `date` | Date | Time variable | VERIFIED |
| `store_id` | Store number | Store key | VERIFIED |

## Structural File Characteristics

The following characteristics were verified during the Phase 17 re-audit and apply to the raw files:

- Every raw CSV contains a leading unnamed index column exported as `Unnamed: 0`. This is a file-format artifact and is excluded from all later processing.
- `catalog.csv` is UTF-8 encoded with a byte-order mark (BOM).
- `catalog.csv` contains unquoted commas inside several text fields (27,571 lines), which the CSV parser must handle; the inspection script reports these as skipped lines rather than failing.

## Candidate Target

The primary candidate for demand forecasting is:

`quantity`

The final forecasting target and forecasting unit must be confirmed after inspecting the data relationships.

## Candidate Time-Series Key

Potential key:

`store_id + item_id`

This is a working hypothesis and must be verified during Phase 2.

## Holiday Field

No explicit holiday field has been established from the source description.

Status:

NOT VERIFIED

## Promotion Field

No generic `promotion` field has been established.

Markdown data is available and may provide promotion/markdown-related information.

`discounts_history.csv` additionally provides explicit promotion/discount activity (promotional prices, promotion type codes and discount-day counts).

Status:

VERIFIED — PROMOTION-RELATED DATA IS AVAILABLE VIA `markdowns.csv` AND `discounts_history.csv`; NOT VERIFIED FOR FINAL MODELING

## Final Dictionary Status

COMPLETE

The field set, data types and structural characteristics were verified from the actual downloaded files during the Phase 17 re-audit.