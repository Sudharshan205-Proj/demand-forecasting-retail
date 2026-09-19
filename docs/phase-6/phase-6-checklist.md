# Phase 6 — Data Integration Checklist

## Planning

* [x] Define canonical integration grain.
* [x] Identify all source datasets.
* [x] Define the role of each dataset.
* [x] Define join keys.
* [x] Identify possible one-to-many relationships.
* [x] Define protection against many-to-many joins.

## Implementation

* [x] Load cleaned sales.
* [x] Integrate stores.
* [x] Integrate catalog.
* [x] Aggregate and integrate price history.
* [x] Aggregate and integrate markdowns.
* [x] Aggregate and integrate discounts.
* [x] Aggregate online sales separately.
* [x] Integrate actual-matrix coverage.
* [x] Generate integrated dataset.
* [x] Generate quality report.

## Validation

* [x] Verify row-count preservation.
* [x] Verify canonical-grain uniqueness.
* [x] Verify store referential integrity.
* [x] Verify join cardinality.
* [x] Verify catalog unmatched records are retained.
* [x] Verify online sales are not added to physical demand.
* [x] Verify raw files remain unchanged.
* [x] Run unit tests.
* [x] Run compilation.
* [x] Run independent output validation.

## Documentation

* [x] Integration plan.
* [x] Integration methodology.
* [x] Integration quality framework.
* [x] Integration results.
* [x] Course-content coverage.
* [x] Project state.
* [x] File-update register.
* [x] README.

## Git

* [x] Review status.
* [x] Review diff.
* [x] Review staged files.
* [x] Commit once.
* [x] Push branch.
* [x] Verify remote branch.
* [x] Verify clean working tree.

Verified by the documentation review on 2026-09-19: the branch
`phase-6-data-integration` exists locally and on `origin`, its tip `f8aee8b`
("Complete Phase 6 data integration") is merged into `main`, and the Phase 17
re-audit commit `5e158ca` ("Phase 6 Audit") is on `main`, which matches
`origin/main`. The items were originally left unticked because the Phase 17
audit itself ran no Git command; they are now ticked against the verified
repository state.

## Phase 17 Re-Audit Status

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
