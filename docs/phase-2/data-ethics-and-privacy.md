# Data Ethics, Privacy and Responsible Use

## Phase

Phase 2 — Data Acquisition & Data Understanding

## Dataset

Retail Sales Forecasting Data

## Privacy assessment

The raw files contain fields relating to dates, products, stores, quantities,
prices, sales values, markdowns, price changes and promotions/discounts.

No customer-level personally identifiable information is present in the
inspected fields, and the project introduces none.

## Personal data

The project processes no personal data.

## Security

Raw data is stored locally under `data/raw/` and excluded from Git by
`.gitignore`. Credentials are never stored in the repository; Kaggle credentials,
if required for acquisition, remain outside the repository.

## Data ownership

The dataset is externally sourced from Kaggle. The licensing terms were verified
from the Kaggle dataset metadata: CC BY-NC-SA 4.0. Derivatives and
redistributions carry the same license and attribute the source.

## Consent

Customer consent is not applicable, because the project processes no
customer-level personal information.

## Responsible use

Forecasts are presented as analytical estimates rather than guaranteed future
demand. The project does not claim that:

- markdowns cause demand changes,
- prices cause specific demand changes,
- forecasts guarantee inventory requirements,
- historical relationships automatically generalize to every retailer.

Observed relationships are described as associations unless a valid causal
analysis is performed.

## Bias and representativeness

- Limited store coverage (4 stores)
- Limited historical period (≈25 months)
- Retailer-specific pricing practices and product mix
- Potential differences between physical and online sales
- Catalog attribute gaps and catalog text-formatting irregularities
- Future-dated discount records that require interpretation care

These limitations are considered when interpreting forecasts.

## Data minimization

Only the information necessary for the forecasting and analytical objectives is
processed.

## Final privacy status

Complete: no PII exists in the dataset.
