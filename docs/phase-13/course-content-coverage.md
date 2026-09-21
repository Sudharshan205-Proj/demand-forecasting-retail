# Phase 13 — Course Content Coverage

## Purpose

Document how relevant internship-course concepts are applied to forecasting and
inventory interpretation.

## Making Predictions

### Course Concept

Predictive analytics uses historical data to estimate future outcomes.

### Project Application

The project uses the validated Phase 12 forecasting configurations as evidence
for demand planning, and quantifies what those models actually get wrong rather
than assuming they are unbiased. Every selected model under-forecast on the
validation period, so the phase carries an explicit bias correction instead of
asserting accuracy it cannot demonstrate.

Evidence: `inventory_forecast_error_summary.csv`.

## Finding Patterns

### Course Concept

Data analysis can identify recurring and meaningful patterns.

### Project Application

The project examines daily demand levels and variability and incorporates the
validated Phase 12 configurations: a feature-based gradient-boosting model for
Stores 1–3 and weekly Seasonal Naive for Store 4.

The pattern that matters most for planning is the separation of level from
volatility: Store 1 carries the highest average demand while Store 4 carries the
highest *relative* variability, so the two are different risks rather than one
ranking.

Evidence: `inventory_demand_summary.csv`, `inventory_variability_summary.csv`.

## Discovering Connections

### Course Concept

Analysts investigate relationships between variables and business outcomes.

### Project Application

Phase 13 connects demand magnitude and demand variability to inventory planning
scenarios, and connects forecast accuracy to the size of the buffer a store
needs: sizing from raw historical spread produces a materially larger safety
stock than sizing from the error the selected model actually makes, at every
store.

The analysis does not interpret correlation as causation.

## Data-Driven Decision Making

### Course Concept

Analytical findings should support decisions.

### Project Application

Demand and variability statistics are converted into inventory-planning scenarios
using explicit assumptions, and two scenario families are produced so that the
sensitivity to the uncertainty input is visible rather than hidden in a single
number. All 36 scenarios per family are reported rather than a preferred subset.

## Communicating Findings

### Course Concept

Analysis should be translated into understandable business insights.

### Project Application

The phase produces structured insights and a textual findings report. The report
is generated from the loaded evidence, so it cannot drift away from the artifacts
it describes; the quality report fails the run if a selected model is missing from
it.

## Analytical Thinking

### Course Concept

Analytical results should be interpreted in a business context.

### Project Application

The project distinguishes:

- demand level;
- demand uncertainty;
- forecasting evidence;
- inventory assumptions;
- operational limitations.

It also distinguishes which forecast comparisons are legitimate: relative error
is used to compare stores of different size, while raw RMSE is recorded as
scale-bound and only meaningful within a store.

## Statistical Analysis

### Course Concept

Statistical modelling should be evaluated using measurable error metrics.

### Project Application

Each store's bias, residual standard deviation, RMSE and MAPE are recomputed from
the stored Phase 12 validation forecasts, reconciled against Phase 12's recorded
values, and reconciled again against Phase 12's half-period error segments.
Inventory quantities then use those measured properties as inputs.

## Data Integrity

### Course Concept

Analytical conclusions require valid and appropriately structured data.

### Project Application

The phase reconciles the source matrix on rows (7,431,026) and quantity
(41,949,529.910), reconciles the train, validation and test partitions on row
count, verifies store-day key uniqueness, and measures the densification that
puts it on the same series Phases 11–12 use.

## Reproducibility

### Course Concept

Analytical work should be documented and reproducible.

### Project Application

Formulas, assumptions, source data, outputs and limitations are recorded, and
the workflow is deterministic: re-running it over the same inputs reproduces
every artifact, and the test suite asserts that determinism.

## Concepts Outside This Phase

The following belong to other project stages:

- R-specific analysis — Phase 14;
- Tableau visualization — Phase 15;
- application and deployment — Phase 16;
- deep learning — not part of the delivered model set.

## Coverage Rule

A concept is considered implemented only when corresponding project evidence
exists.
