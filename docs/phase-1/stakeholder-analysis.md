# Stakeholder Analysis

## 1. Purpose

The demand forecasting project is designed around decisions rather than around
models alone. Stakeholders are therefore identified before data acquisition and
modelling.

## 2. Primary stakeholders

### Inventory / supply planning manager

Needs:

- Expected future demand
- Product-level demand forecasts
- High-demand periods
- Potential demand increases/decreases
- Forecast reliability
- Information useful for replenishment planning

Key decisions:

- How much inventory should be planned?
- Which products require attention?
- Which periods may require additional inventory?

### Retail operations manager

Needs:

- Demand trends
- Store and product demand patterns
- Promotion effects
- Potential operational pressure periods

Key decisions:

- Where should operational resources be concentrated?
- Which periods may require additional preparation?

## 3. Secondary stakeholders

### Merchandising / category manager

Needs:

- Product demand patterns
- Promotion relationships
- Product comparisons
- Seasonal behaviour

Potential decisions:

- Which products may require additional attention?
- When might promotions affect demand?

### Business / commercial manager

Needs:

- High-level demand trends
- Forecast summaries
- Business implications
- Clear recommendations

### Data analyst

Needs:

- Clean analytical datasets
- Documented transformations
- Reproducible analysis
- Clear definitions
- Reliable metrics

### Data scientist / ML practitioner

Needs:

- Forecasting-ready time-series data
- Valid temporal splits
- Model inputs
- Evaluation datasets
- Reproducible experiments

### Technical / application stakeholder

Needs:

- Stable artifacts
- Predictable inputs and outputs
- Configuration
- Error handling
- Deployment documentation

## 4. Stakeholder information requirements

| Stakeholder | Primary information | Decision supported |
|---|---|---|
| Inventory manager | Future demand | Inventory/replenishment planning |
| Operations manager | Demand patterns | Operational preparation |
| Merchandising manager | Product and promotion patterns | Product/promotion decisions |
| Business manager | Forecast summaries and recommendations | Strategic decisions |
| Analyst | Clean data and definitions | Analysis |
| Data scientist | Forecast-ready data and evaluation | Model development |
| Technical stakeholder | Application/artifact requirements | System operation |

## 5. Stakeholder communication principle

Technical model details are communicated at a level appropriate to the audience.

Business stakeholders can understand:

- What was forecast
- How accurate the forecast was
- What the forecast means
- What action may be considered
- What limitations exist

They are not required to understand model implementation details to interpret
the business recommendation.

## 6. Stakeholder validation

Stakeholder assumptions were revisited after the dataset was selected. Where the
dataset cannot support a stated stakeholder requirement, the requirement is
documented as a limitation rather than fabricated; the holiday requirement is
the working example, recorded in
[`business-requirements.md`](business-requirements.md) BR-003.
