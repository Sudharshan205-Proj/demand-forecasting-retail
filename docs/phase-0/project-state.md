# Project State

## Current Phase

Phase 17 — Testing, Documentation & Final Audit

Current audit target:

Phase 6 — Data Integration

## Overall Status

IN PROGRESS

## Completed Phases

- Phase 0 — Project Setup & Curriculum Audit
- Phase 1 — Business Understanding & Planning
- Phase 2 — Data Acquisition & Data Understanding
- Phase 3 — Spreadsheet-Based Analysis
- Phase 4 — SQL & Database Analysis
- Phase 5 — Data Cleaning & Quality Assurance
- Phase 6 — Data Integration
- Phase 7 — Exploratory Data Analysis
- Phase 8 — Statistical & Analytical Analysis
- Phase 9 — Time-Series Preparation
- Phase 10 — Feature Engineering
- Phase 11 — Forecasting Models
- Phase 12 — Model Evaluation & Tuning
- Phase 13 — Forecasting & Inventory Insights
- Phase 14 — R Analysis
- Phase 15 — Visualization & Tableau
- Phase 16 — Application Development & Deployment

## Remaining Phases

- Phase 17 — Testing, Documentation & Final Audit

Phase 17 is currently auditing completed phases individually. Phase 0 through Phase 5 have been re-audited and approved; Phase 6 has now been re-audited and is reported for the project owner's review.

## Git

Branch:

phase-17-testing-documentation-final-audit

HEAD:

365c6c1 — Phase 3 audit (Phase 0–3 audits committed; Phase 4 re-audit in progress)

Git status:

The Phase 6 re-audit modifies the Phase 6 documentation, its script and tests, and the tracking docs; `data/processed/integrated_retail_data.csv` and `data/processed/integration_quality_report.csv` are generated artifacts excluded from Git, and the stale `data/processed/integration_quality_report.json` was removed. The two reference documents (`AI_Phase_Based_Project_Development_Instructions(1).md` and `Internship Course Content Authority — Eight-Video Curriculum Guide.md`) remain untracked pending the project owner's decision.

Phase branch:

phase-17-testing-documentation-final-audit

## Files Created

Phase 0 established:

- README.md
- .gitignore
- requirements.txt
- pyproject.toml
- docs/phase-0/project-requirements.md
- docs/phase-0/project-plan.md
- docs/phase-0/curriculum-mapping.md
- docs/phase-0/architecture.md
- docs/phase-0/environment.md
- docs/phase-0/data-strategy.md
- docs/phase-0/reproducibility.md
- docs/phase-0/security.md
- docs/phase-0/project-state.md

The Phase 0 validation test (`tests/test_phase0_project_setup.py`) and the tracked data-directory placeholders (`data/raw/.gitkeep`, `data/processed/.gitkeep`, `data/interim/.gitkeep`, `data/external/.gitkeep`) form the Phase 0 setup-contract validation established as part of the Phase 17 audit work.

## Files Modified During Phase 0 Re-Audit

- README.md
- docs/phase-0/environment.md
- docs/phase-0/project-state.md
- docs/project-file-update-register.md
- tests/test_phase0_project_setup.py

No other project phase files are modified as part of the Phase 0 re-audit.

## Files Modified During Phase 1 Re-Audit

- .gitignore
- docs/phase-0/project-state.md
- docs/phase-0/curriculum-mapping.md
- docs/project-file-update-register.md
- docs/phase-1/decision-log.md
- docs/phase-1/hypothesis-register.md
- docs/phase-1/kpi-definitions.md
- docs/phase-1/requirements-traceability.md
- docs/phase-1/scope-and-assumptions.md
- docs/phase-1/stakeholder-analysis.md
- tests/test_phase1_business_understanding.py

The three reference documents were reviewed during the Phase 1 re-audit. `analytical-questions.md` and `phase-1-checklist.md` were verified and left unchanged; `requirements-traceability.md` received content-only corrections (phase references and stage status). All three remain reference-only files per the project owner's instruction: they are not to be committed or pushed in any phase.

## Files Modified During Phase 2 Re-Audit

- scripts/inspect_raw_data.py
- tests/test_inspect_raw_data.py
- docs/phase-2/data-acquisition.md
- docs/phase-2/data-dictionary.md
- docs/phase-2/dataset-inventory.md
- docs/phase-2/initial-data-assessment.md
- docs/phase-2/data-source-assessment.md
- docs/phase-2/data-ethics-and-privacy.md
- docs/phase-2/phase-2-checklist.md
- docs/phase-0/project-state.md
- docs/project-file-update-register.md
- docs/phase-0/curriculum-mapping.md

No raw data files are modified; the raw dataset remains immutable.

## Files Modified During Phase 3 Re-Audit

- docs/phase-3/spreadsheet-results.md
- docs/phase-3/phase-3-checklist.md
- docs/phase-3/course-content-coverage.md
- docs/phase-2/data-ethics-and-privacy.md (license confirmation text)
- docs/phase-0/project-state.md
- docs/project-file-update-register.md
- docs/phase-0/curriculum-mapping.md

The spreadsheet workbook is a reproducible generated artifact and is not source-controlled. No raw data files are modified.

## Files Modified During Phase 4 Re-Audit

- docs/phase-4/sql-results.md
- docs/phase-4/phase-4-checklist.md
- docs/phase-4/sql-analysis.md
- docs/phase-4/database-schema.md
- docs/phase-4/sql-analysis-plan.md
- docs/phase-4/course-content-coverage.md
- tests/test_sql_analysis.py
- docs/phase-0/project-state.md
- docs/project-file-update-register.md
- docs/phase-0/curriculum-mapping.md

The SQLite database and SQL query result files are reproducible generated artifacts and are not source-controlled. No raw data files are modified.

## Files Modified During Phase 5 Re-Audit

- scripts/clean_retail_data.py
- tests/test_clean_retail_data.py
- docs/phase-5/data-quality-results.md
- docs/phase-5/data-cleaning-methodology.md
- docs/phase-5/data-cleaning-plan.md
- docs/phase-5/data-quality-framework.md
- docs/phase-5/course-content-coverage.md
- docs/phase-5/phase-5-checklist.md
- docs/phase-4/sql-results.md
- docs/phase-0/project-state.md
- docs/phase-0/curriculum-mapping.md
- docs/project-file-update-register.md

The cleaned dataset and quality reports are reproducible generated artifacts and are not source-controlled. No raw data files are modified.

## Files Modified During Phase 6 Re-Audit

- scripts/integrate_retail_data.py
- tests/test_integrate_retail_data.py
- docs/phase-6/integration-results.md
- docs/phase-6/integration-methodology.md
- docs/phase-6/integration-quality-framework.md
- docs/phase-6/data-integration-plan.md
- docs/phase-6/course-content-coverage.md
- docs/phase-6/phase-6-checklist.md
- docs/phase-1/requirements-traceability.md
- docs/phase-2/dataset-inventory.md
- docs/phase-0/project-state.md
- docs/phase-0/curriculum-mapping.md
- docs/project-file-update-register.md

The integrated dataset and its quality report are reproducible generated artifacts and are not source-controlled. No raw data files are modified.

## Important Decisions

- The project uses the six-stage Ask/Prepare/Process/Analyze/Share/Act methodology.
- ARIMA is mandatory.
- Prophet or LSTM may be evaluated rather than installed unnecessarily at setup time.
- RMSE and MAPE are used for forecast evaluation.
- Time-aware validation is required.
- Course concepts require actual project evidence.
- Security and reproducibility are maintained throughout the project.
- Git branches correspond to phases.
- One logical commit is normally used per phase.
- The Phase 0 audit does not globally mark curriculum topics as implemented; evidence status must remain tied to actual phase evidence.

## Dependencies

Initial Python dependencies:

- numpy
- pandas
- matplotlib
- scipy
- scikit-learn
- statsmodels
- openpyxl
- jupyter
- pytest

The existing dependency set was retained during the Phase 0 audit because dependency removal would require a project-wide audit rather than a Phase 0-only audit.

## Dataset

Status:

ACQUIRED AND USED BY LATER PROJECT PHASES; raw and generated data are excluded from Git according to the repository data policy.

Phase 0 itself does not acquire or transform the dataset.

## Models

Status:

IMPLEMENTED IN LATER PROJECT PHASES

Phase 0 only establishes the forecasting/model strategy.

## Application

Status:

IMPLEMENTED IN PHASE 16

Phase 0 only establishes the application/deployment direction.

## Deployment

Status:

IMPLEMENTED AND VALIDATED IN PHASE 16 ACCORDING TO THE COMPLETED PHASE 16 PROJECT STATE

Phase 0 does not audit deployment behavior.

## Documentation

Phase 0 documentation:

AUDITED

The README project-status table, environment version record, project-state record and project file-update register were corrected during the Phase 0 re-audit so the setup documentation matches the actual repository and environment. The curriculum mapping remains evidence-driven and was not globally rewritten.

Phase 1 documentation:

AUDITED — COMPLETE

The Phase 1 planning documents were reviewed against the completed project. The decision log, requirements traceability, scope and assumptions, KPI definitions and stakeholder validation statements were corrected where they had become stale relative to the completed dataset and forecasting phases.

Phase 2 documentation:

AUDITED — COMPLETE

The Phase 2 data acquisition and understanding documentation was brought in line with the actual verified raw dataset. The documentation now records all eight raw files, verified dimensions, data types, missing values, duplicates, date ranges, store/product counts, structural file characteristics and known data-quality concerns. The dataset license was confirmed as CC BY-NC-SA 4.0 and recorded.

Phase 3 documentation:

AUDITED — COMPLETE

The Phase 3 spreadsheet documentation was reviewed against the regenerated workbook. The results document was populated with verified analytical findings (761 daily records, 4-store summary, 28,182-item summary, formula and validation details) and the course-content coverage chart was corrected to the project's actual phase numbering (R, Visualization, Tableau, Forecasting).

Phase 4 documentation:

AUDITED — COMPLETE

The Phase 4 SQL documentation was reviewed against the rebuilt database and re-executed queries. The results document was populated with verified table row counts, the 18 query summaries and the Query 17 data-coverage finding; the schema plan and course-content coverage received re-audit records confirming execution.

Phase 5 documentation:

AUDITED — COMPLETE

The Phase 5 documentation was brought in line with the executed pipeline. The results document was populated with verified execution figures, the methodology recorded the catalog reference check, the valid-date coverage and the chunk-local duplicate-detection limitation, the plan and quality framework received re-audit records, the course-content coverage mapped the Course 4 SQL topics to their Phase 4 evidence, and the checklist was completed.

Phase 6 documentation:

AUDITED — COMPLETE

The Phase 6 documentation was brought in line with the executed pipeline. The results document was populated with verified input/output figures and validation results, the methodology recorded the same-day price-event tie-break and the measured exactness of the chunked aggregation, the plan, quality framework and course-content coverage received re-audit records, and the checklist was completed.

## Tests

Phase 0 validation:

VERIFIED — 6 TESTS PASS

The Phase 0 validation test verifies the setup contract: required files, data-directory placeholders, .gitignore rules, declared dependencies, pytest configuration and non-empty Phase 0 documentation.

Phase 1 validation:

VERIFIED — 5 TESTS PASS

The Phase 1 validation test verifies the required documents exist and are non-empty, the business problem contains its scope boundary, the decision log preserves temporal and evidence constraints, the requirements cover the internship forecasting scope, and the KPI definitions document the zero-safe MAPE limitation. The decision-log assertion was updated to reflect the D004 `RESOLVED` status.

Phase 2 validation:

VERIFIED — 6 TESTS PASS

The Phase 2 validation test verifies the raw-data inspection utilities: basic structure and duplicate reporting, missing-value and invalid-date counting, unnamed-index-column detection, ragged-line (unquoted comma) reporting, non-CSV rejection, and empty-directory rejection. The inspection script now completes successfully on the full raw dataset.

Phase 3 validation:

VERIFIED — 10 TESTS PASS

The Phase 3 validation test verifies the spreadsheet pipeline: store lookup loading, required workbook sheets, required course formulas, exact aggregation across chunk boundaries, invalid-date exclusion from the daily sheet only, table-reference handling, autofilter/table conflicts, VLOOKUP store-cell targets, bounded validation references, and the dynamic (non-hardcoded) store-selection dropdown.

Phase 4 validation:

VERIFIED — 11 TESTS PASS

The Phase 4 validation verifies SQLite schema creation, row counting and aggregation (database tests), plus SQL analytical patterns (GROUP BY, joins, HAVING, subqueries, CTEs) and the SQL runner's query parser and missing-file handling (9 original + 2 QA-added tests).

Phase 5 validation:

VERIFIED — 19 TESTS PASS

The Phase 5 validation verifies required-column handling, store-id loading, negative quantity/price/revenue detection, invalid-date detection, unknown-store detection, revenue-mismatch reporting, record retention, duplicate detection, non-numeric coercion, the new catalog reference check, valid-date coverage, catalog-id loading, full cross-chunk pipeline output (single header, correct rows, reports written) and missing-sales-file handling (11 original + 8 audit-added tests).

Phase 6 validation:

VERIFIED — 22 TESTS PASS

The Phase 6 validation covers key normalisation and required-column handling plus the previously untested integration core: catalog and store dimension deduplication, price-history event aggregation, markdown discount calculation, promotion aggregation, online-channel aggregation, the actual-matrix indicator, end-to-end `build_integration` row preservation and grain uniqueness (including unmatched-catalog retention, online/physical separation and the new validation metrics), the many-to-one row-multiplication guard, and missing-source-file handling (13 original, one vacuous test replaced, 9 tests added).

## Known Issues

- The repository's original Phase 0 commit did not contain the Phase 0 test source even though a compiled `test_phase0_project_setup` bytecode artifact existed locally.
- The original Phase 0 documentation was stale in several places relative to the completed project state; the re-audit corrected the README status table, environment versions, project-state HEAD record and file-update register.
- Exact RStudio and Tableau Public versions are not recorded.
- BigQuery is not required by the current project implementation.
- Two reference documents (`AI_Phase_Based_Project_Development_Instructions(1).md` and `Internship Course Content Authority — Eight-Video Curriculum Guide.md`) remain untracked pending the project owner's decision on whether they should be source-controlled.
- Phase 17 must continue to audit later phases individually; this Phase 0 re-audit does not certify them.
- The Phase 5 checklist Git items are retained as the original phase record and are not re-asserted by the Phase 17 audit, which performs no Git operations.

## Unresolved Decisions

- Final presentation/portfolio packaging remains part of the final project work.
- Any deployment-platform-specific operational details are outside the Phase 0 audit scope.
- Global curriculum status will be finalized only as each corresponding phase is audited and its evidence is verified.
- Whether to source-control the two reference documents listed under Known Issues.

## Phase 0 Audit Status

AUDITED

The Phase 0 setup contract, planning documentation, environment record, repository structure, security rules, reproducibility requirements and curriculum-mapping role were reviewed. No Phase 0 forecasting, data-processing or application implementation exists to execute; the phase is principally a setup/documentation phase.

## Phase 1 Re-Audit Status

Phase 1 — Business Understanding & Planning has been re-audited as part of Phase 17.

AUDITED — COMPLETE

The Phase 1 re-audit verified the business problem, stakeholders, analytical questions, hypotheses, KPIs, scope, assumptions, requirements and decision log against the completed project. The decision-log entry D004 was updated from `PENDING DATASET REVIEW` to `RESOLVED` because the dataset review and model decision were completed in the forecasting phases (Phase 11 implemented naive, seasonal-naive and ARIMA(1,1,1)). Phase-reference errors in the requirements traceability were corrected, and forecasting-unit, forecast-horizon, constraint and KPI statements that had become stale relative to the completed phases were revised. The application of the decision-log phrase "PENDING DATASET REVIEW" in the Phase 1 test was updated accordingly.

## Phase 2 Re-Audit Status

Phase 2 — Data Acquisition & Data Understanding has been re-audited as part of Phase 17.

AUDITED — COMPLETE

The Phase 2 re-audit verified the raw dataset and made the inspection script robust to the dataset's actual structural characteristics (leading unnamed index column on every file, UTF-8 BOM and unquoted commas inside text fields in `catalog.csv`). The script was re-executed successfully over the full 824 MB dataset and its verified output was used to populate the Phase 2 documentation. The documentation previously listed only four raw files; the actual raw directory contains eight, and all eight are now recorded with verified statistics. Known data-quality concerns (negative quantities in sales, duplicate rows in markdowns/price_history, future-dated discount records, catalog gaps) are documented for the downstream cleaning and integration phases.

The dataset license was confirmed by the project owner as CC BY-NC-SA 4.0 and is recorded in the Phase 2 documentation.

## Phase 3 Re-Audit Status

Phase 3 — Spreadsheet-Based Analysis has been re-audited as part of Phase 17.

AUDITED — COMPLETE

The Phase 3 re-audit reviewed the spreadsheet pipeline against the actual workbook. The regeneration script was re-executed successfully and its output was programmatically compared with the committed workbook: identical sheets, dimensions, record counts (761 daily, 4 store, 28,182 items), totals and key values. The results documentation was populated with the verified findings, the course-content coverage chart was corrected to the project's actual phase numbering, and the phase checklist was verified. The workbook is treated as a reproducible generated artifact and is no longer tracked in Git.

## Phase 4 Re-Audit Status

Phase 4 — SQL & Database Analysis has been re-audited as part of Phase 17.

AUDITED — COMPLETE

The Phase 4 re-audit rebuilt the SQLite database from the Phase 2 raw files and re-executed all 18 SQL analysis queries. Verified row counts match the Phase 2 facts (stores 4, catalog 219,810, sales 7,432,685, markdowns 8,979, price_history 698,626; sales date range 2022-08-28 to 2024-09-26). Two QA tests were added (SQL query parser + missing-input handling; 9 → 11 tests). A genuine data-coverage finding was documented: 36,585 sales rows (948 distinct items) have no matching catalog record (Query 17). The database and query results remain untracked generated artifacts.

## Phase 5 Re-Audit Status

Phase 5 — Data Cleaning & Quality Assurance has been re-audited as part of Phase 17.

AUDITED — COMPLETE

The Phase 5 cleaning pipeline was re-executed over the complete raw dataset (113 seconds) and its three generated artifacts were inspected. Two checks that the phase plan and quality framework required were implemented (catalog-membership reference check; valid-date coverage), and the cleaning-summary "rows removed" reporting was corrected to `rows read - rows written` (1,659) while the previous overlapping rule count (2,837) is retained as a labelled diagnostic. The cleaning rules and the retained row set are unchanged (7,432,685 read, 7,431,026 written). The catalog gap (36,585 raw / 36,580 cleaned; 948 distinct items) reconciles with Phase 4 and Phase 6, and valid-date coverage (2022-08-28 to 2024-09-26) reconciles with Phase 2 and Phase 4. Phase 5 tests increased from 11 to 19 and the full suite passes (160 tests).

## Phase 6 Re-Audit Status

Phase 6 — Data Integration has been re-audited as part of Phase 17.

AUDITED — COMPLETE

The Phase 6 integration pipeline was re-executed over the complete dataset (350 seconds) and produced a byte-identical 1,283,886,539-byte output with 7,431,026 rows. Independent output validation confirmed row preservation and canonical-grain uniqueness (0 duplicates), unknown stores (0) and 36,580 unmatched catalog rows (reconciling with the Phase 4 raw count of 36,585). The stale, unreproducible `integration_quality_report.json` was removed and its validation metrics folded into the CSV report (date coverage 2022-08-28 to 2024-09-26; 28,180 unique items; 4 stores; total demand 41,949,529.91; total sales revenue 5,659,219,309.90). The chunked aggregation was measured to be numerically exact (no key spans a chunk; maximum difference 0.0). Phase 6 tests increased from 13 to 22 and the full suite passes (169 tests).

The next Phase 17 audit target is Phase 7.