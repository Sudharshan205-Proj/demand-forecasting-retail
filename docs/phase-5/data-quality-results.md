# Phase 5 — Data Quality Results

## Execution status

**Status:** NOT YET VERIFIED

This document must be updated after the Phase 5 cleaning pipeline has actually
been executed.

## Source

`data/raw/sales.csv`

## Output

`data/processed/sales_clean.csv`

## Quality report

`data/processed/data_quality_report.csv`

## Cleaning summary

`data/processed/cleaning_summary.csv`

## Results

| Metric | Result |
|---|---:|
| Rows read | NOT YET VERIFIED |
| Rows written | NOT YET VERIFIED |
| Missing required rows | NOT YET VERIFIED |
| Duplicate rows | NOT YET VERIFIED |
| Invalid date rows | NOT YET VERIFIED |
| Negative quantity rows | NOT YET VERIFIED |
| Negative price rows | NOT YET VERIFIED |
| Negative revenue rows | NOT YET VERIFIED |
| Unknown store rows | NOT YET VERIFIED |
| Revenue mismatch rows | NOT YET VERIFIED |
| Potential quantity outlier rows | NOT YET VERIFIED |

## Validation

The following must be executed:

- cleaning script
- Phase 5 unit tests
- syntax validation
- processed-output inspection
- post-cleaning quality checks

## Interpretation

No numerical interpretation should be added until the pipeline has been
executed and its output verified.

## Known data-quality considerations

- Raw data must remain unchanged.
- Revenue mismatches must be investigated rather than automatically rewritten.
- Extreme demand observations must not automatically be treated as errors.
- Temporal anomalies in supporting datasets remain documented for later
  investigation.