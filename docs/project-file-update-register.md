# Project File Update Register

## Purpose

This document records which project files are expected to be created or modified during each phase.

The register must be updated at the end of every phase.

A file should only be listed as modified when the phase actually requires a change.

---

## Phase 0 — Project Setup & Curriculum Audit

### Files created

- `README.md`
- `.gitignore`
- `requirements.txt`
- `pyproject.toml`
- `docs/phase-0/project-requirements.md`
- `docs/phase-0/project-plan.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-0/architecture.md`
- `docs/phase-0/environment.md`
- `docs/phase-0/data-strategy.md`
- `docs/phase-0/reproducibility.md`
- `docs/phase-0/security.md`
- `docs/phase-0/project-state.md`

### Files modified

None reported at the end of Phase 0.

### Phase 17 audit modifications

- `README.md`
- `docs/phase-0/environment.md`
- `docs/phase-0/project-state.md`
- `docs/project-file-update-register.md`
- `tests/test_phase0_project_setup.py`

These changes are part of the Phase 17 re-audit of Phase 0 and correct documentation that had become stale relative to the completed project state.

---

## Phase 1 — Business Understanding & Planning

### Files created

- `docs/phase-1/analytical-questions.md`
- `docs/phase-1/business-problem.md`
- `docs/phase-1/business-requirements.md`
- `docs/phase-1/decision-log.md`
- `docs/phase-1/hypothesis-register.md`
- `docs/phase-1/kpi-definitions.md`
- `docs/phase-1/phase-1-checklist.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-1/scope-and-assumptions.md`
- `docs/phase-1/stakeholder-analysis.md`

### Files modified during Phase 1 implementation

None. The implementation phase created documentation only.

### Phase 17 audit modifications

- `docs/phase-1/decision-log.md`
- `docs/phase-1/hypothesis-register.md`
- `docs/phase-1/kpi-definitions.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-1/scope-and-assumptions.md`
- `docs/phase-1/stakeholder-analysis.md`
- `tests/test_phase1_business_understanding.py`

### Reference-only files

The following Phase 1 documents are local reference files only and are not committed or pushed in any phase:

- `docs/phase-1/analytical-questions.md`
- `docs/phase-1/phase-1-checklist.md`
- `docs/phase-1/requirements-traceability.md`

During the Phase 1 re-audit, `requirements-traceability.md` received content-only corrections but remains a reference-only file.

### Existing files requiring synchronization

- `README.md`
- `docs/phase-0/project-state.md`
- `docs/project-file-update-register.md`

These synchronization changes are recorded as part of the Phase 17 audit and do not alter the Phase 1 implementation architecture.

---

## Phase 2 — Data Acquisition & Data Understanding

### New files

- `docs/phase-2/data-acquisition.md`
- `docs/phase-2/data-source-assessment.md`
- `docs/phase-2/data-dictionary.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-2/data-ethics-and-privacy.md`
- `docs/phase-2/initial-data-assessment.md`
- `docs/phase-2/phase-2-checklist.md`
- `docs/project-file-update-register.md`
- `scripts/inspect_raw_data.py`
- `tests/test_inspect_raw_data.py`

### Existing files to update

- `README.md`
- `docs/phase-0/project-state.md`

### Raw data files

Expected locally but intentionally excluded from Git:

- `data/raw/sales.csv`
- `data/raw/online.csv`
- `data/raw/markdowns.csv`
- `data/raw/price_history.csv`

### End-of-phase status

VERIFIED — all eight raw files acquired, inspected and documented during the Phase 17 re-audit.

### Phase 17 audit modifications

- `scripts/inspect_raw_data.py`
- `tests/test_inspect_raw_data.py`
- `docs/phase-2/data-acquisition.md`
- `docs/phase-2/data-dictionary.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-2/initial-data-assessment.md`
- `docs/phase-2/data-source-assessment.md`
- `docs/phase-2/data-ethics-and-privacy.md`
- `docs/phase-2/phase-2-checklist.md`
- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/project-file-update-register.md`

The re-audit corrected the inspection script so it handles the dataset's structural characteristics (unnamed index column, BOM, unquoted commas in catalog text fields) and populated the documentation with verified statistics. The dataset license remains to be confirmed manually on Kaggle.

---

## Phase 3 — Spreadsheet-Based Analysis

### New files

- `docs/phase-3/spreadsheet-analysis.md`
- `docs/phase-3/spreadsheet-methodology.md`
- `docs/phase-3/course-content-coverage.md`
- `docs/phase-3/spreadsheet-results.md`
- `docs/phase-3/phase-3-checklist.md`
- `scripts/create_spreadsheet_analysis.py`
- `tests/test_create_spreadsheet_analysis.py`

### Existing files to update

- `README.md`
- `docs/phase-0/project-state.md`
- `docs/project-file-update-register.md`

### Generated local artifacts

- `data/analysis/retail_spreadsheet_analysis.xlsx`

The workbook is generated from raw data and is excluded from Git under the project's generated-artifact policy (the workbook was untracked by the project owner during the Phase 3 re-audit). It is regenerated reproducibly by `scripts/create_spreadsheet_analysis.py`.

### Phase 3 status

VERIFIED — workbook regenerated and confirmed functionally identical during the Phase 17 re-audit.

### Phase 17 audit modifications

- `docs/phase-3/spreadsheet-results.md`
- `docs/phase-3/phase-3-checklist.md`
- `docs/phase-3/course-content-coverage.md`
- `docs/phase-2/data-ethics-and-privacy.md` (license confirmation)
- `docs/phase-0/project-state.md`
- `docs/project-file-update-register.md`
- `docs/phase-0/curriculum-mapping.md`

The re-audit regenerated and verified the workbook (761 daily records, 4 stores, 28,182 items), populated the results documentation with verified findings, corrected the deferred-phase chart, and confirmed the course-technology coverage claims against the actual workbook.

IN PROGRESS

---

## Phase 4 — SQL & Database Analysis

### Planned files

- `docs/phase-4/sql-analysis.md`
- `docs/phase-4/sql-analysis-plan.md`
- `docs/phase-4/database-schema.md`
- `docs/phase-4/sql-results.md`
- `docs/phase-4/course-content-coverage.md`
- `docs/phase-4/phase-4-checklist.md`
- `scripts/create_sqlite_database.py`
- `scripts/run_sql_analysis.py`
- `tests/test_create_sqlite_database.py`
- `tests/test_sql_analysis.py`
- `sql/schema.sql`
- `sql/retail_analysis.sql`

### Generated local artifacts

- `data/analysis/retail_demand.db` (1.06 GB SQLite database)
- `data/analysis/sql_results/query_1.csv` through `query_18.csv`

The database and query results are generated from raw data and are excluded from Git under the project's generated-artifact policy.

### Phase 4 status

VERIFIED — database rebuilt and all 18 SQL queries re-executed during the Phase 17 re-audit.

### Phase 17 audit modifications

- `docs/phase-4/sql-results.md`
- `docs/phase-4/phase-4-checklist.md`
- `docs/phase-4/sql-analysis.md`
- `docs/phase-4/database-schema.md`
- `docs/phase-4/sql-analysis-plan.md`
- `docs/phase-4/course-content-coverage.md`
- `tests/test_sql_analysis.py`

The re-audit rebuilt the SQLite database, re-executed all 18 queries, verified row counts against Phase 2 facts, documented the Query 17 data-coverage finding (36,585 unmatched catalog rows / 948 distinct items), and added SQL-parser and missing-input regression tests.

---

## Phase 5 — Data Cleaning & Quality Assurance

### Planned files

- `docs/phase-5/data-cleaning-plan.md`
- `docs/phase-5/data-quality-framework.md`
- `docs/phase-5/data-cleaning-methodology.md`
- `docs/phase-5/data-quality-results.md`
- `docs/phase-5/course-content-coverage.md`
- `docs/phase-5/phase-5-checklist.md`
- `scripts/clean_retail_data.py`
- `tests/test_clean_retail_data.py`

### Generated local artifacts

- `data/processed/sales_clean.csv` (322.8 MB, 7,431,026 rows)
- `data/processed/data_quality_report.csv`
- `data/processed/cleaning_summary.csv`

The cleaned dataset and quality reports are generated from raw data and are
excluded from Git under the project's generated-artifact policy.

### Phase 5 status

VERIFIED — the cleaning pipeline was re-executed over the full dataset and all
three generated artifacts were inspected during the Phase 17 re-audit.

### Phase 17 audit modifications

- `scripts/clean_retail_data.py`
- `tests/test_clean_retail_data.py`
- `docs/phase-5/data-quality-results.md`
- `docs/phase-5/data-cleaning-methodology.md`
- `docs/phase-5/data-cleaning-plan.md`
- `docs/phase-5/data-quality-framework.md`
- `docs/phase-5/course-content-coverage.md`
- `docs/phase-5/phase-5-checklist.md`
- `docs/phase-4/sql-results.md`
- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/project-file-update-register.md`

The re-audit added the catalog-membership reference check and valid-date
coverage that the phase plan and quality framework required, corrected the
cleaning-summary rows-removed reporting, and added eight tests (11 to 19). The
cleaning rules and retained row set are unchanged; no raw data files are
modified.

---

## Phase 6 — Data Integration

### Planned files

- `docs/phase-6/data-integration-plan.md`
- `docs/phase-6/integration-methodology.md`
- `docs/phase-6/integration-quality-framework.md`
- `docs/phase-6/integration-results.md`
- `docs/phase-6/course-content-coverage.md`
- `docs/phase-6/phase-6-checklist.md`
- `scripts/integrate_retail_data.py`
- `tests/test_integrate_retail_data.py`

### Generated local artifacts

- `data/processed/integrated_retail_data.csv` (1.28 GB, 7,431,026 rows, 34 columns)
- `data/processed/integration_quality_report.csv`

The integrated dataset and its quality report are generated from raw data and
are excluded from Git under the project's generated-artifact policy.

### Phase 6 status

VERIFIED — the integration pipeline was re-executed over the full dataset
(350 seconds) and its output was independently validated during the Phase 17
re-audit.

### Phase 17 audit modifications

- `scripts/integrate_retail_data.py`
- `tests/test_integrate_retail_data.py`
- `docs/phase-6/integration-results.md`
- `docs/phase-6/integration-methodology.md`
- `docs/phase-6/integration-quality-framework.md`
- `docs/phase-6/data-integration-plan.md`
- `docs/phase-6/course-content-coverage.md`
- `docs/phase-6/phase-6-checklist.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/project-file-update-register.md`

The re-audit added six validation metrics to the quality report (date coverage,
unique items/stores, total demand and revenue), removed the stale
`integration_quality_report.json` artifact that the current script cannot
reproduce, documented the same-day price-event tie-break, and replaced a vacuous
test with real coverage of the integration core (13 to 22 tests). No grain, join
key or release policy was changed; the integrated output is byte-identical and
no raw data files are modified.

---

## Phase 7 — Exploratory Data Analysis

### Planned files

- `docs/phase-7/eda-plan.md`
- `docs/phase-7/eda-methodology.md`
- `docs/phase-7/eda-quality-framework.md`
- `docs/phase-7/eda-results.md`
- `docs/phase-7/course-content-coverage.md`
- `docs/phase-7/phase-7-checklist.md`
- `scripts/exploratory_data_analysis.py`
- `tests/test_exploratory_data_analysis.py`

### Generated local artifacts

- `data/analysis/eda_summary.csv` (45 metric rows)
- `data/analysis/eda_monthly_demand.csv` (26 months)
- `data/analysis/eda_store_summary.csv` (4 stores)
- `data/analysis/eda_category_summary.csv` (182 rows)
- `data/analysis/eda_top_items.csv` (100 items)
- `data/analysis/eda_correlation.csv` (7x7 matrix)
- `data/analysis/eda_findings.txt`
- `reports/figures/eda_demand_over_time.png`
- `reports/figures/eda_monthly_demand.png`
- `reports/figures/eda_store_demand.png`
- `reports/figures/eda_top_categories.png`
- `reports/figures/eda_demand_distribution.png`

The EDA summaries and figures are regenerated from the integrated dataset and
are excluded from Git under the project's generated-artifact policy.

### Phase 7 status

VERIFIED — the EDA pipeline was re-executed over the complete integrated
dataset (61-63 seconds) and all seven summary files and five figures were
inspected against the summaries they derive from during the Phase 17 re-audit.

### Phase 17 audit modifications

- `scripts/exploratory_data_analysis.py`
- `tests/test_exploratory_data_analysis.py`
- `docs/phase-7/eda-results.md`
- `docs/phase-7/eda-methodology.md`
- `docs/phase-7/eda-plan.md`
- `docs/phase-7/eda-quality-framework.md`
- `docs/phase-7/course-content-coverage.md`
- `docs/phase-7/phase-7-checklist.md`
- `docs/phase-6/integration-results.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/project-file-update-register.md`

The re-audit replaced the sampled correlation matrix with an exact full-dataset
pairwise-complete calculation, added item-level distribution, outlier and
concentration metrics plus promotion/markdown record frequency and non-finite
counters, fixed a chart-label failure when a category has no value, replaced
sixteen per-chunk missingness passes with one vectorized pass, and added
twenty-four tests (10 to 34). No raw data files are modified.

No Git commands were run during this audit, so no commit or push is recorded
for Phase 7.

---

## Phase 8

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `scripts/statistical_analytical_analysis.py`
- `tests/test_statistical_analytical_analysis.py`
- `docs/phase-8/statistical-analysis-plan.md`
- `docs/phase-8/statistical-methodology.md`
- `docs/phase-8/statistical-quality-framework.md`
- `docs/phase-8/statistical-results.md`
- `docs/phase-8/course-content-coverage.md`
- `docs/phase-8/phase-8-checklist.md`
- `data/analysis/statistical_summary.csv`
- `data/analysis/statistical_correlations.csv`
- `data/analysis/statistical_store_analysis.csv`
- `data/analysis/statistical_category_analysis.csv`
- `data/analysis/statistical_price_demand.csv`
- `data/analysis/statistical_promotion_analysis.csv`
- `data/analysis/statistical_autocorrelation.csv`
- `data/analysis/statistical_trend.csv`
- `data/analysis/statistical_monthly_activity.csv` (added in the re-audit)
- `data/analysis/statistical_quality_report.csv` (added in the re-audit)
- `data/analysis/statistical_findings.txt`
- `reports/figures/statistical_demand_trend.png`
- `reports/figures/statistical_price_demand.png`
- `reports/figures/statistical_store_variability.png`
- `reports/figures/statistical_demand_autocorrelation.png`

The re-audit also corrected the promotion comparison, replaced the retained
analysis frame with streaming accumulators, added covariance and quality
validation, added Newey-West trend inference, and synchronised the Phase 0-7
records that carry Phase 8 findings.

---

## Phase 9

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `scripts/prepare_time_series.py`
- `tests/test_prepare_time_series.py`
- `docs/phase-9/time-series-preparation-plan.md`
- `docs/phase-9/time-series-methodology.md`
- `docs/phase-9/time-series-quality-framework.md`
- `docs/phase-9/time-series-results.md`
- `docs/phase-9/course-content-coverage.md`
- `docs/phase-9/phase-9-checklist.md`
- `data/processed/time_series_daily.csv` (generated; excluded from Git)
- `data/analysis/time_series_summary.csv` (generated; excluded from Git)
- `data/analysis/time_series_gap_summary.csv` (generated; excluded from Git)
- `data/analysis/time_series_split_summary.csv` (generated; excluded from Git)
- `data/analysis/time_series_quality_report.csv` (generated; excluded from Git)
- `data/analysis/time_series_findings.txt` (generated; excluded from Git)

Cross-phase files synchronised:

- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-7/eda-results.md`
- `docs/phase-8/statistical-results.md`
- `docs/project-file-update-register.md`
- `README.md` (reviewed; unchanged)

The re-audit re-executed the preparation workflow over the full integrated
dataset (206.4 seconds, 1,356.9 MB peak), reconciled 7,431,026 rows and
41,949,529.910 quantity with Phase 6, rebuilt the quality report (15 checks,
all passing), removed the second full-source read, replaced two vacuous gap
checks, and fixed three-date split handling and quantity formatting. The
prepared dataset and analysis outputs are reproducible generated artifacts and
are not source-controlled. No raw data files are modified. No Git commands
were run.

---

## Phase 10

Not yet started.

Files will be determined at Phase 10 start.

---

## Phase 11

Not yet started.

Files will be determined at Phase 11 start.

---

## Phase 12

Not yet started.

Files will be determined at Phase 12 start.

---

## Phase 13

Not yet started.

Files will be determined at Phase 13 start.

---

## Phase 14

Not yet started.

Files will be determined at Phase 14 start.

---

## Phase 15

Not yet started.

Files will be determined at Phase 15 start.

---

## Phase 16

Not yet started.

Files will be determined at Phase 16 start.

---

## Phase 17

IN PROGRESS — Testing, Documentation & Final Audit

Phase 0 through Phase 9 have been re-audited and approved. Phase 10 is the next audit target. The Phase 9 re-audit re-executed the time-series preparation workflow over the full integrated dataset, rebuilt its quality report (15 checks, all passing), corrected the second full-source read and the two vacuous gap checks, and synchronised the Phase 0–8 records that carry Phase 9 constraints.