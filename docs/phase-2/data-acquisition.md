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

NOT YET VERIFIED LOCALLY

The dataset has been selected as the preferred project dataset.

The actual local acquisition must be verified by inspecting the repository's `data/raw/` directory.

## Known Dataset Description

According to the Kaggle dataset description, the dataset contains sales information from four stores over approximately 25 months and is intended for demand forecasting.

The dataset documentation identifies the following files:

- `sales.csv`
- `online.csv`
- `markdowns.csv`
- `price_history.csv`

The dataset also includes a one-month holdout period for forecasting.

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

## Acquisition Date

NOT YET VERIFIED

## Dataset Version

NOT YET VERIFIED

## License

NOT YET VERIFIED

The license must be recorded from the dataset's current Kaggle metadata rather than guessed.

Phase 2 Verification

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