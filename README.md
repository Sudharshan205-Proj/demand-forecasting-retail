# Demand Forecasting for Retail

An internship-level data analytics case study that forecasts daily retail demand
and translates the forecasts into conditional inventory-planning insights.

The project follows the full analytical lifecycle:

**Ask → Prepare → Process → Analyze → Share → Act**

## Project Overview

Demand Forecasting for Retail works from a historical retail sales dataset
covering four stores over a 25-month period. It cleans and integrates the sales
and supporting product, price, promotion and discount data, explores and
quantifies demand behaviour, prepares a chronological forecasting dataset,
builds leakage-safe time-series features, develops and evaluates forecasting
models, and converts the validated results into store-level inventory-planning
scenarios.

The complete analytical chain is delivered end to end:

Business problem → analytical questions → data acquisition → data preparation →
data cleaning → data integration → exploratory analysis → statistical analysis →
time-series preparation → feature engineering → forecasting → model evaluation →
inventory insights → R analysis → visualization and Tableau → application →
conclusions.

## Business Problem

Retail demand varies across stores and over time, so inventory planning has to
account for both the level of demand and its variability. Ordering too little
risks stockouts; ordering too much ties up working capital and creates excess
stock. The dataset does not contain supplier lead times, service-level policies,
costs or current stock, so the project answers the analytical part of the
problem — how much demand should be expected, how variable it is, and how
reliable the forecasts are — and expresses inventory quantities as explicit
scenarios rather than operational requirements.

## Objective

- Forecast daily store-level demand from historical sales.
- Quantify demand level, variability and seasonality.
- Compare forecasting approaches against benchmarks under chronological
  validation.
- Evaluate forecasts with RMSE and MAPE.
- Translate the validated forecasts into inventory-planning scenarios.
- Communicate the results through static figures, an interactive Tableau
  dashboard and a Streamlit application.

## Analytical Approach

| Stage | What the project does |
|---|---|
| Ask | Defines the business problem, SMART analytical questions, stakeholders and KPIs |
| Prepare | Acquires the dataset, documents sources and the data dictionary, assesses credibility and ethics, and analyses the sales data with spreadsheets and SQL |
| Process | Cleans the sales data under deterministic rules and integrates eight sources into one analytical matrix |
| Analyze | Explores demand patterns, quantifies statistics, prepares the chronological time series, engineers features, and develops and evaluates forecasting models |
| Share | Communicates the results through static figures, a published Tableau dashboard and an R Markdown report |
| Act | Derives inventory-planning scenarios and serves the results through a deployed Streamlit application |

## Dataset

| Property | Value |
|---|---|
| Source | Kaggle retail sales forecasting dataset (CC BY-NC-SA 4.0) |
| Raw files | 8 CSVs, ≈824 MB |
| Coverage | 2022-08-28 → 2024-09-26 |
| Stores | 4 |
| Sales rows | 7,432,685 raw → 7,431,026 cleaned |
| Integrated dataset | 34 columns, 1,283,859,491 bytes |
| Total demand | 41,949,529.910 units |
| Total revenue | 5,659,219,309.90 |

The raw data is not committed to the repository; the dataset is downloaded and
the pipeline is re-run to reproduce it. The integrated dataset reconciles with
the cleaned source on rows and on total quantity.

Two dataset characteristics shape the analysis:

- **No holiday field.** Phase 2 verified an explicit holiday variable is absent,
  so holiday analysis is recorded as not applicable rather than approximated.
- **No lead times, costs or stock levels.** Inventory outputs are therefore
  scenario-based estimates.

## Technologies

| Area | Tools |
|---|---|
| Data preparation and analysis | Python 3.12, pandas, NumPy, SciPy |
| Spreadsheet analysis | Excel workbook generated with openpyxl |
| Database analysis | SQLite, SQL |
| Forecasting | statsmodels (ARIMA), scikit-learn (HistGradientBoostingRegressor) |
| Statistical analysis | SciPy, statsmodels |
| Visualization | matplotlib; Tableau Public |
| R analysis | R 4.6.1, tidyverse (dplyr, ggplot2, readr), yardstick, R Markdown, RStudio |
| Application | Streamlit |
| Testing | pytest |
| Version control | Git, GitHub |

## Project Structure

```text
app/            Streamlit application (config, data loading, formatting, UI)
.streamlit/     Streamlit runtime configuration
data/           raw / processed / analysis data (raw and generated data excluded from Git)
deploy/         committed artifact bundle so a repository build can start the app
docs/           phase-by-phase documentation — start at docs/README.md
r/              R analysis script and R Markdown report
reports/        generated analysis figures (rebuilt by the phase scripts)
scripts/        phase-owned Python pipeline scripts
sql/            SQL schema and analysis queries
tableau/        Tableau workbook and dashboard documentation
tests/          pytest suite (532 tests)
```

## Methodology

The project is organized into 18 phases (`docs/phase-0/` … `docs/phase-17/`).
Each technical phase documents its method, its results and the quality practices
that its outputs are held to.

| Phase | Name |
|---|---|
| 0 | Project Setup & Curriculum Mapping |
| 1 | Business Understanding & Planning |
| 2 | Data Acquisition & Data Understanding |
| 3 | Spreadsheet-Based Analysis |
| 4 | SQL & Database Analysis |
| 5 | Data Cleaning & Quality Assurance |
| 6 | Data Integration |
| 7 | Exploratory Data Analysis |
| 8 | Statistical & Analytical Analysis |
| 9 | Time-Series Preparation |
| 10 | Feature Engineering |
| 11 | Forecasting Models |
| 12 | Model Evaluation & Tuning |
| 13 | Forecasting & Inventory Insights |
| 14 | R Analysis |
| 15 | Visualization & Tableau |
| 16 | Application Development & Deployment |
| 17 | Testing, Documentation & Finalization |

Key methodological decisions:

- **Chronological separation.** Train → 2024-02-10 (4,315,416 rows), validation →
  2024-06-03 (1,548,957 rows), test → 2024-09-26 (1,566,653 rows, reserved).
  No random shuffling is used anywhere in the forecasting workflow.
- **Missing observations stay missing.** Phase 9 records 12,553,017 missing
  intermediate dates across 55,122 of 58,022 item-store series instead of
  zero-filling them; the store-day models densify to a complete calendar, where
  an absent day correctly means no recorded quantity.
- **Leakage-safe features.** Lags and rolling statistics are computed on the
  shifted series, so the target day's own demand never enters its own features.

## Forecasting

| Model | Definition |
|---|---|
| Naive | Last observed training value |
| Seasonal naive | `season_length = 7` (7, 14 and 28 evaluated) |
| ARIMA | `ARIMA(1,1,1)` per store, `enforce_stationarity=False`, `enforce_invertibility=False` |
| Feature-based | `HistGradientBoostingRegressor` over 16 store-day lag, rolling and calendar features, with recursive multi-step forecasting |

Phase 12 evaluates nine candidate configurations per store over expanding-window
cross-validation with a fixed 28-day horizon, selects one configuration per
store on training-period cross-validation evidence only, and then evaluates the
selection on the untouched validation period.

## Evaluation

- **RMSE** (root mean squared error) is the primary selection metric.
- **MAPE** (mean absolute percentage error) is the complementary metric and the
  tie-break; zero-demand observations are excluded, and none occur at the
  store-day grain.
- Every reported metric is recomputed from the stored forecasts, so a metric
  cannot drift from the predictions that produced it.
- The reserved test period is never used for selection, tuning or evaluation of
  the delivered models.

## Results

| Item | Value |
|---|---|
| Seasonal-naive mean validation RMSE | 3,223.0630 |
| Selected models | `feature_gbm` for Stores 1–3; `seasonal_naive(7)` for Store 4 |
| Tuned mean validation RMSE | 3,079.4286 (−4.46% against the best single Phase 11 model) |
| Store-level validation RMSE | 4,233.49 / 711.21 / 1,309.96 / 6,063.06 |
| Systematic bias | Every selected model under-forecasts; mean 1,409.941 units/day |
| Highest average daily demand | Store 1 — 29,711.253352 |
| Highest relative variability | Store 4 — CV 0.380098 |
| Lowest relative validation error | Store 2 — MAPE 8.141356 % |
| 14-day / 95 % reorder points | 448,302.49 / 95,240.14 / 91,617.64 / 476,010.14 |
| Forecast-error safety stock | 20.19%–57.67% lower than historical-variability safety stock |

## Key Insights

1. **Demand level and demand variability are different risks.** Store 1 carries
   the highest average demand while Store 4 carries the highest relative
   variability, so a single ranking of "riskiest store" would be misleading.
2. **The store-day forecasting unit is dominated by weekly seasonality.** A
   seven-day seasonal-naive benchmark beats ARIMA(1,1,1) on the validation
   period; the feature-based model adds value beyond it for the three stores with
   full history.
3. **The models systematically under-forecast.** Bias is positive at every
   store, which is why the inventory analysis carries an explicit bias
   correction instead of assuming unbiased forecasts.
4. **Buffer sizing depends on which uncertainty you use.** Sizing safety stock
   from raw historical spread produces a materially larger buffer than sizing it
   from the error the selected model actually makes, at every store.
5. **Evidence strength varies by store.** Store 4's configuration rests on one
   cross-validation fold and 60 training observations; the project states that
   caveat wherever the store's numbers appear.

## Inventory Insights

Two scenario families are produced at every combination of 7, 14 and 28-day lead
times and 90 %, 95 % and 99 % service levels (36 scenarios each):

- **historical-variability** — level = training-period mean demand, uncertainty =
  training-period standard deviation;
- **forecast-error** — level = the selected model's bias-corrected validation
  demand, uncertainty = the standard deviation of its validation residual.

Safety stock uses `SS = z × σ × √L` and the reorder point uses
`ROP = expected lead-time demand + SS`. These are planning scenarios: the
dataset provides no lead times, service-level policies or costs, so the
assumptions are stated explicitly rather than presented as business policy.

## Visualization

- Four matplotlib figures: average daily demand by store, relative demand
  variability, reorder-point scenarios by lead time, and lowest validation RMSE.
- A Tableau Public dashboard, *Retail Demand Forecasting & Inventory Planning*,
  with six worksheets — average demand, variability, forecast evidence,
  reorder-point scenarios, safety-stock scenarios and a KPI summary row — and six
  filter cards across store, lead time and service level.
- A ggplot2 figure set and R Markdown report from the R track.

Published dashboard:
<https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning>

## Application

The Streamlit application presents the validated results as a decision-support
interface with four sections: Demand Overview, Inventory Scenario, Selected
Model (Phase 12) and Forecast Model Comparison (Phase 11). It reads seven
compact CSV artifacts and never retrains a model.

Artifacts resolve, in order, from:

1. the `APP_ANALYSIS_DIR` environment variable;
2. `data/analysis/`, when that directory holds every required artifact;
3. `deploy/artifacts/`, the committed bundle that lets a repository build start
   the application.

Per-store model evidence — selected model, configuration, cross-validation fold
count and validation metrics — is derived from the Phase 12 tables rather than
hardcoded, and a store whose selection rests on a single fold is labelled as
validated with an explicit caveat.

Live deployment: <https://demand-forecasting-retail-internship.streamlit.app/>

## Limitations

- The dataset contains no holiday field, so holiday analysis is not applicable.
- The dataset contains no lead times, costs, current stock or purchase orders, so
  inventory outputs are conditional planning scenarios rather than operational
  policy.
- The reserved test period is not evaluated: the delivered models are validated on
  the validation period only.
- Store 4 first appears on 2023-12-13, so its model rests on 60 training days and
  a single cross-validation fold; the 2023-12 level shift is a coverage change
  rather than a demand shift.
- Lag and rolling features operate over previous observed records rather than
  calendar days, because 95.0% of item-store series contain intermediate date
  gaps.
- RMSE is scale-bound and rewards the smallest store; cross-store comparisons use
  MAPE.
- Price and promotion fields are excluded from the feature matrix until their
  temporal semantics are validated.
- The committed Tableau workbook keeps an absolute local data-source path; the
  published view is insulated from it by its extract.
- Generated data is excluded from Git, except the `deploy/artifacts/` bundle that
  the application needs.

## Reproducibility

Prerequisites: Python 3.12 with `requirements.txt` installed, the raw dataset in
`data/raw/`, and R 4.6.1 with the packages listed in
`docs/phase-14/r-analysis-results.md` for the R track.

Each pipeline stage is re-runnable from its own script and is deterministic:

```bash
python scripts/inspect_raw_data.py
python scripts/create_spreadsheet_analysis.py
python scripts/create_sqlite_database.py
python scripts/run_sql_analysis.py
python scripts/clean_retail_data.py
python scripts/integrate_retail_data.py
python scripts/exploratory_data_analysis.py
python scripts/statistical_analytical_analysis.py
python scripts/prepare_time_series.py
python scripts/feature_engineering.py
python scripts/forecasting_models.py
python scripts/evaluate_and_tune_models.py
python scripts/forecasting_inventory_insights.py
```

The R track, the visualization workflow and the application:

```bash
Rscript r/r_analysis.R
Rscript -e "rmarkdown::render('r/r_analysis_report.Rmd', output_dir = file.path(getwd(), 'data', 'analysis', 'r'))"
python scripts/create_visualizations.py
python scripts/sync_tableau_workbook_schema.py --check
python -m streamlit run app/streamlit_app.py
```

Run the full test suite with:

```bash
python -m pytest -q
```

Command-by-command reproduction, including expected outputs and timings, is in
[`docs/reproducibility-runbook.md`](docs/reproducibility-runbook.md).

## Project Status

**Complete.** All 18 phases are finished, the automated suite passes 532 tests
across 18 modules, the run-gating quality reports pass 272 of 272 checks, the
Streamlit application is deployed and the Tableau dashboard is published.

## Documentation

The full reading order is in [`docs/README.md`](docs/README.md). The short
version:

- [`docs/project-status.md`](docs/project-status.md) — the finished project on one
  page: phases, dataset, models, tests, deployment and limitations.
- [`docs/phase-17/final-case-study.md`](docs/phase-17/final-case-study.md) — the
  whole project as a case study, in course order.
- [`docs/reproducibility-runbook.md`](docs/reproducibility-runbook.md) —
  command-by-command reproduction.
- [`docs/course-coverage.md`](docs/course-coverage.md) — which course topics the
  project demonstrates, and where.
- [`docs/phase-17/final-presentation.md`](docs/phase-17/final-presentation.md) —
  presentation script and prepared Q&A.
- [`docs/phase-17/portfolio-packaging.md`](docs/phase-17/portfolio-packaging.md) —
  internship submission guide.

## Disclaimer

Forecasts are analytical estimates. They support inventory decision-making
rather than acting as guaranteed future demand, and the inventory figures in this
repository are scenario outputs under stated assumptions.
