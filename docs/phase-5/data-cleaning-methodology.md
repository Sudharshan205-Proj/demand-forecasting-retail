# Phase 5 — Data Cleaning Methodology

## Processing strategy

The sales dataset contains millions of records, so the cleaning process uses
chunked CSV processing.

The raw dataset is never loaded into memory as one complete DataFrame.

The processing flow is:

1. Load the store lookup.
2. Load the catalog item reference.
3. Read sales records in chunks.
4. Validate the required schema.
5. Convert dates.
6. Record valid-date coverage.
7. Convert numeric fields.
8. Detect missing required values.
9. Detect duplicates.
10. Detect invalid dates.
11. Detect invalid quantities.
12. Detect invalid prices.
13. Detect invalid revenue.
14. Detect unknown stores.
15. Check the catalog-membership reference.
16. Check revenue consistency.
17. Identify potential quantity outliers.
18. Write valid records to the processed dataset.
19. Write quality metrics.
20. Write the cleaning summary.

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

Duplicate detection is chunk-local: it identifies duplicates within each
processed chunk. A duplicate pair split across a chunk boundary would not be
detected by this screen. The raw sales dataset contains no duplicate rows
(verified in Phase 2), so this limitation does not affect the current results;
it is recorded so the behaviour is not overstated.

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

## Catalog reference check

Sales item identifiers are compared with the catalog item list.

Rows whose `item_id` has no matching catalog record are counted and reported.

They are not removed. Catalog coverage can legitimately differ from sales
coverage, so a missing catalog match is a reference-integrity observation rather
than a reason to discard a genuine demand record. The count is reported on the
same raw basis as the Phase 4 validation query, and the distinct unmatched item
count is reported alongside it.

## Date coverage

The minimum and maximum successfully parsed sale dates are recorded across all
processed chunks.

Coverage is computed over every valid date that is read, not only over the rows
that survive cleaning, so it describes the temporal span of the source data.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
