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
dataset (231.6 seconds, 1,405.5 MB peak), reconciled 7,431,026 rows and
41,949,529.910 quantity with Phase 6, rebuilt the quality report (15 checks,
all passing), removed the second full-source read, replaced two vacuous gap
checks, and fixed three-date split handling, quantity formatting (the summary,
the findings and the quality report all render `41949529.910`) and date parsing
(explicit ISO). Phase 9 tests: 37, all passing. The Phase 9 and Phase 10
pipelines were re-run after the final source change — Phase 9 first, because
Phase 10 consumes its output — so every artifact post-dates the script that
produced it. The prepared dataset and analysis outputs are reproducible
generated artifacts and are not source-controlled. No raw data files are
modified. No Git commands were run.

---

## Phase 10

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `scripts/feature_engineering.py`
- `tests/test_feature_engineering.py`
- `docs/phase-10/feature-engineering-plan.md`
- `docs/phase-10/feature-engineering-methodology.md`
- `docs/phase-10/feature-engineering-quality-framework.md`
- `docs/phase-10/feature-engineering-results.md`
- `docs/phase-10/course-content-coverage.md`
- `docs/phase-10/phase-10-checklist.md`
- `data/processed/feature_engineered_daily.csv` (generated; excluded from Git)
- `data/analysis/feature_engineering_summary.csv` (generated; excluded from Git)
- `data/analysis/feature_engineering_quality_report.csv` (generated; excluded from Git)
- `data/analysis/feature_engineering_feature_summary.csv` (generated; excluded from Git)
- `data/analysis/feature_engineering_split_summary.csv` (generated; excluded from Git)
- `data/analysis/feature_engineering_findings.txt` (generated; excluded from Git)

Cross-phase files synchronised:

- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-9/time-series-results.md`
- `docs/project-file-update-register.md`
- `README.md` (reviewed; unchanged)

The re-audit re-executed the feature-engineering workflow over the full Phase 9
dataset (365.6 seconds, 2,510.3 MB peak), reconciled 7,431,026 rows and
41,949,529.910 quantity with Phase 9, rebuilt the quality report (14 checks,
all passing), added a per-feature completeness artifact, replaced two constant
quality checks and the Python-level rolling transform with a value-identical
compiled path, formatted the reconciled quantity so the report carries no
floating-point artefacts, made date parsing explicitly ISO, and documented that
the engineered features are not currently consumed as predictors by Phases
11–13. Phase 10 tests: 32, all passing. The feature-engineered dataset and its
analysis outputs are reproducible generated artifacts and are not
source-controlled. No raw data files are modified. No Git commands were run.

---

## Phase 11

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `scripts/forecasting_models.py`
- `tests/test_forecasting_models.py`
- `docs/phase-11/forecasting-models-plan.md`
- `docs/phase-11/forecasting-models-methodology.md`
- `docs/phase-11/forecasting-models-quality-framework.md`
- `docs/phase-11/forecasting-models-results.md`
- `docs/phase-11/course-content-coverage.md`
- `docs/phase-11/phase-11-checklist.md`
- `data/analysis/forecasting_model_results.csv` (generated; excluded from Git)
- `data/analysis/forecasting_model_configurations.csv` (generated; excluded from Git)
- `data/analysis/forecasting_summary.csv` (generated; excluded from Git)
- `data/analysis/forecasting_predictions.csv` (generated; excluded from Git)
- `data/analysis/forecasting_quality_report.csv` (generated; excluded from Git)
- `data/analysis/forecasting_findings.txt` (generated; excluded from Git)

Cross-phase files synchronised:

- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-1/kpi-definitions.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-9/time-series-results.md`
- `docs/phase-10/feature-engineering-results.md`
- `docs/project-file-update-register.md`
- `README.md` (reviewed; unchanged)

The re-audit re-executed the forecasting workflow over the full Phase 10
dataset (21.4 seconds, 1,279.6 MB peak), reconciled 7,431,026 rows and
41,949,529.910 quantity at the store-day grain, and rebuilt the phase's
verification machinery. Six gaps were corrected: there was no machine-readable
validation artifact, no source reconciliation, no stored predictions, no
baseline verification, an incomplete reproducibility record and a findings
report that mislabelled the validation start as the training end. The phase
now writes a 24-check quality report that gates the run, a 1,368-row
predictions artifact that reconciles every reported metric, measured
store-day densification (one zero-filled store-day), pooled summary metrics
and explicit temporal and test-isolation checks. The model results artifact is
byte-identical to the pre-audit run. Phase 11 tests increased from 11 to 52
and the full suite passes (321 tests). The forecasting outputs are
reproducible generated artifacts and are not source-controlled. No raw data
files are modified. No Git commands were run.

Cross-phase: the engineered lag, rolling and calendar features are still not
used as predictors by the classical forecasting scripts. Phase 11's documented
scope is classical univariate models, so the finding is carried forward to the
Phase 12–13 audits.

---

## Phase 12

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `scripts/evaluate_and_tune_models.py`
- `tests/test_evaluate_and_tune_models.py`
- `docs/phase-12/model-evaluation-and-tuning-plan.md`
- `docs/phase-12/model-evaluation-and-tuning-methodology.md`
- `docs/phase-12/model-evaluation-and-tuning-quality-framework.md`
- `docs/phase-12/model-evaluation-and-tuning-results.md`
- `docs/phase-12/course-content-coverage.md`
- `docs/phase-12/phase-12-checklist.md`
- `data/analysis/model_tuning_results.csv` (generated; excluded from Git)
- `data/analysis/model_tuning_summary.csv` (generated; excluded from Git)
- `data/analysis/selected_model_configurations.csv` (generated; excluded from Git)
- `data/analysis/tuned_validation_results.csv` (generated; excluded from Git)
- `data/analysis/model_error_analysis.csv` (generated; excluded from Git)
- `data/analysis/model_evaluation_predictions.csv` (generated; excluded from Git)
- `data/analysis/model_evaluation_quality_report.csv` (generated; excluded from Git)
- `data/analysis/model_evaluation_findings.txt` (generated; excluded from Git)

Cross-phase files synchronised:

- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-1/kpi-definitions.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-8/statistical-results.md` (forward reference to per-item evaluation corrected)
- `docs/phase-10/feature-engineering-results.md`
- `docs/phase-11/forecasting-models-results.md`
- `docs/phase-13/forecasting-and-inventory-insights-plan.md` (downstream correction, see below)
- `docs/phase-13/forecasting-and-inventory-insights-methodology.md`
- `docs/phase-13/forecasting-and-inventory-insights-results.md`
- `docs/phase-13/course-content-coverage.md` (selection claim corrected)
- `docs/project-file-update-register.md`
- `README.md` (reviewed; unchanged)

The re-audit re-executed the evaluation workflow over the full Phase 10
dataset (70.9 seconds, 236.6 MB peak). The stale pre-audit artifacts
predated the regenerated input and reproduced byte-for-byte when the
original script was re-run, so the comparison point was sound. Four
defects were corrected: store 4 was silently excluded from tuning (its 60
training observations cannot support the fixed three-fold design),
configuration strings were parsed back into season lengths and orders,
the engineered features were unused, and no machine-readable validation
existed. The phase now adapts its fold count so all four stores are tuned,
carries typed configurations through a single dispatcher, adds a
deterministic gradient-boosting candidate over the 16 store-day feature
families, stores all 2,976 forecasts, and gates the run on a 30-check
quality report (all passing). The tuned portfolio reduces the mean
validation RMSE from 3,223.0630 to 3,079.4286, improving stores 1 and 2 and
leaving store 3 marginally worse than the weekly benchmark. Phase 12 tests
increased from 12 to 64 and the full suite passes (373 tests). The
evaluation outputs are reproducible generated artifacts and are not
source-controlled. No raw data files are modified. No Git commands were
run.

Downstream correction: Phase 13's documentation asserted that store 4 had
no tuned model and that seasonal-naive had been selected for stores 1–3.
Both claims became false. The affected statements were corrected and
Phase 13's generated artifacts remain to be re-executed during its own
audit.

---

## Phase 13

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `scripts/forecasting_inventory_insights.py`
- `tests/test_forecasting_inventory_insights.py`
- `docs/phase-13/forecasting-and-inventory-insights-plan.md`
- `docs/phase-13/forecasting-and-inventory-insights-methodology.md`
- `docs/phase-13/forecasting-and-inventory-insights-quality-framework.md`
- `docs/phase-13/forecasting-and-inventory-insights-results.md`
- `docs/phase-13/course-content-coverage.md`
- `docs/phase-13/phase-13-checklist.md`
- `data/analysis/inventory_demand_summary.csv` (generated; excluded from Git)
- `data/analysis/inventory_variability_summary.csv` (generated; excluded from Git)
- `data/analysis/inventory_densification_summary.csv` (generated; excluded from Git)
- `data/analysis/inventory_scenarios.csv` (generated; excluded from Git)
- `data/analysis/inventory_forecast_scenarios.csv` (generated; excluded from Git)
- `data/analysis/inventory_forecast_error_summary.csv` (generated; excluded from Git)
- `data/analysis/forecast_inventory_insights.csv` (generated; excluded from Git)
- `data/analysis/forecasting_inventory_findings.txt` (generated; excluded from Git)
- `data/analysis/forecasting_inventory_quality_report.csv` (generated; excluded from Git)

Cross-phase files synchronised:

- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-1/kpi-definitions.md`
- `docs/phase-2/dataset-inventory.md`
- `docs/phase-12/model-evaluation-and-tuning-results.md` (downstream note resolved)
- `docs/phase-16/application-quality-framework.md` (downstream correction, see below)
- `docs/phase-16/application-results.md`
- `docs/phase-16/course-content-coverage.md`
- `docs/phase-16/deployment-validation.md`
- `docs/phase-16/phase-16-checklist.md`
- `docs/project-file-update-register.md`
- `README.md` (reviewed; unchanged)

The re-audit re-executed the insights workflow over the complete Phase 10
dataset (16.7 seconds, 149.6 MB peak). The pre-audit artifacts were dated
8 Sep while the Phase 12 evidence they consume was rewritten on 19 Sep, so
the phase had never run against its own inputs. Four substantive defects
were corrected: the generated findings asserted that Store 4 had no tuned
Phase 12 configuration and, because the sentence was hardcoded, reproduced
byte-for-byte on re-execution with the false claim intact; the phase loaded
the Phase 12 forecasts and used none of them, leaving its stated purpose
unmet; the demand basis silently differed from Phases 11–12; and no
machine-readable validation existed. The phase now densifies identically
(1,656 training store-days, one zero-filled, matching Phase 11), adds a
forecast-error scenario family that consumes the stored forecasts, asserts
that the bias-adjusted level is the recovered validation mean so it cannot
be described as a forward forecast, reconciles the source matrix on rows and
quantity, derives the findings from evidence, and gates the run on a
43-check quality report that all passed. Phase 13 tests increased from 10 to
78 and the full suite passes (441 tests). The insights outputs are
reproducible generated artifacts and are not source-controlled. No raw data
files are modified. No Git commands were run.

Downstream correction: Phase 16's documentation asserted that Store 4 was
descriptive-only because no validated tuned configuration existed for it.
Phase 12's adaptive fold count falsified that. The affected statements were
corrected and Phase 16's generated artifacts remain to be re-executed during
its own audit.

---

## Phase 14

AUDITED — COMPLETE (Phase 17 re-audit).

Files:

- `r/r_analysis.R`
- `r/r_analysis_report.Rmd`
- `tests/test_r_analysis.py` (added in the re-audit)
- `docs/phase-14/r-analysis-plan.md`
- `docs/phase-14/r-analysis-methodology.md`
- `docs/phase-14/r-analysis-quality-framework.md`
- `docs/phase-14/r-analysis-results.md`
- `docs/phase-14/course-content-coverage.md`
- `docs/phase-14/phase-14-checklist.md`
- `data/analysis/r/r_store_analysis.csv` (generated; excluded from Git)
- `data/analysis/r/r_inventory_scenario_summary.csv` (generated; excluded from Git)
- `data/analysis/r/r_forecast_inventory_scenario_summary.csv` (generated; excluded from Git)
- `data/analysis/r/r_baseline_inventory_scenario.csv` (generated; excluded from Git)
- `data/analysis/r/r_baseline_forecast_inventory_scenario.csv` (generated; excluded from Git)
- `data/analysis/r/r_phase13_consistency.csv` (generated; excluded from Git)
- `data/analysis/r/r_phase13_reconciliation.csv` (generated; excluded from Git)
- `data/analysis/r/r_metric_reconciliation.csv` (generated; excluded from Git)
- `data/analysis/r/r_analysis_quality_report.csv` (generated; excluded from Git)
- `data/analysis/r/r_environment.csv` (generated; excluded from Git)
- `data/analysis/r/r_analysis_findings.txt` (generated; excluded from Git)
- `data/analysis/r/plots/average_daily_demand_by_store.png` (generated; excluded from Git)
- `data/analysis/r/plots/demand_variability_by_store.png` (generated; excluded from Git)
- `data/analysis/r/plots/inventory_reorder_point_scenarios.png` (generated; excluded from Git)
- `data/analysis/r/plots/inventory_scenario_family_comparison.png` (generated; excluded from Git)
- `data/analysis/r/r_analysis_report.html` (generated; excluded from Git)

Cross-phase files synchronised:

- `docs/phase-0/project-state.md`
- `docs/phase-0/curriculum-mapping.md`
- `docs/phase-0/environment.md`
- `docs/phase-1/requirements-traceability.md`
- `docs/phase-1/analytical-questions.md`
- `docs/phase-12/course-content-coverage.md`
- `docs/phase-13/forecasting-and-inventory-insights-results.md`
- `docs/project-file-update-register.md`
- `README.md`

The re-audit re-executed the R workflow against the current Phase 13 evidence
(91 of 91 quality checks) and registered the HTML report. The pre-audit
artifacts were dated 8 Sep while the Phase 13 inputs were regenerated on
19 Sep, so the phase had never run against its own inputs: the stale,
untracked `r_store_analysis.csv` still carried the pre-audit Store 3
statistics
(531 days, 5,843.874970, minimum 173.898). Fourteen defects were corrected.
The workflow was rebuilt around 28 named functions, extended to consume nine
inputs including both scenario families and the 456 stored Phase 12
validation forecasts, and given a 91-check quality report that gates the run
and withholds the findings report on failure. All seven Phase 13 insight
types are reconciled on store, metric name and value (13 of 13 rows), and
RMSE, MAE and MAPE are recomputed with `yardstick` and reconciled with the
reported values, making the previously idle `tidymodels` dependency genuine.
Project-root and directory resolution no longer depends on the checkout
directory name. The R Markdown report sources the audited workflow, resolves
its four figures correctly and refuses to knit when validation fails.
Malformed inputs are reported instead of crashing the run. Phase 14 tests
increased from 0 to 36 (twelve failure paths) and the full suite passes (477
tests). The R outputs are reproducible generated artifacts and are not
source-controlled. No raw data files are modified. No Git commands were run.

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

Phase 0 through Phase 14 have been re-audited and approved. Phase 15 is the next audit target. The Phase 14 re-audit moved the R analysis onto the current Phase 13 evidence, extended it to the forecast-error scenario family, the densification summary and the stored Phase 12 forecasts, reconciled all seven Phase 13 insight types on store, metric and value, recomputed RMSE, MAE and MAPE in R with `yardstick`, and rebuilt the phase's validation as a 91-check quality report that gates the run. It also synchronised the Phase 0–13 records that carry Phase 14 status or path claims, including Phase 13's audit row that named `scripts/r_analysis.*` as an unexecuted downstream dependency.

Carried forward to the Phase 15 audit:

- `docs/phase-15/visualization-and-tableau-plan.md` lists Phase 14 as an input, while the Phase 15 script consumes no R output.
- Phase 15's results and deployment documents still say NOT YET EXECUTED.
- Phase 16's generated artifacts still require re-execution during its own audit.