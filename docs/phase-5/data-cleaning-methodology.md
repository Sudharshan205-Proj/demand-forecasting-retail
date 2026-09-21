# Phase 5 — Data Cleaning Methodology

## Processing strategy

The sales dataset contains millions of records, so the cleaning process uses
chunked CSV processing. The raw dataset is never loaded into memory as one
complete DataFrame.

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

The raw file remains `data/raw/sales.csv`; the processed file is
`data/processed/sales_clean.csv`. No operation writes to the raw directory.

## Type conversion

The pipeline explicitly converts:

- `date` → datetime
- `quantity` → numeric
- `price_base` → numeric
- `sum_total` → numeric
- `item_id` → cleaned string
- `store_id` → cleaned string

## Duplicate handling

Duplicate rows are identified using the complete row contents, and duplicate
rows after the first occurrence are removed. The number detected is recorded in
the quality report.

Duplicate detection is chunk-local: it identifies duplicates within each
processed chunk, so a duplicate pair split across a chunk boundary would not be
detected by this screen. The raw sales dataset contains no duplicate rows
(recorded in Phase 2), so this does not affect the current results.

## Missing values

Rows missing required analytical fields are excluded. This is preferable to
silently imputing sales demand, because fabricated demand would directly affect
forecasting.

## Invalid values

The following are invalid for the primary demand dataset:

- invalid dates
- missing required fields
- negative quantity
- negative base price
- negative revenue
- unknown store IDs
- non-numeric required measures

## Revenue validation

Revenue is checked by comparing `quantity × price_base` against `sum_total`. A
mismatch is recorded but does not invalidate the row, which avoids changing
potentially legitimate source-system calculations.

## Outlier handling

Potential quantity outliers are identified using the 99th percentile within each
processed chunk. They are reported but not deleted.

Chunk-local outlier identification is a screening mechanism rather than a final
statistical outlier decision; the exploratory analysis in Phase 7 investigates
temporal and store-level demand patterns in more detail.

## Output

The pipeline produces:

- `data/processed/sales_clean.csv`
- `data/processed/data_quality_report.csv`
- `data/processed/cleaning_summary.csv`

All outputs are reproducible from the raw dataset and script.

## Catalog reference check

Sales item identifiers are compared with the catalog item list. Rows whose
`item_id` has no matching catalog record are counted and reported, and are not
removed: catalog coverage can legitimately differ from sales coverage, so a
missing catalog match is a reference-integrity observation rather than a reason
to discard a genuine demand record. The count is reported on the same raw basis
as the Phase 4 validation query, with the distinct unmatched item count
alongside it.

## Date coverage

The minimum and maximum successfully parsed sale dates are recorded across all
processed chunks. Coverage is computed over every valid date read, not only over
the rows that survive cleaning, so it describes the temporal span of the source
data.

## Cleaning summary reporting

The summary reports "Rows removed" as `rows read − rows written` (1,659). The
per-rule failure counters overlap, so their sum (2,837) is reported separately
and labelled "Rule failures (diagnostic)" rather than added to the rows removed.
