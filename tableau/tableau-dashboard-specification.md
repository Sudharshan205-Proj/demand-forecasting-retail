# Tableau Dashboard Specification

## Dashboard

**Name:** Retail Demand Forecasting & Inventory Planning

## Audience

Retail operations and inventory-planning stakeholders.

## Primary Question

Where is demand concentrated, how variable is it, what forecasting evidence is
available, and how do inventory scenarios change under different planning
assumptions?

## Layout

### Top

Headline KPIs:

- highest average-demand store;
- highest variability store;
- strongest validated result, charted as MAPE — the relative measure, because
  RMSE is scale-bound and not comparable across stores.

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

Forecasting evidence.

## Filters

- Store
- Lead time
- Service level

## Interaction

Selecting a store updates the relevant scenario views.

Changing lead time or service level updates the inventory scenario visualization.

## Accessibility

The dashboard remains understandable without relying exclusively on colour.

Important values are directly labelled or available through clear tooltips.

## Storytelling

The dashboard moves from:

Demand → Variability → Forecast Evidence → Inventory Planning → Action.

## As Built

### Measured state of the committed workbook

Measured from `tableau/Retail_Demand_Forecasting.twb`:

| Element | Value |
|---|---|
| Data sources | 3 — `tuned_validation_results.csv`, `inventory_variability_summary.csv`, `inventory_scenarios.csv` |
| Worksheets | **6** — Average Demand by Store; Relative Demand Variability; Forecast Evidence; Reorder-Point Scenarios; Safety Stock Scenarios; **KPI Summary** |
| Dashboards | **1** — *Retail Demand Forecasting & Inventory Planning*, fixed 1600 × 900 |
| Dashboard zones | 41 `<zone>` elements — 23 in the desktop layout (6 chart zones, 6 filter zones, 2 colour-legend zones, the title and the `Filters:` label, and 7 layout containers) plus 18 in the auto-generated phone layout |
| Filters | 11 `<filter>` elements across the sheets for the six intended cards; 6 filter zones in the desktop layout over 5 field/source combinations |
| Marks | 3 Bar, 2 Line, **1 Text** (the `KPI Summary` tiles) |
| Field instances | 46 `<column-instance>` elements |
| Hidden fields | 5 — `order` and `season_length` (Validation Results); `p90`, `p95`, `p99_daily_demand` (Store Variability) |
| `<repository-location>` | present — `id='Retail_Demand_Forecasting'`, `path='/workbooks'`, `revision='1.0'` |
| Published URL | `https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |
| Authoring build | Tableau 2026.2.2 (20262.26.0819.2015) |

All six worksheets are fully built — shelves, mark types, encodings, tooltips,
mark-label settings, shelf sorts, store filters and the KPI tiles are all present
— and the workbook carries the dashboard and the publication stamp. The published
workbook is the workbook committed here.

### Element notes

Two elements are built with a narrower shape than the wording above implies:

| Element | Requirement | State |
|---|---|---|
| Headline KPIs (top row) | three tiles — highest average-demand store, highest relative-variability store, strongest validated result | **Built** as the sixth worksheet `KPI Summary`, computed from the CSVs by blended measures. The tiles read `29,711 units/day`, `0.3801` and `8.14%`: each shows the extreme value under its KPI-name header. The evidence tile is **MAPE**, the relative measure, not RMSE — RMSE is scale-bound and appears in the `Forecast Evidence` tooltip instead — and the sheet's tooltip definition is one literal sentence covering all three tiles, because Tableau does not permit `[Measure Names]` inside a calculation |
| `KPI Summary` tooltip | the KPI name, its value, a definition and the source | **Built.** The tooltip carries the KPI name, its value, a plain-text definition and the source CSV |

The rest of this specification is met as built: the narrative order, the three
filter families, the store interaction and the accessibility requirements.
Attributing an outcome to a store — which the charts may not do — appears in no
tile or tooltip.

### Aggregation rule

Every row of all three sources is already an aggregate: one row of
`inventory_scenarios.csv` is a single store at a single lead time and service
level, and one row of `inventory_variability_summary.csv` is a store's whole
history. Summing them is meaningless. All measures therefore default to
**Average**, and that is what the sheets use: `Reorder-Point Scenarios` carries
`AVG(Scenario Reorder Point (units))` filtered to the 95 % baseline, and
`Safety Stock Scenarios` carries `AVG(Scenario Safety Stock (units))` with the
service level on colour. A plotted point on the safety-stock sheet is the mean
across the stores the filter selects, not a total: at 14 days and all four stores
selected the three lines read 22,735 (90 %), 29,180 (95 %) and 41,270 (99 %).

### Chart encoding decisions

| Decision | Rationale |
|---|---|
| The workbook charts MAPE as its cross-store accuracy measure, while the static figure charts the lowest validation RMSE | RMSE is measured in demand units and is not comparable across stores of different size, so the workbook uses the relative measure and the static figure states the scale-bound caveat on its axis. The two differ deliberately and say so |
| The Reorder-Point Scenarios rail is filtered to the 95 % baseline service level | Otherwise the chart would plot a sum across service-level scenarios rather than a reorder point |
| The lead-time axis is fixed at 7 → 28 days | Those are the smallest and largest assumed lead times, so the axis cannot imply observations between them |
| The Safety Stock Scenarios sheet colours by service level and filters to one store | Each scenario sheet then carries one grouping variable and one constant |
| Five fields are hidden in the sources | `order` and `season_length` are configuration metadata; `p90`, `p95` and `p99_daily_demand` are percentile fields the sheets do not chart. Each source's extract omits them by design |

Each of these is recorded in
[`../docs/phase-15/visualization-results.md`](../docs/phase-15/visualization-results.md).
