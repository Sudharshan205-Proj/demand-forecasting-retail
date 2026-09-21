# Phase 15 — Visualization & Tableau

## Purpose

Phase 15 communicates the project's demand forecasting and inventory-planning
findings to non-technical stakeholders through four static matplotlib figures and
an interactive, published Tableau dashboard.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Static figures | 4 PNGs in `data/analysis/visualizations/` — store average daily demand, store demand variability, reorder-point scenarios by lead time, lowest validation RMSE |
| Manifest | `visualization_manifest.csv` — byte size and SHA-256 per figure |
| Pipeline | `scripts/create_visualizations.py`, gated on 55 checks |
| Quality record | `visualization_quality_report.csv` — 55 checks, all passing |
| Tableau workbook | `tableau/Retail_Demand_Forecasting.twb` — 3 data sources, 6 worksheets, 1 dashboard (1600 × 900), 41 layout zones, 3 Bar / 2 Line / 1 Text marks |
| Tableau documentation | `tableau/tableau-dashboard-specification.md`, `tableau/tableau-data-dictionary.md` |
| Tableau Public | Published dashboard at `https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |
| Schema tooling | `scripts/sync_tableau_workbook_schema.py` — idempotent reconciliation of the workbook's cached textscan schema with the current CSV headers |
| Storytelling | `data-storytelling.md` — audience, context, problem, evidence, insights, conditional recommendations, limitations |
| Tests | `tests/test_create_visualizations.py` — 34 tests, all passing |

## Key results

| Finding | Value |
|---|---|
| Charted inputs | 5 analytical files — demand (4 rows), variability (4 rows), scenarios (36 rows), insights (13 rows), validation results (4 rows) |
| Reconciliation | Every charted value matches its source CSV (differences 0); RMSE insight reconciled to `tuned_validation_results.csv` |
| Scenario chart | Reorder points at the assumed 14-day / 95 % baseline — 448,302.491763 / 95,240.141608 / 91,617.640793 / 476,010.139796 |
| Leakage guard | No test-period artifact declared as an input; the forecast-evidence insight must be a validation metric |
| Dashboard KPIs | `29,711 units/day`, `0.3801`, `8.14%` |
| Hidden fields | 5 — `order`, `season_length`, `p90`, `p95`, `p99_daily_demand` |

## Commands

```bash
python scripts/create_visualizations.py
python scripts/sync_tableau_workbook_schema.py
```

## Course coverage

Phase 15 carries the **Share** stage: data visualization, visual analysis, static
and dynamic charting, dashboards, filters, labelling, scale integrity,
accessibility, clutter control, audience awareness and data storytelling
([`course-content-coverage.md`](course-content-coverage.md)).

## Limitations

Scenario lead times and service levels are planning assumptions, not operational
requirements; validation RMSE is scale-bound and is not comparable across stores;
the committed `.twb` requires its three CSV connections re-pointing on a fresh
machine; the published dashboard reflects its publish-time extract; and the
Tableau Public client version is not recorded. Distribution and correlation
visualization are delivered by Phases 7 and 8 rather than this phase.

## Related documents

- [`visualization-methodology.md`](visualization-methodology.md) — method
- [`visualization-quality-framework.md`](visualization-quality-framework.md) — quality practices
- [`visualization-results.md`](visualization-results.md) — results
- [`tableau-dashboard-guide.md`](tableau-dashboard-guide.md) — dashboard structure
- [`data-storytelling.md`](data-storytelling.md) — narrative design
