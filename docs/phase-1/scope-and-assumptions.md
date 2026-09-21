# Scope and Assumptions

## 1. Project scope

The project develops an end-to-end retail demand forecasting system.

## 2. In scope

### Business analysis

- Retail demand problem
- Inventory-planning context
- Stakeholder requirements
- SMART analytical questions
- Hypothesis development

### Data

- Historical sales
- Promotions (available in the dataset)
- Product information
- Store information
- Holidays — recorded as not applicable; no holiday field exists

### Analysis

- Spreadsheet analysis
- SQL analysis
- Python analysis
- R analysis
- Exploratory analysis
- Statistical analysis
- Demand pattern analysis

### Forecasting

- Baseline models
- ARIMA
- An additional permitted forecasting approach (feature-based gradient boosting)
- Time-aware validation
- RMSE
- MAPE
- Forecast comparison

### Communication

- Visualizations
- Tableau dashboard
- Analytical reporting
- Business recommendations
- Presentation

### Engineering

- Reproducible pipeline
- Testing
- Configuration
- Logging
- Application
- Deployment
- Documentation

## 3. Out of scope

The following are not part of the project:

- Real-time inventory integration
- Live ERP integration
- Automatic purchase orders
- Real-time supply-chain optimization
- Supplier management
- Warehouse routing optimization
- Financial accounting integration
- Guaranteed stockout prevention
- Automated business decisions without human review

## 4. Forecasting scope

The forecasting unit is date × item × store at a daily frequency, established
after dataset inspection and documented in the Phase 9 time-series preparation
and Phase 11 forecasting records.

## 5. Forecast horizon

The forecast horizon was defined once the dataset was selected and its temporal
frequency, historical coverage and business use case were established. The
defined horizon is recorded in the Phase 11 and Phase 12 forecasting records:
the validation period runs 2024-02-11 → 2024-06-03, and the reserved test period
2024-06-04 → 2024-09-26 is left unused.

## 6. Geographic scope

Not applicable beyond store level: the dataset carries no geographic
attributes, so the four store identifiers are the only location dimension
(recorded in Phases 2 and 4).

## 7. Product scope

The project uses the product dimension the dataset supports: 28,180 items after
cleaning, described by `catalog.csv`.

## 8. Key assumptions

- **A1** Historical demand contains information useful for estimating future
  demand.
- **A2** The dataset contains sufficient temporal observations for forecasting.
- **A3** Historical data can be transformed into a consistent time series.
- **A4** Promotions can be incorporated because the dataset provides reliable
  promotion information; holidays cannot, because no holiday field exists.
- **A5** The forecasting evaluation period represents future observations
  relative to the training period.
- **A6** No future information leaks into training.
- **A7** Forecast accuracy does not guarantee optimal inventory decisions.
- **A8** External factors not contained in the dataset may affect future demand.

## 9. Constraints

The realized constraints are:

- Dataset availability and quality
- Missing variables (no holiday field; no lead times, costs or stock levels)
- Uneven store history (Store 4 first appears on 2023-12-13)
- Sparse item-store series (intermediate date gaps)
- Computational resources on a single machine (chunked streaming processing)
- Model limitations (validation-period evaluation; scale-bound RMSE)

The dataset constraints are documented in
[`../phase-2/initial-data-assessment.md`](../phase-2/initial-data-assessment.md)
and the Phase 2 data-quality records.

## 10. Scope changes

Any major scope change is recorded in the decision log with its reason and
impact.
