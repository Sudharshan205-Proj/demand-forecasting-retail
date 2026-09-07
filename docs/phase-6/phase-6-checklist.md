# Phase 6 — Data Integration Checklist

## Planning

* [ ] Define canonical integration grain.
* [ ] Identify all source datasets.
* [ ] Define the role of each dataset.
* [ ] Define join keys.
* [ ] Identify possible one-to-many relationships.
* [ ] Define protection against many-to-many joins.

## Implementation

* [ ] Load cleaned sales.
* [ ] Integrate stores.
* [ ] Integrate catalog.
* [ ] Aggregate and integrate price history.
* [ ] Aggregate and integrate markdowns.
* [ ] Aggregate and integrate discounts.
* [ ] Aggregate online sales separately.
* [ ] Integrate actual-matrix coverage.
* [ ] Generate integrated dataset.
* [ ] Generate quality report.

## Validation

* [ ] Verify row-count preservation.
* [ ] Verify canonical-grain uniqueness.
* [ ] Verify store referential integrity.
* [ ] Verify join cardinality.
* [ ] Verify catalog unmatched records are retained.
* [ ] Verify online sales are not added to physical demand.
* [ ] Verify raw files remain unchanged.
* [ ] Run unit tests.
* [ ] Run compilation.
* [ ] Run independent output validation.

## Documentation

* [ ] Integration plan.
* [ ] Integration methodology.
* [ ] Integration quality framework.
* [ ] Integration results.
* [ ] Course-content coverage.
* [ ] Project state.
* [ ] File-update register.
* [ ] README.

## Git

* [ ] Review status.
* [ ] Review diff.
* [ ] Review staged files.
* [ ] Commit once.
* [ ] Push branch.
* [ ] Verify remote branch.
* [ ] Verify clean working tree.
