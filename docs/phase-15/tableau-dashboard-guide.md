# Phase 15 — Tableau Dashboard Guide

## Objective

Create an interactive Tableau Public dashboard communicating the project's
retail demand forecasting and inventory-planning findings.

**Delivered:** `tableau/Retail_Demand_Forecasting.twb`, authored with Tableau
2026.2.2, published at

`https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning`

(verified HTTP 200 on 19 September 2026; canonical URL
`https://public.tableau.com/app/profile/sudharshan.moodley/viz/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning`).

## Dashboard

**Title:** Retail Demand Forecasting & Inventory Planning

**Sections, in narrative order:**

1. Demand Overview
2. Store Demand Comparison
3. Demand Variability
4. Forecast Evidence
5. Inventory Scenario Planning

## Data Sources

| Source | Rows | Role |
|---|---|---|
| `inventory_scenarios.csv` | 36 | Scenario reorder points, filters and the scenario table |
| `inventory_variability_summary.csv` | 4 | Store-level variability |
| `tuned_validation_results.csv` | 4 | Forecast validation evidence |

The workbook connects with Tableau's textscan connector. Each connection's
directory is an absolute local path, so opening the workbook on another
machine requires re-pointing the three sources.

## Worksheets

| Worksheet | Chart | Measure | Dimension |
|---|---|---|---|
| Average Demand by Store | Horizontal bar | Mean daily demand | Store |
| Relative Demand Variability | Horizontal bar | Coefficient of variation | Store |
| Reorder-Point Scenarios | Line | Reorder point | Lead time, by store |
| Forecast Evidence | Comparison of validated metrics | Validation RMSE / MAPE | Store |
| Safety Stock Scenarios | Line | Safety stock | Lead time, by service level |

All five worksheets are present in the committed workbook, together with the
dashboard that arranges them.

## Filters

Six filters are applied across the worksheets:

- **Store** — the four stores.
- **Lead time** — 7 to 28 days.
- **Service level** — 0.90 to 0.99.

Filters are limited to those that materially improve exploration.

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

*Performed:* the workbook's cached field schema is reconciled against the
current CSV headers by `scripts/sync_tableau_workbook_schema.py`, and the test
suite asserts that every `<columns>` block lists the current headers in order
with contiguous ordinals. The values charted by the static workflow are
reconciled against the same three sources, so the numbers a reader compares
across the two media come from one set of files.

*Open item:* the `Reorder-Point Scenarios` worksheet uses a fixed axis range
whose lead-time minimum sits slightly below zero. It should be reset to start
at the smallest assumed lead time.

## Publication

A Tableau Public URL is recorded only after the workbook has actually been
published and the URL verified. That condition is now met, and the URL is
recorded above and in `visualization-results.md`.

The published view was published before the Phase 17 audit and embeds extracts
built on 8 September 2026. Refreshing those extracts and re-publishing
requires Tableau Desktop; until then the live view may show pre-audit values
while the static figures in this repository are current.

## Phase 17 Re-Audit Note

This guide previously described the dashboard as a recommendation. It now
describes the workbook that exists: its five worksheets, six filters, three
data sources, published URL and the two open items above.
