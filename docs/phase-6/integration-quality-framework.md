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

AUDITED — COMPLETE

Every dimension and acceptance criterion above was checked against a fresh
execution during the Phase 17 re-audit:

* Completeness: row-count difference = 0 (7,431,026 integrated rows equals
  7,431,026 cleaned sales rows).
* Uniqueness: duplicate canonical-grain rows = 0, independently re-verified by
  streaming the regenerated output.
* Referential integrity: unknown store rows = 0; 36,580 catalog-unmatched rows
  reported and retained.
* Join cardinality: all auxiliary joins validated many-to-one, with a
  regression test proving a non-unique key raises an error.
* Data preservation: raw files unchanged; primary sales measures unchanged.
* Channel integrity: online features kept separate from physical demand.
* Temporal integrity: no future information propagated backwards.
* Missing auxiliary information: reported, not treated as missing sales.
* Quality report: the report now carries the six metrics listed in section 9
  plus date coverage, unique item/store counts and demand/revenue totals.

All acceptance criteria are satisfied. The exact verified figures are in
`integration-results.md`.
