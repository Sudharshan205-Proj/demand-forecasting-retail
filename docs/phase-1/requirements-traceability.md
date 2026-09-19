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
| BR-003 | Holidays | Integrated dataset + analysis | 2–8 | ❌ |
| BR-004 | Forecasting | Time-series preparation (Phase 9) and forecasting pipeline (11–13) | 9–13 | 🟩 |
| BR-005 | Baseline | Baseline model | 11 | 🟩 |
| BR-006 | ARIMA | ARIMA implementation | 11 | 🟩 |
| BR-007 | Prophet/LSTM assessment | Model decision and implementation if justified | 11 | 🟩 |
| BR-008 | RMSE/MAPE | Evaluation report | 12 | 🟩 |
| BR-009 | Model comparison | Model comparison | 12 | 🟩 |
| BR-010 | Inventory insights | Business analysis | 13 | 🟩 |
| BR-011 | Visualization | Python/R/Tableau | 7–15 | 🟩 |
| BR-012 | Tableau | Tableau dashboard | 15 | 🟩 |
| BR-013 | Application | Deployed application | 16 | 🟨 |
| BR-014 | Reproducibility | Documentation/configuration | All | 🟩 |
| BR-015 | Documentation | Repository documentation | All | 🟩 |

## Course Methodology

| Course Stage | Project Evidence | Phase | Status |
|---|---|---|---|
| Ask | Business problem, stakeholders, questions | 1 | 🟩 |
| Prepare | Data acquisition and understanding | 2–3 | 🟩 |
| Process | Cleaning and integration | 5–6 | 🟩 |
| Analyze | Analysis and forecasting | 7–14 | 🟩 |
| Share | Tableau/storytelling/presentation | 15 | 🟩 |
| Act | Forecast-based recommendations | 13–16 | 🟩 |

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
| Quantitative analysis | Phase 7-8 descriptive and statistical analysis | 🟩 |
| Qualitative/contextual analysis | Business context | 🟨 |
| Data ethics | Scope/security/ethics documentation | 🟨 |
| Data-driven decision making | Forecasting and recommendations | 🟩 |
| Data storytelling | Phase 17 final case study and presentation | 🟩 |
| Portfolio case study | Phase 17 final case study and portfolio packaging | 🟩 |

## Per-Phase Re-Audit Notes

Phases 9–16 were each re-audited during the Phase 17 pass. Those eight records
were consolidated on 2026-09-19 into the
[Phase 17 Re-Audit Record](../phase-17/re-audit-record.md), whose Contents table
lists the entry for each phase.

## Phase 17 Final Audit Note

The final Phase 17 review closed the requirements that belong to the project as
a whole and corrected the rows that had drifted from the per-phase notes.

- **BR-003 (Holidays) moves from ⬜ to ❌ NOT APPLICABLE.** The requirement is
  conditional ("when reliable holiday data is available"). Phase 2 established
  that no holiday field exists in the dataset — the Phase 2 source assessment
  records an explicit holiday variable as "VERIFIED ABSENT". The condition was
  never satisfied, so the honest status is Not Applicable, not "not started".
- **BR-004 (Forecasting) moves from 🟨 to 🟩.** The requirement is to produce
  forecasts of future demand. Phases 9, 11, 12 and 13 produce and verify them:
  forecasts are generated on the validated store-day series, evaluated with RMSE
  and MAPE, tuned, and translated into inventory scenarios. The reserved
  test-period evaluation belongs to evaluation rigour (BR-008's framework), not
  to BR-004, and remains a separately recorded open item.
- **BR-013 (Application) stays 🟨.** The application is implemented, tested and
  verified running locally and is deployable from the repository, but the
  requirement names a *deployed* application and no hosted URL exists.
- **BR-014 (Reproducibility) moves from ⬜ to 🟩.** Every pipeline stage is
  re-runnable from documented, project-root-relative commands and is
  deterministic; artifacts reconcile on rows, quantity and, at the integration
  stage, bytes; dependencies and the runtime are pinned; and R, pandoc and
  package versions are recorded. The one open item — the two root reference
  documents remain untracked — is an owner decision and does not affect
  reproducibility of the project itself.
- **BR-015 (Documentation) moves from ⬜ to 🟩.** All sixteen preceding phases
  carry re-audit records, the cross-phase records now match the implementation,
  and the final audit, case study and presentation are produced.
- The `Share` stage moves from ⬜ to 🟩 and the `Act` stage from 🟨 to 🟩,
  matching the Phase 15 and Phase 16 notes whose rows had been left stale.
- Course-skill rows advance: quantitative analysis, data-driven decision making,
  data storytelling and portfolio case study are now 🟩. Data ethics and
  qualitative/contextual analysis remain 🟨 because their evidence is
  documented but not exhaustively verified.

The full audit is in `docs/phase-17/final-audit-report.md`.

## Evidence Rule

A requirement will only be marked VERIFIED when actual implementation or documented evidence exists.

A planned feature is not evidence of completion.