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