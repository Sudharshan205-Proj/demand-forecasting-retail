# Phase 3 Course-Content Coverage

## Spreadsheet curriculum mapping

| Course concept | Phase 3 implementation | Evidence |
|---|---|---|
| Spreadsheet analysis | Excel workbook | `data/analysis/retail_spreadsheet_analysis.xlsx` |
| Sorting | Analytical sheets designed for sorting | `Daily_Analysis`, `Store_Summary`, `Item_Summary` |
| Multiple-variable sorting | Workbook columns support multi-column sorting | Analytical tables |
| Filtering | Excel tables with filters | Analytical sheets |
| Freeze header row | Freeze panes | `Daily_Analysis`, `Store_Summary`, `Item_Summary` |
| Formulas | Formula demonstration sheet | `Formula_Analysis` |
| VLOOKUP | Lookup example | `Formula_Analysis` |
| SUMPRODUCT | Calculation example | `Formula_Analysis` |
| Data validation | Store selection list | `Formula_Analysis` |
| Conditional formatting | Demand ranking emphasis | `Item_Summary` |
| Pivot-table concepts | Aggregated summary tables | `Store_Summary`, `Item_Summary` |
| Aggregate calculations | SUM, AVERAGE, MIN, MAX, COUNTIF | `Formula_Analysis` |
| Data validation/checking | Dedicated validation sheet | `Data_Validation` |

## Why these techniques are included

The techniques are connected to the demand-forecasting problem rather than
included as isolated demonstrations:

- Sorting identifies high- and low-demand observations.
- Filtering isolates stores, products and periods.
- Formulas quantify historical demand.
- VLOOKUP connects store identifiers with business metadata.
- SUMPRODUCT demonstrates weighted/multi-cell calculations.
- Conditional formatting highlights demand differences.
- Data validation controls user selections.
- Aggregated summaries provide pivot-table-style business analysis.

## Techniques delivered by later phases

| Concept | Phase |
|---|---|
| SQL queries | Phase 4 |
| Relational joins | Phase 4 / Phase 6 |
| Data cleaning | Phase 5 |
| Statistical analysis | Phase 8 |
| Forecasting | Phase 11 |
| R | Phase 14 |
| Visualization, Tableau and storytelling | Phase 15 |
| Application | Phase 16 |

## Coverage principle

A technique counts as covered only when project evidence exists; listing a
technique in documentation is not implementation.
