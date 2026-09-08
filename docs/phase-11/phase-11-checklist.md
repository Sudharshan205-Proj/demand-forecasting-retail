# Phase 11 — Forecasting Models Checklist

## Objective

Develop and evaluate classical forecasting models using the Phase 10 feature-engineered retail demand data.

## Models

* [ ] Naive baseline
* [ ] Seasonal-naive baseline
* [ ] ARIMA

## Data

* [ ] Use physical retail quantity as the target.
* [ ] Preserve chronological partitions.
* [ ] Do not randomly shuffle temporal observations.
* [ ] Do not use the test period for model selection.

## Evaluation

* [ ] RMSE
* [ ] MAPE
* [ ] Document zero-demand handling for MAPE.
* [ ] Record model configurations.
* [ ] Record forecast horizons.
* [ ] Record validation dates.

## Validation

* [ ] Input schema validation
* [ ] Forecast-length validation
* [ ] Chronological validation
* [ ] Metric validation
* [ ] Model configuration validation
* [ ] Automated tests

## Documentation

* [ ] Forecasting plan
* [ ] Methodology
* [ ] Quality framework
* [ ] Results
* [ ] Course-content mapping
* [ ] README
* [ ] Project state
* [ ] File-update register

## Git

* [ ] Create Phase 11 branch.
* [ ] Review changes.
* [ ] Stage correct files.
* [ ] Commit once at phase completion.
* [ ] Push branch.
* [ ] Verify clean working tree.
