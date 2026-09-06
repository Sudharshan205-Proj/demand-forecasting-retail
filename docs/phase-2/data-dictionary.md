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
| `date` | Price-change date | Time variable | Source documented; local verification required |
| `item_id` | Product identifier | Product key | Source documented; local verification required |
| `price` | New item price | Pricing variable | Source documented; local verification required |
| `code` | Price-change code | Price-change metadata | Source documented; local verification required |
| `store_id` | Store number | Store key | Source documented; local verification required |

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

Status:

NOT VERIFIED FOR FINAL MODELING

## Final Dictionary Status

PARTIALLY COMPLETE

The remaining fields and exact data types must be populated from the actual downloaded files.