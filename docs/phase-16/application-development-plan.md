# Phase 16 — Application Development Plan

## Objective

Develop a lightweight decision-support application that exposes the validated
retail demand forecasting and inventory-analysis results produced by the
previous project phases.

## Design Principle

The application presents existing validated analytical artifacts.

It does not retrain forecasting models during normal application use.

## Inputs

The application reads seven compact CSV artifacts. Their names are declared
once, in `app/config.py`, and resolved in this order:

| Order | Location | Use |
|---|---|---|
| 1 | `APP_ANALYSIS_DIR` environment variable | Test and advanced override |
| 2 | `data/analysis/` | Local pipeline output, excluded from Git |
| 3 | `deploy/artifacts/` | Committed deployment bundle (14,977 bytes) |

| Artifact | Produced by |
|---|---|
| `inventory_demand_summary.csv` | Phase 13 |
| `inventory_variability_summary.csv` | Phase 13 |
| `inventory_scenarios.csv` | Phase 13 |
| `forecasting_model_results.csv` | Phase 11 |
| `forecasting_model_configurations.csv` | Phase 11 |
| `selected_model_configurations.csv` | Phase 12 |
| `tuned_validation_results.csv` | Phase 12 |

The large processed and feature-engineered datasets are intentionally not
loaded by the Streamlit interface.

## Main User Functions

1. Select a store.
2. Review average demand and training-window length.
3. Review demand variability.
4. Select inventory lead-time scenarios.
5. Select service-level scenarios.
6. Review reorder-point estimates.
7. Review the selected model for the chosen store, with its configuration,
   cross-validation fold count and validation metrics (Phase 12).
8. Review the model comparison behind the selection (Phase 11).
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

- Configuration (`app/config.py`)
- Data loading (`app/data_loader.py`)
- Formatting (`app/formatting.py`)
- Logging (`app/logging_config.py`)
- User interface (`app/streamlit_app.py`)

This separation supports maintainability and testing. Every Streamlit call
lives inside `main()`, so the pure helpers can be imported and tested without
a running Streamlit runtime.

## Phase 17 Re-Audit Record

The plan was reviewed against the implementation and the executed evidence.

- The input list is now explicit about the three-step resolution order rather
  than naming `data/analysis/` alone. Under the original wording a repository
  build would have had no inputs at all, because `data/analysis/` is
  gitignored.
- A ninth user function was separated out: the Phase 12 selected-model
  evidence. The original list conflated the model comparison with the model
  configuration, and the application displayed only the comparison.
- "Understand limitations" is retained and is now backed by a concrete,
  data-derived caveat for single-fold stores.
