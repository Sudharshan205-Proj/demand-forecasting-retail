# Phase 15 — Tableau Dashboard Guide

## Objective

Create an interactive Tableau Public dashboard communicating the project's
retail demand forecasting and inventory-planning findings.

## Recommended Dashboard

### Dashboard title

Retail Demand Forecasting & Inventory Planning

### Primary sections

1. Demand Overview
2. Store Demand Comparison
3. Demand Variability
4. Forecast Evidence
5. Inventory Scenario Planning

## Recommended Filters

Where supported by the source data:

- Store
- Lead Time
- Service Level
- Forecast Model

Filters should be limited to those that materially improve exploration.

## Recommended Worksheets

### Worksheet 1 — Average Demand by Store

Chart:

- horizontal bar chart.

Measure:

- mean daily demand.

Dimension:

- store.

### Worksheet 2 — Demand Variability by Store

Chart:

- horizontal bar chart.

Measure:

- coefficient of variation.

Dimension:

- store.

### Worksheet 3 — Reorder-Point Scenarios

Chart:

- line chart.

X-axis:

- lead time.

Y-axis:

- reorder point.

Grouping:

- service level and/or store.

### Worksheet 4 — Forecast Evidence

Chart:

- comparison of validated model metrics.

The dashboard should clearly identify the evaluation metric.

### Worksheet 5 — Inventory Scenario Table

Include:

- store;
- model status;
- lead time;
- service level;
- expected lead-time demand;
- safety stock;
- reorder point.

## Design Requirements

Use:

- descriptive titles;
- readable units;
- consistent terminology;
- concise annotations;
- accessible visual distinctions;
- sensible spacing.

Avoid:

- unnecessary 3D charts;
- decorative graphics;
- excessive filters;
- misleading axes;
- unexplained abbreviations;
- unsupported causal statements.

## Validation

Every displayed numerical value should be traceable to a project analytical
output.

## Publication

A Tableau Public URL will only be recorded after the workbook has actually
been published and the URL has been verified.