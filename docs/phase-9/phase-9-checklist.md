# Phase 9 — Time-Series Preparation

## Purpose

Phase 9 converts the integrated retail dataset into the chronological
forecasting dataset: a date-item-store grain with a documented temporal quality
record and contiguous train, validation and test partitions.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Prepared dataset | `data/processed/time_series_daily.csv` — 7,431,026 rows; `date, item_id, store_id, quantity, split` |
| Analysis tables | `time_series_summary.csv`, `time_series_gap_summary.csv`, `time_series_split_summary.csv`, `time_series_quality_report.csv`, `time_series_findings.txt` |
| Pipeline | `scripts/prepare_time_series.py` — single chunked pass over the 1.28 GB integrated source (250,000-row chunks) |
| Tests | `tests/test_prepare_time_series.py` — 37 tests, all passing |
| Quality record | `time_series_quality_report.csv` — 15 checks, all True |

## Key results

| Finding | Value |
|---|---|
| Prepared rows / quantity | 7,431,026 / 41,949,529.910, both reconciling exactly with Phase 6 |
| Date range | 2022-08-28 to 2024-09-26 (761 calendar days) |
| Duplicate date-item-store keys | 0 |
| Partitions | Train 4,315,416 rows to 2024-02-10; validation 1,548,957 rows to 2024-06-03; test 1,566,653 rows from 2024-06-04 |
| Item-store series | 58,022, of which 55,122 (95.0%) contain at least one gap |
| Missing intermediate days | 12,553,017, reported and never zero-filled |

## Course coverage

Phase 9 carries the **Prepare → Process** transition: data preparation, data
organisation, data-type control, validation, integrity reconciliation, quality
assessment, structured thinking and reproducibility
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`time-series-methodology.md`](time-series-methodology.md) — method
- [`time-series-quality-framework.md`](time-series-quality-framework.md) — quality practices
- [`time-series-results.md`](time-series-results.md) — results
