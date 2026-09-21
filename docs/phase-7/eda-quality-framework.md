# Phase 7 — EDA Quality Framework

## Quality dimensions

### Completeness

The analysis accounts for the full integrated dataset. Aggregates, correlations
and distributions are calculated from every applicable row; no sampled subset is
used anywhere in Phase 7.

### Correctness

Aggregated quantities and revenues reconcile with the integrated source.
Non-finite values are quantified per column and excluded from pairwise statistics
rather than allowed to propagate silently.

### Reproducibility

The pipeline is deterministic for a given input file. It uses no sampling and no
random seed.

### Traceability

Every generated summary has a documented relationship to the integrated dataset.
The correlation summary records the pairwise-complete basis of each coefficient,
and record-frequency metrics are derived from `discount_record_count` and
`markdown_record_count` so that presence is not inferred from nullability alone.

### Interpretability

EDA results distinguish descriptive association from causation.

### Temporal integrity

The analysis preserves chronological meaning.

### Data preservation

EDA does not modify the integrated source or raw datasets. Unusual demand is
identified for investigation only; Phase 7 removes nothing.

## Validation checks

- required columns exist
- input file exists, with an actionable failure message
- row count is processed
- temporal range is identified
- store count is identified
- item count is identified
- missingness is reported
- non-finite values are quantified
- promotion and markdown record frequency is reported
- item-level distribution, outlier fence and concentration are reported
- aggregate summaries are generated
- aggregate results are independent of the chunk size
- correlation is calculated from the complete dataset
- correlation handles missing and infinite values pairwise
- figures are generated
- chart categories with no value are labelled explicitly
- tests pass

## Acceptance criteria

Phase 7 is complete when:

1. The EDA script executes successfully.
2. Required summary files are generated.
3. Required figures are generated.
4. Automated tests pass.
5. Output validation succeeds.
6. Documentation reflects the actual results.
