# Documentation Index

Project documentation for **Retail Demand Forecasting & Inventory Planning**. The
project runs across 18 phases; each phase owns a folder (`docs/phase-0/` …
`docs/phase-17/`) holding its method, results, quality framework and checklist.

## Start here

Reading order for someone seeing this project for the first time:

| # | Document | What it gives you |
|---|---|---|
| 1 | [`../README.md`](../README.md) | Goal, status table, reproduction commands, known limitations |
| 2 | [`project-status.md`](project-status.md) | Where the project stands: phases, dataset, models, tests, open items |
| 3 | [`phase-17/final-case-study.md`](phase-17/final-case-study.md) | The whole project as a case study, in course order |
| 4 | [`phase-17/portfolio-packaging.md`](phase-17/portfolio-packaging.md) | What to show, headline results, how to reproduce |
| 5 | [`phase-17/final-presentation.md`](phase-17/final-presentation.md) | Presentation script and prepared Q&A |
| 6 | [`phase-17/final-audit-report.md`](phase-17/final-audit-report.md) | The project audited against the final-audit checklist |
| 7 | [`phase-17/independent-verification.md`](phase-17/independent-verification.md) | Independent re-execution of the entire pipeline |
| 8 | [`course-coverage.md`](course-coverage.md) | Which course topics are demonstrated, and where |
| 9 | [`reproducibility-runbook.md`](reproducibility-runbook.md) | Command-by-command reproduction, Phase 0 → 17 |
| 10 | [`phase-17/re-audit-record.md`](phase-17/re-audit-record.md) | The consolidated per-phase re-audit records |

## Phase folders

Each phase folder follows the same pattern:

| Document | Purpose |
|---|---|
| `<topic>-methodology.md` | How the phase was actually carried out |
| `<topic>-results.md` | What it produced, with figures verified against the generated artifacts |
| `<topic>-quality-framework.md` | The machine-checked gates that must pass before the phase writes output |
| `course-content-coverage.md` | Which course topics this phase demonstrates |
| `phase-N-checklist.md` | The phase's completion checklist |

The pattern is not uniform. Phases 3–16 follow it closely, with names that vary
by topic (Phase 16, for example, pairs `application-development-plan.md` and
`deployment-validation.md` with `application-results.md`). Four phases differ
structurally:

- **Phase 0** is a setup and curriculum-audit phase and carries
  `project-requirements.md`, `project-plan.md`, `architecture.md`,
  `curriculum-mapping.md`, `environment.md`, `data-strategy.md`,
  `reproducibility.md`, `security.md` and `phase-0-checklist.md`.
- **Phase 1** is entirely business framing: `business-problem.md`,
  `analytical-questions.md`, `stakeholder-analysis.md`, `kpi-definitions.md`,
  `business-requirements.md`, `requirements-traceability.md`, `decision-log.md`,
  `hypothesis-register.md`, `scope-and-assumptions.md`, `phase-1-checklist.md`.
- **Phase 2** documents acquisition and understanding: `data-acquisition.md`,
  `dataset-inventory.md`, `data-source-assessment.md`, `data-dictionary.md`,
  `initial-data-assessment.md`, `data-ethics-and-privacy.md`,
  `phase-2-checklist.md`.
- **Phase 17** holds the project-level deliverables: the case study,
  presentation, portfolio guide, audit report, independent verification,
  findings register and the consolidated re-audit record.

Phases 0, 1, 2 and 17 have no separate `course-content-coverage.md`; their course
evidence is carried in `phase-0/curriculum-mapping.md` and `course-coverage.md`.

## What this repository is, and is not

**Is:** an internship-level retail demand forecasting case study — a data-analysis
project that forecasts store-level demand and translates the forecasts into
conditional inventory-planning scenarios, using spreadsheets, SQL, Python, R and
Tableau, with a reproducible pipeline, an automated test suite and a locally
verified Streamlit application.

**Is not:** a production platform, a deep-learning research project, or a generic
machine-learning benchmark. Scope decisions and everything deliberately left out
are recorded in `phase-17/final-audit-report.md` §15 and
`phase-0/curriculum-mapping.md`.

## Conventions

- **Status vocabulary** — `VERIFIED`, `PARTIAL`, `NOT VERIFIED`,
  `NOT APPLICABLE`, `COMPLETE`, `PENDING`. A claim is `VERIFIED` only when a
  named test, artifact, command or inspection backs it.
- **Figures** — quantitative statements name their source artifact. Figures that
  were true when written are labelled as at-the-time readings rather than
  silently replaced.
- **Audit records** — the per-phase re-audit records were consolidated on
  2026-09-19 into `phase-17/re-audit-record.md`. Each phase document keeps its
  heading and a one-line pointer. The records are historical: they say what the
  Phase 17 pass found and changed in that phase.
- **Generated data is not committed** — `data/raw/`, `data/processed/`,
  `data/analysis/` and `reports/` are excluded from Git; the runbook rebuilds
  them. The one exception is the committed `deploy/artifacts/` bundle that lets
  the application start from a fresh clone.
