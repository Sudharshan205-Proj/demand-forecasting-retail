# Phase 9 — Time-Series Preparation Results

## Status

VERIFIED

Verified during the Phase 17 re-audit by executing the preparation workflow
against the full integrated dataset (7,431,026 rows) and inspecting every
generated artifact. All reported values come from the complete dataset; no
value is sampled.

## Source

`data/processed/integrated_retail_data.csv`

Produced by Phase 6. The integrated grain is already unique, so aggregation
preserves the source row count and total quantity exactly.

## Outputs

Prepared dataset in `data/processed/`:

- `time_series_daily.csv` — 283,764,237 bytes, 7,431,026 rows plus header,
  columns `date, item_id, store_id, quantity, split`.

Analysis tables in `data/analysis/`:

- `time_series_summary.csv`
- `time_series_gap_summary.csv`
- `time_series_split_summary.csv`
- `time_series_quality_report.csv`
- `time_series_findings.txt`

## Verified results

### Dataset and reconciliation

| Metric | Result |
|---|---:|
| Prepared rows | 7,431,026 |
| Source rows | 7,431,026 |
| Rows reduced by aggregation | 0 |
| Unique items | 28,180 |
| Unique stores | 4 |
| Date range | 2022-08-28 to 2024-09-26 |
| Calendar days covered | 761 |
| Total quantity | 41,949,529.910 |
| Source quantity | 41,949,529.910 |
| Within-chunk duplicate source keys | 0 |
| Duplicate prepared keys | 0 |

Row count, quantity, date range, stores and items reconcile exactly with the
Phase 6 integration report and the Phase 7 and Phase 8 results (7,431,026
rows, 41,949,529.910 quantity, 2022-08-28 to 2024-09-26). The aggregation is a
type-conversion and chronological-ordering pass: it reduces 0 rows because the
integrated source already carries the unique date-item-store grain.

### Chronological partitions

| Split | Rows | Quantity | Date range | Dates | Share |
|---|---:|---:|---|---:|---:|
| Train | 4,315,416 | 24,038,416.097 | 2022-08-28 to 2024-02-10 | 532 | 69.9% |
| Validation | 1,548,957 | 8,811,477.346 | 2024-02-11 to 2024-06-03 | 114 | 15.0% |
| Test | 1,566,653 | 9,099,636.467 | 2024-06-04 to 2024-09-26 | 115 | 15.1% |

Split boundaries: train ends **2024-02-10**, validation ends **2024-06-03**
and the test partition begins **2024-06-04**.

The partition rows sum to 7,431,026 and the partition quantities sum to
41,949,529.910, so the three partitions exactly partition the prepared frame.
The date ranges are contiguous and non-overlapping: no future observation
appears in an earlier partition and no random shuffling is used.

### Temporal gaps

| Metric | Result |
|---|---:|
| Item-store series | 58,022 |
| Series containing gaps | 55,122 |
| Series without gaps | 2,900 |
| Total missing intermediate days | 12,553,017 |
| Maximum single gap | 757 days |
| Maximum per-series missing-day total | 756 days |

The prepared dataset keeps only observed date-item-store records. Because the
daily grain covers all 761 calendar dates but individual series are sparse,
most series are missing intermediate dates: 55,122 of 58,022 series
(95.0%) contain at least one gap. These missing dates are reported as missing
and are never converted to zero demand. The largest single gap (757 days) comes
from series observed at both ends of the history with almost nothing between.

This gap structure is the single most important modelling constraint for
later phases: a "lag 7" or "rolling 28" window over previous observed records
does not necessarily correspond to seven or twenty-eight calendar days.

## Interpretation

The prepared dataset distinguishes:

- **observed demand** — 7,431,026 date-item-store records with a quantity;
- **missing observations** — intermediate calendar dates with no record, which
  are left missing rather than zero-filled (12,553,017 across all series);
- **chronological partitions** — contiguous train/validation/test date ranges;
- **future information** — excluded from every earlier partition.

No forecasting performance is reported in Phase 9.

Phase 10 preserves this grain and these chronological partitions unchanged:
7,431,026 rows and split rows and quantities identical to the prepared
dataset. Because the series are sparse, Phase 10 defines its lag and rolling
features over previous observed records rather than calendar days.

## Limitations

- The item-store series are sparse, so calendar-based lag windows are not
  directly supported without an explicit densification decision, which this
  phase deliberately does not make.
- A missing record can mean zero demand or that the item was not carried; the
  integrated data does not distinguish these cases. The phase therefore treats
  a missing date as unknown rather than as zero.
- The split is defined on the date axis, so an individual item-store series
  may appear in more than one partition. This is correct for temporal
  validation and is not leakage.
- The 2023-12 coverage change (store 4 entering on 2023-12-13, diagnosed in
  Phase 8) is inherited unchanged; modelling it is Phase 10–12 work.

## Phase status

Phase 9 is implemented, executed and verified.

## Phase 17 Re-Audit Record

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/prepare_time_series.py` |
| Tests | `tests/test_prepare_time_series.py` |
| Phase 9 documents | all six files in `docs/phase-9/` |
| Generated artifacts | `data/processed/time_series_daily.csv`, four CSVs and `time_series_findings.txt` in `data/analysis/` |
| Inputs | `data/processed/integrated_retail_data.csv` |
| Downstream | `scripts/feature_engineering.py` (consumer of the Phase 9 grain and split) |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-2/dataset-inventory.md`, `docs/phase-7/eda-results.md`, `docs/phase-8/statistical-results.md`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Documentation never updated after execution | `time-series-results.md` said "will be executed"; the checklist was entirely unchecked; the register said "Not yet started" while the README reported COMPLETE | Medium |
| F2 | Two quality checks were vacuous | `maximum_observed_gap_days >= 0` and `missing_intermediate_days >= 0` can never fail | Medium |
| F3 | Framework validation was unimplemented | The framework required date-range, partition-overlap, all-rows-assigned, split-quantity reconciliation, numeric-quantity and source-preservation checks; only six checks existed, two of them vacuous | Medium |
| F4 | Documented chunked strategy violated | `calculate_quality_report` re-read the whole 1.28 GB source with `pd.read_csv` after the chunked pass had already read it | Medium |
| F5 | Float artefacts | `time_series_summary.csv` and the findings printed `41949529.910000004` | Low |
| F6 | Test coverage missed the core | 10 tests covered pure functions; `aggregate_daily`, `calculate_quality_report`, `write_findings` and `main` were untested | Medium |
| F7 | Three-date edge case raised | `calculate_split_boundaries` documented a three-date minimum but exactly three dates raised "Invalid chronological split boundaries" | Low |
| F8 | Structural magnitude unreported | 55,122 of 58,022 series with gaps and 12,553,017 missing intermediate days were absent from the summary and were presented without context | Medium |

**Leakage audit:** none. The workflow aggregates row-level records and assigns
contiguous date partitions only; there is no fill, no forward or backward
carry and no shuffle.

**Positive validation:** the re-executed artifacts reproduce the pre-audit
artifacts exactly — prepared rows 7,431,026, total quantity 41,949,529.910,
split boundaries 2024-02-10 / 2024-06-03, 58,022 series, 55,122 with gaps and
the same output dataset size (283,764,237 bytes). The rewrite changed the
verification machinery, not the data.

### Code changes

1. **Single-pass reconciliation (F4).** `aggregate_daily` now returns
   `(prepared, source_stats)`, accumulating source rows, source quantity,
   source date range and within-chunk duplicate keys inside the one chunked
   pass. The separate full-source read in `calculate_quality_report`
   disappeared.
2. **Real quality checks (F2, F3).** The two `>= 0` checks were replaced with
   span-bounded gap checks, and fourteen checks now cover schema, key, date,
   demand, gap, partition, leakage and preservation requirements
   (`time_series_quality_report.csv`, 15 checks, all True).
3. **Quantity formatting (F5).** The summary CSV and findings print quantities
   as `41949529.910`; raw values remain in the quality report.
4. **Three-date split handling (F7).** Boundary indices are clamped so each
   partition holds at least one date, honouring the documented minimum; the
   verified 761-date boundaries are unchanged.
5. **Gap magnitude surfaced (F8).** The summary now records `item_store_series`,
   `series_with_gaps` and `missing_intermediate_days`, and the findings report
   the reconciliation, gap and partition detail.
6. **Stable sort.** The final grain ordering uses a stable sort (`mergesort`).
7. **Design preserved.** Observed rows only, no densification, no zero-filling,
   no lag features and no models.

### Testing

| Test | Result |
|---|---|
| Phase 9 test file | 36 tests, all passing (was 10) |
| Full suite | 257 tests, all passing (231 previously; Phase 9 added 26) |

Coverage added: end-to-end aggregation, within-chunk duplicate detection,
chunk-size independence, numeric coercion, invalid-date/quantity/column
rejection, output ordering, gap detection and clipping, single-observation
series, series separation, the span identity, split proportions for 761 dates,
the three-date case, partition non-overlap, quality-report pass and five
deliberate-failure cases, quantity formatting, findings content and the
complete `main()` workflow with source preservation.

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/prepare_time_series.py
Exit status: 0
Runtime:     206.4 seconds
Peak memory: 1,356.9 MB
Result:      "Time-series preparation completed successfully."
```

The peak is dominated by the retained 7,431,026-row prepared frame, which is
required to write the output dataset; the source itself is still streamed in
chunks and is read once.

### Generated-file verification

| File | Exists | Size | Structure | Validation |
|---|---|---|---|---|
| `time_series_daily.csv` | yes | 283,764,237 B | 7,431,026 rows + header | grain unique; quantities reconcile |
| `time_series_summary.csv` | yes | 12 metric rows | — | values reconcile with Phase 6/8 |
| `time_series_gap_summary.csv` | yes | 58,022 rows | 7 columns | per-series gaps; bounds verified |
| `time_series_split_summary.csv` | yes | 3 rows | 5 columns | rows and quantities reconcile |
| `time_series_quality_report.csv` | yes | 15 rows | check/passed/actual/expected | all True |
| `time_series_findings.txt` | yes | 6 sections | — | no float artefacts; integer counts |

### Documentation changes

All six Phase 9 documents were rewritten under their existing headings, and the
cross-phase records listed under "Files reviewed" were synchronised.

### Remaining issues

- None open for Phase 9.
- Flagged for the Phase 10 audit: `scripts/feature_engineering.py` derives
  `series_age_days` from a series' first date across its entire history, a
  potential leakage point to examine when Phase 10 is re-audited.
- The sparse-series gap structure is a modelling constraint for Phase 10–12,
  not a Phase 9 defect.
