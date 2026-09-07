# Phase 5 — Data Cleaning Methodology

## Processing strategy

The sales dataset contains millions of records, so the cleaning process uses
chunked CSV processing.

The raw dataset is never loaded into memory as one complete DataFrame.

The processing flow is:

1. Load the store lookup.
2. Read sales records in chunks.
3. Validate the required schema.
4. Convert dates.
5. Convert numeric fields.
6. Detect missing required values.
7. Detect duplicates.
8. Detect invalid dates.
9. Detect invalid quantities.
10. Detect invalid prices.
11. Detect invalid revenue.
12. Detect unknown stores.
13. Check revenue consistency.
14. Identify potential quantity outliers.
15. Write valid records to the processed dataset.
16. Write quality metrics.
17. Write the cleaning summary.

## Raw data preservation

The raw file remains:

`data/raw/sales.csv`

The processed file is:

`data/processed/sales_clean.csv`

No operation writes to the raw directory.

## Type conversion

The pipeline explicitly converts:

- `date` → datetime
- `quantity` → numeric
- `price_base` → numeric
- `sum_total` → numeric
- `item_id` → cleaned string
- `store_id` → cleaned string

## Duplicate handling

Duplicate rows are identified using the complete row contents.

Duplicate rows after the first occurrence are removed.

The number detected is recorded in the quality report.

## Missing values

Rows missing required analytical fields are excluded.

This is preferable to silently imputing sales demand because fabricated demand
could directly affect future forecasting.

## Invalid values

The following are considered invalid for the primary demand dataset:

- invalid dates
- missing required fields
- negative quantity
- negative base price
- negative revenue
- unknown store IDs
- non-numeric required measures

## Revenue validation

Revenue is checked using:

`quantity × price_base`

against:

`sum_total`

A mismatch is recorded but does not automatically invalidate the row.

This avoids changing potentially legitimate source-system calculations.

## Outlier handling

Potential quantity outliers are identified using the 99th percentile within
each processed chunk.

They are reported but not deleted.

Chunk-local outlier identification is intentionally treated as a screening
mechanism rather than a final statistical outlier decision.

Later exploratory analysis can investigate temporal and store-level demand
patterns in more detail.

## Output

The pipeline produces:

- `sales_clean.csv`
- `data_quality_report.csv`
- `cleaning_summary.csv`

All outputs are reproducible from the raw dataset and script.