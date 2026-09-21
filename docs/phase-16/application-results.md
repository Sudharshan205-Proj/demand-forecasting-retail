# Phase 16 — Application Results

## Environment

| Tool | Version | Evidence |
|---|---|---|
| Python | 3.12.10 | `python -V`; `.python-version` pins the minor line, `3.12` |
| streamlit | 1.63.0 | `pip show streamlit` |
| pandas | 3.0.5 | `pip show pandas` |
| numpy | 2.5.2 | `pip show numpy` |
| matplotlib | 3.11.1 | `pip show matplotlib` |

`requirements.txt` pins every version; `.streamlit/config.toml` sets the server
options the hosted platform uses.

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

Every field is derived from the Phase 12 tables, so adding a store would not
require a code change:

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
plainly in a caveat rather than describing the store as unvalidated.

## Sections rendered

| Section | Source |
|---|---|
| Demand Overview | `inventory_demand_summary.csv` |
| Inventory Scenario | `inventory_scenarios.csv` |
| Selected Model (Phase 12) | `selected_model_configurations.csv`, `tuned_validation_results.csv` |
| Forecast Model Comparison (Phase 11) | `forecasting_model_configurations.csv` |

## Testing

### Automated tests

`tests/test_application.py` — **36 tests, all passing**. They cover:

- formatting helpers, including missing values;
- CSV loading and the missing-artifact message;
- the three-step artifact resolution order, including the deployment-bundle
  fallback and the incomplete-location case;
- bundle integrity: the committed bundle is complete, holds nothing unexpected,
  and is byte-identical to the pipeline output;
- per-store evidence derivation, the fold-count label, and the single-fold
  caveat — including that the caveat never denies the configuration exists;
- scenario filtering and training-day lookup;
- static guarantees: import safety, no module-scope Streamlit calls, no secrets,
  project-relative paths;
- a headless startup smoke test that serves the app on a free port and asserts
  HTTP 200.

### Local application smoke test

```bash
python -m streamlit run app/streamlit_app.py --server.port 8523 --server.headless true
```

HTTP 200 was returned and the accessibility tree contained the page title, all
four section headings, the store selector, both scenario controls and four data
tables. The application was then stopped.

### Full suite

```bash
python -m pytest -q
532 passed
```

## Deployment

The application loads its artifacts from, in order:

1. the `APP_ANALYSIS_DIR` environment variable, when set;
2. `data/analysis/`, when it holds every required artifact;
3. `deploy/artifacts/`, the committed deployment bundle.

`data/analysis/` is excluded from Git, so a platform building from the repository
would otherwise start with no data. The bundle at `deploy/artifacts/` holds all
seven artifacts in **14,977 bytes**, each byte-identical to its pipeline
counterpart.

The hosted deployment is live at
<https://demand-forecasting-retail-internship.streamlit.app/> and renders all four
sections; see [`deployment-validation.md`](deployment-validation.md).

## Analytical limitations

1. Inventory values are scenario-based analytical estimates, not operational
   requirements. Actual lead times and service-level policies are not available.
2. Demand history covers a limited window with no promotional or price data.
3. Store 4's selected configuration rests on a single fold.

## Forecasting limitations

1. Python remains the primary forecasting implementation; the application
   presents validated outputs and never retrains a model.
2. The held-out test period is never used for model selection.
