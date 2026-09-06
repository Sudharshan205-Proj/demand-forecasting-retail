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