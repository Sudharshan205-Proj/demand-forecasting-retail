# Initial Data Assessment

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Assessment Rule

This document records the state of the raw dataset before cleaning.

No cleaning or transformation should be performed during this assessment.

## Dataset Files

Expected:

- `sales.csv`
- `online.csv`
- `markdowns.csv`
- `price_history.csv`

## Dimensions

| File | Rows | Columns |
|---|---:|---:|
| `sales.csv` | NOT VERIFIED | NOT VERIFIED |
| `online.csv` | NOT VERIFIED | NOT VERIFIED |
| `markdowns.csv` | NOT VERIFIED | NOT VERIFIED |
| `price_history.csv` | NOT VERIFIED | NOT VERIFIED |

## Data Types

Data types must be obtained from the inspection script.

Status:

NOT YET VERIFIED

## Missing Values

Missing-value counts must be obtained from the inspection script.

Status:

NOT YET VERIFIED

Important:

Missing values are being measured only at this stage.

No missing-value treatment is performed in Phase 2.

## Duplicate Records

Duplicate counts must be obtained from the inspection script.

Status:

NOT YET VERIFIED

Duplicates will be investigated and handled in the appropriate cleaning phase.

## Temporal Coverage

Source documentation indicates approximately 25 months of data.

Exact minimum and maximum dates must be obtained from the raw files.

Status:

NOT YET VERIFIED

## Chronological Ordering

The inspection will determine whether each time-based file is already ordered chronologically.

If not ordered, the raw files will not be modified.

Ordering will be handled during later processing.

## Target Candidate

Candidate demand variable:

`quantity`

Final target definition:

NOT YET VERIFIED

## Time-Series Granularity

Expected:

Daily

Actual:

NOT YET VERIFIED

## Forecasting Unit

Potential unit:

`store_id + item_id`

Status:

NOT YET VERIFIED

## Promotions / Markdowns

The dataset contains markdown information.

This will initially be treated as markdown/pricing information.

No causal promotional effect will be assumed.

## Holidays

An explicit holiday variable has not been identified from the source description.

Status:

NOT VERIFIED

If no holiday field exists, the project will document this as a dataset limitation rather than inventing a holiday feature.

## Holdout

The source describes a one-month holdout.

Exact file and date range:

NOT YET VERIFIED

## Initial Quality Concerns

Potential issues to investigate:

- missing values
- duplicate records
- inconsistent data types
- date parsing
- duplicate store-item-date combinations
- missing dates within time series
- negative or zero quantities
- inconsistent prices
- inconsistent identifiers
- differences between physical and online sales
- overlapping information across tables

## Phase 2 Assessment Status

IN PROGRESS

The assessment becomes complete only after the local raw data has been inspected.