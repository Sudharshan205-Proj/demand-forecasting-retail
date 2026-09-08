# Phase 16 — Application Architecture

## Architecture

```text
Validated Phase 12–13 Analysis Artifacts
                |
                v
        Application Data Loader
                |
        +-------+--------+
        |                |
        v                v
   Formatting         Validation
        |                |
        +-------+--------+
                |
                v
        Streamlit Interface
                |
       +--------+---------+
       |        |         |
       v        v         v
     Demand   Forecast  Inventory
     KPIs     Results   Scenarios
```
## Separation of Concerns

### Configuration

```text
app/config.py

Defines project-relative paths.

### Data Loading

```text
app/data_loader.py
```

Loads validated analytical CSV artifacts.

### Formatting

```text
app/formatting.py
```

Handles user-facing numeric formatting.

### Logging

```text
app/logging_config.py
```

Provides application logging.

### Presentation

```text
app/streamlit_app.py
```

Contains Streamlit UI and interaction logic.

## Data Flow

The application reads existing analytical outputs.

No model training occurs during application startup or user interaction.

## Security

The application requires no API keys or credentials for the documented
local workflow.

No credentials should be hardcoded into source code.