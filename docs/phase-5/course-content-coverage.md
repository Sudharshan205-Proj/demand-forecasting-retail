# Phase 5 — Course Content Coverage

## Course

Course 4 — Processing and Cleaning Data for Data Analysis

## Coverage

| Course concept | Project evidence |
|---|---|
| Data preparation | Phase 5 cleaning pipeline |
| Data cleaning | `scripts/clean_retail_data.py` |
| Data integrity | Schema, identifier and consistency checks |
| Referential integrity | Store and catalog reference checks |
| Data completeness | Missing required-field checks |
| Data accuracy | Numeric and revenue validation |
| Data consistency | Revenue consistency checks |
| Data validation | Automated validation functions |
| Data formatting | Type conversion and identifier normalization |
| Data type conversion | pandas numeric/date conversion |
| Missing data | Missing required-field handling |
| Duplicate records | Duplicate detection/removal |
| Incorrect values | Range and validity checks |
| Outliers | Potential quantity outlier reporting |
| Transformation | Controlled cleaning transformations |
| Tidy data | Clean analytical column structure |
| Change logs | Cleaning summary and quality report |
| Documentation | Phase 5 methodology and results |
| Troubleshooting | Explicit validation/error handling |
| Error checking | Automated quality counters |
| Verification | Post-cleaning validation |
| Business-objective alignment | Sales-demand cleaning rules |

## Concepts with special treatment

### Sampling

The primary cleaning pipeline processes the complete sales dataset in chunks
rather than drawing a statistical sample, because the complete source dataset is
available and the goal is to preserve every valid demand observation. Sampling
concepts remain relevant to the later statistical analysis and are recorded in
the overall course-content mapping.

### Statistical power and margin of error

These concepts are not required for deterministic cleaning of the full available
dataset. They remain part of the course-content record and apply to the
inferential analysis rather than to cleaning.

### Cleaning with SQL and temporary tables

Course 4 also teaches cleaning with SQL and temporary tables. Those topics are
not demonstrated in this Python cleaning pipeline, which uses pandas chunked
processing rather than SQL. The SQL evidence already exists in Phase 4:
Queries 16 and 17 are SQL validation queries (unmatched store and unmatched
catalog records), and Query 11 uses a common table expression (CTE), which the
curriculum treats as a temporary analytical result. Explicit temporary tables
are not used.

## Course principle demonstrated

The cleaning workflow follows **Inspect → Validate → Clean → Document → Verify**
rather than modifying data without evidence.
