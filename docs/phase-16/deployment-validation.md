# Phase 16 — Deployment Validation

## Status

Local deployment is verified end to end, and the hosted public deployment is live
and verified: all four sections render at the public URL.

## Validation Checklist

| Check | Result | Evidence |
|---|---|---|
| Application imports without a Streamlit runtime | Pass | `test_module_imports_without_a_streamlit_runtime` |
| No Streamlit call runs at module scope | Pass | `test_no_streamlit_calls_run_at_module_scope` |
| All seven artifacts resolve locally | Pass | `resolve_analysis_dir()` → `data/analysis` |
| Resolution honours the environment override | Pass | `test_resolution_honours_the_environment_override` |
| Resolution falls back to `deploy/artifacts/` | Pass | `test_resolution_falls_back_to_the_deployment_bundle` |
| An incomplete location is rejected, not half-used | Pass | `test_resolution_returns_the_local_path_when_nothing_is_complete` |
| Bundle is complete | Pass | `test_deployment_bundle_is_complete` |
| Bundle holds nothing unexpected | Pass | `test_deployment_bundle_holds_nothing_unexpected` |
| Bundle matches the pipeline output | Pass | `test_deployment_bundle_matches_the_pipeline_output` (SHA-256, 7 of 7 identical) |
| Application source contains no secrets | Pass | `test_application_source_contains_no_secrets` |
| Paths are project-relative | Pass | `test_application_uses_project_relative_paths` |
| Hosted platform configuration present | Pass | `.streamlit/config.toml`, `.python-version`, `requirements.txt` |
| Hosted public deployment reachable | Pass | `https://demand-forecasting-retail-internship.streamlit.app/` — all four sections rendered |

## Local Smoke Test

Command:

```text
python -m streamlit run app/streamlit_app.py --server.port 8523 --server.headless true
```

Observed:

| Observation | Result |
|---|---|
| HTTP status | 200 |
| Page title | `Retail Demand Forecasting & Inventory Insights` |
| Section headings rendered | 4 |
| Store selector | Present, stores 1-4 |
| Scenario controls | Lead time, service level |
| Data tables rendered | 4 |
| Console errors | None |

The four sections rendered were: *Demand Overview*, *Inventory Scenario*,
*Selected Model (Phase 12)* and *Forecast Model Comparison (Phase 11)*. The
Phase 12 section showed `seasonal_naive`, `season_length=7`, 1-fold CV for Store 4
with its caveat, and `feature_gbm` with 3-fold CV for stores 1-3.

The server was stopped after the check; the automated suite starts its own
instance on a free port so it never collides with a running session.

## Deployment Target

| Setting | Value |
|---|---|
| Platform | Streamlit Community Cloud |
| Repository | `Sudharshan205-Proj/demand-forecasting-retail` |
| Branch | `main` |
| Main file path | `app/streamlit_app.py` |
| Secrets | None |

## Hosted Deployment Result

| Item | Value |
|---|---|
| Public URL | `https://demand-forecasting-retail-internship.streamlit.app/` |
| Sections rendered | 4 — Demand Overview, Inventory Scenario, Selected Model (Phase 12), Forecast Model Comparison (Phase 11) |
| Data source on the host | `deploy/artifacts/` (the committed repository bundle) |
| Secrets | None |

Deployment was performed through the vendor's web UI: the owner signed in with
GitHub, authorised the repository, chose the branch `main` and the main file path
`app/streamlit_app.py`, and the platform built the application from the committed
configuration.

Everything the platform needs is committed, so the deployed instance starts from
the repository alone. A first visit can take a moment while a sleeping instance
starts; the application renders once it does.
