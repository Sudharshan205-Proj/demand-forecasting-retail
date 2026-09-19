# Phase 15 — Course Content Coverage

Every row below was re-checked during the Phase 17 audit against a file, a
test or the workbook itself. Rows that could not be evidenced are marked as
such rather than claimed.

## Visualization

| Concept | Project Evidence | Status |
|---|---|---|
| Data visualization | 4 matplotlib figures + published Tableau dashboard | VERIFIED |
| Visual analysis | Tableau dashboard (5 worksheets) and 4 static figures | VERIFIED |
| Charts | matplotlib bar/line figures and Tableau marks (3 Bar, 2 Line) | VERIFIED |
| Bar charts | Store demand, store variability, forecast evidence | VERIFIED |
| Line charts | Reorder-point scenarios by lead time | VERIFIED |
| Distribution visualization | Phase 7 `scripts/exploratory_data_analysis.py` histogram; Phase 15 adds none | VERIFIED ELSEWHERE — not a Phase 15 output |
| Correlation visualization | Phase 7/8 correlation table and heat map; Phase 15 adds none | VERIFIED ELSEWHERE — not a Phase 15 output |
| Static visualization | 4 PNG figures with direct value labels | VERIFIED |
| Dynamic visualization | Published Tableau Public dashboard | VERIFIED |
| Dashboards | `tableau/Retail_Demand_Forecasting.twb`, 1 dashboard / 19 zones | VERIFIED |
| Filters | 6 workbook filters (store, lead time, service level) | VERIFIED |
| Labels | Direct labels on all 4 figures; 6 Tableau mark-label settings | VERIFIED |
| Annotations | Scenario axis carries the assumption caveat; the workbook contains no `<annotation>` elements | PARTIAL — caveat text only, no in-chart annotation |
| Accessibility | Colour-independent distinctions and 7 tooltips present | PARTIAL — structural review only; no human usability review was performed |
| Direct labeling | Value labels on all four static figures | VERIFIED |
| Colour selection | Distinct non-colour-only encodings; default Tableau palette | VERIFIED |
| Avoiding misleading scales | RMSE axis annotated as not cross-store comparable | VERIFIED |
| Avoiding clutter | Single-series charts carry no redundant legend | VERIFIED |
| Audience awareness | `data-storytelling.md`; units stated on every axis | VERIFIED |

## Tableau

| Concept | Evidence | Status |
|---|---|---|
| Tableau | `tableau/Retail_Demand_Forecasting.twb`, authored with Tableau 2026.2.2 | VERIFIED |
| Interactive dashboards | Published dashboard, HTTP 200, canonical URL resolves | VERIFIED |
| Filters | 6 filters in the workbook | VERIFIED |
| Dashboard storytelling | Dashboard *Retail Demand Forecasting & Inventory Planning* plus `tableau-dashboard-specification.md` | VERIFIED |
| Accessibility | Colour-independent encodings and tooltips; no manual usability review | PARTIAL |
| Tableau Public client version | Not obtainable from the command line | NOT EVIDENCED |

## Data Storytelling

| Concept | Evidence | Status |
|---|---|---|
| Audience identification | `data-storytelling.md` §1 | VERIFIED |
| Context | `data-storytelling.md` §2 | VERIFIED |
| Problem | `data-storytelling.md` §3 | VERIFIED |
| Insight | `data-storytelling.md` §5 | VERIFIED |
| Evidence | Verified Phase 13 outputs, reconciled in 55 checks | VERIFIED |
| Recommendation | `data-storytelling.md` §6, conditional | VERIFIED |
| Narrative flow | `data-storytelling.md` §8; dashboard specification | VERIFIED |
| Visual hierarchy | `visualization-quality-framework.md` | VERIFIED |
| Data-driven conclusions | Phase 12 validation evidence, reconciled | VERIFIED |

## Notes

- "Distribution visualization" and "Correlation visualization" are satisfied by
  Phase 7 and Phase 8 artifacts, not by this phase. They are marked
  VERIFIED ELSEWHERE so the Phase 15 claim is not overstated.
- "Annotations" and "Accessibility" are deliberately not marked VERIFIED: the
  workbook contains no annotation objects, and no human usability or
  screen-reader review was performed. Both are recorded as PARTIAL with the
  specific gap named.
- The Tableau Public client version cannot be read from the command line; only
  the workbook's authoring build is recorded.
- No row in this table is claimed on the basis of a plan, a specification or an
  intent — each cites a file, a test or the workbook.
