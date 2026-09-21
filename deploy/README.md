# Deployment bundle

`artifacts/` holds a frozen snapshot of the compact analytical inputs the
application needs, so a deployed instance can start without the analysis pipeline
having been run on the host.

## Why this exists

The application reads its inputs from `data/analysis/`, and `.gitignore` excludes
that directory because those files are generated artifacts of Phases 11–13. A host
that builds from the repository would therefore start with no data at all and fail
on load.

The bundle is a deliberate, labelled exception: seven small CSVs, 14,977 bytes in
total, committed so the application is genuinely deployable.

## What is in it

| File | Produced by |
|---|---|
| `inventory_demand_summary.csv` | Phase 13 |
| `inventory_variability_summary.csv` | Phase 13 |
| `inventory_scenarios.csv` | Phase 13 |
| `forecasting_model_results.csv` | Phase 11 |
| `forecasting_model_configurations.csv` | Phase 11 |
| `selected_model_configurations.csv` | Phase 12 |
| `tuned_validation_results.csv` | Phase 12 |

## How it is used

`app/config.py` resolves the artifact directory in this order:

1. `APP_ANALYSIS_DIR`, when set;
2. `data/analysis/`, when it holds every required artifact (the local case);
3. `deploy/artifacts/`, this bundle (the deployed case).

The application's **Data source** panel shows which directory was used.

## Consistency with the pipeline

`tests/test_application.py` reconciles every bundled file against the pipeline
output by SHA-256, so the deployed application cannot silently drift from the
local one. Refresh the bundle after a pipeline re-run that changes these
artifacts:

```bash
cp data/analysis/inventory_demand_summary.csv \
   data/analysis/inventory_variability_summary.csv \
   data/analysis/inventory_scenarios.csv \
   data/analysis/forecasting_model_results.csv \
   data/analysis/forecasting_model_configurations.csv \
   data/analysis/selected_model_configurations.csv \
   data/analysis/tuned_validation_results.csv \
   deploy/artifacts/
```
