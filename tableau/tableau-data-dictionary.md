# Tableau Data Dictionary

## Primary Tableau Source

The Tableau dashboard should use a compact analytical source rather than the
full raw dataset where possible.

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

## Fields Actually Connected

Verified against the committed workbook on 19 September 2026. The workbook
connects to three sources, and every field it references is present in them.

| Source | Fields |
|---|---|
| `inventory_scenarios.csv` | `store_id`, `model`, `configuration`, `season_length`, `order`, `lead_time_days`, `service_level`, `z_value`, `mean_daily_demand`, `std_daily_demand`, `expected_lead_time_demand`, `safety_stock`, `reorder_point` |
| `inventory_variability_summary.csv` | `store_id`, `mean_daily_demand`, `std_daily_demand`, `variance_daily_demand`, `p90_daily_demand`, `p95_daily_demand`, `p99_daily_demand`, `coefficient_of_variation` |
| `tuned_validation_results.csv` | `store_id`, `model`, `configuration`, `season_length`, `order`, `validation_start`, `validation_end`, `forecast_horizon`, `rmse`, `mape_percent` |

The workbook's cached copy of these schemas is reconciled against the current
CSV headers by `scripts/sync_tableau_workbook_schema.py`. Before that repair
the cached schema predated the addition of `season_length` and `order`, which
had shifted the position of every later field.

`season_length` is numeric where a seasonal model applies and empty
thereafter; `order` is empty throughout and is therefore typed as text.