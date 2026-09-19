# Tableau Dashboard Specification

## Dashboard

**Name:** Retail Demand Forecasting & Inventory Planning

## Audience

Retail operations and inventory-planning stakeholders.

## Primary Question

Where is demand concentrated, how variable is it, what forecasting evidence
is available, and how do inventory scenarios change under different planning
assumptions?

## Layout

### Top

Headline KPIs:

- highest average-demand store;
- highest variability store;
- strongest validated validation-RMSE result.

### Middle

Store comparison:

- average demand;
- coefficient of variation.

### Lower section

Inventory scenario analysis:

- lead time;
- service level;
- reorder point.

### Supporting section

Forecasting evidence and limitations.

## Filters

- Store
- Lead time
- Service level

Additional filters should only be added if they improve the user experience.

## Interaction

Selecting a store should update relevant scenario views.

Changing lead time or service level should update the inventory scenario
visualization.

## Accessibility

The dashboard must remain understandable without relying exclusively on
colour.

Important values should be directly labelled or available through clear
tooltips.

## Storytelling

The dashboard should move from:

Demand → Variability → Forecast Evidence → Inventory Planning → Action.

## As Built

Verified against `tableau/Retail_Demand_Forecasting.twb` on 19 September 2026:

| Element | Count / value |
|---|---|
| Worksheets | 5 — Average Demand by Store; Relative Demand Variability; Reorder-Point Scenarios; Forecast Evidence; Safety Stock Scenarios |
| Dashboard | 1 — *Retail Demand Forecasting & Inventory Planning* |
| Layout zones | 19 |
| Filters | 6 (store, lead time, service level) |
| Field instances | 27 |
| Marks | 3 bar, 2 line |
| Authoring build | Tableau 2026.2.2 |
| Published URL | `https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |

Open item: the Reorder-Point Scenarios worksheet uses a fixed axis range whose
lead-time minimum sits slightly below zero and should be reset to start at the
smallest assumed lead time.