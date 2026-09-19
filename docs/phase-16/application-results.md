# Phase 16 — Application Results

## Status

VERIFIED — the application was executed locally on 19 September 2026, its
36 tests pass, the deployment bundle is committed and its artifact-resolution
order is tested end to end. The public hosted deployment is PENDING: it
requires a one-time Streamlit Community Cloud authorisation that only the
project owner can perform in a browser.

Every number below was read from a generated artifact or produced by a
command recorded in this document. Nothing was entered by hand.

## Environment

| Tool | Version | Evidence |
|---|---|---|
| Python | 3.12.10 | `.python-version`, `python -V` |
| streamlit | 1.63.0 | `pip show streamlit` |
| pandas | 3.0.5 | `pip show pandas` |
| numpy | 2.5.2 | `pip show numpy` |
| matplotlib | 3.11.1 | `pip show matplotlib` |

`requirements.txt` pins every version; `.streamlit/config.toml` sets the
server options the hosted platform uses.

## Implementation

| File | Lines | Role |
|---|---|---|
| `app/config.py` | 74 | Artifact names, resolution order, required-file check |
| `app/data_loader.py` | 69 | CSV loading, missing-artifact reporting, `load_application_data()` |
| `app/formatting.py` | 48 | `format_number`, `format_percent`, `format_ratio_as_percent` |
| `app/logging_config.py` | 21 | Shared logger |
| `app/streamlit_app.py` | 451 | UI plus the pure helpers the tests exercise |

Seven named artifacts are loaded, all listed once in `ARTIFACT_FILES`:

`inventory_demand_summary.csv`, `inventory_variability_summary.csv`,
`inventory_scenarios.csv`, `forecasting_model_results.csv`,
`forecasting_model_configurations.csv`, `selected_model_configurations.csv`,
`tuned_validation_results.csv`.

## Per-store model evidence

The application no longer hardcodes which stores are "validated". Every field
is derived from the Phase 12 tables, so adding a store would not require a
code change:

| Store | Model | Configuration | Folds | Mean CV RMSE | Validation RMSE | Label |
|---|---|---|---|---|---|---|
| 1 | `feature_gbm` | HistGradientBoosting, `max_iter=200`, `max_depth=3` | 3 | 3,804.01 | 4,233.49 | Validated (3-fold CV) |
| 2 | `feature_gbm` | HistGradientBoosting, `max_iter=200`, `max_depth=3` | 3 | 620.51 | 711.21 | Validated (3-fold CV) |
| 3 | `feature_gbm` | HistGradientBoosting, `max_iter=200`, `max_depth=3` | 3 | 599.44 | 1,309.96 | Validated (3-fold CV) |
| 4 | `seasonal_naive` | `season_length=7` | 1 | 3,908.95 | 6,063.06 | Validated (1-fold CV) |

Source: `deploy/artifacts/selected_model_configurations.csv` and
`deploy/artifacts/tuned_validation_results.csv`.

Store 4 is a **validated configuration** selected on a single cross-validation
fold because its 60-day history supports only one. The application states that
plainly in a caveat instead of describing the store as unvalidated — the
earlier `"Descriptive"` label was false and contradicted the project's own
Phase 12 evidence.

## Sections rendered

| Section | Source |
|---|---|
| Demand Overview | `inventory_demand_summary.csv` |
| Inventory Scenario | `inventory_scenarios.csv` |
| Selected Model (Phase 12) | `selected_model_configurations.csv`, `tuned_validation_results.csv` |
| Forecast Model Comparison (Phase 11) | `forecasting_model_configurations.csv` |

The section previously headed "Selected Model Configuration" displayed the
Phase 11 three-model comparison and never showed the Phase 12 selection. The
two are now separate, correctly named sections.

## Testing

### Automated tests

`tests/test_application.py` — **36 tests, all passing**. They cover:

- formatting helpers, including missing values;
- CSV loading and the missing-artifact message;
- the three-step artifact resolution order, including the deployment-bundle
  fallback and the incomplete-location case;
- bundle integrity: the committed bundle is complete, holds nothing
  unexpected, and is byte-identical to the pipeline output;
- per-store evidence derivation, the fold-count label, and the single-fold
  caveat — including that the caveat never denies the configuration exists;
- scenario filtering and training-day lookup;
- static guarantees: import safety, no module-scope Streamlit calls, no
  secrets, project-relative paths;
- a headless startup smoke test that serves the app on a free port and
  asserts HTTP 200.

### Local application smoke test

```
python -m streamlit run app/streamlit_app.py --server.port 8523 --server.headless true
```

HTTP 200 was returned and the accessibility tree contained the page title, all
four section headings, the store selector, both scenario controls and four
data tables. The application was then stopped.

### Full suite

```
python -m pytest -q
530 passed, 1 warning in 248.36s
```

## Deployment

The application loads its artifacts from, in order:

1. the `APP_ANALYSIS_DIR` environment variable, when set;
2. `data/analysis/`, when it holds every required artifact;
3. `deploy/artifacts/`, the committed deployment bundle.

`data/analysis/` is excluded from Git, so a platform building from the
repository would otherwise start with no data. The bundle at
`deploy/artifacts/` holds all seven artifacts in **14,977 bytes**, each
byte-identical to its pipeline counterpart.

The hosted deployment itself is **PENDING**: it needs a one-time authorisation
in the Streamlit Community Cloud web UI, which cannot be performed from the
development environment. See `deployment-validation.md`.

## Analytical limitations

1. Inventory values are scenario-based analytical estimates, not operational
   requirements. Actual lead times and service-level policies are not
   available.
2. Demand history covers a limited window with no promotional or price data.
3. Store 4's selected configuration rests on a single fold.

## Forecasting limitations

1. Python remains the primary forecasting implementation; the application
   presents validated outputs and never retrains a model.
2. The held-out test period is never used for model selection.

## Phase 17 Re-Audit Record

**Defects found in this audit**

| ID | Defect | Resolution |
|---|---|---|
| F1 | `application-results.md` said IN PROGRESS with tests, smoke test and deployment "NOT YET VERIFIED" while the application was implemented and committed | Re-executed and rewritten from measured results |
| F2 | `streamlit_app.py` hardcoded `"Validated" if store in [1,2,3] else "Descriptive"` and warned that Store 4 had no validated tuned configuration — both false | Evidence now derived from the Phase 12 tables; caveat states the single-fold limitation accurately |
| F3 | The "Selected Model Configuration" section displayed the Phase 11 comparison, and the Phase 12 selection was never shown | Sections split and correctly named |
| F4 | Every artifact the app loads lived under gitignored `data/analysis/`, so a repository build had no data | `deploy/artifacts/` bundle committed with a tested resolution order |
| F5 | An empty `if/else` with identical branches in the service-level filter | Removed |
| F6 | `forecast_inventory_insights.csv` was loaded and never displayed | Removed from `ARTIFACT_FILES` |
| F7 | `FORECAST_SUMMARY_FILE` was declared and never used | Removed |
| F8 | `sys.path.insert` hack plus module-scope Streamlit calls made the app unimportable | All Streamlit calls moved into `main()`; import safety is now a test |
| F9 | 5 trivial tests never exercised loading, derivation or startup | Grown to 36, including end-to-end and failure paths |
| F10 | Broken code fence in `application-architecture.md` | Corrected |

**Verification performed**

- `python -m pytest tests/test_application.py -q` → 36 passed
- `python -m pytest -q` → 530 passed
- Headless launch → HTTP 200, four tables, four section headings
- Bundle reconciliation → 7 of 7 files byte-identical (SHA-256 compared)
- Store evidence derivation printed for all four stores and checked against
  `selected_model_configurations.csv`

**Known gaps recorded, not smoothed over**

- The hosted public deployment is not yet live; it awaits owner authorisation.
- No human usability review has been performed.
