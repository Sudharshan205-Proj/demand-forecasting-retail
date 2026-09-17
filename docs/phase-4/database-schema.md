# Phase 4 — SQLite Database Schema

## Purpose

This document describes the relational structure used for SQL analysis.

## Tables

### stores

| Column | Purpose |
|---|---|
| store_id | Store identifier |
| division | Store division |
| format | Store format |
| city | Store city |
| area | Store area |

### catalog

| Column | Purpose |
|---|---|
| item_id | Product identifier |
| dept_name | Department |
| class_name | Product class |
| subclass_name | Product subclass |
| item_type | Product type |
| weight_volume | Product volume/weight measure |
| weight_netto | Net weight |
| fatness | Product fatness attribute |

### sales

| Column | Purpose |
|---|---|
| date | Sales date |
| item_id | Product identifier |
| quantity | Recorded demand quantity |
| price_base | Base price |
| sum_total | Recorded sales value |
| store_id | Store identifier |

### markdowns

| Column | Purpose |
|---|---|
| date | Markdown date |
| item_id | Product identifier |
| normal_price | Normal price |
| price | Markdown price |
| quantity | Recorded markdown quantity |
| store_id | Store identifier |

### price_history

| Column | Purpose |
|---|---|
| date | Price date |
| item_id | Product identifier |
| price | Recorded price |
| code | Price-history code |
| store_id | Store identifier |

## Relationships

```text
stores
   │
   └──── store_id ──── sales
                         │
                         └──── item_id ──── catalog

stores
   │
   ├──── store_id ──── markdowns
   │
   └──── store_id ──── price_history
```
## Design principles

The database separates store information, product information, sales,
markdowns, and price history so that analytical queries can combine
attributes through relational joins.

The original CSV files are not modified.

## Phase 17 Re-Audit Record

The schema was re-verified during the Phase 17 audit. The regenerated
database contains the five documented tables (stores, catalog, sales,
markdowns, price_history) plus seven indexes, with foreign keys enabled after
loading. Row counts match the Phase 2 verified source files.

Two observations are recorded:

- The `stores.area` column is declared `TEXT`, while the source `stores.csv`
  `area` values are integers (109, 210, 1500, 1887). SQLite's dynamic typing
  stores them as text; downstream phases read `stores.csv` via pandas, so this
  does not affect later analysis.
- The `catalog` table contains 219,810 rows, including the 27,571 ragged lines
  described in Phase 2. Their trailing attribute columns (item_type,
  weight_*, fatness) are shifted on those rows, but `item_id` remains correct
  and usable as the join key.