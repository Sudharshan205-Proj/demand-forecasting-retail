# Phase 7 — EDA Quality Framework

## Quality dimensions

### Completeness

The analysis must account for the full integrated dataset.

Aggregates, correlations and distributions are all calculated from every
applicable row. No sampled subset is used anywhere in Phase 7.

### Correctness

Aggregated quantities and revenues must reconcile with the integrated source.

Non-finite values (infinite values in a numeric column) must be quantified per
column and excluded from pairwise statistics rather than being allowed to
propagate silently.

### Reproducibility

The pipeline is deterministic for a given input file. It uses no sampling and
no random seed.

### Traceability

Every generated summary must have a documented relationship to the integrated
dataset.

The correlation summary records the pairwise-complete basis of each
coefficient, and record-frequency metrics are derived from
`discount_record_count` and `markdown_record_count` so that presence is not
inferred from nullability alone.

### Interpretability

EDA results must distinguish descriptive association from causation.

### Temporal integrity

The analysis must preserve chronological meaning.

### Data preservation

EDA must not modify the integrated source or raw datasets.

Unusual demand is identified for investigation only; Phase 7 removes nothing.

## Validation checks

The following must be validated:

* required columns exist
* input file exists, with an actionable failure message
* row count is processed
* temporal range is identified
* store count is identified
* item count is identified
* missingness is reported
* non-finite values are quantified
* promotion and markdown record frequency is reported
* item-level distribution, outlier fence and concentration are reported
* aggregate summaries are generated
* aggregate results are independent of the chunk size
* correlation is calculated from the complete dataset
* correlation handles missing and infinite values pairwise
* figures are generated
* chart categories with no value are labelled explicitly
* tests pass

## Acceptance criteria

Phase 7 can only be marked complete when:

1. The EDA script executes successfully.
2. Required summary files are generated.
3. Required figures are generated.
4. Automated tests pass.
5. Independent output validation succeeds.
6. Documentation reflects actual results.
7. Git changes are reviewed.
8. The phase is committed and pushed.
9. The final repository state is verified.

Items 7 to 9 are repository and version-control actions. They are not performed
during the Phase 17 re-audit because that audit runs without Git commands; the
change set is recorded in `docs/project-status.md` instead.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
