# Phase 16 — Application Development & Deployment

## Purpose

Phase 16 delivers the project's decision-support interface: a Streamlit
application that presents the validated demand, model and inventory results, and
the deployment that makes it reachable from the repository alone.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Application | `app/streamlit_app.py` (451 lines) with `config.py`, `data_loader.py`, `formatting.py`, `logging_config.py` |
| Sections | Demand Overview, Inventory Scenario, Selected Model (Phase 12), Forecast Model Comparison (Phase 11) |
| Inputs | Seven compact CSV artifacts, resolved from `APP_ANALYSIS_DIR` → `data/analysis/` → `deploy/artifacts/` |
| Deployment bundle | `deploy/artifacts/` — seven CSVs, 14,977 bytes, byte-identical to the pipeline output |
| Host configuration | `.streamlit/config.toml`, `.python-version`, `requirements.txt` |
| Tests | `tests/test_application.py` — 36 tests, all passing, including a headless startup smoke test |
| Hosted deployment | Streamlit Community Cloud — `https://demand-forecasting-retail-internship.streamlit.app/` |

## Key results

| Item | Value |
|---|---|
| Per-store evidence | Stores 1–3 `feature_gbm`, 3-fold CV; Store 4 `seasonal_naive`, `season_length=7`, 1-fold CV with caveat |
| Local launch | HTTP 200, 4 section headings, store selector, both scenario controls, 4 data tables |
| Artifact resolution | Environment override, then `data/analysis/`, then the deployment bundle; incomplete locations rejected |
| Security | No secrets required or committed; project-relative paths only; asserted by tests |
| Regression safety | Application imports without a Streamlit runtime; no Streamlit call at module scope |
| Full suite | 532 passed |

## Commands

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py
```

## Course coverage

Phase 16 carries the **Act** stage: application development, interactive
filtering, data interpretation and communication, KPI presentation, decision
support and deployment ([`course-content-coverage.md`](course-content-coverage.md)).

## Limitations

Automated tests do not replace human usability review; the application presents
model evidence without validating it, so input integrity remains a pipeline
concern; and inventory scenario values remain planning estimates rather than
operational requirements.

## Related documents

- [`application-development-plan.md`](application-development-plan.md) — design
- [`application-architecture.md`](application-architecture.md) — structure
- [`application-quality-framework.md`](application-quality-framework.md) — quality practices
- [`application-results.md`](application-results.md) — results
- [`deployment-plan.md`](deployment-plan.md) — deployment model
- [`deployment-validation.md`](deployment-validation.md) — deployment evidence
