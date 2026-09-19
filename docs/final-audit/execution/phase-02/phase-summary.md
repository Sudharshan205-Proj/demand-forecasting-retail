# Phase 2 — Data Acquisition & Data Understanding

## Purpose
Inspect the raw dataset (8 files, ~824 MB) and record structure, schemas, missing values, duplicates, date ranges and identifiers. `inspect_raw_data.py` is the phase's executable evidence.

## Starting State
Phase 1 PASSED. Raw files present (baseline checksums recorded).

## Inputs
`data/raw/*.csv` (8 files).

## Commands Executed
- CMD-P2-01: `.venv/Scripts/python.exe scripts/inspect_raw_data.py` — exit 0. Complete stdout in `command-001-stdout.txt` (210 lines), stderr empty in `command-001-stderr.txt`. Duration ~1–2 min (824 MB parsed).
- CMD-P2-02: `pytest tests/test_inspect_raw_data.py -q -p no:cacheprovider` — exit 0, 6 passed, 3.64 s (`command-002.txt`).

## Tests
6/6 PASSED.

## Artifacts
No new artifacts (inspection prints to stdout). Raw-file facts re-verified: sales date range 2022-08-28 → 2024-09-26; 4 stores; unique item ids in catalog/sales; invalid dates 0.

## Expected Results
Per docs: 8 raw files recorded with verified dimensions; sales 7,432,685 rows; stores 4; invalid dates 0.

## Actual Results
exit 0, empty stderr. Observed facts include: DATE MIN 2022-08-28, DATE MAX 2024-09-26, INVALID DATE VALUES 0, UNIQUE store_id 4, item_id 28,182 (catalog). Consistent with documented facts. Full per-file detail preserved in the stdout capture.

## Discrepancies
None observed.

## Changes
None.

## Regression Checks
Not applicable (no modification). Raw-data checksums re-verified unchanged after the run.

## Final Status
PASSED
