# Data Dictionary

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Source

Kaggle — Retail Sales Forecasting Data

<https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data>

## Rule

The dictionary distinguishes fields documented by the source from fields that
were inferred or remain unresolved. No field is assigned a business meaning that
the source documentation or data inspection does not support.

## `sales.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `date` | Sales date | Time variable | Confirmed |
| `item_id` | Unique product identifier | Time-series grouping variable | Confirmed |
| `quantity` | Total quantity sold per day | Demand target | Confirmed |
| `price_base` | Average sales price per day | Explanatory variable | Confirmed |
| `sum_total` | Total daily sales amount | Revenue/value measure | Confirmed |
| `store_id` | Store number | Time-series grouping variable | Confirmed |

## `online.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `date` | Sales date | Time variable | Confirmed |
| `item_id` | Unique product identifier | Time-series grouping variable | Confirmed |
| `quantity` | Total quantity sold per day online | Online-demand measure | Confirmed |
| `price_base` | Average sales price per day | Explanatory variable | Confirmed |
| `sum_total` | Total daily sales amount | Revenue/value measure | Confirmed |
| `store_id` | Store number | Grouping variable | Confirmed |

## `markdowns.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `date` | Markdown date | Time variable | Confirmed |
| `item_id` | Product identifier | Product key | Confirmed |
| `normal_price` | Regular price | Pricing variable | Confirmed |
| `price` | Markdown price | Pricing/promotional variable | Confirmed |
| `quantity` | Quantity sold at markdown | Markdown-demand measure | Confirmed |
| `store_id` | Store number | Store key | Confirmed |

## `price_history.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `date` | Price-change date | Time variable | Confirmed |
| `item_id` | Product identifier | Product key | Confirmed |
| `price` | New item price | Pricing variable | Confirmed |
| `code` | Price-change code | Price-change metadata | Confirmed |
| `store_id` | Store number | Store key | Confirmed |

## `stores.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `store_id` | Store number | Store key | Confirmed |
| `division` | Store division | Store attribute | Confirmed |
| `format` | Store format | Store attribute | Confirmed |
| `city` | Store city | Store attribute | Confirmed |
| `area` | Store area | Store attribute | Confirmed |

## `catalog.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `item_id` | Product identifier | Product key | Confirmed |
| `dept_name` | Department name | Product attribute | Confirmed |
| `class_name` | Class name | Product attribute | Confirmed |
| `subclass_name` | Subclass name | Product attribute | Confirmed |
| `item_type` | Item type | Product attribute | Confirmed (large proportion missing) |
| `weight_volume` | Weight/volume | Product attribute | Confirmed (large proportion missing) |
| `weight_netto` | Net weight | Product attribute | Confirmed (large proportion missing) |
| `fatness` | Fatness | Product attribute | Confirmed (large proportion missing) |

## `discounts_history.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `date` | Discount date | Time variable | Confirmed |
| `item_id` | Product identifier | Product key | Confirmed |
| `sale_price_before_promo` | Price before promotion | Pricing variable | Confirmed |
| `sale_price_time_promo` | Price during promotion | Promotional variable | Confirmed |
| `promo_type_code` | Promotion type code | Promotional variable | Confirmed (some missing) |
| `doc_id` | Promotion document identifier | Promotional metadata | Confirmed |
| `number_disc_day` | Number of discount days | Promotional variable | Confirmed |
| `store_id` | Store number | Store key | Confirmed |

## `actual_matrix.csv`

| Column | Description | Role | Status |
|---|---|---|---|
| `item_id` | Product identifier | Product key | Confirmed |
| `date` | Date | Time variable | Confirmed |
| `store_id` | Store number | Store key | Confirmed |

## Structural file characteristics

- Every raw CSV contains a leading unnamed index column exported as
  `Unnamed: 0`. This is a file-format artifact, excluded from all later
  processing.
- `catalog.csv` is UTF-8 encoded with a byte-order mark.
- `catalog.csv` contains unquoted commas inside several text fields (27,571
  lines), which the CSV parser handles; the inspection script reports these as
  ragged lines, and the parser retains all 219,810 rows rather than failing or
  dropping them.

## Target

The demand forecasting target is `quantity` at the date × item × store grain,
aggregated to the store-day grain for the forecasting phases.

## Time-series keys

`date + item_id + store_id` is the canonical grain, unique across the integrated
dataset.

## Holiday field

No explicit holiday field exists in `sales.csv` or any supporting file.

## Promotion field

No generic `promotion` field exists. Markdown data is available in
`markdowns.csv`, and `discounts_history.csv` provides explicit promotion/discount
activity (promotional prices, promotion type codes and discount-day counts).

Promotion-related data is integrated and analyzed; it is available as an
explanatory variable but is not used as a forecasting model feature.
