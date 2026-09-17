# Phase 5 — Course Content Coverage

## Course

Course 4 — Processing and Cleaning Data for Data Analysis

## Coverage

| Course concept | Project evidence | Status |
|---|---|---|
| Data preparation | Phase 5 cleaning pipeline | Implemented |
| Data cleaning | `scripts/clean_retail_data.py` | Implemented |
| Data integrity | Schema, identifier and consistency checks | Implemented |
| Referential integrity | Store and catalog reference checks | Implemented |
| Data completeness | Missing required-field checks | Implemented |
| Data accuracy | Numeric and revenue validation | Implemented |
| Data consistency | Revenue consistency checks | Implemented |
| Data validation | Automated validation functions | Implemented |
| Data formatting | Type conversion and identifier normalization | Implemented |
| Data type conversion | pandas numeric/date conversion | Implemented |
| Missing data | Missing required-field handling | Implemented |
| Duplicate records | Duplicate detection/removal | Implemented |
| Incorrect values | Range and validity checks | Implemented |
| Outliers | Potential quantity outlier reporting | Implemented |
| Transformation | Controlled cleaning transformations | Implemented |
| Tidy data | Clean analytical column structure | Implemented |
| Change logs | Cleaning summary and quality report | Implemented |
| Documentation | Phase 5 methodology and results | Implemented |
| Troubleshooting | Explicit validation/error handling | Implemented |
| Error checking | Automated quality counters | Implemented |
| Verification | Post-cleaning tests and validation | Implemented |
| Business-objective alignment | Sales-demand cleaning rules | Implemented |

## Concepts requiring special treatment

### Sampling

The primary cleaning pipeline processes the complete sales dataset in chunks
rather than drawing a statistical sample for cleaning.

This is appropriate because the complete source dataset is available and the
goal is to preserve all valid demand observations.

Sampling concepts remain relevant to later statistical analysis and are
therefore tracked for the overall course-content checklist.

### Statistical power and margin of error

These concepts are not required for deterministic data cleaning of the full
available sales dataset.

They remain part of the course-content record and can be applied later if
the project performs inferential statistical analysis.

### Random sampling

Random sampling is not used to clean the complete historical sales dataset
because doing so would discard potentially useful demand observations.

The project therefore documents the reason rather than claiming false
coverage.

### Cleaning with SQL and temporary tables

Course 4 also teaches cleaning with SQL and temporary tables.

Those topics are not demonstrated in this Python cleaning pipeline because it
uses pandas chunked processing rather than SQL.

The evidence for SQL-based validation already exists in Phase 4:

- `sql/retail_analysis.sql` queries 16 and 17 are SQL validation queries
  (unmatched store and unmatched catalog records).
- Query 11 uses a common table expression (CTE), which the curriculum treats as
  a temporary analytical result; explicit temporary tables are not used.

Adding a second SQL cleaning path inside Phase 5 would duplicate the Phase 4
work without adding analytical value, so the coverage is recorded as delivered
by Phase 4 instead.

## Course principle demonstrated

The cleaning workflow follows:

**Inspect → Validate → Clean → Document → Verify**

rather than modifying data without evidence.

## Phase 17 Re-Audit Record

AUDITED — COMPLETE

Every concept listed above was checked against the executed script during the
Phase 17 re-audit. The catalog reference check was added to the pipeline during
this audit, so a "Referential integrity" row was added to the coverage table and
the Course 4 SQL-cleaning/temporary-table topics are now explicitly mapped to
their actual Phase 4 evidence.

The "Outliers" concept remains a screening capability in this phase (potential
quantity outliers are reported but not resolved); full outlier analysis belongs
to the Phase 7 exploratory analysis.