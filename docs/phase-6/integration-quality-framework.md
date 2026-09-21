# Phase 6 — Integration Quality Framework

`data/processed/integration_quality_report.csv` is a **metric/value table**, not
a pass/fail gate: it records one row per measured quantity (`metric`, `value`) so
that every figure in [`integration-results.md`](integration-results.md) is
reproducible from a single file. It carries no `passed` column by design, and the
dimensions below are enforced by `tests/test_integrate_retail_data.py`. It is
excluded from the run-gating quality total, which counts only the reports that
gate a run.

## Integration-quality dimensions

### 1. Completeness

The integrated dataset contains the same number of rows as the cleaned sales
dataset.

### 2. Uniqueness

`date + item_id + store_id` is unique.

### 3. Referential integrity

Sales store IDs exist in stores; product references are measured against
catalog; auxiliary records use valid integration keys.

### 4. Join cardinality

Each dimension or pre-aggregated auxiliary dataset has at most one row per join
key.

### 5. Data preservation

The integration does not modify the raw datasets, and the primary sales measures
remain unchanged.

### 6. Channel integrity

Online sales remain separate from physical sales.

### 7. Temporal integrity

Price and promotion information is not propagated backwards from future
observations.

### 8. Missing auxiliary information

Missing catalog, promotion, markdown or price-history information is not treated
as a missing sales observation; it is reported separately.

### 9. Quality report

The integration pipeline reports sales rows read, integrated rows written,
row-count difference, duplicate canonical-grain rows, unknown store rows,
unmatched catalog rows, date coverage, unique item and store counts, and total
demand quantity and sales revenue.

## Acceptance criteria

Integration validation passes when:

- row-count difference = 0
- duplicate canonical-grain rows = 0
- unknown store rows = 0
- all auxiliary joins satisfy their expected cardinality
- tests pass
- the integrated file is generated successfully

## Realized values

All acceptance criteria are satisfied:

| Criterion | Result |
|---|---|
| Row-count difference | 0 (7,431,026 = 7,431,026) |
| Duplicate canonical-grain rows | 0 |
| Unknown store rows | 0 |
| Join cardinality | All auxiliary joins validated many-to-one |
| Unmatched catalog rows | 36,580, retained |
| Integrated output | 7,431,026 rows, 34 columns, 1,283,859,491 bytes |
| Date coverage | 2022-08-28 → 2024-09-26 |
