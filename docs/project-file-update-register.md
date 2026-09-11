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

The workbook is generated from raw data and should remain outside Git if generated artifacts are excluded by the project's Git policy.

### Phase 3 status

IN PROGRESS

---

## Phase 4

Not yet started.

Files will be determined at Phase 4 start.

---

## Phase 5

Not yet started.

Files will be determined at Phase 5 start.

---

## Phase 6

Not yet started.

Files will be determined at Phase 6 start.

---

## Phase 7

Not yet started.

Files will be determined at Phase 7 start.

---

## Phase 8

Not yet started.

Files will be determined at Phase 8 start.

---

## Phase 9

Not yet started.

Files will be determined at Phase 9 start.

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

Phase 0 and Phase 1 have been re-audited and approved. Phase 2 is currently being re-audited; its script, tests and documentation have been corrected and verified against the full raw dataset.