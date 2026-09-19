# Phase 5 — Data Quality Results

## Execution status

**Status:** VERIFIED

The Phase 5 cleaning pipeline was executed against the complete raw sales
dataset during the Phase 17 re-audit, and its outputs were inspected and
reconciled against the Phase 2 and Phase 4 verified facts.

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
| Rows read | 7,432,685 |
| Rows written | 7,431,026 |
| Rows removed | 1,659 |
| Missing required rows | 0 |
| Duplicate rows | 0 |
| Invalid date rows | 0 |
| Negative quantity rows | 1,160 |
| Negative price rows | 67 |
| Negative revenue rows | 1,610 |
| Unknown store rows | 0 |
| Sales rows with no catalog match | 36,585 |
| Distinct items with no catalog match | 948 |
| Revenue mismatch rows | 1,041,252 |
| Potential quantity outlier rows | 73,507 |
| Earliest valid date | 2022-08-28 |
| Latest valid date | 2024-09-26 |

## Validation

The following were executed during the Phase 17 re-audit:

- cleaning script (full dataset)
- Phase 5 unit tests (19 passed)
- syntax validation
- processed-output inspection
- post-cleaning quality checks

## Interpretation

- The documented validity rules removed 1,659 of 7,432,685 rows (about 0.02%),
  so the cleaned dataset retains essentially the complete source while still
  applying the documented quality rules.
- Missing, duplicate, invalid-date and unknown-store counts are all zero, which
  is consistent with the Phase 2 verified raw assessment.
- The 1,041,252 revenue mismatches (about 14%) are reported but not removed, by
  design. They most plausibly reflect discounts, promotions or rounding applied
  to `sum_total` rather than `price_base`; resolving them belongs to integration
  and feature engineering.
- The 73,507 potential quantity outliers are a screening result: the chunk-local
  99th-percentile rule flags about 1% of each chunk by construction. They are
  retained, not deleted.
- 36,585 sales rows (948 distinct items) have no matching catalog record. This
  is an informational reference check; those rows are retained and handled with
  left-join/null logic during integration.

## Known data-quality considerations

- Raw data must remain unchanged.
- Revenue mismatches must be investigated rather than automatically rewritten.
- Extreme demand observations must not automatically be treated as errors.
- Temporal anomalies in supporting datasets remain documented for later
  investigation.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
