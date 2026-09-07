# Phase 8 — Statistical Analysis Methodology

## Data source

The analysis uses:

`data/processed/integrated_retail_data.csv`

The integrated dataset contains the cleaned physical-store sales data and
associated store, catalog, pricing, markdown, promotion and online-channel
information.

## Processing strategy

The integrated dataset is approximately 1.28 GB and is therefore processed
using pandas chunked CSV reading.

The complete source dataset is not loaded into memory at once.

## Demand

Physical demand is represented by:

`quantity`

Online quantity is retained as a separate variable and is not added to
physical-store demand.

## Descriptive statistics

Daily aggregate demand is summarized using:

- mean;
- median;
- standard deviation;
- minimum;
- maximum;
- coefficient of variation.

The coefficient of variation is:

`standard deviation / mean`

and is useful for comparing relative demand variability.

## Correlation

Pearson correlation is used to quantify linear association between numeric
variables.

Correlation values range from -1 to +1.

Correlation does not establish causation.

## Price-demand analysis

Price and quantity are evaluated using:

- Pearson correlation;
- p-value;
- simple linear regression;
- regression slope;
- R-squared.

This is an analytical relationship, not a causal elasticity estimate.

## Promotion analysis

Records are separated according to whether a positive promotional
discount rate is present.

Demand distributions are compared between groups.

A Mann-Whitney U test is used where sufficient observations are available.

## Trend analysis

Aggregate daily demand is regressed against chronological observation index.

The resulting slope indicates the estimated linear change per day.

## Autocorrelation

Demand autocorrelation is calculated for recent daily lags.

This provides evidence about temporal dependence and whether previous demand
contains information about current demand.

## Statistical interpretation

Results are interpreted using both:

1. statistical significance; and
2. practical magnitude.

A small p-value alone does not establish business importance.

## Forecasting boundary

No final forecasting model is trained in Phase 8.

The statistical findings will inform subsequent forecasting methodology.