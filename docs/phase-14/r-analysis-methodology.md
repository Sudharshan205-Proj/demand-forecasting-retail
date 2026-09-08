# Phase 14 — R Analysis Methodology

## 1. Analytical Approach

The R analysis uses the compact analytical outputs generated in Phase 13.

This avoids unnecessarily loading the full retail dataset into R while still
providing access to the project's established demand, variability and
inventory-planning results.

## 2. Tidy Data Workflow

The analysis uses tidyverse and dplyr operations to:

1. load analytical datasets;
2. select relevant variables;
3. join demand and variability summaries;
4. group inventory scenarios;
5. calculate summary statistics;
6. arrange analytical results.

## 3. Demand Analysis

Store-level demand is evaluated using:

- mean daily demand;
- median daily demand;
- minimum daily demand;
- maximum daily demand;
- total quantity;
- training-day count;
- coefficient of variation.

## 4. Variability

Relative variability is represented using the coefficient of variation:

CV = standard deviation / mean

A higher CV indicates greater demand variability relative to the store's
average demand.

## 5. Inventory Scenarios

The analysis uses the Phase 13 scenario framework.

Reorder point:

ROP = expected lead-time demand + safety stock

Safety stock:

SS = z × sigma_daily × sqrt(L)

where:

- z = service-level factor;
- sigma_daily = daily demand standard deviation;
- L = assumed lead time.

Scenario assumptions remain:

- 7-day lead time;
- 14-day lead time;
- 28-day lead time;
- 90% service level;
- 95% service level;
- 99% service level.

## 6. Visualization

ggplot2 is used to demonstrate:

- data-to-aesthetic mapping with aes();
- geometric layers;
- bar charts;
- line charts;
- points;
- faceting;
- labels and titles.

Plots are exported programmatically with ggsave().

## 7. Reproducible Reporting

The R Markdown report combines:

- YAML metadata;
- Markdown narrative;
- R code chunks;
- generated output;
- visualizations;
- interpretation.

## 8. Forecasting Boundary

The R phase does not replace the validated forecasting workflow.

Forecast model selection and tuning remain based on the Python
implementation established in Phases 11 and 12.

## 9. Interpretation

Observed demand statistics describe historical training-period behaviour.

Inventory values are scenario estimates rather than operational requirements.

No causal interpretation is assigned to descriptive relationships.