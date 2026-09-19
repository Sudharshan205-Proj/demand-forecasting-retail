# Baseline Audit — Evidence

All commands run 2026-09-19 from the repository root, before any project modification.

## CMD-B01 — Python package versions

- Command: `.venv/Scripts/python.exe -m pip list --format=freeze`
- Exit code: 0
- Evidence: `baseline-pip-freeze.txt` (137 packages)
- Key pins match `requirements.txt` exactly: numpy 2.5.2, pandas 3.0.5, matplotlib 3.11.1, scipy 1.18.1, scikit-learn 1.9.0, statsmodels 0.15.0, streamlit 1.63.0, openpyxl 3.1.5, jupyter 1.1.1, pytest 9.1.1.
- Streamlit import check: `streamlit importable 1.63.0`.

## CMD-B02 — Baseline checksums + file inventory

- Command: `.venv/Scripts/python.exe docs/final-audit/execution/audit_baseline_helper.py`
- First run FAILED (exit 1): `ROOT` resolved to `docs/docs/final-audit/...` — the helper's own path bug (three `dirname` levels instead of four). Fixed in the helper (not a project file), re-run.
- Second run: exit 0, completed 2026-09-19T12:57:38.
- Evidence: `baseline-checksums.tsv` (124 hashed artifacts + header), `baseline-inventory.tsv` (308 files + header).
- One DeprecationWarning in the helper (utcfromtimestamp) — audit tooling only, not project code.

## CMD-B03 — Static compile check

- Command: `.venv/Scripts/python.exe -m py_compile scripts/*.py app/*.py`
- Exit code: 0 — all 15 scripts and 5 application modules compile.

## CMD-B04 — Tableau workbook schema check

- Command: `.venv/Scripts/python.exe scripts/sync_tableau_workbook_schema.py --check`
- Exit code: 0. Output: "Workbook schema already matches its sources." (13/8/10 columns reconciled across the three sources).

## CMD-B05 — Baseline full test suite

- Command: `time .venv/Scripts/python.exe -m pytest -q > baseline-pytest-full.txt 2>&1`
- Exit code: 0
- Result: **530 passed, 1 warning in 223.58s (0:03:43)**
- Warning (benign, from `scripts/clean_retail_data.py:127`): pandas `to_datetime` format-inference fallback in the *test fixture path*; noted for the Phase 5 audit.
- Full output: `baseline-pytest-full.txt`

## Baseline verdict

- Environment: VERIFIED (versions match the pinned requirements exactly).
- Static checks: PASSED (compile + workbook schema).
- Test suite: PASSED at baseline — 530/530. The Phase 17 self-audit's claim is reproduced by independent execution.
- Inventory classification counts: documentation 125, generated-analysis 94, test 18, source-script 15, report 9, raw-data 8 (+1 header row), generated-processed 8, deployment 8, application 6, unknown 5 (helper + .gitkeep + root md files), configuration 4, tableau 3, sql 2, r-analysis 2.
