# Dataset Inventory

## Purpose

This document records the actual files obtained for the project and their verified characteristics.

## Source

Kaggle — Retail Sales Forecasting Data

https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data

## Expected Files

| File | Expected Purpose | Exists Locally | Rows | Columns | Status |
|---|---|---:|---:|---:|---|
| `sales.csv` | Physical/store sales | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | Pending inspection |
| `online.csv` | Online sales | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | Pending inspection |
| `markdowns.csv` | Markdown sales | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | Pending inspection |
| `price_history.csv` | Price changes | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | Pending inspection |

## Dataset-Level Characteristics

| Characteristic | Value | Status |
|---|---|---|
| Stores | 4 according to source | Source documented |
| Historical period | Approximately 25 months | Source documented |
| Time granularity | Expected daily | Local verification required |
| Product identifier | `item_id` | Source documented |
| Store identifier | `store_id` | Source documented |
| Candidate demand target | `quantity` | Source documented |
| Pricing information | Yes | Source documented |
| Markdown information | Yes | Source documented |
| Explicit holiday data | Not established | Requires inspection |
| Holdout period | 1 month according to source | Requires inspection |

## Verified File Statistics

These values must be populated from the local inspection script.

### `sales.csv`

- Rows: NOT YET VERIFIED
- Columns: NOT YET VERIFIED
- Date minimum: NOT YET VERIFIED
- Date maximum: NOT YET VERIFIED
- Missing values: NOT YET VERIFIED
- Duplicate rows: NOT YET VERIFIED
- Unique products: NOT YET VERIFIED
- Unique stores: NOT YET VERIFIED

### `online.csv`

- Rows: NOT YET VERIFIED
- Columns: NOT YET VERIFIED
- Date minimum: NOT YET VERIFIED
- Date maximum: NOT YET VERIFIED
- Missing values: NOT YET VERIFIED
- Duplicate rows: NOT YET VERIFIED
- Unique products: NOT YET VERIFIED
- Unique stores: NOT YET VERIFIED

### `markdowns.csv`

- Rows: NOT YET VERIFIED
- Columns: NOT YET VERIFIED
- Date minimum: NOT YET VERIFIED
- Date maximum: NOT YET VERIFIED
- Missing values: NOT YET VERIFIED
- Duplicate rows: NOT YET VERIFIED

### `price_history.csv`

- Rows: NOT YET VERIFIED
- Columns: NOT YET VERIFIED
- Date minimum: NOT YET VERIFIED
- Date maximum: NOT YET VERIFIED
- Missing values: NOT YET VERIFIED
- Duplicate rows: NOT YET VERIFIED

## Data Relationships

The expected relationship is:

`store_id + item_id + date`

This must be verified before integration.

## Holdout

The source describes a one-month holdout sample.

The exact holdout file and date range must be verified from the downloaded dataset.

## Raw Data Policy

Raw files are not committed to Git.

Only metadata, documentation, scripts, validation logic, and reproducible project code should be committed.