# Spreadsheet Methodology

## Analytical Workflow

The Phase 3 workflow follows:

1. Identify the analytical question.
2. Select the appropriate dataset.
3. Aggregate the large raw dataset to spreadsheet-compatible summaries.
4. Load analytical summaries into Excel.
5. Sort relevant variables.
6. Filter relevant records.
7. Apply formulas.
8. Apply lookup logic.
9. Apply conditional formatting.
10. Apply data validation.
11. Perform consistency checks.
12. Interpret the results.
13. Document limitations.

## Why Aggregation Is Necessary

The raw sales dataset contains more than seven million rows.

Excel is therefore used as an analytical presentation and exploration tool rather than as the storage location for all raw records.

Aggregation also demonstrates an important analytical principle:

> The analytical representation should match the question being answered.

## Sorting

The workbook supports sorting by:

- date
- total demand
- sales value
- average price
- product
- store

Multiple-column sorting can be performed interactively in Excel.

## Filtering

Excel tables provide filtering controls.

Examples include:

- selecting a specific store
- identifying high-demand products
- isolating specific periods
- filtering by day of week

## Freeze Panes

Header rows are frozen so that column names remain visible while scrolling.

This directly demonstrates the spreadsheet workflow taught in the course.

## Formulas

The workbook includes formulas for:

- totals
- averages
- minimums
- maximums
- counts

Derived spreadsheet values should use formulas where practical rather than manually entered results.

## VLOOKUP

VLOOKUP is demonstrated using the store summary and store metadata.

Its purpose is to demonstrate joining contextual information into an analytical spreadsheet.

## SUMPRODUCT

SUMPRODUCT is demonstrated as a spreadsheet calculation for combining corresponding values.

This demonstrates array-based spreadsheet calculations taught in the course.

## Data Validation

A store-selection cell uses a controlled list:

- 1
- 2
- 3
- 4

This prevents invalid store IDs from being selected in the demonstration field.

## Conditional Formatting

Demand quantities are conditionally formatted to make relatively low, middle, and high values easier to identify.

## Pivot-Style Analysis

The store and item summary sheets provide pivot-style aggregation of the underlying sales data.

They answer questions that would commonly be explored through spreadsheet pivot tables.

## Validation

The workbook includes a dedicated validation sheet containing formula-based checks for:

- number of analytical records
- missing dates
- negative quantities

## Limitations

The workbook does not replace the raw data.

It is an analytical representation designed for spreadsheet-based exploration.

More complex relational analysis will be implemented using SQL in a later phase.

Time-series forecasting will be implemented in later phases.