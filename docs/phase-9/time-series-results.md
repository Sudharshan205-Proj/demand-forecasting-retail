# Phase 9 — Time-Series Preparation Results

## Source

`data/processed/integrated_retail_data.csv`, produced by Phase 6. The integrated
grain is already unique, so aggregation preserves the source row count and total
quantity exactly.

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

## Results

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
Phase 6 integration results and with the Phase 7 and Phase 8 analyses
(7,431,026 rows, 41,949,529.910 quantity, 2022-08-28 to 2024-09-26). The
aggregation is a type-conversion and chronological-ordering pass: it reduces 0
rows because the integrated source already carries the unique date-item-store
grain.

### Chronological partitions

| Split | Rows | Quantity | Date range | Dates | Share |
|---|---:|---:|---|---:|---:|
| Train | 4,315,416 | 24,038,416.097 | 2022-08-28 to 2024-02-10 | 532 | 69.9% |
| Validation | 1,548,957 | 8,811,477.346 | 2024-02-11 to 2024-06-03 | 114 | 15.0% |
| Test | 1,566,653 | 9,099,636.467 | 2024-06-04 to 2024-09-26 | 115 | 15.1% |

Split boundaries: train ends **2024-02-10**, validation ends **2024-06-03** and
the test partition begins **2024-06-04**.

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
daily grain covers all 761 calendar dates but individual series are sparse, most
series are missing intermediate dates: 55,122 of 58,022 series (95.0%) contain
at least one gap. These missing dates are reported as missing and are never
converted to zero demand. The largest single gap (757 days) comes from a series
observed at both ends of the history with almost nothing between.

## Interpretation

The prepared dataset distinguishes:

- **observed demand** — 7,431,026 date-item-store records with a quantity;
- **missing observations** — intermediate calendar dates with no record, which
  are left missing rather than zero-filled (12,553,017 across all series);
- **chronological partitions** — contiguous train/validation/test date ranges;
- **future information** — excluded from every earlier partition.

No forecasting performance is reported in Phase 9.

The sparse-series structure established here is the single most important
modelling constraint for later phases: an observation-based window such as a
seven-record lag does not necessarily span seven calendar days. Phase 10
preserves this grain and these chronological partitions unchanged —
7,431,026 rows with split rows and quantities identical to the prepared dataset
— and defines its lag and rolling features over previous observed records
accordingly.

## Limitations

- The item-store series are sparse, so calendar-based lag windows are not
  supported without an explicit densification decision, which this phase
  deliberately does not make.
- A missing record can mean zero demand or that the item was not carried; the
  integrated data does not distinguish these cases. The phase therefore treats
  a missing date as unknown rather than as zero.
- The split is defined on the date axis, so an individual item-store series may
  appear in more than one partition. This is correct for temporal validation and
  is not leakage.
- The 2023-12 coverage change (store 4 entering on 2023-12-13, quantified in
  Phase 8) is inherited unchanged; modelling it belongs to Phases 10–12.

## Reproduction runbook

Run from the project root with the virtual environment present.

| # | Purpose | Command | Expected result |
|---|---|---|---|
| 1 | Confirm the environment | `.venv\Scripts\python.exe --version` | Python 3.12 |
| 2 | Run the Phase 9 tests | `.venv\Scripts\python.exe -m pytest tests/test_prepare_time_series.py -q -p no:cacheprovider` | 37 passed |
| 3 | Execute the preparation workflow | `.venv\Scripts\python.exe scripts/prepare_time_series.py` | "Time-series preparation completed successfully." |
| 4 | Verify the quality report | `.venv\Scripts\python.exe -c "import pandas as pd; r=pd.read_csv('data/analysis/time_series_quality_report.csv'); print(len(r), bool(r['passed'].all()))"` | `15 True` |
| 5 | Verify reconciliation | `.venv\Scripts\python.exe -c "import pandas as pd; print(pd.read_csv('data/analysis/time_series_summary.csv').to_string(index=False))"` | 7,431,026 rows; quantity 41949529.910 |
| 6 | Regression: dependent phase | `.venv\Scripts\python.exe -m pytest tests/test_feature_engineering.py -q -p no:cacheprovider` | 32 passed |
| 7 | Regression: full suite | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | 532 passed |
