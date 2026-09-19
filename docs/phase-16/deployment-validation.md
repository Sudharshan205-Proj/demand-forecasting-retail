# Phase 16 — Deployment Validation

## Status

PARTIAL — local deployment is verified end to end; the hosted public
deployment is prepared and pending a one-time authorisation that only the
project owner can grant.

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
| Hosted public deployment reachable | **Pending** | Requires owner authorisation in the Streamlit Cloud UI |

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
Phase 12 section showed `seasonal_naive`, `season_length=7`, 1-fold CV for
Store 4 with its caveat, and `feature_gbm` with 3-fold CV for stores 1-3.

The server was stopped after the check; the automated suite starts its own
instance on a free port so it never collides with a running session.

## Deployment Target

| Setting | Value |
|---|---|
| Platform | Streamlit Community Cloud |
| Repository | `Sudharshan205-Proj/demand-forecasting-retail` |
| Branch | `phase-17-testing-documentation-final-audit` |
| Main file path | `app/streamlit_app.py` |
| Secrets | None |

## Final Deployment Result

A public URL cannot be recorded yet.

Deployment on this platform is performed through the vendor's web UI: the
owner signs in with GitHub, authorises the repository, chooses the branch and
main file path, and the platform builds. That authorisation is an interactive
browser step tied to the owner's account and is not something the development
environment can perform on the owner's behalf.

Everything the platform needs is committed, so the remaining action is a
one-time click-through. This document intentionally records the step as
pending rather than claiming a deployment that has not been observed.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
