# Data Source Assessment

## Dataset

Retail Sales Forecasting Data

## Source

Kaggle

https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data

## Source Classification

External dataset published through Kaggle.

## Business Relevance

The dataset is directly relevant to the project because its stated purpose is retail demand forecasting.

The available sales data provides a candidate historical demand target.

Store and product identifiers support analysis at multiple retail levels.

Markdown and price-history information may provide explanatory information related to pricing and promotional activity.

## Known Source Characteristics

The Kaggle description states that the dataset covers four stores over approximately 25 months.

It provides:

- Store sales
- Online sales
- Product identifiers
- Daily quantities
- Prices
- Sales amounts
- Markdown information
- Price-history information
- A one-month holdout period

## ROCCC Assessment

### Reliable

Initial assessment:

VERIFIED

The source is hosted on Kaggle and has a documented dataset description; the actual data was inspected and found structurally usable, with the file-format characteristics documented in the dataset inventory.

### Original

VERIFIED

The dataset is published by the Kaggle account `svizor`.

### Comprehensive

VERIFIED

The dataset contains several related retail data sources (sales, online, markdowns, price history, discounts, catalog, stores, actual matrix) rather than only one sales table.

Coverage and completeness were verified from the downloaded files.

### Current

VERIFIED FOR HISTORICAL FORECASTING

The dataset represents historical retail activity rather than current operational retail data.

Its suitability for this internship project is based on historical forecasting rather than real-time forecasting.

### Cited

YES

The Kaggle dataset page provides the source and dataset description.

## Relevance to Project Requirements

| Requirement | Initial Assessment |
|---|---|
| Historical sales | Available — VERIFIED |
| Product identifier | Available — VERIFIED |
| Store identifier | Available — VERIFIED |
| Demand quantity | Available — VERIFIED |
| Pricing | Available — VERIFIED |
| Markdown/promotional information | Available — VERIFIED (`markdowns.csv`, `discounts_history.csv`) |
| Explicit holiday variable | Not established — VERIFIED ABSENT |
| Forecasting target | Confirmed `quantity` in later phases |
| Time series | Available through `date` — VERIFIED |
| Holdout period | Reported by source; not present in raw files |
| Multiple related series | Available — VERIFIED |
| Inventory levels | Not reported in source description |
| Supplier information | Not reported |
| Real-time data | No |
| Customer personal information | Not present in inspected fields |

## Important Interpretation Rules

The presence of markdown data must not automatically be interpreted as proof of causal promotional uplift.

The project will initially describe these variables as associations or explanatory features.

Holiday information must not be claimed unless the downloaded dataset actually contains a holiday field or an appropriate external holiday source is introduced later.

## Potential Biases

Potential limitations include:

- The dataset represents a specific retailer context.
- Only four stores are represented according to the source description.
- The observed historical period may not represent all retail environments.
- Online and physical-store sales may represent different demand-generating processes.
- Historical pricing and markdown policies may not generalize to future pricing strategies.
- The dataset may contain missing or irregular observations.

These are hypotheses for assessment, not confirmed findings.

## Privacy

The inspected fields concern retail products, stores, prices, quantities and dates.

No customer-level personally identifiable information is present in the inspected files.

## Licensing

VERIFIED

CC BY-NC-SA 4.0


## Final Assessment

The dataset is confirmed as the project dataset because it provides:

- Multiple retail time series
- Product-level information
- Store-level information
- Daily demand observations
- Pricing information
- Markdown information
- Promotion/discount information
- Product/store coverage matrix
- A holdout forecasting period (per source)

Structural characteristics (index column, catalog ragged lines, future-dated discounts) are documented and handled by later phases.