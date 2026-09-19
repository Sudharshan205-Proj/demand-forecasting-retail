# Phase 16 — Deployment Plan

## Objective

Make the Streamlit application reproducible and deployable without requiring
the large raw or feature-engineered datasets during normal application use.

## Deployment Model

The application runs from the project repository. Because `data/analysis/` is
excluded from Git, the repository carries a small frozen snapshot of the
compact artifacts the application loads:

```text
deploy/artifacts/     seven CSVs, 14,977 bytes
```

Resolution order, implemented in `app/config.py`:

| Order | Location | When it applies |
|---|---|---|
| 1 | `APP_ANALYSIS_DIR` environment variable | Explicit override, used by the tests |
| 2 | `data/analysis/` | Local development, after the pipeline has run |
| 3 | `deploy/artifacts/` | A host that built from the repository |

A location is only accepted when it holds **every** required artifact, so a
half-populated `data/analysis/` falls through to the bundle rather than
failing halfway through a render.

## Local Deployment

```text
python -m streamlit run app/streamlit_app.py
```

## Hosted Deployment

| Setting | Value |
|---|---|
| Platform | Streamlit Community Cloud |
| Repository | `Sudharshan205-Proj/demand-forecasting-retail` |
| Branch | `phase-17-testing-documentation-final-audit` |
| Main file path | `app/streamlit_app.py` |
| Python version | 3.12 (from `.python-version`) |
| Secrets | None required |

`.streamlit/config.toml` sets `headless = true`, `enableCORS = true` and
`gatherUsageStats = false` so the same configuration serves both the local run
and the host.

## Deployment Requirements

The deployment environment requires:

- Python 3.12
- Project dependencies from `requirements.txt`
- Application source code
- The analytical CSV artifacts, supplied by `deploy/artifacts/`

## Security

No secrets are required by the application.

No credentials are committed to Git. A test asserts that the application
source contains no secret-like assignments.

## Important Limitation

A successful deployment must not be claimed until the application has actually
been launched and validated in the target environment.

## Deployment Status

- Local launch: **VERIFIED**. HTTP 200 on port 8523, all four sections
  rendered, then stopped.
- Artifact availability from a clean clone: **VERIFIED**. The committed bundle
  is complete, contains nothing unexpected and is byte-identical to the
  pipeline output.
- Hosted public deployment: **PENDING**. Streamlit Community Cloud deployment
  requires a one-time authorisation in the platform's web UI, which cannot be
  performed from the development environment.

## Phase 17 Re-Audit Record

The original plan named `data/analysis/` as the deployment input. That
directory is gitignored, so the plan as written could not have produced a
working deployment on any host: the build would have succeeded and the first
page load would have failed. The committed bundle and the resolution order
close that gap, and a test reconciles the bundle against the pipeline output
so it cannot silently drift.

The status line previously read `NOT YET VERIFIED` while nothing had been run.
Status is now split into the three verifiable claims above.
