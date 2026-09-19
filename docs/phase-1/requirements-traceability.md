# Requirements Traceability

## Status Definitions

- ⬜ NOT STARTED
- 🟨 IN PROGRESS
- 🟩 VERIFIED
- ❌ NOT APPLICABLE

## Retail Requirements

| ID | Requirement | Planned Evidence | Phase | Status |
|---|---|---|---|---|
| BR-001 | Historical sales | Dataset + processing pipeline | 2–6 | 🟩 |
| BR-002 | Promotions | Integrated dataset + analysis | 2–8 | 🟩 |
| BR-003 | Holidays | Integrated dataset + analysis | 2–8 | ⬜ |
| BR-004 | Forecasting | Time-series preparation (Phase 9) and forecasting pipeline (11–13) | 9–13 | 🟨 |
| BR-005 | Baseline | Baseline model | 11 | 🟩 |
| BR-006 | ARIMA | ARIMA implementation | 11 | 🟩 |
| BR-007 | Prophet/LSTM assessment | Model decision and implementation if justified | 11 | 🟩 |
| BR-008 | RMSE/MAPE | Evaluation report | 12 | 🟩 |
| BR-009 | Model comparison | Model comparison | 12 | 🟩 |
| BR-010 | Inventory insights | Business analysis | 13 | 🟩 |
| BR-011 | Visualization | Python/R/Tableau | 7–15 | 🟩 |
| BR-012 | Tableau | Tableau dashboard | 15 | 🟩 |
| BR-013 | Application | Deployed application | 16 | 🟨 |
| BR-014 | Reproducibility | Documentation/configuration | All | ⬜ |
| BR-015 | Documentation | Repository documentation | All | ⬜ |

## Course Methodology

| Course Stage | Project Evidence | Phase | Status |
|---|---|---|---|
| Ask | Business problem, stakeholders, questions | 1 | 🟩 |
| Prepare | Data acquisition and understanding | 2–3 | 🟩 |
| Process | Cleaning and integration | 5–6 | 🟩 |
| Analyze | Analysis and forecasting | 7–14 | 🟩 |
| Share | Tableau/storytelling/presentation | 15 | ⬜ |
| Act | Forecast-based recommendations | 13–16 | 🟨 |

## Course Analytical Problem Types

| Problem Type | Application | Status |
|---|---|---|
| Making predictions | Phase 9 preparation, Phase 11 forecast models and Phase 12 evaluation and tuning verified | 🟩 |
| Categorizing | Product/demand categories where useful | ⬜ |
| Spotting something unusual | Phase 7 item-level outlier and concentration analysis | 🟨 |
| Identifying themes | Phase 7 temporal and product themes | 🟨 |
| Discovering connections | Phase 8 promotion and price/demand relationships | 🟨 |
| Finding patterns | Phase 8 trend and weekly seasonality | 🟨 |

## Course Skills

| Skill | Evidence | Status |
|---|---|---|
| SMART questions | Analytical questions | 🟩 |
| Stakeholder analysis | Stakeholder document | 🟩 |
| Hypothesis thinking | Hypothesis register | 🟩 |
| Business context | Business problem | 🟩 |
| Quantitative analysis | Phase 7-8 descriptive and statistical analysis | 🟨 |
| Qualitative/contextual analysis | Business context | 🟨 |
| Data ethics | Scope/security/ethics documentation | 🟨 |
| Data-driven decision making | Forecasting and recommendations | ⬜ |
| Data storytelling | Final case study | ⬜ |
| Portfolio case study | Final project | ⬜ |

## Phase 9 Re-Audit Note

The Phase 9 re-audit verified the prepared time-series dataset (7,431,026
rows, 2022-08-28 to 2024-09-26, train/validation/test boundaries 2024-02-10
and 2024-06-03). On that evidence BR-004 (Forecasting) moved from ⬜ to 🟨:
the temporal dataset is prepared and verified, while the forecasting models
themselves remain Phase 11–13 work. BR-005 through BR-010 and the `Act` stage
remain ⬜ until their phases are individually audited.

## Phase 10 Re-Audit Note

The Phase 10 re-audit verified the feature-engineering workflow against the
complete Phase 9 dataset: 7,431,026 rows and 16 features, reconciled with
Phase 9 on rows, keys, target values, split labels and total quantity, with
leakage-safe historical features verified. BR-004 (Forecasting) remains 🟨:
the feature matrix is prepared and verified, while the forecasting models
remain Phase 11–13 work. A cross-phase finding is recorded — the engineered
features are not currently used as predictors by the Phase 11–13 model scripts
— for those audits to address.

## Phase 11 Re-Audit Note

The Phase 11 re-audit verified the forecasting workflow against the complete
Phase 10 dataset: 7,431,026 rows aggregated to 2,571 store-days with total
quantity 41,949,529.910 reconciled against the source, three documented models
fitted per store on the training window ending 2024-02-10, and a 114-day
validation period (2024-02-11 to 2024-06-03) evaluated with RMSE and MAPE. The
test period from 2024-06-04 is verified unused, the naive and seasonal-naive
forecasts are verified against their definitions, and the reported metrics are
reproduced from the 1,368 stored predictions. The 24-check quality report
passes fully.

On that evidence BR-005 (Baseline) and BR-006 (ARIMA) move from ⬜ to 🟩, and
BR-007 (Prophet/LSTM assessment) moves to 🟩: the requirement is an assessment,
and the assessment is documented — Phase 11 records that neither Prophet nor
LSTM was implemented and why (LSTM belongs to a later deep-learning stage and
Prophet may be reconsidered if a specific experiment benefits). No Prophet or
LSTM implementation is claimed.

BR-004 (Forecasting) remains 🟨 because the forecasting pipeline continues in
Phases 12–13 (evaluation, tuning and inventory insights). The `Act` stage and
BR-008 through BR-016 remain ⬜ until their phases are individually audited.

## Phase 12 Re-Audit Note

The Phase 12 re-audit verified the evaluation and tuning workflow against the
complete Phase 10 dataset: nine candidate configurations per store
(naive, three seasonal-naive periods, four ARIMA orders and a feature-based
gradient-boosting candidate) evaluated over 90 expanding-window
cross-validation folds, with all four stores tuned and validated,
configurations selected on training-period cross-validation only, 2,976
stored forecasts and a 30-check quality report that all passed. Every RMSE
and MAPE value is recomputed from the stored forecasts.

On that evidence BR-008 (RMSE/MAPE) and BR-009 (Model comparison) move from
⬜ to 🟩, and the "Making predictions" analytical problem type moves to 🟩.

BR-004 (Forecasting) remains 🟨 because the pipeline continues into Phase 13
(inventory insights). The `Act` stage, BR-010 (Inventory insights) and
BR-011 through BR-016 remain ⬜ until their phases are individually audited.

The cross-phase finding carried from the Phase 10 and Phase 11 notes is
resolved: the engineered features now reach a model.

## Phase 13 Re-Audit Note

The Phase 13 re-audit verified the inventory-insights workflow against the
complete Phase 10 dataset: 1,656 densified training store-days (1,655
observed, one zero-filled) reconciled against the source matrix on rows and
quantity, demand level and variability statistics computed on the same
series Phases 11–12 fitted, forecast error recomputed from the 456 stored
Phase 12 validation forecasts and reconciled with Phase 12's recorded RMSE,
MAPE and segment analysis, two scenario families covering 36 scenarios
each, a 43-check quality report that all passed, and a findings report
derived from the loaded evidence.

On that evidence BR-010 (Inventory insights) moves from ⬜ to 🟩, and the
`Act` stage moves from ⬜ to 🟨: the phase produces scenario-based
recommendations with stated assumptions, while the application and
presentation stages that would deliver them belong to Phases 15–16.

BR-004 (Forecasting) remains 🟨. The forecasting pipeline itself is now
verified end to end through Phase 13, but the requirement's final element —
an evaluation on the reserved test period — still has no owning phase, and
BR-011 through BR-016 remain ⬜ until their own phases are audited.

A substantive finding was corrected rather than merely recorded: the
insights artifacts asserted that Store 4 had no tuned Phase 12 model, and
because that sentence was hardcoded it survived re-execution while the
phase's own data contradicted it. Findings are now derived from the
evidence, and the quality report blocks the stale claim from returning.

## Phase 14 Re-Audit Note

The Phase 14 re-audit verified the R analysis workflow against the current
Phase 13 evidence: the workflow was re-executed, 91 quality checks all
passed, all seven Phase 13 insight types were reconciled on store, metric
name and value, and RMSE, MAE and MAPE were recomputed from the 456 stored
Phase 12 validation forecasts with `yardstick` and reconciled with the
reported values (maximum relative difference 2.94e-13 and 5.56e-13).

On that evidence:

- The `Analyze` stage moves from 🟨 to 🟩: spreadsheet (Phase 3), SQL
  (Phase 4), Python (Phases 5–13), R (Phase 14), statistical (Phase 8) and
  forecasting (Phases 11–13) analysis are all backed by verified evidence.
- BR-011 (Visualization, Python/R/Tableau) moves from ⬜ to 🟨. Its Python
  and R components are now verified — the R workflow exports four figures and
  the knitted report renders two more — while the Tableau component belongs
  to Phase 15.
- BR-004 (Forecasting) remains 🟨: the reserved test-period evaluation still
  has no owning phase, and BR-012 through BR-016 remain ⬜ until their phases
  are audited.

## Phase 15 Re-Audit Note

The Phase 15 re-audit re-executed the visualization workflow against the
current Phase 13 evidence and verified the committed Tableau workbook and its
published view: 55 quality checks all passed, every charted value reconciled
with its source CSV, the workbook's 5 worksheets / 1 dashboard / 6 filters
were confirmed, its stale cached schema was reconciled with the current CSV
headers, and the Tableau Public URL was confirmed to resolve (HTTP 200).

On that evidence:

- **BR-011 (Visualization, Python/R/Tableau) moves from 🟨 to 🟩.** All three
  components are now verified: the Python workflow exports four figures with
  direct value labels and a digest manifest, the R workflow exports four more
  in Phase 14, and the Tableau component is a committed workbook with a
  published, reachable dashboard.
- The `Share` stage moves from ⬜ to 🟩: charts, static and dynamic
  visualization, the dashboard, filters, labels, direct labelling,
  visualization design, audience awareness and storytelling are all backed by
  verified evidence.
- BR-004 (Forecasting) remains 🟨: the reserved test-period evaluation still
  has no owning phase, and BR-012 through BR-016 remain ⬜ until their phases
  are audited.
- Two limitations are recorded rather than smoothed over: the published
  dashboard reflects the extract built when it was published on 8 September
  2026 and needs a Tableau refresh to show post-audit values, and Phase 15's
  course-coverage record marks "Annotations" and "Accessibility" as PARTIAL
  because no in-chart annotations exist and no human usability review was
  performed.

## Phase 16 Re-Audit Note

The Phase 16 re-audit re-executed the Streamlit application against the
current artifacts, corrected two user-visible falsehoods and removed the
deployment blocker: per-store model evidence is now derived from the Phase 12
tables instead of hardcoded store identifiers, the mislabelled "Selected Model
Configuration" section was split into a Phase 12 selection section and a
Phase 11 comparison section, and a seven-file, 14,977-byte artifact bundle is
committed under `deploy/artifacts/` because `data/analysis/` is excluded from
Git.

36 application tests pass (up from 5), including the artifact-resolution
order, bundle reconciliation by SHA-256 and a headless startup test that
asserts HTTP 200; the full suite passes (530 tests). A local launch rendered
the page title, four section headings, both scenario controls and four data
tables.

On that evidence:

- **BR-013 (Application, deployed application) moves from ⬜ to 🟨, not 🟩.**
  The application itself is implemented, tested, verified running locally and
  genuinely deployable from the repository. What is *not* verified is the
  deployed instance: Streamlit Community Cloud requires a one-time
  interactive authorisation tied to the project owner's account, so no public
  URL has been observed. The requirement names a *deployed* application, so
  it stays short of fully verified until that URL exists.
- **BR-011 (Visualization) moves from 🟨 to 🟩 and BR-012 (Tableau) from ⬜
  to 🟩.** The table rows above were left stale by the Phase 15 audit, whose
  note on this page already recorded both as verified. The rows now match the
  note.
- **BR-014 (Reproducibility) and BR-015 (Documentation) remain ⬜.** Neither
  names an owning phase; both are properties of the project as a whole and
  belong to the final Phase 17 review. Phase 16 contributes to BR-014 — the
  runtime is pinned by `requirements.txt`, `.python-version` and
  `.streamlit/config.toml`, and the application is reproducible from a fresh
  clone — but it does not close the requirement on its own.
- The `Act` stage moves from ⬜ to 🟩. Forecasts and inventory recommendations
  were produced in Phase 13 and are now delivered through a validated
  decision-support interface that states its scenario assumptions and
  evidence strength.
- One limitation is recorded rather than smoothed over: no human usability or
  accessibility review of the rendered interface has been performed. Layout,
  contrast and structure were observed during the smoke test; they were not
  evaluated.

## Evidence Rule

A requirement will only be marked VERIFIED when actual implementation or documented evidence exists.

A planned feature is not evidence of completion.