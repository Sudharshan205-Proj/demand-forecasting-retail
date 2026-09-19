# Link Audit

External links extracted from all documentation (grep over `docs/`, `README.md`, `deploy/README.md`, `tableau/*.md`); every unique URL HTTP-checked with `curl -sL -o /dev/null -w "%{http_code}"` on 2026-09-19 (raw evidence: `execution/link-checks.txt`).

| Link | Location | Status | Purpose | Action |
|---|---|---|---|---|
| https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning | README.md; docs/phase-15/visualization-results.md; tableau-dashboard-guide.md; docs/phase-0/environment.md; docs/phase-17/{portfolio-packaging,final-presentation,final-case-study}.md | 200 OK | Published Phase 15 Tableau Public dashboard | Keep. Documented caveat retained: published extract dates to 8 Sep 2026; refresh requires Tableau Desktop. |
| https://public.tableau.com/app/profile/sudharshan.moodley/viz/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning | docs/phase-15/visualization-results.md; tableau-dashboard-guide.md (canonical form) | 200 OK | Canonical author-profile URL of the same dashboard | Keep. |
| https://www.kaggle.com/datasets/svizor/retail-sales-forecasting-data | docs/phase-2/{data-acquisition,dataset-inventory,data-dictionary,data-source-assessment}.md | 200 OK | Raw dataset source and provenance | Keep. License CC BY-NC-SA 4.0 recorded in Phase 2 docs. |
| https://www.kaggle.com/api/v1/datasets/download/svizor/retail-sales-forecasting-data | docs/phase-2/data-acquisition.md | 200 OK (endpoint resolves) | Documented programmatic download command for dataset acquisition | Keep. Requires Kaggle credentials to actually download; documented as such. |

No dead links, no undocumented external dependencies. All four documented external links are valid and purposeful.
