# Spreadsheet Methodology

## Analytical workflow

The Phase 3 workflow follows:

1. Identify the analytical question.
2. Select the appropriate dataset.
3. Aggregate the large raw dataset to spreadsheet-compatible summaries.
4. Load the analytical summaries into an Excel workbook.
5. Sort relevant variables.
6. Filter relevant records.
7. Apply formulas.
8. Apply lookup logic.
9. Apply conditional formatting.
10. Apply data validation.
11. Perform consistency checks.
12. Interpret the results.
13. Document limitations.

## Why aggregation is necessary

The raw sales dataset contains more than seven million rows, which exceeds the
worksheet row limit.

Excel is therefore used as an analytical presentation and exploration tool
rather than as the storage location for all raw records.

Aggregation also reflects an important analytical principle:

> The analytical representation should match the question being answered.

## Sorting

The workbook supports sorting by date, total demand, sales value, average price,
product and store. Multiple-column sorting can be performed interactively in
Excel.

## Filtering

Excel tables provide filtering controls, for example selecting a specific store,
identifying high-demand products, isolating specific periods, and filtering by
day of week.

## Freeze panes

Header rows are frozen so that column names remain visible while scrolling,
demonstrating the spreadsheet workflow taught in the course.

## Formulas

The workbook includes formulas for totals, averages, minimums, maximums and
counts. The workbook's aggregate formulas reference the `DailySalesTable` Excel
table rather than a fixed cell range, so they span every daily row; derived
spreadsheet values are formula-driven rather than pasted results.

## VLOOKUP

VLOOKUP is demonstrated using the store summary and store metadata, joining
contextual information into the analytical spreadsheet.

## SUMPRODUCT

SUMPRODUCT is demonstrated as a spreadsheet calculation for combining
corresponding values, demonstrating array-based spreadsheet calculations.

## Data validation

A store-selection cell uses a controlled list sourced from the store summary,
which prevents invalid store IDs from being selected in the demonstration field.

## Conditional formatting

Demand quantities are conditionally formatted to make relatively low, middle and
high values easier to identify.

## Pivot-style analysis

The store and item summary sheets provide pivot-style aggregation of the
underlying sales data, answering questions commonly explored through spreadsheet
pivot tables.

## Validation

The workbook includes a dedicated validation sheet containing formula-based
checks for the number of analytical records, missing dates and negative
quantities.

## Limitations

The workbook does not replace the raw data; it is an analytical representation
designed for spreadsheet-based exploration.

The relational analysis is implemented in SQL in Phase 4, and time-series
forecasting is implemented in Phases 9–13.
