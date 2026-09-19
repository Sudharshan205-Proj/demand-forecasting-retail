# File Inventory

Machine-readable inventory: `execution/baseline-inventory.tsv` (308 files classified; raw data, generated data, deployment and sources additionally hashed in `execution/baseline-checksums.tsv`). Audit-only files under `docs/final-audit/` are excluded from the tables below except where noted.

## Repository top level

| File | Phase | Purpose | Source/Generated | Used | Validated | Status |
|---|---|---|---|---|---|---|
| `README.md` | 0/17 | Project overview, status, reproduction commands | Source (tracked) | Yes | Reads correctly against execution | VERIFIED |
| `requirements.txt` | 0 | Pinned environment | Source | Yes | 10/10 pins installed exactly | VERIFIED |
| `pyproject.toml` | 0 | Build metadata + pytest config | Source | Yes | `testpaths=["tests"]` honored | VERIFIED |
| `.python-version` | 0/16 | Python 3.12 pin | Source | Yes | venv is 3.12.10 | VERIFIED |
| `.gitignore` | 0 | Data/secret/cache exclusions | Source | Yes | Matches actual untracked set | VERIFIED |
| `AI_Phase_Based_Project_Development_Instructions(1).md` | ref | Owner reference document | Source (untracked by decision) | Reference only | Not required to run | ACCEPTED untracked |
| `Internship Course Content Authority — Eight-Video Curriculum Guide.md` | ref | Curriculum authority | Source (untracked by decision) | Reference only | Not required to run | ACCEPTED untracked |

## Directories

| Directory | Phase(s) | Purpose | Source/Generated | Key contents | Status |
|---|---|---|---|---|---|
| `app/` | 16 | Streamlit app (5 modules) | Source | `streamlit_app.py`, `data_loader.py`, `config.py`, `formatting.py`, `logging_config.py` | VERIFIED |
| `deploy/` | 16 | Deployment bundle | Generated but **committed intentionally** | `README.md`, `artifacts/*.csv` (7 files) | VERIFIED (byte-identical; reconciles by SHA-256) |
| `data/raw/` | 2 | Immutable raw inputs | Raw data | 8 CSVs (~824 MB) | VERIFIED — 9/9 checksums unchanged |
| `data/processed/` | 5,6,9,10 | Pipeline datasets | Generated | `sales_clean`, `integrated_retail_data`, `time_series_daily`, `feature_engineered_daily`, 2 reports | VERIFIED — 8/8 byte-identical |
| `data/analysis/` | 3,4,7–15 | Analysis outputs | Generated | ~94 files: EDA, statistical, forecasting, evaluation, inventory, R, visualizations, DB, xlsx, sql_results | VERIFIED — 90/94 byte-identical, 4 timestamp-only |
| `data/{interim,external,sql}/` | — | Reserved with `.gitkeep` only | Placeholder | `.gitkeep` | VERIFIED (no orphan data) |
| `docs/phase-0…17/` | 0–17 | Phase documentation (124 files) | Source | phase plans/results/checklists | VERIFIED (evidence-consistent; 2 stale counts) |
| `r/` | 14 | R workflow + report | Source | `r_analysis.R`, `r_analysis_report.Rmd` | VERIFIED — 91/91 checks |
| `reports/figures/` | 7/8 | Generated figures | Generated | 9 PNGs | VERIFIED |
| `scripts/` | 2–15 | Pipeline scripts (15) | Source | see command-log | VERIFIED — all compile, all run |
| `sql/` | 4 | Schema + analysis queries | Source | `schema.sql`, `retail_analysis.sql` | VERIFIED — 18 queries execute |
| `tableau/` | 15 | Workbook + docs | Source | `Retail_Demand_Forecasting.twb`, 2 docs | VERIFIED — schema matches CSV headers |
| `tests/` | 0–17 | pytest suite (18 modules) | Source | 530 tests | VERIFIED — 530/530 pass |

## Missing / unexpected / obsolete / duplicate / temporary / unused

- **Missing expected files**: none. Every artifact named by the documentation and every script named by the README exists and executed.
- **Unexpected files**: only the audit's own additions under `docs/final-audit/` (not collected by pytest; not on any import path) and `.freebuff/` (client scratch). No stray project file.
- **Obsolete files**: none found. The project's self-audit already removed the stale `integration_quality_report.json`, and this audit confirmed no artifact predates its inputs (R HTML was regenerated and now post-dates its `.Rmd`).
- **Duplicate files**: none. `deploy/artifacts/*.csv` duplicate `data/analysis/*.csv` *by design* (Git-committed bundle for hosts that build from the repository) and are reconciled by SHA-256 in `test_application.py`.
- **Temporary/cache files**: `.pytest_cache/`, `__pycache__/`, `.streamlit_run.log` — all Git-ignored; not project content.
- **Unused files**: none identified among tracked files. `scripts/sync_tableau_workbook_schema.py` is used by Phase 15 and tests.
