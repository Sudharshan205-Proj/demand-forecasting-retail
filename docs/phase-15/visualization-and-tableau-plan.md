# Phase 15 — Visualization and Tableau Plan

## Objective

Communicate the project's demand forecasting and inventory-planning findings
to non-technical stakeholders through static visualizations and an interactive
Tableau dashboard.

## Inputs

The phase consumes five compact analytical outputs. All five are read by the
workflow; each is validated before anything is drawn.

| Input | Produced by | Rows |
|---|---|---|
| `inventory_demand_summary.csv` | Phase 13 | 4 |
| `inventory_variability_summary.csv` | Phase 13 | 4 |
| `inventory_scenarios.csv` | Phase 13 | 36 |
| `forecast_inventory_insights.csv` | Phase 13 | 13 |
| `tuned_validation_results.csv` | Phase 12 | 4 |

The Tableau workbook connects to three of these:
`inventory_scenarios.csv`, `inventory_variability_summary.csv` and
`tuned_validation_results.csv`.

Phase 7 (exploratory analysis) and Phase 8 (statistical analysis) supply
context rather than inputs: the distribution and correlation evidence cited in
the course-coverage record belongs to those phases and is not re-derived here.

**Phase 17 correction (F8).** This plan previously listed Phase 14 (R
Analysis) as an input, while the Phase 15 workflow consumed no R output. That
claim was wrong and has been removed. R and Python independently analysed the
same Phase 11–13 evidence; Phase 15 visualizes that shared evidence in
Python, and the R figures belong to Phase 14's own report.

## Static Visualization

Python provides four reproducible figures:

1. Average daily demand by store.
2. Relative demand variability by store.
3. Forecast validation evidence.
4. Inventory reorder-point scenarios.

Each figure is written only after the 55-check quality gate passes, carries
direct value labels and states its unit, its period and any caveat that
changes interpretation.

## Tableau

Tableau Public provides interactive exploration. The committed workbook is
`tableau/Retail_Demand_Forecasting.twb` and the published dashboard is
recorded in `visualization-results.md`.

The dashboard prioritizes:

- store comparison;
- demand level;
- variability;
- inventory scenario analysis;
- validated forecasting evidence.

## Dashboard Principles

The dashboard should:

- communicate one clear purpose;
- use meaningful titles;
- avoid unnecessary charts;
- provide useful filters;
- maintain consistent units;
- avoid misleading scales;
- remain understandable without technical knowledge.

## Story Structure

The dashboard narrative progresses from:

1. Demand context
2. Store comparison
3. Variability
4. Forecast evidence
5. Inventory implications
6. Planning considerations
7. Limitations

## Scope

This phase communicates existing analytical evidence.

It does not:

- retrain forecasting models;
- modify model selection;
- perform final test evaluation;
- introduce unsupported operational assumptions.

## Reproducibility

- `scripts/create_visualizations.py` runs from any working directory, discovers
  the project root and accepts `VISUALIZATION_INPUT_DIR`,
  `VISUALIZATION_OUTPUT_DIR` and `VISUALIZATION_REPORT_DIR` overrides.
- `scripts/sync_tableau_workbook_schema.py` keeps the workbook's cached schema
  aligned with the CSV headers and is idempotent.
- Every figure's size and SHA-256 digest is recorded in
  `visualization_manifest.csv`.

## Phase 17 Re-Audit Note

The plan was re-read during the audit. Its only material defect was the
Phase 14 input claim above. The remaining content was verified against the
delivered artifacts and left unchanged.
