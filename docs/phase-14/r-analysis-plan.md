# Phase 14 — R Analysis Plan

## Purpose

This phase introduces an independent R/RStudio analytical workflow into the
retail demand forecasting project.

R is used for:

- analytical transformation;
- descriptive analysis;
- demand variability analysis;
- inventory scenario analysis;
- visualization;
- reproducible reporting.

Python remains the primary forecasting implementation.

## Inputs

The analysis consumes compact outputs generated during Phase 13:

- inventory_demand_summary.csv
- inventory_variability_summary.csv
- inventory_scenarios.csv
- forecast_inventory_insights.csv

The full raw dataset is not reloaded unnecessarily.

## Analytical Tasks

### 1. Demand Analysis

Calculate and examine:

- mean daily demand;
- median daily demand;
- minimum demand;
- maximum demand;
- total training-period demand;
- coefficient of variation.

### 2. Variability Analysis

Examine:

- standard deviation;
- variance;
- percentile demand;
- coefficient of variation.

### 3. Inventory Scenario Analysis

Examine how reorder-point scenarios change with:

- lead time;
- service level;
- safety stock;
- expected lead-time demand.

### 4. Consistency

Independently reproduce the principal Phase 13 findings.

## Visualization

Use ggplot2 to produce:

- average demand by store;
- demand variability by store;
- reorder-point scenario comparisons.

Faceting is used for store-specific scenario comparisons.

## Reporting

R Markdown provides:

- YAML metadata;
- Markdown narrative;
- executable R code chunks;
- generated tables;
- generated visualizations;
- reproducible HTML reporting.

## Scope Boundary

This phase does not replace the Python forecasting models.

No unsupported production inventory assumptions are introduced.