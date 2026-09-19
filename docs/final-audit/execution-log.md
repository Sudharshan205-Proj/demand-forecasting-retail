# Execution Log

Chronological record of the audit's execution. Complete stdout/stderr are preserved under `execution/phase-NN/`; this log records commands, exit codes, test counts, artifacts and validation outcomes. Commands are enumerated in `command-log.md`.

## Baseline (2026-09-19, before any pipeline execution)

| Step | Exit | Outcome |
|---|---|---|
| Environment verification | 0 | Python 3.12.10, R 4.6.1, SQLite 3.53.4, Git `main` @ `e5a750f`; 10/10 pins match |
| Compile check (20 modules) | 0 | all compile |
| Tableau schema check | 0 | matches sources |
| Inventory + checksums | 0 | 308 files classified; 124 artifacts hashed |
| Full test suite | 0 | **530 passed, 1 warning, 223.58 s** |

## Phase execution

| Phase | Command exit | Tests (passed/total) | Quality gate | Artifacts validated | Status |
|---|---|---|---|---|---|
| 0 | 0 (tests only) | 6/6 | n/a | contract files | PASSED |
| 1 | 0 (tests only) | 5/5 | n/a | planning docs | PASSED |
| 2 | 0 | 6/6 | n/a | 8 raw files inspected | PASSED |
| 3 | 0 | 12/12 | n/a | workbook 761/4/28,182 | PASSED |
| 4 | 0 | 8/8 | n/a | DB + 18 query CSVs; spot-check | PASSED |
| 5 | 0 | 19/19 | n/a | sales_clean byte-identical | PASSED |
| 6 | 0 | 24/24 | n/a | integrated byte-identical | PASSED |
| 7 | 0 | 34/34 | n/a | EDA exact reconciliation | PASSED |
| 8 | 0 | 46/46 | n/a | statistical outputs | PASSED |
| 9 | 0 | 37/37 | **15/15** | time_series byte-identical | PASSED |
| 10 | 0 | 32/32 | **14/14** | features byte-identical | PASSED |
| 11 | 0 | 52/52 | **24/24** | 1,368 predictions to 2024-06-03 | PASSED |
| 12 | 0 | 64/64 | **30/30** | 2,976 predictions; mean RMSE 3,079.4286 | PASSED |
| 13 | 0 | 78/78 | **43/43** | densified 1,656; bias 1,409.941 | PASSED |
| 14 | 0 | 36/36 | **91/91** | report rendered; env recorded | PASSED |
| 15 | 0 | 32/32 | **55/55** | 4 figures; manifest verified | PASSED |
| 16 | 0 | 36/36 | n/a | HTTP 200; bundle reconciled | PASSED |
| 17 | 0 | **530/530** full suite | n/a | drift report: 120/124 identical | PASSED |

Totals: **18 phases executed; 530 tests passed; 0 failed; 0 skipped; quality gates 272/272 checks passed** (15+14+24+30+43+91+55).

## Mid-run events

- CMD-P4-02 first attempt killed at 600 s (queries 1–9 complete) — re-run to completion (22 m 06 s), 18/18 results.
- Background `nohup` retry died with its shell — resolved by an unbounded blocking run.
- CMD-P16-01 first launch failed on shell quoting — resolved with `start_app.ps1` (detached), HTTP 200 confirmed, app stopped, port released.

## Notes

- No command produced a non-zero exit once properly invoked; no pipeline warning other than the pre-existing pandas `to_datetime` format-inference UserWarning inside the Phase 5 test fixture, plus one cosmetic pandoc `--mathjax` deprecation warning during the R Markdown render.
- Every phase's complete stdout/stderr is on disk; nothing was truncated.
