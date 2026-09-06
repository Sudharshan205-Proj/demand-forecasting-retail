# Spreadsheet-Based Analysis

## Phase

Phase 3 — Spreadsheet-Based Analysis

## Objective

Apply the spreadsheet-analysis techniques taught in the internship course to the retail demand forecasting project.

The spreadsheet stage provides an accessible analytical layer before the project progresses to SQL, statistical analysis, and forecasting.

## Raw Dataset Constraint

The raw `sales.csv` file contains 7,432,685 records.

A complete raw transaction table cannot be placed into a standard Excel worksheet because the worksheet row limit is substantially smaller than the dataset.

Therefore, this phase creates spreadsheet-sized analytical summaries rather than copying the raw dataset into Excel.

## Workbook

Expected output:

`data/analysis/retail_spreadsheet_analysis.xlsx`

## Workbook Sheets

### Workbook_ReadMe

Explains:

- workbook purpose
- source dataset
- aggregation strategy
- course techniques
- forecasting-phase boundary

### Daily_Analysis

Contains daily aggregated sales information:

- date
- total quantity
- total sales value
- average price
- active items
- day of week
- month
- year

This sheet supports:

- sorting
- filtering
- time-based comparisons
- demand pattern inspection

### Store_Summary

Contains store-level demand summaries and store metadata.

This sheet supports:

- store comparisons
- VLOOKUP-style lookup concepts
- sorting
- filtering
- business interpretation

### Item_Summary

Contains product-level demand summaries.

This supports:

- high-demand product identification
- low-demand product identification
- ranking
- conditional formatting
- filtering

### Formula_Analysis

Demonstrates spreadsheet formulas including:

- SUM
- AVERAGE
- MAX
- MIN
- SUMPRODUCT
- VLOOKUP
- COUNTIF

### Data_Validation

Provides basic consistency checks using spreadsheet formulas.

## Analytical Scope

The spreadsheet stage focuses on descriptive and diagnostic analysis.

It does not perform final forecasting.

Forecasting models belong to later project phases.

## Business Questions Supported

The workbook supports questions such as:

1. How does total demand change over time?
2. Which stores have the greatest historical demand?
3. Which products account for the largest demand volumes?
4. What are the highest-demand and lowest-demand periods?
5. How does average price vary with demand?
6. Which products and stores deserve additional investigation?

## Course Techniques Demonstrated

- Sorting
- Multi-column sorting
- Filtering
- Freeze panes
- Formulas
- VLOOKUP
- SUMPRODUCT
- Data validation
- Conditional formatting
- Pivot-style summaries
- Aggregation
- Validation checks

## Interpretation Rule

Spreadsheet results describe historical relationships.

They must not be interpreted as proof of causal relationships.

For example, a relationship between price and demand does not establish that price changes caused the observed demand change.

## Data Integrity

The raw data is never modified by the spreadsheet-analysis pipeline.

All spreadsheet data is derived from the raw source through reproducible aggregation.