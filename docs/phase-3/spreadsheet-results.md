# Spreadsheet Analysis Results

## Phase

Phase 3 — Spreadsheet-Based Analysis

## Dataset

Source: `data/raw/sales.csv`

Raw records: 7,432,685 (recorded in Phase 2).

## Analysis

### Historical demand over time

The `Daily_Analysis` worksheet contains **761 daily records** covering
**2022-08-28 to 2024-09-26**:

- Highest-demand date: **2023-12-30** (total quantity ≈ 154,066.88)
- Lowest-demand date: **2023-01-01** (total quantity ≈ 19,245.05)
- Total daily quantity across the period: ≈ **41,938,165**
- Total daily sales value across the period: ≈ **5,658,351,681**
- Day-of-week, month and year fields support day-of-week and monthly pattern
  inspection.

### Store demand

The `Store_Summary` worksheet contains **4 store records** (matching the four
stores recorded in Phase 2):

| Store | Total quantity | Total sales value | Average price | Active items |
|---|---:|---:|---:|---:|
| 1 | 23,064,331.52 | 3,106,158,681.93 | 216.73 | 25,312 |
| 2 | 4,898,827.56 | 492,059,912.92 | 152.35 | 9,842 |
| 3 | 4,755,147.06 | 613,690,645.68 | 194.04 | 5,193 |
| 4 | 9,219,859.06 | 1,446,442,440.18 | 240.13 | 17,680 |

Store 1 is the highest-demand store by total quantity and sales value; stores 2
and 3 have substantially lower volumes.

### Product demand

The `Item_Summary` worksheet contains **28,182 item records** (matching the
unique sales items recorded in Phase 2):

- 28,167 items have positive total quantity; 15 items have zero/undetermined
  quantity after aggregation.
- Highest-demand item: `b0d24502fb66` (total quantity 2,022,732; total sales
  value ≈ 15,116,885.83)
- Highest sales-value item: `9a7e315f3f42` (sales value ≈ 334,093,618.12)
- The sheet supports ranking, conditional formatting and high/low-demand product
  identification.

### Spreadsheet calculations

The `Formula_Analysis` worksheet demonstrates and stores the following formulas.
The five aggregate formulas reference the `DailySalesTable` Excel table rather
than a fixed cell range, so they span all 761 daily rows and return the true
table-wide values, including the highest- and lowest-demand dates recorded above:

| Technique | Formula |
|---|---|
| SUM | `=SUM(DailySalesTable[total_quantity])` |
| AVERAGE | `=AVERAGE(DailySalesTable[average_price])` |
| MAX | `=MAX(DailySalesTable[total_quantity])` |
| MIN | `=MIN(DailySalesTable[total_quantity])` |
| SUMPRODUCT | `=SUMPRODUCT(DailySalesTable[total_quantity],DailySalesTable[average_price])` |
| VLOOKUP | `=VLOOKUP(D2,Store_Summary!A:I,8,FALSE)` |
| COUNTIF | `=COUNTIF(Daily_Analysis!F:F,"Monday")` |

### Data validation

The `Data_Validation` worksheet contains the following formula-based checks:

- Daily records: `=COUNTA(Daily_Analysis!A:A)-1`
- Store records: `=COUNTA(Store_Summary!A:A)-1`
- Item records: `=COUNTA(Item_Summary!A:A)-1`
- Missing daily dates: `=COUNTBLANK(DailySalesTable[date])`
- Negative daily quantity records: `=COUNTIF(DailySalesTable[total_quantity],"<0")`

The store-selection cell (`Formula_Analysis` D2) uses a dynamic data-validation
list sourced from the `Store_Summary` store-id column.

### Workbook structure

- 6 sheets: Workbook_ReadMe, Daily_Analysis, Store_Summary, Item_Summary,
  Formula_Analysis, Data_Validation
- Excel tables with filters on Daily_Analysis (DailySalesTable), Store_Summary
  (StoreSummaryTable) and Item_Summary (ItemSummaryTable)
- Freeze panes at A2 on all analytical sheets
- Conditional formatting (colour scale) on the Item_Summary demand ranking

### Sheet contents

- `Workbook_ReadMe` — explains workbook purpose, source dataset, aggregation
  strategy, course techniques and the forecasting-phase boundary.
- `Daily_Analysis` — contains daily aggregated sales information: date, total
  quantity, total sales value, average price, active items, day of week, month
  and year. The sheet supports sorting, filtering, time-based comparisons and
  demand-pattern inspection.
- `Store_Summary` — contains store-level demand summaries and store metadata,
  supporting store comparisons, VLOOKUP-style lookup concepts, sorting,
  filtering and business interpretation.
- `Item_Summary` — contains product-level demand summaries, supporting
  high-demand and low-demand product identification, ranking, conditional
  formatting and filtering.
- `Formula_Analysis` — demonstrates spreadsheet formulas including SUM, AVERAGE,
  MAX, MIN, SUMPRODUCT, VLOOKUP and COUNTIF.
- `Data_Validation` — provides consistency checks using spreadsheet formulas.

## Business interpretation

The findings answer the Phase 1 analytical questions by supporting:

- identification of high- and low-demand time periods,
- store-level demand comparison,
- product-level demand ranking,
- pricing and demand-pattern inspection.

These results describe historical relationships and do not establish causal
effects.

## Limitations

- Spreadsheet analysis uses aggregated data.
- It does not replace the complete raw dataset.
- It does not perform forecasting.
- It does not establish causal relationships.
- Phase 4 performs the relational analysis in SQL.
