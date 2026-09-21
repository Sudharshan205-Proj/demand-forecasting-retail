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

Loads validated analytical CSV artifacts and reports every missing file by name
before raising.

### Formatting

```text
app/formatting.py
```

Handles user-facing numeric formatting, including values that arrive either as a
ratio or as an already-scaled percentage.

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

## Sections

| Section | Evidence source |
|---|---|
| Demand Overview | `inventory_demand_summary.csv` |
| Inventory Scenario | `inventory_scenarios.csv` |
| Selected Model (Phase 12) | `selected_model_configurations.csv`, `tuned_validation_results.csv` |
| Forecast Model Comparison (Phase 11) | `forecasting_model_configurations.csv` |

## Security

The application requires no API keys or credentials for the documented workflow.

No credentials are hardcoded into source code; a test asserts this and a second
test asserts that every path used is project-relative.
