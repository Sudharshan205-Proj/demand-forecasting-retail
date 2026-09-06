# Data Ethics, Privacy and Responsible Use

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Dataset

Retail Sales Forecasting Data

## Privacy Assessment

The published dataset description indicates fields relating to:

- dates
- products
- stores
- quantities
- prices
- sales values
- markdowns
- price changes

No customer-level personally identifiable information is identified in the documented schema.

Actual downloaded files must still be inspected before making a final privacy statement.

## Personal Data

Status:

NOT IDENTIFIED FROM DOCUMENTED SCHEMA

The project will not introduce customer-level personal information.

## Security

Raw data will be stored locally under:

`data/raw/`

Raw data will be excluded from Git using `.gitignore`.

Credentials must never be stored in the repository.

Kaggle credentials, if required for acquisition, must remain outside the repository.

## Data Ownership

The dataset is externally sourced from Kaggle.

The original ownership and licensing terms must be verified from the current Kaggle dataset metadata.

## Consent

Customer consent is not applicable to the project unless customer-level personal information is discovered.

No customer-level data will intentionally be introduced.

## Responsible Use

Forecasts will be presented as analytical estimates rather than guaranteed future demand.

The project will avoid claiming that:

- markdowns cause demand changes,
- prices cause specific demand changes,
- forecasts guarantee inventory requirements,
- historical relationships automatically generalize to every retailer.

Observed relationships will be described as associations unless a valid causal analysis is performed.

## Bias and Representativeness

Potential limitations include:

- limited store coverage
- limited historical period
- retailer-specific pricing practices
- retailer-specific product mix
- potential differences between physical and online sales

These limitations must be considered when interpreting forecasts.

## Data Minimization

Only information necessary for the forecasting and analytical objectives should be processed.

## Final Privacy Status

PARTIALLY ASSESSED

Final assessment will follow actual raw-data inspection.