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
| BR-010 | Inventory insights | Business analysis | 13 | ⬜ |
| BR-011 | Visualization | Python/R/Tableau | 7–15 | ⬜ |
| BR-012 | Tableau | Tableau dashboard | 15 | ⬜ |
| BR-013 | Application | Deployed application | 16 | ⬜ |
| BR-014 | Reproducibility | Documentation/configuration | All | ⬜ |
| BR-015 | Documentation | Repository documentation | All | ⬜ |

## Course Methodology

| Course Stage | Project Evidence | Phase | Status |
|---|---|---|---|
| Ask | Business problem, stakeholders, questions | 1 | 🟩 |
| Prepare | Data acquisition and understanding | 2–3 | 🟩 |
| Process | Cleaning and integration | 5–6 | 🟩 |
| Analyze | Analysis and forecasting | 7–14 | 🟨 |
| Share | Tableau/storytelling/presentation | 15 | ⬜ |
| Act | Forecast-based recommendations | 13–16 | ⬜ |

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

## Evidence Rule

A requirement will only be marked VERIFIED when actual implementation or documented evidence exists.

A planned feature is not evidence of completion.