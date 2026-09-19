# Phase 0 Checklist

Phase 0 established the repository contract, the development method and the
curriculum audit that every later phase is measured against. Unlike Phases 1–16
it is a setup phase, so this checklist covers repository and environment setup
rather than analysis output.

## Repository Setup

- [x] Phase branch created (`phase-0-project-setup-and-curriculum-audit`)
- [x] Git working tree inspected before any file was created
- [x] Repository root established with the phase-owned directory layout
      (`app/`, `data/`, `deploy/`, `docs/`, `r/`, `reports/`, `scripts/`,
      `sql/`, `tableau/`, `tests/`)
- [x] `data/` subdirectories created (`raw/`, `interim/`, `processed/`,
      `external/`, `analysis/`)
- [x] Tracked placeholders retained so the empty data directories survive a
      clone (`data/raw/.gitkeep`, `data/processed/.gitkeep`,
      `data/interim/.gitkeep`, `data/external/.gitkeep`)
- [x] `.gitignore` created and verified to exclude secrets and generated data
      while keeping the directory placeholders

## Environment

- [x] Python version pinned (`.python-version`, 3.12.10)
- [x] Virtual environment documented
- [x] `requirements.txt` created with the Phase 0 dependency set
- [x] `pyproject.toml` created and configured so `pytest` collects `tests/`
- [x] Python version requirement declared (`>=3.11`)
- [x] Environment and version details recorded in `docs/phase-0/environment.md`

## Project Definition

- [x] Project requirements documented (`docs/phase-0/project-requirements.md`)
- [x] Project plan documented (`docs/phase-0/project-plan.md`)
- [x] System architecture documented (`docs/phase-0/architecture.md`)
- [x] Data strategy documented (`docs/phase-0/data-strategy.md`)
- [x] Reproducibility expectations documented
      (`docs/phase-0/reproducibility.md`)
- [x] Security expectations documented (`docs/phase-0/security.md`)
- [x] Development method fixed as Ask → Prepare → Process → Analyze → Share →
      Act, developed on phase-specific branches with phase-level commits

## Curriculum Audit

- [x] Curriculum authority reviewed
- [x] Every course topic mapped to a planned project component
- [x] Mapping recorded in `docs/phase-0/curriculum-mapping.md`
- [x] Status vocabulary defined (evidenced / documented / not evidenced / not
      applicable)
- [x] Topics with no applicable project component recorded as not applicable
      rather than silently omitted
- [x] Rule adopted that coverage is claimed only where project evidence exists

## Testing

- [x] `tests/test_phase0_project_setup.py` created — 6 tests
- [x] Required Phase 0 files asserted to exist
- [x] Required Phase 0 files asserted to be non-empty
- [x] Data directory placeholders asserted to exist
- [x] `.gitignore` asserted to exclude secrets and keep the data structure
- [x] Phase 0 dependencies asserted to remain declared in `requirements.txt`
- [x] `pyproject.toml` asserted to configure pytest
- [x] Full suite passing at phase close

```text
.venv\Scripts\python.exe -m pytest tests/test_phase0_project_setup.py -q
# 6 passed
```

## Documentation

- [x] README created with the project goal, the forecasting requirement, the
      phase list and the status table
- [x] Phase 0 documents complete:
      `project-requirements.md`, `project-plan.md`, `curriculum-mapping.md`,
      `architecture.md`, `environment.md`, `data-strategy.md`,
      `reproducibility.md`, `security.md`, `phase-0-checklist.md`

## Git

- [x] Changes reviewed before committing
- [x] Only Phase 0 files staged — no generated data, caches or credentials
- [x] Phase 0 committed on its own branch
- [x] Branch pushed to `origin`
- [x] Repository state verified after the push

## Phase completion

**COMPLETE.** Every item above is backed by a committed file or a named test.

## Note on this file

This checklist was added on 2026-09-19, during the documentation cleanup, because
Phase 0 was the only phase without one. It records the Phase 0 contract as it
actually exists in the repository — verified against
`tests/test_phase0_project_setup.py`, the tracked file list and the phase
documents — rather than reconstructing the phase's working order.

See [`project-status.md`](../project-status.md) for the current project state.
