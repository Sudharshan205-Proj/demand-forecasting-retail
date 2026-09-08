# Phase 15 — Data Storytelling

## 1. Audience

The primary audience is a retail operations or inventory-planning stakeholder
who needs concise evidence about demand and planning risk.

The audience should not need to understand the implementation details of
ARIMA, seasonal-naive forecasting or R programming to interpret the dashboard.

## 2. Context

The project analyses historical retail demand to support forecasting and
inventory-planning decisions.

## 3. Problem

Retail demand varies across stores and over time.

Planning must therefore account for:

- demand level;
- demand variability;
- forecast evidence;
- lead-time assumptions;
- service-level assumptions.

## 4. Evidence

The project has established:

- store-level demand differences;
- relative demand variability;
- validated forecasting evidence;
- scenario reorder points.

## 5. Key Insights

The visualization narrative should emphasize:

1. Where demand is concentrated.
2. Which stores have greater relative variability.
3. Which validated forecasting result provides the strongest validation
   evidence under the project's evaluation metric.
4. How reorder-point scenarios change with assumed lead time and service level.

## 6. Recommendations

Recommendations must remain conditional.

Examples include:

- prioritize high-demand stores for demand-monitoring attention;
- investigate highly variable stores for additional operational context;
- use validated forecasting evidence as an input to planning;
- calibrate scenario reorder points using actual supplier and inventory data.

## 7. Limitations

The dataset does not provide all operational information required for
production inventory decisions.

Therefore the dashboard must not present scenario reorder points as
mandatory inventory policies.

## 8. Narrative Flow

The intended flow is:

**What is happening?**
→ demand distribution

**Where is it happening?**
→ store comparison

**How predictable/variable is it?**
→ variability and forecast evidence

**What could this mean for planning?**
→ inventory scenarios

**What should be done next?**
→ conditional recommendations and operational-data requirements