# Phase 15 — Course Content Coverage

Every row below cites a file, a test or the workbook itself. Rows that cannot be
evidenced are marked as such rather than claimed.

## Visualization

| Concept | Project evidence | Status |
|---|---|---|
| Data visualization | 4 matplotlib figures + published Tableau dashboard | VERIFIED |
| Visual analysis | Published Tableau dashboard (5 chart worksheets plus the `KPI Summary` row) and 4 static figures | VERIFIED |
| Charts | matplotlib bar/line figures and Tableau marks (3 Bar, 2 Line, 1 Text) | VERIFIED |
| Bar charts | Store demand, store variability, forecast evidence | VERIFIED |
| Line charts | Reorder-point scenarios by lead time | VERIFIED |
| Distribution visualization | Phase 7 `scripts/exploratory_data_analysis.py` histogram; Phase 15 adds none | VERIFIED ELSEWHERE — not a Phase 15 output |
| Correlation visualization | Phase 7/8 correlation table and heat map; Phase 15 adds none | VERIFIED ELSEWHERE — not a Phase 15 output |
| Static visualization | 4 PNG figures with direct value labels | VERIFIED |
| Dynamic visualization | Published Tableau Public dashboard | VERIFIED |
| Dashboards | `tableau/Retail_Demand_Forecasting.twb`, 1 dashboard / 41 zones | VERIFIED |
| Filters | 6 filter cards (store, lead time, service level); 11 `<filter>` elements as written by Tableau | VERIFIED |
| Labels | Direct labels on all 4 figures; 6 Tableau mark-label settings | VERIFIED |
| Annotations | Scenario axis carries the assumption caveat; the workbook contains no `<annotation>` elements | PARTIAL — caveat text only, no in-chart annotation |
| Accessibility | Colour-independent distinctions and 7 tooltips present; human usability and accessibility review complete | VERIFIED |
| Direct labeling | Value labels on all four static figures | VERIFIED |
| Colour selection | Distinct non-colour-only encodings; default Tableau palette | VERIFIED |
| Avoiding misleading scales | RMSE axis annotated as not cross-store comparable | VERIFIED |
| Avoiding clutter | Single-series charts carry no redundant legend | VERIFIED |
| Audience awareness | `data-storytelling.md`; units stated on every axis | VERIFIED |

## Tableau

| Concept | Evidence | Status |
|---|---|---|
| Tableau | `tableau/Retail_Demand_Forecasting.twb`, authored with Tableau 2026.2.2 | VERIFIED |
| Interactive dashboards | Published dashboard; canonical URL resolves | VERIFIED |
| Filters | 6 filter cards in the workbook, across three families | VERIFIED |
| Dashboard storytelling | Dashboard *Retail Demand Forecasting & Inventory Planning* plus `tableau-dashboard-specification.md` | VERIFIED |
| Accessibility | Colour-independent encodings and tooltips; human usability review complete | VERIFIED |
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
  Phase 7 and Phase 8 artifacts, not by this phase. They are marked VERIFIED
  ELSEWHERE so the Phase 15 claim is not overstated.
- "Annotations" is deliberately not marked VERIFIED: the workbook contains no
  annotation objects, so it is recorded as PARTIAL with the specific gap named.
- The Tableau Public client version cannot be read from the command line; only the
  workbook's authoring build is recorded.
- Every count cited above — the 5 chart worksheets plus `KPI Summary`, the 1
  dashboard / 41 zones, the 6 filter cards, the 5 hidden fields and the
  3 Bar / 2 Line / 1 Text marks — is read from the committed workbook, which is
  also the published one.
- No row in this table is claimed on the basis of a plan, a specification or an
  intent.
