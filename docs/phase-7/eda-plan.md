# Phase 7 — Exploratory Data Analysis Plan

## Purpose

Phase 7 explores the integrated retail dataset to identify demand patterns,
relationships, distributions, anomalies, and forecasting-relevant behaviour.

The analysis is descriptive and does not train forecasting models.

## Primary dataset

`data/processed/integrated_retail_data.csv`

## Analytical grain

The integrated dataset preserves:

`date + item_id + store_id`

as the canonical sales grain.

## EDA questions

### Overall demand

* How much demand is represented?
* What is the total revenue?
* How many stores and items are represented?
* What is the temporal coverage?

### Temporal behaviour

* How does demand change over time?
* Which months have higher or lower demand?
* Are there visible seasonal or trend-like patterns?

### Store behaviour

* Which stores generate the most demand?
* How different are store demand levels?

### Product behaviour

* Which departments contribute the most demand?
* Which products have the highest aggregate demand?
* Is demand concentrated among a small number of products?

### Price behaviour

* How does price vary?
* Is there an observable relationship between price and quantity?

### Promotion behaviour

* How frequently do promotion records occur?
* How does demand behave during promotion activity?

### Markdown behaviour

* How frequently are markdown records present?
* Is markdown activity associated with unusual demand patterns?

### Online channel

Online quantity and sales value are examined separately.

They are not added to the physical sales target.

## Analysis outputs

* Overall EDA summary
* Monthly demand summary
* Store summary
* Department summary
* Top-item summary
* Correlation summary
* Descriptive findings
* Exploratory visualizations

## Interpretation rule

EDA findings describe associations and patterns.

They do not establish causation.

## Reproducibility

The complete analysis is executed by:

`scripts/exploratory_data_analysis.py`

The script uses a fixed random seed when sampling data for correlation analysis.
