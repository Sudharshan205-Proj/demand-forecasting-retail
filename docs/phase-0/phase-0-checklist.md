# Phase 0 — Project Setup & Curriculum Mapping

## Purpose

Phase 0 establishes the repository contract, the development method and the
curriculum mapping that every later phase is measured against. It is a setup
phase, so its deliverable is the repository and environment skeleton rather
than analysis output.

## What the phase delivered

| Area | Delivered |
|---|---|
| Repository layout | The phase-owned directory layout: `app/`, `data/`, `deploy/`, `docs/`, `r/`, `reports/`, `scripts/`, `sql/`, `tableau/`, `tests/` |
| Data directories | `data/raw/`, `data/processed/` and `data/analysis/`, with tracked placeholders in `raw/` and `processed/` so the empty directories survive a clone |
| `.gitignore` | Excludes secrets and generated data while retaining the data-directory placeholders |
| Environment | `.python-version` (Python 3.12), `requirements.txt` with the initial dependency set, `pyproject.toml` configuring pytest to collect `tests/` |
| Project definition | [`project-requirements.md`](project-requirements.md), [`project-plan.md`](project-plan.md), [`architecture.md`](architecture.md), [`data-strategy.md`](data-strategy.md), [`reproducibility.md`](reproducibility.md), [`security.md`](security.md) |
| Environment record | [`environment.md`](environment.md) |
| Curriculum mapping | [`curriculum-mapping.md`](curriculum-mapping.md) — every course topic mapped to a project component, with not-applicable topics recorded explicitly |
| Test contract | `tests/test_phase0_project_setup.py` — 6 tests asserting the required files exist and are non-empty, the data placeholders exist, `.gitignore` excludes secrets and keeps the data structure, the Phase 0 dependencies remain declared, and pytest is configured |

## Methodology

The project follows Ask → Prepare → Process → Analyze → Share → Act, with each
phase owning its scripts, artifacts and documentation.

## Verification

```text
python -m pytest tests/test_phase0_project_setup.py -q
# 6 passed
```

## Related documents

- [`../project-status.md`](../project-status.md) — the project state
- [`../course-coverage.md`](../course-coverage.md) — the curriculum coverage index
