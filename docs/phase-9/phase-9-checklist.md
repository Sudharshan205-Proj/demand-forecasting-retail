# Phase 9 — Time-Series Preparation Checklist

## Objective

Prepare the integrated retail data for chronological demand forecasting.

## Data preparation

- [x] Validate required columns.
- [x] Aggregate to date-item-store grain.
- [x] Validate duplicate forecasting keys (prepared 0; within-chunk source 0;
      cross-chunk merges exposed by the recorded row reduction).
- [x] Validate chronological ordering (stable sort; series monotonic).
- [x] Analyse temporal gaps (58,022 series; 55,122 with gaps; 12,553,017
      missing intermediate days).
- [x] Preserve missing observations as missing rather than blindly converting
      them to zero demand (observed rows only; no filling).
- [x] Reconcile total quantity with the integrated source (41,949,529.910).

## Time-series partitioning

- [x] Establish chronological train period (2022-08-28 to 2024-02-10).
- [x] Establish chronological validation period (2024-02-11 to 2024-06-03).
- [x] Establish chronological test period (2024-06-04 to 2024-09-26).
- [x] Verify no temporal overlap (`partitions_chronological_without_overlap`).
- [x] Verify future observations are not used in earlier partitions.

## Engineering

- [x] Process the large dataset in chunks (250,000 rows; source read once).
- [x] Use project-relative paths.
- [x] Preserve source data (`source_file_not_modified`).
- [x] Use deterministic processing.
- [x] Add tests (37 tests, all passing).
- [x] Validate outputs (`time_series_quality_report.csv`, 15 checks).

## Documentation

- [x] Time-series preparation plan.
- [x] Time-series methodology.
- [x] Time-series quality framework.
- [x] Time-series results (verified values recorded).
- [x] Course-content coverage.
- [x] README update (reviewed; already correct).
- [x] Project-state update.
- [x] File-update register update.

## Git

- [ ] Create Phase 9 branch.
- [ ] Review changes.
- [ ] Stage intended files.
- [ ] Commit once at phase completion.
- [ ] Push branch.
- [ ] Verify clean working tree.

The Git section is not exercised by the Phase 17 audit workflow: this
repository is audited in place and the audit runs no Git commands, so no
branch, commit or push is created for the re-audit. The section is left
unticked deliberately rather than claimed.

## Phase 17 re-audit record

**Audit status: AUDITED.**

Every checklist item above was verified against the re-executed workflow. The
re-audit rebuilt the 15-check quality report, replaced two vacuous gap checks,
removed the second full-source read, formatted the quantity figures, made date
parsing explicitly ISO and fixed three-date split handling. The Git items remain
intentionally unticked because the Phase 17 audit runs no Git commands.
