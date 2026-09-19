# Phase 14 — R Analysis

## Purpose
Independent R track: cross-language verification of the Phase 12/13 analytical outputs, an R Markdown report, and an R environment record. Runs through `Rscript` (no `.Rproj` committed).

## Starting State
Phase 13 PASSED with regenerated inventory artifacts.

## Inputs
Phase 12/13 analytical CSVs under `data/analysis/`; `r/r_analysis.R`, `r/r_analysis_report.Rmd`.

## Commands Executed
- CMD-P14-01: `Rscript r/r_analysis.R` — exit 0, **16.3 s**, stderr empty. Output: "Phase 14 R analysis completed successfully. Quality checks passed: **91 of 91**." Evidence: `command-001-stdout.txt`.
- CMD-P14-02: `Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(),'data','analysis','r'))"` — exit 0, **20.6 s**. 43/43 chunks processed including the `[quality-gate]` chunk; "Output created: data/analysis/r/r_analysis_report.html". Evidence: `command-002-stdout.txt`; one pandoc toolchain deprecation WARNING (`--mathjax`) recorded in `command-002-stderr.txt` — cosmetic, external to the project.
- CMD-P14-03: `pytest tests/test_r_analysis.py -q -p no:cacheprovider` — exit 0, **36 passed**, 246.95 s. Evidence: `command-003.txt`.

## Tests
36/36 PASSED (matches documented 36). Drives the R workflow as a subprocess over synthetic inputs, covering the success path, twelve deliberate-failure paths, structural guarantees and the report gate.

## Artifacts
Regenerated in `data/analysis/r/`: 91-check `r_analysis_quality_report.csv`, `r_analysis_findings.txt`, `r_environment.csv` (R 4.6.1, pandoc 3.11, tidyverse 2.0.0, tidymodels 1.5.0, yardstick 1.4.0, knitr 1.52, rmarkdown 2.32), scenario CSVs, `plots/`, and `r_analysis_report.html` (1,430,678 B, 2026-09-19 14:29 — post-dates its `.Rmd` source, closing the staleness defect recorded by the project's own audit).

## Expected Results
Per docs: 91/91 checks; report renders only when the gate passes; R/pandoc/package versions recorded; 36 tests.

## Actual Results
Exactly as documented. 91/91 checks; report rendered after the gate; environment recorded; RStudio not evidenced (workflow runs via `Rscript`), as the docs state.

## Discrepancies
None. (Cosmetic pandoc `--mathjax` deprecation warning noted.)

## Changes
None.

## Regression Checks
Reconciles Phase 12/13 metrics in `yardstick` within floating-point precision (asserted by the passing tests); HTML staleness defect from the earlier self-audit is now verifiably resolved by regeneration.

## Final Status
PASSED
