# Phase 7 — EDA Quality Framework

## Quality dimensions

### Completeness

The analysis must account for the full integrated dataset unless a specific
analysis explicitly uses a deterministic sample.

### Correctness

Aggregated quantities and revenues must reconcile with the integrated source.

### Reproducibility

Random sampling uses a fixed seed.

### Traceability

Every generated summary must have a documented relationship to the integrated
dataset.

### Interpretability

EDA results must distinguish descriptive association from causation.

### Temporal integrity

The analysis must preserve chronological meaning.

### Data preservation

EDA must not modify the integrated source or raw datasets.

## Validation checks

The following must be validated:

* required columns exist
* input file exists
* row count is processed
* temporal range is identified
* store count is identified
* item count is identified
* missingness is reported
* aggregate summaries are generated
* figures are generated
* deterministic sampling works
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
