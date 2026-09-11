# Data Ethics, Privacy and Responsible Use

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Dataset

Retail Sales Forecasting Data

## Privacy Assessment

The inspected raw files contain fields relating to:

- dates
- products
- stores
- quantities
- prices
- sales values
- markdowns
- price changes
- promotions/discounts

No customer-level personally identifiable information is identified in the inspected fields.

## Personal Data

Status:

NOT IDENTIFIED FROM INSPECTED FIELDS

The project will not introduce customer-level personal information.

## Security

Raw data will be stored locally under:

`data/raw/`

Raw data will be excluded from Git using `.gitignore`.

Credentials must never be stored in the repository.

Kaggle credentials, if required for acquisition, must remain outside the repository.

## Data Ownership

The dataset is externally sourced from Kaggle.

The original ownership and licensing terms must be verified from the current Kaggle dataset metadata (see the Phase 2 data-acquisition and data-source-assessment records; the license could not be confirmed programmatically during the re-audit).

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

- limited store coverage (4 stores)
- limited historical period (≈25 months)
- retailer-specific pricing practices
- retailer-specific product mix
- potential differences between physical and online sales
- catalog attribute gaps and catalog text-formatting irregularities
- future-dated discount records that require interpretation care

These limitations must be considered when interpreting forecasts.

## Data Minimization

Only information necessary for the forecasting and analytical objectives should be processed.

## Final Privacy Status

COMPLETE

No PII was identified in the inspected fields during the Phase 17 re-audit.