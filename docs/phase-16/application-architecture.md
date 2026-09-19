# Phase 16 — Application Architecture

## Architecture

```text
Validated Phase 11-13 Analysis Artifacts
                |
                v
     Artifact Resolution (app/config.py)
     env override -> data/analysis/ -> deploy/artifacts/
                |
                v
        Application Data Loader
        (app/data_loader.py)
                |
        +-------+--------+
        |                |
        v                v
   Formatting        Validation
 (formatting.py)   (required files)
        |                |
        +-------+--------+
                |
                v
        Streamlit Interface
        (streamlit_app.py, all calls inside main())
                |
       +--------+---------+
       |        |         |
       v        v         v
     Demand   Selected  Inventory
     KPIs     Model     Scenarios
              (Phase 12)
```

## Separation of Concerns

### Configuration

```text
app/config.py
```

Defines project-relative paths, the seven artifact file names, the
`APP_ANALYSIS_DIR` override, and the resolution order.

### Data Loading

```text
app/data_loader.py
```

Loads validated analytical CSV artifacts and reports every missing file by
name before raising.

### Formatting

```text
app/formatting.py
```

Handles user-facing numeric formatting, including values that arrive either
as a ratio or as an already-scaled percentage.

### Logging

```text
app/logging_config.py
```

Provides application logging.

### Presentation

```text
app/streamlit_app.py
```

Contains the Streamlit UI and interaction logic. Every Streamlit call happens
inside `main()`, so the module imports cleanly in a test process and the pure
helpers below can be exercised directly:

| Helper | Purpose |
|---|---|
| `find_column` | Case-insensitive column lookup |
| `store_ids` | Sorted store identifiers |
| `selected_model_evidence` | Phase 12 selection for one store |
| `evidence_label` | Fold-count label |
| `evidence_caveat` | Single-fold caveat, or `None` |
| `filter_scenarios` | Lead-time and service-level filter |
| `training_days_for` | Training-window length for one store |

## Data Flow

The application reads existing analytical outputs.

No model training occurs during application startup or user interaction.

## Security

The application requires no API keys or credentials for the documented
workflow.

No credentials are hardcoded into source code; a test asserts this and a
second test asserts that every path used is project-relative.

## Phase 17 Re-Audit Record

- The original diagram's `Configuration` section was opened with a code fence
  that was never closed, which swallowed the rest of the document. The fenced
  block is corrected.
- The original data-flow section claimed the application consumes
  "Phase 12-13" artifacts. It consumes Phase 11 artifacts as well
  (`forecasting_model_results.csv`, `forecasting_model_configurations.csv`),
  so the scope is corrected to Phase 11-13.
- The `Validation` box is now a real stage: resolution requires every artifact
  to exist and the loader names each gap before failing, rather than an
  implicit assumption.

**Known gap recorded, not smoothed over:** the seven pure helpers are covered
by automated tests, but no human usability review of the rendered interface
has been performed. Layout and accessibility have been observed, not
evaluated.
