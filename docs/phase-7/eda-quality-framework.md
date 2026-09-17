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
change set is recorded in `docs/project-file-update-register.md` instead.

## Phase 17 Re-Audit Record

**Audit status:** AUDITED — COMPLETE

Framework changes applied:

* **Completeness** was tightened from "the full dataset unless a specific
  analysis explicitly uses a deterministic sample" to "the full dataset". The
  previous wording permitted the correlation sample, which was measured to
  differ from the exact full-dataset values by up to 0.179. Correlation now
  uses the complete dataset, so no exception remains.
* **Correctness** now requires non-finite values to be quantified and excluded
  from pairwise statistics. This was added because the integrated dataset
  contains 6,760 infinite values in `promo_discount_rate` and 2 in
  `markdown_discount`, and because pandas 3 ignores non-finite values in
  `corr()` while pandas 2 returns NaN, which made the previous output depend
  on the installed pandas version. The script now excludes non-finite values
  explicitly and reports `infinite_<column>` counts.
* **Traceability** now records the pairwise-complete basis of each
  coefficient and the record-count basis of promotion/markdown frequency.
* **Validation checks** gained five checks: input file existence with an
  actionable message, non-finite quantification, record frequency, item-level
  distribution and concentration, chunk-size independence, correlation
  completeness and non-finite handling, and explicit labelling of empty
  chart categories.

Evidence: 34 Phase 7 tests pass (10 before), the full suite passes with 193
tests, the pipeline completed in 61-63 seconds, all 21 correlation
coefficients were validated against two independent calculations, and all
seven summary files plus five figures were inspected against the summaries
they derive from.
