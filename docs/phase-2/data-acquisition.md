# Data Acquisition

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Selected Dataset

Retail Sales Forecasting Data

## Source

Kaggle:

https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data

Dataset owner:

svizor

Dataset slug:

retail-sales-forecasting-data

## Acquisition Status

VERIFIED LOCALLY

The dataset has been acquired and inspected from the repository's `data/raw/` directory.

## Known Dataset Description

According to the Kaggle dataset description, the dataset contains sales information from four stores over approximately 25 months and is intended for demand forecasting.

The dataset documentation identifies the following files; the actual raw directory additionally contains the supporting reference files used by later phases:

- `sales.csv` — physical/store sales (verified)
- `online.csv` — online sales (verified)
- `markdowns.csv` — markdown sales (verified)
- `price_history.csv` — price changes (verified)
- `stores.csv` — store lookup (verified)
- `catalog.csv` — product catalog (verified)
- `discounts_history.csv` — promotion/discount activity (verified)
- `actual_matrix.csv` — product/store coverage matrix (verified)

The dataset also includes a one-month holdout period for forecasting.

## Acquisition Date

2026-09-06 to 2026-09-07 (local file modification timestamps for the downloaded raw files)

## Dataset Version

Version 1

## License

CC BY-NC-SA 4.0

## Expected Raw Data Location

All downloaded raw files must be placed under:

`data/raw/`

Raw files must not be committed to Git.

The repository `.gitignore` excludes raw data files from version control.

## Acquisition Method

Preferred method:

1. Download the dataset from the official Kaggle dataset page.
2. Extract the archive.
3. Place the raw CSV files under `data/raw/`.
4. Do not rename or modify the original raw files.
5. Run the raw-data inspection script.
6. Record the verified dataset characteristics in the Phase 2 documentation.

## Command-Line Acquisition

A direct Kaggle download can be attempted with:

```powershell
Invoke-WebRequest -Uri "https://www.kaggle.com/api/v1/datasets/download/svizor/retail-sales-forecasting-data" -OutFile "data/raw/retail-sales-forecasting-data.zip"
```

Extract it with:

```powershell
Expand-Archive -Path "data/raw/retail-sales-forecasting-data.zip" -DestinationPath "data/raw" 
```

If the direct API download returns an authentication or authorization error, use the Download button on the Kaggle dataset page instead. Do not place Kaggle credentials in the repository or in project documentation.

## Data Acquisition Rules

- Preserve the original raw files.
- Do not clean the raw files.
- Do not overwrite raw files with processed versions.
- Do not manually edit raw records.
- Do not commit raw datasets to Git.
- Record the acquisition date.
- Record the source URL.
- Record the dataset version if Kaggle provides one.
- Record the dataset license exactly as presented by Kaggle.
- Record any download or extraction issues.

## Phase 2 Verification

The acquisition is considered verified only after:

- Raw files exist.
- Expected files have been identified.
- The inspection script executes successfully.
- File dimensions are recorded.
- Columns are recorded.
- Date coverage is recorded.
- Missing values are recorded.
- Duplicate counts are recorded.
- Raw files remain unchanged.

## Phase 17 Re-Audit Record

During the Phase 17 re-audit, the raw directory was verified to contain eight CSV files (the four originally documented plus `stores.csv`, `catalog.csv`, `discounts_history.csv` and `actual_matrix.csv`). The inspection script was made robust to the dataset's actual structural characteristics (leading unnamed index column, UTF-8 BOM on `catalog.csv`, and unquoted commas inside catalog text fields) and re-executed successfully over the full dataset. Acquisition date, version availability and the license limitation are recorded above.