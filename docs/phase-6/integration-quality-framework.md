# Phase 6 — Integration Quality Framework

## Integration-quality dimensions

### 1. Completeness

Check that the integrated dataset contains the same number of rows as the cleaned sales dataset.

### 2. Uniqueness

Check that:

`date + item_id + store_id`

is unique.

### 3. Referential integrity

Check that:

* sales store IDs exist in stores
* product references are measured against catalog
* auxiliary records use valid integration keys

### 4. Join cardinality

Each dimension or pre-aggregated auxiliary dataset must have at most one row per join key.

### 5. Data preservation

The integration must not modify the raw datasets.

The primary sales measures must remain unchanged.

### 6. Channel integrity

Online sales must remain separate from physical sales.

### 7. Temporal integrity

Price and promotion information must not be propagated backwards from future observations.

### 8. Missing auxiliary information

Missing catalog, promotion, markdown, or price-history information is not automatically treated as a missing sales observation.

It is reported separately.

### 9. Quality report

The integration pipeline reports:

* sales rows read
* integrated rows written
* row-count difference
* duplicate canonical-grain rows
* unknown store rows
* unmatched catalog rows

## Acceptance criteria

Phase 6 passes integration validation only when:

* row-count difference = 0
* duplicate canonical-grain rows = 0
* unknown store rows = 0
* all auxiliary joins satisfy their expected cardinality
* tests pass
* the integrated file is generated successfully

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
