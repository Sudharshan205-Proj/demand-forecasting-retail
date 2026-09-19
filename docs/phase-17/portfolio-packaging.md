# Portfolio Packaging — Internship Submission

## What This Is

A one-page guide for presenting this project as an internship/portfolio
submission: what to show, where it lives, and how to reproduce it.

## One-Paragraph Summary

> **Retail Demand Forecasting & Inventory Planning** is an end-to-end data
> project that forecasts store-level product demand and turns the forecasts into
> conditional inventory-planning scenarios. It follows the Ask → Prepare →
> Process → Analyze → Share → Act lifecycle across 18 tracked phases, using
> spreadsheet, SQL, Python, R and Tableau, with a reproducible pipeline, 530
> automated tests and a deployed-ready Streamlit application. It is deliberately
> honest about its limits: no holiday data, no cost or lead-time inputs, a
> reserved test period still to be evaluated, and a hosted deployment pending a
> one-time owner authorisation.

## What To Show

| Artifact | Path | Why |
|---|---|---|
| Documentation index | `docs/README.md` | Reading order for everything below |
| Status | `docs/project-status.md` | One-page state of the project |
| Case study | `docs/phase-17/final-case-study.md` | The full narrative in course order |
| Presentation | `docs/phase-17/final-presentation.md` | Talk script + Q&A |
| Final audit | `docs/phase-17/final-audit-report.md` | Evidence every claim is checked |
| Independent verification | `docs/phase-17/independent-verification.md` | Whole-pipeline re-execution |
| Reproduction | `docs/reproducibility-runbook.md` | Command-by-command rebuild |
| README | `README.md` | Project status and reproduction commands |
| Phase docs | `docs/phase-0/` … `docs/phase-16/` | Per-phase method and evidence |
| Tableau dashboard | <https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning> | Interactive visualization |
| Application | `app/streamlit_app.py` | Decision-support interface |
| Figures | `reports/figures/`, `data/analysis/r/plots/` | Regenerated static evidence — excluded from Git, rebuilt by the phase scripts |

## Headline Results (verbatim from the phase records)

- Tuned mean validation RMSE: **3,223.0630 → 3,079.4286**.
- Highest average daily demand: **Store 1 — 29,711.253352**.
- Highest relative variability: **Store 4 — CV 0.380098** (60 observations).
- Lowest relative validation error: **Store 2 — MAPE 8.141356 %**.
- Systematic under-forecast: mean **1,409.941 units/day** across stores.
- 14-day / 95 % scenario reorder points: **448,302 / 95,240 / 91,618 / 476,010**.

## How To Reproduce

From the repository root, with the virtual environment present:

```text
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Full pipeline reproduction commands are documented in `README.md` and in each
phase's *Reproduction runbook*. Generated data and analytical artifacts are
excluded from Git and rebuilt from the raw dataset.

## Skills Demonstrated

| Skill | Where it is shown |
|---|---|
| Business framing | `docs/phase-1/*` |
| Data acquisition & quality | Phases 2, 4, 5 |
| Spreadsheets | Phase 3 |
| SQL / databases | Phase 4 |
| Python data engineering | Phases 5–10 |
| Statistical analysis | Phase 8 |
| Time-series forecasting (ARIMA) | Phases 9, 11 |
| Model evaluation & tuning | Phase 12 |
| Business interpretation | Phase 13 |
| R programming & R Markdown | Phase 14 |
| Visualization & Tableau | Phase 15 |
| Application development | Phase 16 |
| Testing, audit & documentation | Phase 17 |

## Known Gaps To State If Asked

- Hosted deployment pending owner authorisation.
- Generated figures and reports are not committed; run the Phase 14/15 commands
  in `docs/reproducibility-runbook.md` to rebuild them.
- Tableau Public extract dated 2026-09-08 (static figures regenerated 2026-09-19).
- No human accessibility review.
- Reserved test-period evaluation deferred.
- Holidays Not Applicable (no field in the data).
- Two root reference documents intentionally untracked.

These are recorded in `docs/phase-17/final-audit-report.md` §15 rather than
discovered under questioning.
