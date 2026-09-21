# Requirements Traceability

## Status definitions

- ⬜ Not started
- 🟨 In progress
- 🟩 Verified
- ❌ Not applicable

A requirement is verified only when implementation or documented evidence
exists; a planned feature is not evidence of completion.

## Retail requirements

| ID | Requirement | Evidence | Phase | Status |
|---|---|---|---|---|
| BR-001 | Historical sales | Dataset + processing pipeline | 2–6 | 🟩 |
| BR-002 | Promotions | Integrated dataset + analysis | 2–8 | 🟩 |
| BR-003 | Holidays | No holiday field in the dataset | 2–8 | ❌ |
| BR-004 | Forecasting | Time-series preparation (Phase 9) and forecasting pipeline (11–13) | 9–13 | 🟩 |
| BR-005 | Baseline | Baseline model | 11 | 🟩 |
| BR-006 | ARIMA | ARIMA implementation | 11 | 🟩 |
| BR-007 | Prophet/LSTM assessment | Model decision (assessed, not implemented) | 11 | 🟩 |
| BR-008 | RMSE/MAPE | Evaluation report | 12 | 🟩 |
| BR-009 | Model comparison | Model comparison | 12 | 🟩 |
| BR-010 | Inventory insights | Business analysis | 13 | 🟩 |
| BR-011 | Visualization | Python/R/Tableau | 7–15 | 🟩 |
| BR-012 | Tableau | Tableau dashboard | 15 | 🟩 |
| BR-013 | Application | Deployed application | 16 | 🟩 |
| BR-014 | Reproducibility | Documentation/configuration | All | 🟩 |
| BR-015 | Documentation | Repository documentation | All | 🟩 |

## Course methodology

| Course stage | Project evidence | Phase | Status |
|---|---|---|---|
| Ask | Business problem, stakeholders, questions | 1 | 🟩 |
| Prepare | Data acquisition and understanding | 2–3 | 🟩 |
| Process | Cleaning and integration | 5–6 | 🟩 |
| Analyze | Analysis and forecasting | 7–14 | 🟩 |
| Share | Tableau/storytelling/presentation | 15 | 🟩 |
| Act | Forecast-based recommendations | 13–16 | 🟩 |

## Course analytical problem types

| Problem type | Application | Status |
|---|---|---|
| Making predictions | Phase 9 preparation, Phase 11 forecast models and Phase 12 evaluation and tuning | 🟩 |
| Categorizing | Phase 7 category analysis (182 rows) | 🟩 |
| Spotting something unusual | Phase 7 item-level outlier and concentration analysis | 🟩 |
| Identifying themes | Phase 7 temporal and product themes | 🟩 |
| Discovering connections | Phase 8 promotion and price/demand relationships (holidays not applicable) | 🟩 |
| Finding patterns | Phase 8 trend and weekly seasonality | 🟩 |

The six problem types carry the same status as
[`../phase-0/curriculum-mapping.md`](../phase-0/curriculum-mapping.md), which is
the single source for these capability verdicts; this table mirrors it rather
than maintaining a second status.

## Course skills

| Skill | Evidence | Status |
|---|---|---|
| SMART questions | Analytical questions | 🟩 |
| Stakeholder analysis | Stakeholder document | 🟩 |
| Hypothesis thinking | Hypothesis register | 🟩 |
| Business context | Business problem | 🟩 |
| Quantitative analysis | Phase 7-8 descriptive and statistical analysis | 🟩 |
| Qualitative/contextual analysis | Business context | 🟨 |
| Data ethics | Scope/security/ethics documentation | 🟨 |
| Data-driven decision making | Forecasting and recommendations | 🟩 |
| Data storytelling | Phase 17 final case study and presentation | 🟩 |
| Portfolio case study | Phase 17 final case study and portfolio packaging | 🟩 |
