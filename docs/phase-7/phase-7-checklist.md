# Phase 7 — Exploratory Data Analysis Checklist

## Planning

* [x] Define EDA questions.
* [x] Define analytical grain.
* [x] Define required summaries.
* [x] Define visualization requirements.
* [x] Define quality controls.

## Implementation

* [x] Validate integrated dataset schema.
* [x] Validate that the integrated dataset exists, with an actionable message.
* [x] Process integrated data in chunks.
* [x] Calculate overall demand.
* [x] Calculate temporal summaries.
* [x] Calculate store summaries.
* [x] Calculate product summaries.
* [x] Calculate department summaries.
* [x] Calculate correlation analysis.
* [x] Calculate item-level distribution, outlier and concentration metrics.
* [x] Calculate promotion and markdown record frequency.
* [x] Generate findings.
* [x] Generate visualizations.

## Testing

* [x] Validate required columns.
* [x] Validate schema failure handling.
* [x] Validate missing input file handling.
* [x] Validate temporal aggregation.
* [x] Validate store aggregation.
* [x] Validate item aggregation.
* [x] Validate department aggregation.
* [x] Validate correlation behaviour.
* [x] Validate correlation against a pandas oracle.
* [x] Validate pairwise handling of missing and infinite values.
* [x] Validate chunk-size independence.
* [x] Validate item-level distribution and concentration metrics.
* [x] Validate findings content.
* [x] Validate figure generation, including a category with no value.
* [x] Run Python compilation.
* [x] Run Phase 7 tests.
* [x] Validate generated outputs.

## Documentation

* [x] EDA plan.
* [x] EDA methodology.
* [x] EDA quality framework.
* [x] EDA results.
* [x] Course-content coverage.
* [x] Project state.
* [x] File-update register.
* [x] README (verified: it already lists Phase 7 correctly and required no change).

## Git

* [x] Check status.
* [x] Check branch.
* [x] Review diff.
* [x] Stage correct source files.
* [x] Commit.
* [x] Push.
* [x] Verify remote state.
* [x] Verify clean working tree.

Verified by the documentation review on 2026-09-19: the branch
`phase-7-exploratory-data-analysis` exists locally and on `origin`, its tip
`651ab10` ("Complete Phase 7 exploratory data analysis") is merged into
`main`, and the Phase 17 re-audit commit `266c27f` ("Phase 7 Audit") is on
`main`, which matches `origin/main`. The items were originally left unticked
because the Phase 17 audit itself ran no Git command; they are now ticked
against the verified repository state. The change set is recorded in
`docs/project-status.md` and in the consolidated Phase 17 Re-Audit Record
(`docs/phase-17/re-audit-record.md`, Phase 7 records).

## Completion

* [x] All checklist items complete.
* [x] No unresolved test failures.
* [x] Documentation matches implementation.
* [x] Actual results recorded.
* [x] Phase marked COMPLETE.

## Evidence

```text
Command:  .venv\Scripts\python.exe -m pytest tests/test_exploratory_data_analysis.py -q
Result:   34 passed

Command:  .venv\Scripts\python.exe -m pytest -q
Result:   193 passed, 1 warning (pre-existing Phase 5 warning)

Command:  .venv\Scripts\python.exe scripts/exploratory_data_analysis.py
Result:   exit status 0, 61-63 seconds
```

Artifacts verified: `eda_summary.csv` (45 metric rows), `eda_monthly_demand.csv`
(26 months), `eda_store_summary.csv` (4 stores), `eda_category_summary.csv`
(182 rows), `eda_top_items.csv` (100 items), `eda_correlation.csv` (7x7 matrix,
diagonal exactly 1.0, all 21 coefficients validated independently),
`eda_findings.txt`, and five `eda_*.png` figures.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
