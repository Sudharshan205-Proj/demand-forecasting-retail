# Spreadsheet Quality Framework

The spreadsheet workflow maintains the quality principles below. Each principle
is stated together with how it is enforced; a principle that cannot be checked
mechanically is listed under "Not mechanically enforced" rather than claimed. The
requirements are implemented in `scripts/create_spreadsheet_analysis.py`,
evidenced by the generated workbook
`data/analysis/retail_spreadsheet_analysis.xlsx`, and asserted by
`tests/test_create_spreadsheet_analysis.py` (12 tests).

## Report format

Phase 3 produces **no machine-readable pass/fail report**, so it contributes
nothing to the run-gating quality total. The workbook is the artifact and the
checks below are asserted by the test module. This is a deliberate difference
from Phases 9–15, whose workflows write a report and stop when a check fails: a
spreadsheet cannot gate its own run headlessly, so its quality is asserted by
pytest instead.

## 1. Input integrity

- every required input exists before any work starts;
- the raw inputs are never modified;
- the workbook is written to the generated, Git-excluded `data/analysis/`.

*Implementation:* `main()` raises `FileNotFoundError` naming the missing path
when either `data/raw/sales.csv` or `data/raw/stores.csv` is absent, before any
sheet is created. `test_load_stores` covers the store-directory load.

## 2. Aggregation exactness

- a total does not depend on the chunk size used to build it;
- an unnamed index column cannot corrupt a measure;
- invalid-date rows are excluded from the daily sheet only.

*Implementation:* the aggregation streams the raw file in chunks and accumulates
with Kahan compensated summation (`_kahan_add`), so floating-point addition is
order-insensitive and a chunk boundary cannot change a total. On the raw basis
the workbook reports **41,938,165.205** total quantity and **5,658,351,680.71**
total sales value across 7,432,685 raw records.

*Tests:* `test_aggregate_sales_is_exact_across_chunk_boundaries`,
`test_aggregate_sales_ignores_unnamed_index_column`,
`test_aggregate_sales_excludes_invalid_dates_from_daily_only`.

## 3. Workbook structure

- the six required sheets exist by name;
- each analytical sheet carries an Excel table with filters;
- freeze panes and conditional formatting are applied;
- a structured table reference stays correct beyond column Z.

*Implementation:* `Workbook_ReadMe`, `Daily_Analysis` (`DailySalesTable`),
`Store_Summary` (`StoreSummaryTable`), `Item_Summary` (`ItemSummaryTable`),
`Formula_Analysis` and `Data_Validation`. Freeze panes sit at `A2`, and
`Item_Summary` carries a colour-scale conditional format on item demand.
Measured record counts: **761** daily rows, **4** store rows and **28,182** item
rows.

*Tests:* `test_create_workbook_creates_required_sheets`,
`test_daily_sheet_table_has_no_conflicting_autofilter`,
`test_table_reference_handles_more_than_26_columns`,
`test_store_selection_dropdown_is_dynamic_not_hardcoded`,
`test_data_validation_uses_bounded_table_references`.

## 4. Formula integrity

The course techniques are present as live formulas, not pasted values, and they
reference the whole table rather than a fixed range.

*Implementation:* the five aggregate formulas reference `DailySalesTable`, so
they span all 761 daily rows; `VLOOKUP` resolves the city of the store selected
in the interactive cell; `COUNTIF` counts Mondays.

| Technique | Formula as written |
|---|---|
| SUM | `=SUM(DailySalesTable[total_quantity])` |
| AVERAGE | `=AVERAGE(DailySalesTable[average_price])` |
| MAX | `=MAX(DailySalesTable[total_quantity])` |
| MIN | `=MIN(DailySalesTable[total_quantity])` |
| SUMPRODUCT | `=SUMPRODUCT(DailySalesTable[total_quantity],DailySalesTable[average_price])` |
| VLOOKUP | `=VLOOKUP(D2,Store_Summary!A:I,8,FALSE)` |
| COUNTIF | `=COUNTIF(Daily_Analysis!F:F,"Monday")` |

*Tests:* `test_workbook_contains_required_course_formulas`,
`test_workbook_contains_all_required_course_formulas`,
`test_vlookup_formula_targets_the_selected_store_cell`.

## 5. Data validation

The validation sheet and the interactive store selector are formula- and
list-driven rather than hardcoded.

*Implementation:* `Data_Validation` holds five formula checks — daily, store and
item record counts, missing daily dates and negative daily quantity — and the
store-selection cell (`Formula_Analysis` D2) carries a data-validation list
sourced from the `Store_Summary` store-id column.

## 6. Course-technique coverage

The workbook includes sorting, multiple-column sorting, filtering, freeze panes,
formulas, VLOOKUP, SUMPRODUCT, data validation, conditional formatting,
pivot-style summaries, aggregate calculations and validation checks.
**Pivot-style summaries** are delivered as the aggregated `Daily_Analysis`,
`Store_Summary` and `Item_Summary` sheets; no native PivotTable object is
created, and the coverage record says so.

## 7. Failure behaviour

| Situation | Behaviour |
|---|---|
| `data/raw/sales.csv` absent | `FileNotFoundError` naming the path; no workbook is written |
| `data/raw/stores.csv` absent | `FileNotFoundError` naming the path; no workbook is written |
| Ragged or unnamed index column | The unnamed index is dropped; totals are unaffected |
| Invalid dates in the raw file | Excluded from the daily sheet and daily totals; the store and item sheets are unaffected |

## 8. Not mechanically enforced

- **Evaluated formula results.** The workbook stores formula *text*; the cached
  values are computed by Excel, Google Sheets or LibreOffice when the file is
  opened, and no headless spreadsheet engine exists in the project environment.
  The formulas are therefore checked as text and by their table references, while
  the values are confirmed independently against the phase artifacts and the
  Phase 7/8 outputs.
- Visual layout, readability and colour judgement.
- Whether the chosen summary grain is the most useful for a given reader.

## 9. Reproducibility

One command regenerates the workbook
(`scripts/create_spreadsheet_analysis.py`), the run is deterministic, and
regeneration reproduces the same six sheets and the same 761 / 4 / 28,182
record counts. The workbook is a generated artifact and is excluded from Git
under the project's generated-data policy.

## 10. Documentation

The method, results and course mapping are recorded in
[`spreadsheet-methodology.md`](spreadsheet-methodology.md),
[`spreadsheet-results.md`](spreadsheet-results.md) and
[`course-content-coverage.md`](course-content-coverage.md), with the phase
summary in [`phase-3-checklist.md`](phase-3-checklist.md).
