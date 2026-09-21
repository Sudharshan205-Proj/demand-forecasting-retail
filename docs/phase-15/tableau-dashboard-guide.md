# Phase 15 — Tableau Dashboard Guide

## Objective

Communicate the project's retail demand forecasting and inventory-planning
findings through an interactive Tableau Public dashboard.

**Delivered:** `tableau/Retail_Demand_Forecasting.twb`, authored with Tableau
2026.2.2, published at

`https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning`

with the canonical URL

`https://public.tableau.com/app/profile/sudharshan.moodley/viz/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning`.

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
directory is an absolute local path, so opening the workbook on another machine
requires re-pointing the three sources.

## Workbook structure

The workbook's structure — the three connections and their field types, every
field's role and encoding, the six worksheets, the `KPI Summary` row, the
dashboard layout and interactions — is recorded in
[`../../tableau/tableau-dashboard-specification.md`](../../tableau/tableau-dashboard-specification.md)
and
[`../../tableau/tableau-data-dictionary.md`](../../tableau/tableau-data-dictionary.md),
against Tableau 2026.2.2, the build the workbook declares.

The committed `tableau/Retail_Demand_Forecasting.twb` holds the three data
sources, the five chart worksheets, the `KPI Summary` row, the dashboard and the
`<repository-location>` publication stamp. The five hidden fields recorded in
`tableau/tableau-data-dictionary.md` are a deliberate decision — each source's
extract omits them, which is why the workbook's cached schema blocks differ by
source.

## Worksheets

| Worksheet | Chart | Measure | Dimension |
|---|---|---|---|
| Average Demand by Store | Horizontal bar | Mean daily demand | Store |
| Relative Demand Variability | Horizontal bar | Coefficient of variation | Store |
| Reorder-Point Scenarios | Line | Reorder point | Lead time, by store |
| Forecast Evidence | Comparison of validated metrics | Validation RMSE / MAPE | Store |
| Safety Stock Scenarios | Line | Safety stock | Lead time, by service level |
| `KPI Summary` | Three text tiles | bare `MAX(mean daily demand)`, `MAX(std ÷ mean)`, `MIN(MAPE)` | none — each tile shows the extreme value |

All six worksheets and the dashboard that arranges them are present in the
committed workbook, and `KPI Summary` sits in the dashboard's top row. The sheet's
tiles read `29,711 units/day`, `0.3801` and `8.14%` under their KPI-name headers.

## Filters

Six filter cards are applied across the worksheets (Tableau writes 11 `<filter>`
elements for them: the lead-time family is placed on both scenario sheets in its
discrete and continuous forms, and the `KPI Summary` sheet carries its own
`Measure Names` filter):

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

Every displayed numerical value is traceable to a project analytical output.

The workbook's cached field schema is reconciled against the current CSV headers
by `scripts/sync_tableau_workbook_schema.py`, and the test suite asserts that
every `<columns>` block lists the current headers in order with contiguous
ordinals. The values charted by the static workflow are reconciled against the
same three sources, so the numbers a reader compares across the two media come
from one set of files.

The `Reorder-Point Scenarios` worksheet carries a **fixed 7 → 28** lead-time
range, matching the smallest and largest assumed lead times, so the axis cannot
imply observations between them.

## Publication

A Tableau Public URL is recorded because the workbook has been published and the
URL verified. It appears above and in
[`visualization-results.md`](visualization-results.md).

The published view is the workbook committed here: the `<repository-location>`
stamp it carries, its workbook id and its view slug all match the URL, and the
extracts it embeds were rebuilt at publish time. Their values match the current
CSVs, so the live view and the static figures in this repository agree as at the
publish date. A later pipeline re-run would change the repository's figures and
not the live view until the workbook is re-published, which needs Tableau Desktop.
