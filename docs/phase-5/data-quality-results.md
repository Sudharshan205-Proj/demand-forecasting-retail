# Phase 5 — Data Quality Results

## Source and outputs

- Source: `data/raw/sales.csv`
- Cleaned dataset: `data/processed/sales_clean.csv`
- Quality report: `data/processed/data_quality_report.csv`
- Cleaning summary: `data/processed/cleaning_summary.csv`

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

## Interpretation

- The validity rules remove 1,659 of 7,432,685 rows (about 0.02%), so the cleaned
  dataset retains essentially the complete source while applying the documented
  quality rules.
- Missing, duplicate, invalid-date and unknown-store counts are all zero,
  consistent with the raw assessment in Phase 2.
- The 1,041,252 revenue mismatches (about 14%) are reported but not removed, by
  design. They most plausibly reflect discounts, promotions or rounding applied
  to `sum_total` rather than `price_base`; the integrated dataset carries them
  unchanged.
- The 73,507 potential quantity outliers are a screening result: the chunk-local
  99th-percentile rule flags about 1% of each chunk by construction. They are
  retained, not deleted.
- 36,585 sales rows (948 distinct items) have no matching catalog record. This is
  an informational reference check; those rows are retained and handled with
  left-join/null logic during integration.

## Cross-phase reconciliation

- The catalog reference count of 36,585 on the raw basis matches Phase 4 Query 17
  exactly. On the cleaned basis it is 36,580, matching the Phase 6 integration
  report; the 5-row difference is removed rows that were also unmatched. The
  distinct unmatched item count is 948 on both bases.
- The valid-date coverage (2022-08-28 to 2024-09-26) matches the Phase 2 and
  Phase 4 facts.

## Data-quality considerations

- Raw data remains unchanged.
- Revenue mismatches are investigated rather than automatically rewritten.
- Extreme demand observations are not automatically treated as errors.
- Temporal anomalies in supporting datasets remain documented for later
  investigation.
