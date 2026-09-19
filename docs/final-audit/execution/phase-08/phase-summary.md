# Phase 8 — Statistical & Analytical Analysis

## Purpose
Statistical evidence track: descriptive statistics, promotion comparison, trend with HAC inference, correlations, autocorrelation, category/store analyses, monthly activity diagnosis.

## Starting State
Phase 7 PASSED.

## Inputs
`data/processed/integrated_retail_data.csv` (byte-identical to baseline).

## Commands Executed
- CMD-P8-01: `.venv/Scripts/python.exe scripts/statistical_analytical_analysis.py` — exit 0, **0m 56.3s** (documented ~41 s; same order), empty stderr. Evidence: `command-001-stdout.txt`.
- CMD-P8-02: `pytest tests/test_statistical_analytical_analysis.py -q -p no:cacheprovider` — exit 0, **46 passed**, 10.96 s. Evidence: `command-002.txt`.

## Tests
46/46 PASSED (matches documented count of 46).

## Artifacts
`data/analysis/statistical_*.csv` + `statistical_findings.txt` regenerated; `reports/figures/statistical_*.png` regenerated.

## Expected Results
Per docs: streaming accumulators (no sampled statistics), presence-based promotion comparison, Newey-West trend inference, 46 tests.

## Actual Results
exit 0; findings/summary regenerated; tests pass. Methodology claims (streaming, HAC) are additionally locked by the passing test suite, which asserts the quality framework.

## Discrepancies
None.

## Changes
None.

## Regression Checks
Consumes the byte-identical integrated dataset; outputs reconcile with Phase 7 (price coefficient agreement verified in the Phase 7 summary).

## Final Status
PASSED
