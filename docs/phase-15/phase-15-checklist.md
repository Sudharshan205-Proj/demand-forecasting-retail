# Phase 15 — Visualization & Tableau Checklist

## Phase Objective

Communicate the project's demand forecasting and inventory-planning findings
to non-technical stakeholders through static visualizations and an interactive
Tableau dashboard.

## Visualization

- [x] Existing analytical outputs inspected — five Phase 13/12 inputs
- [x] Stakeholder visualization requirements identified — `data-storytelling.md`
- [x] Static Python visualization workflow implemented — `scripts/create_visualizations.py`
- [x] Store demand visualization created — 32,067 B, direct labels
- [x] Demand variability visualization created — 36,079 B, direct labels
- [x] Forecast evidence visualization created — 43,048 B
- [x] Inventory scenario visualization created — 103,628 B, 4 stores × 3 lead times
- [x] Visual labels reviewed — every axis states its unit and period
- [x] Scales reviewed — auto-scaled; RMSE axis annotated as not cross-store comparable
- [x] Clutter minimized — no legends where a single series, no gridlines except the scenario chart
- [x] Audience suitability reviewed — technical terms defined on the axis itself

## Workflow Quality

- [x] Every input validated before drawing — demand, variability, scenarios, insights, validation
- [x] Formula reconciliation implemented — CV, variance, expected demand, safety stock, reorder point
- [x] Scenario coverage validated — 3 lead times × 3 service levels per store
- [x] Insight values reconciled on store, metric and value — all five families
- [x] Store sets validated as identical across inputs
- [x] Missing insight raises instead of silently skipping a figure
- [x] Test-period leakage guard implemented and reported as a check
- [x] Machine-readable quality report gates the run — 55 checks
- [x] Output manifest records byte size and SHA-256 for every figure
- [x] Run fails loudly — non-zero exit, no "completed" message
- [x] Location-independent — discovered root plus environment overrides

## Tableau

- [x] Tableau-compatible source prepared — three compact analytical CSVs
- [x] Tableau data dictionary created — `tableau/tableau-data-dictionary.md`
- [x] Tableau dashboard specification created — `tableau/tableau-dashboard-specification.md`
- [x] Tableau workbook created — `tableau/Retail_Demand_Forecasting.twb`
- [x] Worksheets created — 5
- [x] Filters implemented — 6, across store / lead time / service level
- [x] Labels implemented — 6 mark-label settings across the worksheets
- [x] Dashboard layout created — 1 dashboard, 19 zones
- [x] Accessibility reviewed — behaviour not relying on colour alone; **not fully verifiable from the workbook file**
- [x] Dashboard calculations validated — every displayed field reconciles with its CSV source
- [x] Tableau Public publication completed — HTTP 200, canonical URL resolves
- [x] Tableau URL documented only after verification — recorded in `visualization-results.md`
- [x] Cached workbook schema reconciled with the current CSV headers
- [x] Schema reconciliation is idempotent and covered by tests

## Storytelling

- [x] Audience identified — `data-storytelling.md`
- [x] Business context defined
- [x] Problem communicated
- [x] Evidence presented — store demand, variability, forecast evidence, scenarios
- [x] Key insights identified — four insight families plus the scenario reorder points
- [x] Recommendations developed — conditional
- [x] Limitations included
- [x] Narrative flow reviewed — demand → variability → forecast evidence → planning

## Quality

- [x] Python syntax validated
- [x] Python tests passed — 32 Phase 15 tests
- [x] Visualization outputs verified — four non-empty figures, manifest digests matched
- [x] No test-set leakage introduced — leakage guard passes
- [x] Tableau calculations reconciled
- [x] Documentation synchronized

## Git

- [x] Phase branch created — the original Phase 15 implementation was committed
- [x] Changes reviewed
- [x] Correct files staged
- [x] Phase commit created — `f1146d8` "Complete Phase 15 visualization and Tableau"
- [x] Branch pushed
- [x] Final Git state verified

The Git items above are the original Phase 15 implementation record. The
Phase 17 audit performs no Git operations, so they are retained as the phase
record rather than re-asserted by the audit.

## Audit-Added Items (Phase 17 re-audit)

- [x] Re-execute the workflow against the current Phase 13 inputs (the figures
      predated them by eleven days).
- [x] Consume and validate `forecast_inventory_insights.csv` and
      `tuned_validation_results.csv` rather than reading only the first.
- [x] Reconcile every charted value against its source CSV.
- [x] Fail the run when the forecast-evidence insight is missing instead of
      silently drawing three of four figures.
- [x] Add a run-gating 55-check quality report and an output manifest.
- [x] Add `scripts/sync_tableau_workbook_schema.py` and reconcile the
      workbook's stale cached schema in place, preserving declared datatypes.
- [x] Record and verify the published Tableau Public URL.
- [x] Replace the 10 unit-only tests with 32 tests, including workflow
      end-to-end runs and six failure paths.
- [x] Synchronise the Phase 0–14 records that carry Phase 15 status.

## Completion Criteria

| Criterion | Status |
|---|---|
| All phase checklist items completed | COMPLETE |
| Required files exist | COMPLETE — 4 figures, 1 workbook, 2 reports |
| Required code implemented | COMPLETE |
| Required commands executed successfully | COMPLETE — exit 0, 55/55 checks |
| Tests and validation passing | COMPLETE — 32 Phase 15 tests, 55 checks |
| Documentation complete and synchronised | COMPLETE |
| Git state checked and reported | COMPLETE — no Git operation performed by the audit |

Known limitations and unresolved items are recorded in
`docs/phase-15/visualization-results.md` under "Assumptions and Limitations"
and "Remaining Issues".
