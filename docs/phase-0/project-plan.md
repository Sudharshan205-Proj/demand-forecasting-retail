# Project Plan

## Project

Demand Forecasting for Retail

## Analytical methodology

The project follows:

Ask → Prepare → Process → Analyze → Share → Act

## Software/ML lifecycle

The project covers the following lifecycle stages:

1. Planning
2. Requirements
3. Architecture
4. Repository setup
5. Environment setup
6. Dependency management
7. Data acquisition
8. Data understanding
9. Data validation
10. Data preprocessing
11. Exploratory data analysis
12. Feature engineering
13. Baseline development
14. Model development
15. Model comparison
16. Hyperparameter tuning
17. Evaluation
18. Error analysis
19. Model persistence — assessed, not applicable (`architecture.md` §Model persistence)
20. Application development
21. API assessment — assessed, not applicable (`architecture.md` §API)
22. Testing
23. Configuration
24. Logging
25. Deployment
26. Deployment validation
27. Monitoring considerations — recorded as out of internship scope
28. Documentation
29. Quality review
30. Final cleanup
31. Final Git state

## Phases

| Phase | Name |
|---|---|
| 0 | Project Setup & Curriculum Mapping |
| 1 | Business Understanding & Planning |
| 2 | Data Acquisition & Data Understanding |
| 3 | Spreadsheet-Based Analysis |
| 4 | SQL & Database Analysis |
| 5 | Data Cleaning & Quality Assurance |
| 6 | Data Integration |
| 7 | Exploratory Data Analysis |
| 8 | Statistical & Analytical Analysis |
| 9 | Time-Series Preparation |
| 10 | Feature Engineering |
| 11 | Forecasting Models |
| 12 | Model Evaluation & Tuning |
| 13 | Forecasting & Inventory Insights |
| 14 | R Analysis |
| 15 | Visualization & Tableau |
| 16 | Application Development & Deployment |
| 17 | Testing, Documentation & Finalization |

## Dataset

The dataset contains enough temporal information to support forecasting, with
sales, promotion and product data for four stores over 2022-08-28 → 2024-09-26.
It has no holiday field and no lead times, costs or stock levels; both absences
are recorded as limitations.

## Model strategy

ARIMA is mandatory and is implemented as ARIMA(1,1,1) per store, alongside
naive and seasonal-naive baselines. The additional permitted forecasting
approach is a deterministic feature-based gradient-boosting candidate
(`feature_gbm`) over the engineered store-day features. Prophet and LSTM were
assessed on technical suitability and deliberately not implemented; the
assessment is recorded in Phase 11.

## Evaluation strategy

Forecast evaluation uses:

- RMSE
- MAPE

Validation is time-aware, and test data is never used for model selection.

## Deployment

A lightweight Python application exposes the forecasting workflow to users. It
is deployed on Streamlit Community Cloud and reads a committed artifact bundle
so a repository build can start it.

## Documentation

Documentation is part of each phase: every phase owns its methodology, results,
quality framework, course-content coverage and summary.

## Quality review

The project closes with a consolidated test suite (532 tests) and a review of
course coverage, code, data, models, testing, security, documentation,
deployment and reproducibility, recorded in
[`../phase-17/phase-17-checklist.md`](../phase-17/phase-17-checklist.md).
