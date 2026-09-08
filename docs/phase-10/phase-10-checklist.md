# Phase 10 — Feature Engineering Checklist

## Objective

Create a leakage-safe feature matrix for retail demand forecasting using the Phase 9 time-series dataset.

## Data Grain

`date + item_id + store_id`

## Target

`quantity`

## Checklist

* [ ] Use Phase 9 time-series data as the input.
* [ ] Preserve the physical-sales demand target.
* [ ] Do not use online quantity as the forecasting target.
* [ ] Create calendar features.
* [ ] Create lag 1.
* [ ] Create lag 7.
* [ ] Create lag 14.
* [ ] Create lag 28.
* [ ] Create shifted 7-period rolling mean.
* [ ] Create shifted 7-period rolling standard deviation.
* [ ] Create shifted 28-period rolling mean.
* [ ] Create shifted 28-period rolling standard deviation.
* [ ] Create series age.
* [ ] Preserve chronological split labels.
* [ ] Prevent target leakage.
* [ ] Validate uniqueness.
* [ ] Validate chronology.
* [ ] Validate target preservation.
* [ ] Validate feature schema.
* [ ] Run automated tests.
* [ ] Generate quality reports.
* [ ] Document limitations caused by missing intermediate dates.
* [ ] Update README.
* [ ] Update project state.
* [ ] Update file-update register.
* [ ] Review Git changes.
* [ ] Commit Phase 10.
* [ ] Push Phase 10 branch.
* [ ] Verify Git state.
