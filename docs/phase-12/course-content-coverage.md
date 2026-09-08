# Phase 12 — Course Content Coverage

## Purpose

This document records the internship course concepts demonstrated by Phase 12.

## Model Evaluation

### Concept

Model evaluation compares model predictions against observed outcomes
using appropriate metrics.

### Project Application

Phase 12 evaluates forecasting configurations using:

- RMSE
- MAPE

Evidence:

- `scripts/evaluate_and_tune_models.py`
- `tests/test_evaluate_and_tune_models.py`
- generated evaluation results

## Time-Aware Validation

### Concept

Time-series data must be evaluated chronologically to avoid leakage.

### Project Application

Phase 12 uses expanding-window cross-validation with fixed future forecast
windows.

## Analytical Thinking

### Concept

Different analytical approaches should be compared against a baseline.

### Project Application

The project retains the Naive model as a benchmark and compares it with
Seasonal Naive and ARIMA configurations.

## Statistical Analysis

### Concept

Statistical modeling should be evaluated using measurable error metrics.

### Project Application

ARIMA configurations are compared using cross-validation RMSE and MAPE.

## Model Selection

### Concept

Models should be selected using evidence rather than assumptions.

### Project Application

Configurations are selected using training-period cross-validation results.

## Data Integrity

### Concept

Analytical conclusions require valid and appropriately structured data.

### Project Application

Phase 12 validates chronological split ordering and temporal cross-validation.

## Reproducibility

### Concept

Analytical work should be reproducible.

### Project Application

The project records model configurations, fold definitions, metrics,
selection criteria, and generated result artifacts.

## Course Concepts Not Added in This Phase

Deep learning is not implemented in Phase 12 because it belongs to a later
model-development stage.

Visualization and Tableau are not implemented here because they belong to
later presentation phases.

R analysis is not implemented here because it belongs to the dedicated
Phase 14 R Analysis stage.

## Coverage Rule

A concept is considered implemented only when corresponding project
evidence exists.