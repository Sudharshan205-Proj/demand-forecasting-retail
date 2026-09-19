# Phase 15 — Visualization & Tableau

## Purpose
Static figures and their gated metadata (55-check quality report + SHA-256 manifest), plus the committed Tableau workbook schema reconciliation.

## Starting State
Phase 14 PASSED; Phase 12/13 analytical outputs regenerated.

## Inputs
Five Phase 12/13 analytical CSVs (demand, variability, scenarios, insights, validation results).

## Commands Executed
- CMD-P15-01: `.venv/Scripts/python.exe scripts/create_visualizations.py` — exit 0, **8.9 s**, empty stderr. Output: "Phase 15 visualizations completed successfully (**55 of 55 checks**)." Evidence: `command-001-stdout.txt`.
- CMD-P15-02: `.venv/Scripts/python.exe scripts/sync_tableau_workbook_schema.py --check` — exit 0. "Workbook schema already matches its sources." (13/8/10 columns reconciled; unchanged). Evidence: `command-002-stdout.txt`.
- CMD-P15-03: `pytest tests/test_create_visualizations.py -q -p no:cacheprovider` — exit 0, **32 passed**, 51.67 s. Evidence: `command-003.txt`.
- CMD-P15-04 (independent manifest audit): re-hashed all 4 figures against `visualization_manifest.csv` — **byte size + SHA-256 match: True** (one auditor column-name error corrected first; recorded). Evidence: `command-004-manifest-check.txt`.

## Tests
32/32 PASSED (matches documented 32), including six subprocess failure paths that must withhold every figure.

## Artifacts
`data/analysis/visualizations/*.png` (4 figures: store_average_daily_demand, store_demand_variability, reorder_point_by_lead_time, lowest_validation_rmse — 32,067 / 36,079 / 103,628 / 43,048 B), `visualization_quality_report.csv` (55/55), `visualization_manifest.csv`.

## Expected Results
Per docs: 55/55 checks; 4 figures; manifest records byte size and SHA-256; workbook schema matches current CSV headers.

## Actual Results
All confirmed. Manifest digests independently re-verified against the files on disk.

## Discrepancies
None. Published Tableau Public dashboard URL resolves HTTP 200 but reflects the 8 September 2026 extract (already documented as a limitation; refresh requires Tableau Desktop — see link-audit.md).

## Changes
None.

## Regression Checks
Consumes Phase 12/13 outputs; workbook schema check confirms no drift after the full pipeline re-run.

## Final Status
PASSED
