# Scope and Assumptions

## 1. Project Scope

The project will develop an end-to-end retail demand forecasting system.

## 2. In Scope

### Business Analysis

- Retail demand problem
- Inventory-planning context
- Stakeholder requirements
- SMART analytical questions
- Hypothesis development

### Data

- Historical sales
- Promotions where available
- Holidays where available
- Product information where available
- Store/location information where available

### Analysis

- Spreadsheet analysis
- SQL analysis
- Python analysis
- R analysis
- Exploratory analysis
- Statistical analysis
- Demand pattern analysis

### Forecasting

- Baseline
- ARIMA
- Additional permitted forecasting approach where justified
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

## 3. Out of Scope

The following are not guaranteed to be included unless the selected dataset and project requirements justify them:

- Real-time inventory integration
- Live ERP integration
- Automatic purchase orders
- Real-time supply-chain optimization
- Supplier management
- Warehouse routing optimization
- Financial accounting integration
- Guaranteed stockout prevention
- Automated business decisions without human review

## 4. Forecasting Scope

The forecasting unit was determined after dataset inspection during the forecasting phases.

The implemented forecasting unit is documented in the Phase 9 time-series preparation and Phase 11 forecasting records.

## 5. Forecast Horizon

The exact forecast horizon was defined once:

1. The dataset was selected.
2. Its temporal frequency was understood.
3. Its historical coverage was established.
4. The business use case was finalized.

The defined horizon is recorded in the Phase 11 and Phase 12 forecasting records.

## 6. Geographic Scope

TBD based on dataset availability.

## 7. Product Scope

The project will use the product dimension supported by the selected dataset.

## 8. Key Assumptions

### A1

Historical demand contains information useful for estimating future demand.

### A2

The selected dataset contains sufficient temporal observations for forecasting.

### A3

Historical data can be transformed into a consistent time series.

### A4

Promotions and holidays can be incorporated when the selected dataset provides reliable information.

### A5

The forecasting evaluation period will represent future observations relative to the training period.

### A6

No future information will be allowed to leak into training.

### A7

Forecast accuracy does not guarantee optimal inventory decisions.

### A8

External factors not contained in the dataset may affect future demand.

## 9. Constraints

Potential constraints include:

- Dataset availability
- Dataset quality
- Missing variables
- Missing promotion information
- Missing holiday information
- Limited historical coverage
- Computational resources
- Forecasting assumptions
- Model limitations

Actual constraints were documented during Phase 2 after the dataset was acquired; see `docs/phase-2/initial-data-assessment.md` and the Phase 2 data-quality records.

## 10. Scope Change Rule

Any major scope change must be recorded in the decision log.

The change must include:

- Original decision
- New decision
- Reason
- Impact
- Affected documentation