# Data Strategy

## Objective

Identify the data required to forecast retail demand and investigate demand drivers.

## Required Core Data

### Sales

The sales dataset should ideally provide:

- Date
- Product identifier
- Store/location identifier where available
- Quantity sold/demand
- Price where available
- Revenue where available

### Promotions

Where available:

- Promotion indicator
- Promotion type
- Discount
- Promotion dates

### Holidays

Where available:

- Date
- Holiday indicator
- Holiday name
- Holiday type

## Optional Supporting Variables

Depending on the selected dataset:

- Store characteristics
- Product category
- Pricing
- Weather
- Events
- Season indicators

Additional variables will only be used if they are relevant and appropriately sourced.

## Data Source Requirements

The source must be assessed for:

- Reliability
- Originality
- Comprehensiveness
- Currency
- Citation

These correspond to the course's ROCCC data-quality framework.

## Dataset Selection Criteria

The selected dataset should:

1. Contain meaningful temporal coverage.
2. Contain sufficient observations for time-series analysis.
3. Provide a clear demand target.
4. Allow aggregation at a meaningful retail level.
5. Support historical/future separation.
6. Be legally and ethically appropriate to use.
7. Have sufficient documentation.
8. Allow reproducible analysis.

## Data Privacy

Public/open datasets are preferred.

Personally identifiable information should not be required.

If a dataset contains sensitive fields, they must be assessed and handled appropriately.

## Data Versioning

The project will document:

- Source
- Download date
- Dataset version where available
- File name
- File size where useful
- Checksums where useful
- License
- Known limitations

## Data Storage

Raw data will remain immutable.

Processed datasets will be generated through documented processing pipelines.

Large datasets will not automatically be committed to Git.

## Data Quality

Before modeling, the project must inspect:

- Dimensions
- Columns
- Data types
- Missing values
- Duplicate records
- Date range
- Chronological ordering
- Target distribution
- Invalid values
- Outliers

## Data Leakage

Time-series data must preserve temporal order.

Future information must never be allowed to influence historical training observations.