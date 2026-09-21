# Data Source Assessment

## Dataset

Retail Sales Forecasting Data

## Source

Kaggle — <https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data>

## Source classification

External dataset published through Kaggle.

## Business relevance

The dataset is directly relevant to the project because its stated purpose is
retail demand forecasting.

The available sales data provides the historical demand target. Store and
product identifiers support analysis at multiple retail levels. Markdown and
price-history information provides explanatory information related to pricing
and promotional activity.

## Source characteristics

The dataset covers four stores over approximately 25 months and provides:

- Store sales
- Online sales
- Product identifiers
- Daily quantities
- Prices
- Sales amounts
- Markdown information
- Price-history information
- A one-month holdout period (described by the source; not present in the public
  training files)

## ROCCC assessment

| Criterion | Assessment | Basis |
|---|---|---|
| Reliable | Yes | Hosted on Kaggle with a documented description; the actual data was inspected and found structurally usable, with the file-format characteristics documented in [`dataset-inventory.md`](dataset-inventory.md) |
| Original | Yes | Published by the Kaggle account `svizor` |
| Comprehensive | Yes | Contains several related retail data sources (sales, online, markdowns, price history, discounts, catalog, stores, actual matrix) rather than a single sales table; coverage verified from the downloaded files |
| Current | Yes, for historical forecasting | Represents historical retail activity rather than current operational data; suitable for historical rather than real-time forecasting |
| Cited | Yes | The Kaggle dataset page provides the source and dataset description |

## Relevance to project requirements

| Requirement | Assessment |
|---|---|
| Historical sales | Available |
| Product identifier | Available |
| Store identifier | Available |
| Demand quantity | Available |
| Pricing | Available |
| Markdown/promotional information | Available (`markdowns.csv`, `discounts_history.csv`) |
| Explicit holiday variable | Not available — no holiday field exists in any inspected file |
| Forecasting target | `quantity` |
| Time series | Available through `date` |
| Holdout period | Reported by the source; not present in the raw files |
| Multiple related series | Available |
| Inventory levels | Not provided |
| Supplier information | Not provided |
| Real-time data | No |
| Customer personal information | Not present in the inspected fields |

## Interpretation rules

Markdown data is not interpreted as proof of causal promotional uplift. The
project describes these variables as associations or explanatory features.

No holiday effect is claimed, because the dataset contains no holiday field.

## Potential biases

- The dataset represents a specific retailer context.
- Only four stores are represented.
- The historical period may not represent all retail environments.
- Online and physical-store sales may represent different demand-generating
  processes.
- Historical pricing and markdown policies may not generalize to future pricing
  strategies.
- The dataset contains missing and irregular observations, catalogued in
  [`initial-data-assessment.md`](initial-data-assessment.md).

## Privacy

The inspected fields concern retail products, stores, prices, quantities and
dates. No customer-level personally identifiable information is present.

## Licensing

CC BY-NC-SA 4.0.

## Final assessment

The dataset is the project dataset because it provides multiple retail time
series, product-level and store-level information, daily demand observations,
pricing, markdown and promotion/discount information, a product/store coverage
matrix, and a source-described holdout period. Its structural characteristics
(index column, catalog ragged lines, future-dated discounts) are documented and
handled by the later phases.
