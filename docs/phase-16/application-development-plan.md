# Phase 16 — Application Development Plan

## Objective

Develop a lightweight decision-support application that exposes the
validated retail demand forecasting and inventory-analysis results produced
by the previous project phases.

## Design Principle

The application presents existing validated analytical artifacts.

It does not retrain forecasting models during normal application use.

## Inputs

The application uses compact CSV artifacts from `data/analysis/`.

The large processed and feature-engineered datasets are intentionally not
loaded by the Streamlit interface.

## Main User Functions

1. Select a store.
2. Review average demand.
3. Review demand variability.
4. Select inventory lead-time scenarios.
5. Select service-level scenarios.
6. Review reorder-point estimates.
7. Review forecasting model evaluation.
8. Review model configuration.
9. Understand limitations and assumptions.

## Non-Goals

The application does not:

- Retrain forecasting models.
- Modify source datasets.
- Replace the analytical pipeline.
- Automatically make operational inventory decisions.
- Claim that scenario assumptions represent actual business policy.

## Architecture

The application separates:

- Configuration
- Data loading
- Formatting
- Logging
- User interface

This separation supports maintainability and testing.