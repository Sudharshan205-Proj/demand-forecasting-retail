# Phase 6 — Integration Methodology

## 1. Primary fact

The cleaned sales dataset is the integration anchor.

Each record represents daily sales for an item at a store.

## 2. Canonical integration grain

All integration operations use:

`date + item_id + store_id`

as the canonical key.

## 3. Dimension integration

### Stores

Store attributes are one row per store and are joined using:

`store_id`

The join is validated as many-to-one.

### Catalog

Product attributes are one row per item and are joined using:

`item_id`

A left join is used so sales records without catalog metadata remain available.

## 4. Event-data integration

Price history, markdowns, and discounts can contain multiple records for the same analytical key.

They are therefore aggregated before integration.

Examples include:

* number of price changes
* markdown quantity
* markdown price
* promotion record count
* promotion discount rate

## 5. Online channel

Online sales are aggregated separately and attached as online-channel features.

They are not added to the primary physical-sales demand measure.

## 6. Actual matrix

Actual-matrix records are converted into an exact-key indicator.

A missing indicator does not automatically imply that the product was unavailable because the source only records represented matrix observations.

## 7. Join validation

Pandas merge validation is used to enforce expected cardinality.

The integration rejects a join when an auxiliary table violates its expected uniqueness.

## 8. Row preservation

The number of integrated records must equal the number of cleaned sales records.

Any difference is treated as a pipeline failure.

## 9. Temporal integrity

Phase 6 does not propagate future price information backwards through time.

Any future-looking feature construction belongs to chronological feature engineering and must be performed without temporal leakage.

## 10. Reproducibility

The integration is implemented in a deterministic Python script using project-relative paths and existing project dependencies.
