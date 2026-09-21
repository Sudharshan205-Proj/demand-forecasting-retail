# Portfolio Packaging — Internship Submission

## What This Is

A one-page guide for presenting this project as an internship/portfolio
submission: what to show, where it lives, and how to reproduce it.

## One-Paragraph Summary

> **Demand Forecasting for Retail** is an end-to-end data project that forecasts
> store-level product demand and turns the forecasts into conditional
> inventory-planning scenarios. It follows the Ask → Prepare → Process →
> Analyze → Share → Act lifecycle across 18 phases, using spreadsheet, SQL,
> Python, R and Tableau, with a reproducible pipeline, 532 automated tests and a
> deployed Streamlit application. It states its limits openly: no holiday data,
> no cost or lead-time inputs, and a reserved test period the project does not
> evaluate. The application is live at
> <https://demand-forecasting-retail-internship.streamlit.app/>.

## What To Show

| Artifact | Path | Why |
|---|---|---|
| Documentation index | `docs/README.md` | Reading order for everything below |
| Status | `docs/project-status.md` | One-page state of the project |
| Case study | `docs/phase-17/final-case-study.md` | The full narrative in course order |
| Presentation | `docs/phase-17/final-presentation.md` | Talk script + Q&A |
| Reproduction | `docs/reproducibility-runbook.md` | Command-by-command rebuild |
| README | `README.md` | Project overview and reproduction commands |
| Phase docs | `docs/phase-0/` … `docs/phase-16/` | Per-phase method and evidence |
| Tableau dashboard | <https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning> | Interactive visualization |
| Application | <https://demand-forecasting-retail-internship.streamlit.app/> | Deployed decision-support interface (`app/streamlit_app.py`) |
| Figures | `reports/figures/`, `data/analysis/r/plots/` | Regenerated static evidence — excluded from Git, rebuilt by the phase scripts |

## Headline Results

- Tuned mean validation RMSE: **3,223.0630 → 3,079.4286**.
- Highest average daily demand: **Store 1 — 29,711.253352**.
- Highest relative variability: **Store 4 — CV 0.380098** (60 observations).
- Lowest relative validation error: **Store 2 — MAPE 8.141356 %**.
- Systematic under-forecast: mean **1,409.941 units/day** across stores.
- 14-day / 95 % scenario reorder points: **448,302 / 95,240 / 91,618 / 476,010**.

## How To Reproduce

From the repository root, with the virtual environment present:

```text
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

Full pipeline reproduction commands are documented in `README.md` and in
[`reproducibility-runbook.md`](../reproducibility-runbook.md). Generated data and
analytical artifacts are excluded from Git and rebuilt from the raw dataset.

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
| Testing & documentation | Phase 17 |

## Limitations To State If Asked

- Holidays are not applicable — the dataset has no holiday field.
- Generated figures and reports are not committed; the Phase 14/15 commands in
  [`reproducibility-runbook.md`](../reproducibility-runbook.md) rebuild them.
- Reserved test-period evaluation is deferred; the project reports
  validation-period accuracy.
- Store 4's model rests on 60 training days and a single cross-validation fold.
- RMSE is scale-bound; cross-store comparison uses MAPE.
- The Tableau workbook keeps an absolute local data-source path, insulated in the
  published view by its extract.

These are also listed in [`project-status.md`](../project-status.md) and
[`final-case-study.md`](final-case-study.md) §13.
