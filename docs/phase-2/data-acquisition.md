# Data Acquisition

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Selected dataset

Retail Sales Forecasting Data

## Source

Kaggle: <https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data>

Dataset owner: svizor

Dataset slug: retail-sales-forecasting-data

## Acquisition status

Acquired, inspected and used from the repository's `data/raw/` directory.

## Dataset description

The dataset contains sales information from four stores over approximately 25
months and is intended for demand forecasting.

It provides the following files:

- `sales.csv` — physical/store sales
- `online.csv` — online sales
- `markdowns.csv` — markdown sales
- `price_history.csv` — price changes
- `stores.csv` — store lookup
- `catalog.csv` — product catalog
- `discounts_history.csv` — promotion/discount activity
- `actual_matrix.csv` — product/store coverage matrix

The source also describes a one-month holdout period for the internal Kaggle
leaderboard; it is not present in the public training files.

## Acquisition details

| Property | Value |
|---|---|
| Acquisition date | 2026-09-06 to 2026-09-07 (local file modification timestamps) |
| Dataset version | 1 |
| License | CC BY-NC-SA 4.0 |
| Raw data location | `data/raw/` |
| Total size | ≈824 MB (not committed — data policy) |

## Acquisition method

1. Download the dataset from the Kaggle dataset page.
2. Extract the archive.
3. Place the raw CSV files under `data/raw/`.
4. Do not rename or modify the original raw files.
5. Run the raw-data inspection script.
6. Record the dataset characteristics in the Phase 2 documentation.

A direct Kaggle download can be attempted with:

```bash
curl -L "https://www.kaggle.com/api/v1/datasets/download/svizor/retail-sales-forecasting-data" -o data/raw/retail-sales-forecasting-data.zip
```

If the direct API download returns an authentication or authorization error, use
the Download button on the Kaggle dataset page. Kaggle credentials must never be
placed in the repository or in project documentation.

## Data acquisition rules

- Preserve the original raw files.
- Do not clean the raw files.
- Do not overwrite raw files with processed versions.
- Do not manually edit raw records.
- Do not commit raw datasets to Git.
- Record the acquisition date, source URL, dataset version and license exactly
  as presented by Kaggle.

## Verification

Each downloaded file was inspected for dimensions, columns, date coverage,
missing values, duplicate counts and file identity. The results are recorded in
[`dataset-inventory.md`](dataset-inventory.md) and
[`initial-data-assessment.md`](initial-data-assessment.md). The raw files remain
unchanged, and the inspection is reproducible with
`python scripts/inspect_raw_data.py`.
