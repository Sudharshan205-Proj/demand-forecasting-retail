# Phase 9 — Time-Series Preparation Checklist

## Objective

Prepare the integrated retail data for chronological demand forecasting.

## Data preparation

- [ ] Validate required columns.
- [ ] Aggregate to date-item-store grain.
- [ ] Validate duplicate forecasting keys.
- [ ] Validate chronological ordering.
- [ ] Analyse temporal gaps.
- [ ] Preserve missing observations as missing rather than blindly converting
      them to zero demand.
- [ ] Reconcile total quantity with the integrated source.

## Time-series partitioning

- [ ] Establish chronological train period.
- [ ] Establish chronological validation period.
- [ ] Establish chronological test period.
- [ ] Verify no temporal overlap.
- [ ] Verify future observations are not used in earlier partitions.

## Engineering

- [ ] Process the large dataset in chunks.
- [ ] Use project-relative paths.
- [ ] Preserve source data.
- [ ] Use deterministic processing.
- [ ] Add tests.
- [ ] Validate outputs.

## Documentation

- [ ] Time-series preparation plan.
- [ ] Time-series methodology.
- [ ] Time-series quality framework.
- [ ] Time-series results.
- [ ] Course-content coverage.
- [ ] README update.
- [ ] Project-state update.
- [ ] File-update register update.

## Git

- [ ] Create Phase 9 branch.
- [ ] Review changes.
- [ ] Stage intended files.
- [ ] Commit once at phase completion.
- [ ] Push branch.
- [ ] Verify clean working tree.