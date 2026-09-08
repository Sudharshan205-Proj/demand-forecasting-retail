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