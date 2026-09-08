# Phase 11 — Forecasting Models Quality Framework

## Objective

Ensure forecasting experiments are valid, reproducible, and free from temporal leakage.

## Input Validation

Verify:

* required columns exist
* dates are parseable
* quantity is available
* split labels exist

## Temporal Validation

Verify:

* training ends before validation
* validation ends before test
* forecasts correspond to the correct validation horizon
* observations are chronologically ordered

## Model Validation

Verify:

* naive baseline produces the correct forecast
* seasonal-naive forecast repeats the expected seasonal pattern
* ARIMA configuration is explicit
* model output contains the requested forecast horizon

## Metric Validation

Verify:

* RMSE is calculated correctly
* MAPE handles zero actual values explicitly
* actual and predicted lengths match

## Leakage Validation

The following are prohibited:

* fitting models on validation data before evaluating validation performance
* using test observations for model selection
* random shuffling of temporal observations
* future information entering historical forecasts

## Reproducibility

Record:

* model name
* model configuration
* training period
* validation period
* forecast horizon
* evaluation metrics

## Model Selection Policy

A model must not be described as superior unless the validation results support the claim.

Final model selection is deferred until the complete model-development and evaluation workflow is available.
