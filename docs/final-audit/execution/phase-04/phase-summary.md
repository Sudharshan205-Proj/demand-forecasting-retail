# Phase 4 — SQL & Database Analysis

## Purpose
Database evidence track: rebuild the SQLite database from raw files and execute the 18 documented SQL analysis queries to CSV results.

## Starting State
Phase 3 PASSED; prior DB and results were 2026-09-16 vintage (regenerated now).

## Inputs
`data/raw/{sales,catalog,stores,markdowns,price_history}.csv`.

## Commands Executed
- CMD-P4-01: `.venv/Scripts/python.exe scripts/create_sqlite_database.py` — exit 0, empty stderr. Verified printed row counts: stores 4; catalog 219,810; sales 7,432,685; markdowns 8,979; price_history 698,626. Evidence: `command-001-stdout.txt`.
- CMD-P4-02: `.venv/Scripts/python.exe scripts/run_sql_analysis.py` — **exit 0 after 22m 06s** (single blocking run). Output ends: "SQL analysis completed successfully. Generated 18 result files." 18 CSVs written to `data/analysis/sql_results/`. Evidence: `command-002-stdout.txt` (complete), `command-002-stderr.txt` (empty).
  - Execution note: a first foreground attempt hit the audit harness's 600 s limit and was killed mid-query-10 (no artifact corruption; queries are written per-file). A background `nohup` attempt died with its shell (Git Bash child kill on session close) — audit-tooling limitation recorded in `command-log.md`. The successful run used an unbounded blocking timeout.
- CMD-P4-03: `pytest tests/test_sql_analysis.py -q -p no:cacheprovider` — exit 0, **8 passed**, 0.83 s. Evidence: `command-003.txt`.
- CMD-P4-04 (independent spot check): direct sqlite3 queries against the rebuilt DB — `sales_rows = 7,432,685`; `sales_dates = 2022-08-28 → 2024-09-26`; raw `SUM(quantity) = 41,938,165.205`; raw `SUM(sum_total) = 5,658,351,680.71`; `store_count = 4`. Evidence: `command-004-spotcheck.txt` (includes one failed first attempt due to an auditor's wrong column-name guess, `total_sales` vs actual `sum_total`, then corrected).

## Tests
8/8 PASSED (schema creation, row counts, aggregation patterns, parser, missing-input handling).

## Artifacts
`data/analysis/retail_demand.db` (rebuilt); `data/analysis/sql_results/query_1..18.csv` (all regenerated 2026-09-19).

## Expected Results
Per docs: DB row counts as above; 18 queries; Query 17 catalog-gap finding; 11 documented tests.

## Actual Results
All row counts exact; 18/18 result files; spot-check reconciles with Phase 2/6 facts. Raw quantity/revenue totals (41,938,165.205 / 5,658,351,680.71) are *below* the cleaned totals (41,949,529.910 / 5,659,219,309.90) because cleaning removes negative-quantity rows — directionally consistent, reconciled. **Discrepancy (documentation only): 8 tests passed vs 11 documented** — DOC-03 (Documentation, Low).

## Discrepancies
DOC-03 (Documentation, Low): Phase 4 test count stale (11 documented vs 8 executed).

## Changes
None to project code.

## Regression Checks
Raw-data checksums unchanged after DB rebuild (raw immutability confirmed).

## Final Status
PASSED
