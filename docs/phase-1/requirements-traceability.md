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
| BR-005 | Baseline | Baseline model | 11 | ⬜ |
| BR-006 | ARIMA | ARIMA implementation | 11 | ⬜ |
| BR-007 | Prophet/LSTM assessment | Model decision and implementation if justified | 11 | ⬜ |
| BR-008 | RMSE/MAPE | Evaluation report | 12 | ⬜ |
| BR-009 | Model comparison | Model comparison | 12 | ⬜ |
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
| Making predictions | Phase 9 time-series preparation; forecasting models in Phases 11–12 | 🟨 |
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

## Evidence Rule

A requirement will only be marked VERIFIED when actual implementation or documented evidence exists.

A planned feature is not evidence of completion.