# Tableau Data Dictionary

## Primary Tableau Source

The dashboard uses compact analytical sources rather than the full raw dataset.

## Core Fields

| Field | Meaning |
|---|---|
| store_id | Store identifier |
| mean_daily_demand | Average observed daily physical demand |
| median_daily_demand | Median observed daily physical demand |
| min_daily_demand | Minimum observed daily demand |
| max_daily_demand | Maximum observed daily demand |
| coefficient_of_variation | Relative demand variability |
| std_daily_demand | Daily demand standard deviation |
| lead_time_days | Assumed inventory lead time |
| service_level | Assumed service-level probability |
| z_value | Standard-normal service-level factor |
| expected_lead_time_demand | Expected demand during assumed lead time |
| safety_stock | Scenario safety stock |
| reorder_point | Scenario reorder point |
| model | Forecasting model associated with the scenario |
| configuration | Forecasting configuration |

## Interpretation

Inventory fields represent planning scenarios.

They do not represent actual supplier contracts, inventory policies or
procurement requirements.

## Fields Connected

The workbook connects to three sources, and every field it references is present
in them.

| Source | Fields | Hidden in the Data pane |
|---|---|---|
| `inventory_scenarios.csv` | `store_id`, `model`, `configuration`, `season_length`, `order`, `lead_time_days`, `service_level`, `z_value`, `mean_daily_demand`, `std_daily_demand`, `expected_lead_time_demand`, `safety_stock`, `reorder_point` | none |
| `inventory_variability_summary.csv` | `store_id`, `mean_daily_demand`, `std_daily_demand`, `variance_daily_demand`, `p90_daily_demand`, `p95_daily_demand`, `p99_daily_demand`, `coefficient_of_variation` | `p90_daily_demand`, `p95_daily_demand`, `p99_daily_demand` |
| `tuned_validation_results.csv` | `store_id`, `model`, `configuration`, `season_length`, `order`, `validation_start`, `validation_end`, `forecast_horizon`, `rmse`, `mape_percent` | `season_length`, `order` |

Five fields in total are hidden, every one of them unused by every sheet and
tooltip.

The workbook's cached copy of these schemas is reconciled against the current CSV
headers by `scripts/sync_tableau_workbook_schema.py`.

Each source carries **two** cached descriptions, and they differ by design: the
live textscan relation lists every CSV column in header order, while the extract
omits the five hidden fields above and numbers its own columns continuously. The
reconciliation therefore compares the live block against the full header order
and the extract block against the visible subset; it never re-introduces a hidden
field. See
[`../docs/phase-15/visualization-results.md`](../docs/phase-15/visualization-results.md).

`season_length` is numeric where a seasonal model applies and empty thereafter —
populated in 9 of the 36 scenario rows and 1 of the 4 validation rows (Store 4's
seasonal-naive configuration). The sync script infers it as `real` and the
workbook declares `integer`; reconciliation preserves a declared type, so either
is stable. `order` is empty throughout and is therefore typed as text, which is
also what an all-empty column infers to.

## Field Roles and Renames

Every field is renamed so that the unit and the caveat travel with the mark, the
axis and the tooltip. The rename is part of the labelling requirement, not
cosmetics; the underlying CSV header is unchanged and the cached schema is
reconciled against the header, not the display name.

| Original field | Tableau name | Role | Aggregation |
|---|---|---|---|
| `store_id` | `Store` | Dimension, integer, discrete | — |
| `mean_daily_demand` (variability) | `Avg Daily Demand (units)` | Measure, continuous | Average |
| `std_daily_demand` | `Std Dev of Daily Demand (units)` | Measure, continuous | Average |
| `coefficient_of_variation` | `Demand Variability (CV = std ÷ mean)` | Measure, continuous | Average |
| `variance_daily_demand` | `Daily Demand Variance (units²)` | Measure, continuous | Average |
| `p90_daily_demand` | `P90 Daily Demand (units)` | Measure, continuous | Average |
| `p95_daily_demand` | `P95 Daily Demand (units)` | Measure, continuous | Average |
| `p99_daily_demand` | `P99 Daily Demand (units)` | Measure, continuous | Average |
| `lead_time_days` | `Lead Time (days) — assumption` | Dimension, integer, continuous on the axis | — |
| `service_level` | `Service Level — assumption` | Dimension, decimal, discrete | — |
| `z_value` | `Service-Level Z Factor` | Measure, continuous | Average |
| `expected_lead_time_demand` | `Expected Demand During Lead Time (units)` | Measure, continuous | Average |
| `safety_stock` | `Scenario Safety Stock (units)` | Measure, continuous | Average |
| `reorder_point` | `Scenario Reorder Point (units)` | Measure, continuous | Average |
| `model` | `Model` | Dimension, text | — |
| `configuration` | `Configuration` | Dimension, text | — |
| `season_length` | `Season Length (days) — not populated for every store` | Measure, decimal (partly populated) | Average |
| `order` | `Order (p,d,q) — not populated` | Dimension, text | — |
| `validation_start` | `Validation Start` | Dimension, date, discrete | — |
| `validation_end` | `Validation End` | Dimension, date, discrete | — |
| `forecast_horizon` | `Validation Horizon (days)` | Measure, integer | Average |
| `rmse` | `Validation RMSE (units — not comparable across stores)` | Measure, continuous | Average |
| `mape_percent` | `Validation MAPE (%)` | Measure, continuous | Average |

`inventory_demand_summary.csv` also carries a `mean_daily_demand` column. That
file is **not** one of the three connected sources, so the rename collision does
not arise in the workbook. The training-day caveat that file supplies (532 days
for Stores 1–3, 60 for Store 4) is carried as static text, because `training_days`
does not exist in any connected source.

## Hidden Fields

Exactly **five** fields are hidden in the workbook:

| Field | Source | Why it is hidden |
|---|---|---|
| `Order (p,d,q) — not populated` | Validation Results | Empty in all four rows |
| `Season Length (days) — not populated for every store` | Validation Results | Populated for one store (`seasonal_naive`, 7 days); not comparable across the set |
| `P90 Daily Demand (units)` | Store Variability | Percentile not charted; the mean and standard deviation carry the variability story |
| `P95 Daily Demand (units)` | Store Variability | As above |
| `P99 Daily Demand (units)` | Store Variability | As above |

Hidden fields remain in the data source, so they stay addressable by a tooltip or
a reference line, but they do not clutter the Data pane. Everything else stays
visible because a tooltip reads it: `Daily Demand Variance (units²)`,
`Service-Level Z Factor` and `Expected Demand During Lead Time (units)` are the
workings behind charted values, `Configuration` names the selected estimator, and
`Validation Start`, `Validation End` and `Validation Horizon (days)` date and scope
the evidence.

**The five hidden fields are absent from each source's extract**, which is why the
workbook's extract blocks list 8 and 5 columns where the live relations list 10
and 8. That is a deliberate data-source decision, not drift.

## Aggregation

All measures default to **Average**, and that is what the sheets use:
`Reorder-Point Scenarios` carries `AVG(Scenario Reorder Point (units))` filtered to
the 95 % baseline and `Safety Stock Scenarios` carries `AVG(Scenario Safety Stock
(units))`. Every row of all three sources is already an aggregate — a scenario row
is one store at one lead time and one service level — so `Sum` would add scenarios
together.

## Number Formats

| Field | Format |
|---|---|
| Demand and inventory unit measures | Number, 0 decimals, thousands separator |
| `Demand Variability (CV = std ÷ mean)` | Number, 4 decimals |
| `Validation RMSE (units — not comparable across stores)` | Number, 0 decimals |
| `Validation MAPE (%)` | Number, 2 decimals with a `%` suffix (`mape_percent` already holds 8.14, so the percentage format would print 814 %) |
| `Service Level — assumption` | Percentage format, 0 decimals (`service_level` holds 0.95, so it prints 95 %) |

The two percentage fields need opposite treatments; that is why they are
documented separately.

**The `KPI Summary` tiles are the exception: they are numeric aggregates, not the
per-field-formatted measures above.** Each of the three measures is a bare
aggregate — `MAX([mean_daily_demand])`, `MAX([std_daily_demand] /
[mean_daily_demand])`, `MIN([mape_percent])` — on a Text mark, and each tile
carries its own cell-level format (`*#,##0 "units/day"`, `*0.0000`, `*0.00"%"`).
The tiles therefore read `29,711 units/day`, `0.3801` and `8.14%` under their
KPI-name headers.
