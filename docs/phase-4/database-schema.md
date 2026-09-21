# Phase 4 — SQLite Database Schema

## Purpose

This document describes the relational structure used for the SQL analysis. It
is defined in `sql/schema.sql` and loaded by
`scripts/create_sqlite_database.py`.

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

## Keys and indexes

`stores.store_id` and `catalog.item_id` are primary keys. The item and store
foreign keys are declared on `sales`, `markdowns` and `price_history`, and seven
indexes support the analysis:

| Index | Table (columns) |
|---|---|
| `idx_sales_date` | `sales (date)` |
| `idx_sales_item` | `sales (item_id)` |
| `idx_sales_store` | `sales (store_id)` |
| `idx_sales_store_date` | `sales (store_id, date)` |
| `idx_markdowns_item` | `markdowns (item_id)` |
| `idx_markdowns_store_date` | `markdowns (store_id, date)` |
| `idx_price_history_item_store_date` | `price_history (item_id, store_id, date)` |

The bulk load runs with `PRAGMA foreign_keys = OFF` and re-enables it at the end
of the build, with `PRAGMA journal_mode = WAL` and `PRAGMA synchronous = NORMAL`.

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

Store references are fully satisfied (unknown-store rows = 0). Catalog
references are informational rather than enforced: `PRAGMA foreign_key_check`
reports **42,426** unsatisfied catalog references — 36,585 in `sales` (948
distinct items), 5,690 in `price_history` (1,174 distinct items) and 151 in
`markdowns` (3 distinct items). The analyses retain those rows through left
joins; the counts are recorded in
[`sql-results.md`](sql-results.md).

## Design principles

The database separates store information, product information, sales, markdowns
and price history so that analytical queries combine attributes through
relational joins. The original CSV files are not modified.
