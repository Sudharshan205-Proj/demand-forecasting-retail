# Phase 5 — Data Cleaning & Quality Assurance

## Purpose
Clean raw sales data (deduplication, invalid dates, negative quantities, catalog reference checks) into `data/processed/sales_clean.csv` with quality reports.

## Starting State
Phase 4 PASSED; raw checksums unchanged; prior sales_clean from 2026-09-18.

## Inputs
`data/raw/sales.csv`, `data/raw/catalog.csv` (immutable).

## Commands Executed
- CMD-P5-01: `.venv/Scripts/python.exe scripts/clean_retail_data.py` — exit 0, **2m 21.6s**, empty stderr. Verified printed facts: Rows read 7,432,685; Rows written 7,431,026; Unmatched catalog rows 36,585; dates 2022-08-28 → 2024-09-26. Evidence: `command-001-stdout.txt`.
- CMD-P5-02: `pytest tests/test_clean_retail_data.py -q -p no:cacheprovider` — exit 0, **19 passed**, 1 warning (the pre-existing pandas `to_datetime` format-inference UserWarning, benign), 1.32 s. Evidence: `command-002.txt`.
- CMD-P5-03: SHA-256 of regenerated `sales_clean.csv` = `5d99cc856395887a7fcdcb81408f3aef97f1e3735b8a6939e8959bf1e8216d7d` — **byte-identical to the baseline checksum**. Determinism proven.

## Tests
19/19 PASSED (matches documented count of 19 — DOC list consistent).

## Artifacts
`data/processed/sales_clean.csv` (322,801,399 B, byte-identical), `data_quality_report.csv`, `cleaning_summary.csv` (regenerated).

## Expected Results
7,432,685 → 7,431,026 rows; ~113 s documented runtime (this run 2m22s — same order, machine-load dependent); 19 tests.

## Actual Results
Exact row-count match; byte-identical output; tests pass.

## Discrepancies
None (runtime variance only, expected).

## Changes
None.

## Regression Checks
Raw checksums unchanged; downstream integration re-executed next (Phase 6) and reconciled.

## Final Status
PASSED
