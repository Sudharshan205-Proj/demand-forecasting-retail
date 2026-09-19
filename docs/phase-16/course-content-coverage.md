# Phase 16 — Course Content Coverage

Every row below was re-checked during the Phase 17 audit against a file, a
test or an observed run. Rows that could not be evidenced are marked as such
rather than claimed.

## Application Development

| Concept | Project Evidence | Status |
|---|---|---|
| Application development | `app/streamlit_app.py` (451 lines) plus four support modules | VERIFIED |
| Streamlit | streamlit 1.63.0; headless launch returned HTTP 200 | VERIFIED |
| Interactive application | Store selector, lead-time selector, service-level selector | VERIFIED |
| Layout and structure | Four named sections: Demand Overview, Inventory Scenario, Selected Model (Phase 12), Forecast Model Comparison (Phase 11) | VERIFIED |
| Data applications | Reads seven validated CSV artifacts | VERIFIED |
| Deployment | Local launch verified; commit-backed deployment bundle at `deploy/artifacts/` | VERIFIED (local) |
| Public hosting | Streamlit Community Cloud configuration committed; authorisation pending | PARTIAL — no hosted URL observed |

## Data Interpretation

| Concept | Evidence | Status |
|---|---|---|
| Demand levels | `inventory_demand_summary.csv` rendered as KPIs | VERIFIED |
| Demand variability | `inventory_variability_summary.csv` rendered as KPIs | VERIFIED |
| Model evaluation | Phase 11 comparison table | VERIFIED |
| Selected model evidence | Phase 12 selection, fold count and validation metrics per store | VERIFIED |
| Inventory estimates | `inventory_scenarios.csv` reorder-point estimates | VERIFIED |
| Units and scale | Every displayed figure carries its unit; MAPE rendered as a percentage | VERIFIED |

## Filtering and Interaction

| Concept | Evidence | Status |
|---|---|---|
| Store selection | `store_ids()` over the demand summary; stores 1-4 | VERIFIED |
| Lead-time filtering | `filter_scenarios` plus the lead-time selector | VERIFIED |
| Service-level filtering | `filter_scenarios` plus the service-level selector | VERIFIED |
| Filter interaction | `test_filter_scenarios_selects_one_lead_time_and_level` | VERIFIED |
| Empty-result handling | Filtered frame is checked before rendering | VERIFIED |

## Data Communication

| Concept | Evidence | Status |
|---|---|---|
| KPI metrics | Store demand and variability metrics | VERIFIED |
| Tables | Four data tables rendered in the smoke test | VERIFIED |
| Section labelling | Sections named for the phase that produced their evidence | VERIFIED |
| Explanatory notes | `NON_RETRAINING_NOTE`, `SCENARIO_ASSUMPTION_NOTE` | VERIFIED |
| Scenario warnings | Assumption caveat rendered with the scenario section | VERIFIED |
| Numerical formatting | `format_number`, `format_percent`, `format_ratio_as_percent`, each unit-tested | VERIFIED |

## Decision Support

| Concept | Evidence | Status |
|---|---|---|
| Distinguishing evidence strength | Per-store fold count shown in the label | VERIFIED |
| Scenario-based estimates | Assumption caveat rendered alongside scenario values | VERIFIED |
| Single-fold caveat | `evidence_caveat()` states Store 4's weaker basis without denying the configuration | VERIFIED |
| No unsupported operational claims | No section presents scenario output as a business requirement | VERIFIED |
| Data-driven conclusions | Every value read from a committed artifact; nothing hardcoded per store | VERIFIED |

## Concepts Not Applicable

### Real-Time Model Training

Not applicable to the application interface: model training happens in the
analytical pipeline, and the interface never retrains or refits a model. This
is asserted by `NON_RETRAINING_NOTE` and by the fact that no modelling
dependency is imported by the application.

### Production Banking-Style Authentication

Not required for this internship-level analytical application. No user
accounts, no restricted data and no secrets are involved; a test asserts that
the application source contains no secret-like assignments.

## Verification

Coverage is marked complete only where the functionality has been tested or
observed in a recorded run. Two rows are deliberately left short of VERIFIED:

- **Public hosting** — the platform configuration is committed, but no hosted
  deployment has been executed or observed.
- **Human usability review** — no manual accessibility or usability
  assessment of the rendered interface has been performed; layout and
  contrast have been observed, not evaluated.

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
