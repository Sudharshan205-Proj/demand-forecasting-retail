# Project Architecture

## Design goals

The project is a modular retail demand forecasting system that separates data
acquisition, data validation, data processing, analysis, forecasting,
evaluation, visualization, application and deployment.

Phases are the organizing unit: each phase owns its own scripts, artifacts and
documentation, which keeps a phase's method, output and evidence together.

## Repository layout

```text
demand-forecasting-retail/
│
├── app/                       Streamlit application (Phase 16)
├── .streamlit/config.toml     application runtime configuration
├── data/
│   ├── raw/                   source CSVs (Git-excluded; placeholder tracked)
│   ├── processed/             cleaned and integrated datasets (Git-excluded; placeholder tracked)
│   └── analysis/              generated analytical outputs (Git-excluded)
├── deploy/
│   ├── artifacts/             committed bundle of 7 CSV artifacts
│   └── README.md
├── docs/                      phase-0/ … phase-17/
├── r/                         r_analysis.R, r_analysis_report.Rmd (Phase 14)
├── reports/figures/           generated figures (Git-excluded)
├── scripts/                   15 phase-owned Python scripts
├── sql/                       schema.sql, retail_analysis.sql (Phase 4)
├── tableau/                   Retail_Demand_Forecasting.twb and specifications (Phase 15)
├── tests/                     18 pytest modules
├── demand-forecasting-retail.Rproj
├── requirements.txt
├── pyproject.toml
├── .python-version
├── .gitignore
└── README.md
```

Each pipeline stage is a single named script under `scripts/`, runnable from the
repository root with no hardcoded absolute paths. Generated data is excluded
from Git and rebuilt from the raw dataset; the one committed data exception is
the `deploy/artifacts/` bundle, which lets a repository build start the
application.

## Data flow

```text
Raw data (8 CSVs)
   │
   ▼
Inspection and validation        (Phase 2)
   │
   ▼
Cleaning                          (Phase 5)
   │
   ▼
Integration                       (Phase 6)
   │
   ▼
Analytical dataset (34 columns)
   │
   ├────► Spreadsheet analysis    (Phase 3)
   ├────► SQL analysis            (Phase 4)
   ├────► Exploratory analysis    (Phase 7)
   ├────► Statistical analysis    (Phase 8)
   └────► R analysis              (Phase 14)
   │
   ▼
Time-series partitions            (Phase 9)
   │
   ▼
Feature matrix                    (Phase 10)
   │
   ▼
Forecasting models                (Phase 11)
   │
   ▼
Evaluation and selection          (Phase 12)
   │
   ▼
Inventory insights                (Phase 13)
   │
   ├────► Tableau dashboard       (Phase 15)
   ├────► Static figures          (Phase 15)
   └────► Streamlit application   (Phase 16)
   │
   ▼
Business insights and recommendations
```

## Separation of concerns

- Data-processing code contains no dashboard logic.
- Forecasting code contains no user-interface logic.
- Evaluation is independent of visualization.
- The application consumes validated artifacts rather than duplicating the
  data-processing pipeline. It reads seven compact CSV artifacts and never
  retrains a model.

## Application and deployment

The Streamlit application resolves its seven input artifacts, in order, from the
`APP_ANALYSIS_DIR` environment variable, from `data/analysis/` when that
directory is complete, or from the committed `deploy/artifacts/` bundle.
`tests/test_application.py` reconciles every bundled file against pipeline
output by SHA-256.

The application is deployed on Streamlit Community Cloud at
<https://demand-forecasting-retail-internship.streamlit.app/>, where it reads the
committed bundle.

## API

An API was assessed during application development and deliberately not
introduced. The application is a single-process Streamlit interface that reads
seven committed CSV artifacts; an API would add a service boundary with no
consumer.

## Model persistence

No trained model is persisted as a versioned artifact. Every stage is
deterministic with fixed seeds, so the selected configurations are refit from
the validated Phase 10–12 artifacts on demand and the application never
retrains; a serialised model would duplicate evidence that is already
reproducible and version-controlled as data.

## Configuration

Environment-specific settings are separated from source code. The application
reads its artifact directory from `APP_ANALYSIS_DIR` when set. Secrets are never
hardcoded, and the project requires none.

## Logging

Application and pipeline operations use structured logging. Sensitive
information is never logged.
