# Performance Log

All timings observed on this machine (Windows, x86-64, Python 3.12.10, R 4.6.1) during the 2026-09-19 re-execution. Wall-clock measured with `time`; no memory profiler was run on the pipeline scripts (the project records peak memory in its own Phase 8/9 docs).

## Observed durations vs documentation

| Phase / command | Documented | Observed | Note |
|---|---|---|---|
| Baseline `pytest -q` | 530 passed | 223.58 s | — |
| Final `pytest -q` | 530 passed | 281.66 s | +26 % vs baseline, same host, background VS Code LSP load |
| P2 `inspect_raw_data.py` | — | ~1–2 min (824 MB read) | full raw dataset parsed |
| P3 `create_spreadsheet_analysis.py` | — | seconds | 761/4/28,182 records |
| P4 `create_sqlite_database.py` | — | seconds (DB ~1.06 GB) | row counts as documented |
| P4 `run_sql_analysis.py` | not documented | **1,326 s (22 m 06 s)** | **anomaly** — the same 18 queries took ~2 min on 2026-09-16 (file mtimes). Cause not proven: cold page cache / concurrent load; all 18 results were produced correctly. Recorded, not explained away. |
| P5 `clean_retail_data.py` | ~113 s | 141.6 s | same order |
| P6 `integrate_retail_data.py` | ~350 s | 295.2 s | faster than documented |
| P7 `exploratory_data_analysis.py` | ~61 s | 82.2 s | same order |
| P8 `statistical_analytical_analysis.py` | ~41 s, peak 483.4 MB (documented) | 56.3 s | same order |
| P9 `prepare_time_series.py` | ~232 s, 1,405.5 MB peak (documented) | 219.8 s | matches |
| P10 `feature_engineering.py` | full-memory transform | 429.8 s | 888 MB output written |
| P11 `forecasting_models.py` | — | 51.6 s | 12 model fits, 114-day horizon × 4 stores |
| P12 `evaluate_and_tune_models.py` | 90 CV folds | 58.6 s | fast because the feature candidate is a shallow HistGradientBoosting |
| P13 `forecasting_inventory_insights.py` | — | 21.5 s | — |
| P14 `r_analysis.R` | 91 checks | 16.3 s | — |
| P14 R Markdown render | 43 chunks | 20.6 s | — |
| P15 `create_visualizations.py` | 55 checks | 8.9 s | — |
| P16 Streamlit startup→HTTP 200 | — | ~15–20 s | headless, port 8523 |

## Observations

1. **P4 SQL run anomaly** — 22 minutes versus the ~2-minute historical mtimes. No code change, all outputs correct, tests pass. Flagged as a performance observation only; a cold disk cache or the concurrent VS Code LSP processes are plausible but unproven. Not a correctness issue.
2. **Total re-execution wall clock** ≈ 55 minutes of pipeline compute (dominated by P4 22 m, P10 7 m, P6 5 m, P9 3.7 m, P14 tests 4.1 m, and the two full suites ≈ 8.4 m).
3. **Test-suite cost** is dominated by `test_r_analysis.py` (≈247 s above baseline, driving 530 tests to ~280 s) which drives the R workflow as a subprocess over synthetic data — appropriate for the coverage it buys.
4. No memory failure, no swap pressure, and no disk-space pressure (77 GB free). Peak artifacts: integrated 1.28 GB + feature-engineered 888 MB + DB 1.06 GB.
5. Efficiency: no meaningful, low-risk optimization was identified that would materially change correctness/reproducibility. The chunked streaming design is already in place in Phases 5/6/9/10; Phase 8 uses streaming accumulators. No change proposed (internship scope: no speculative optimization).
