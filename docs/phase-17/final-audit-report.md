# Phase 17 — Final Project Audit Report

## Purpose

This is the consolidated, project-level audit required before the project can be
declared complete. Phases 0–16 were each re-audited individually during Phase 17;
this report reviews the project as a whole against the final-audit checklist:
project structure, source code, tests, data pipeline, models, evaluation,
configuration, dependencies, Git, documentation, README, deployment, security,
reproducibility, and course-content coverage.

Every statement below is tied to a named test, a generated artifact, a recorded
command or a documented inspection. Statuses use the project's own vocabulary:

- **VERIFIED** — backed by named evidence that was inspected during this review.
- **PARTIAL** — implemented and verified in part; the residual gap is named.
- **NOT VERIFIED** — no evidence exists; recorded rather than claimed.
- **NOT APPLICABLE** — the requirement does not apply, with a stated reason.

## 1. Project structure — VERIFIED

The repository is a single, coherent Python project with an R analysis track and
a committed Tableau workbook.

| Area | Path | Status |
|---|---|---|
| Application | `app/` | VERIFIED |
| Deployment bundle | `deploy/artifacts/` (7 files, 14,977 bytes) | VERIFIED |
| Data staging | `data/{raw,interim,processed,external,analysis}/` | VERIFIED (raw/generated excluded from Git; placeholders tracked) |
| Documentation | `docs/phase-0/` … `docs/phase-16/` | VERIFIED |
| R analysis | `r/` | VERIFIED |
| Reports & figures | `reports/figures/` | VERIFIED |
| Python scripts | `scripts/` (15 scripts) | VERIFIED |
| SQL | `sql/` | VERIFIED |
| Tableau | `tableau/` | VERIFIED |
| Tests | `tests/` (18 test modules) | VERIFIED |

Tracked file count: 183 (verified with `git ls-files` on 2026-09-19; an earlier
figure of 178 was stale). `.gitignore` excludes virtual environments, caches,
`data/raw/*`, `data/processed/*`, `data/analysis/*`, `*.db`, `reports/*` and
secrets, while retaining the data-directory placeholders.

## 2. Source code — VERIFIED

- Every pipeline stage is a named, project-root-relative script under `scripts/`
  with no hardcoded absolute paths (asserted by tests).
- The application is import-safe: every Streamlit call lives inside `main()`.
- The R workflow is organised as 28 named functions with a `main()` entry point.

## 3. Tests — VERIFIED

| Suite | Command | Result |
|---|---|---|
| Full project suite | `.venv\Scripts\python.exe -m pytest -q` | 530 passed, 1 warning |

The suite covers setup contracts, each data pipeline stage, model validation,
application behaviour (including a headless HTTP 200 startup test), the R
workflow as a subprocess (including twelve deliberate-failure paths) and the
visualization workflow (including six subprocess failure paths).

During this review one test did not pass on first run:
`test_report_html_is_regenerated_after_the_report_source` failed because the
knitted R HTML report predated its committed R Markdown source. This was a real
generated-artifact staleness defect, not a false alarm. The report was re-knitted
from the audited workflow (43 chunks; quality gate passed) and the full suite is
now green. The finding is recorded in `docs/phase-14/r-analysis-results.md`'s
audit record rather than smoothed over.

## 4. Data pipeline — VERIFIED

The pipeline reconciles end to end:

| Stage | Verified fact |
|---|---|
| Raw sales | 7,432,685 rows; 2022-08-28 to 2024-09-26 |
| Directory | 4 stores; 219,810 catalog rows |
| Cleaning | 7,431,026 rows retained; 36,585 raw rows without a catalog match (948 distinct items) |
| Integration | 7,431,026 rows, 34 columns; byte-identical on re-execution |
| Totals | 41,949,529.910 total quantity; 5,659,219,309.90 total revenue; 28,180 unique items |
| Time-series split | train to 2024-02-10, validation to 2024-06-03, test to 2024-09-26; contiguous, non-overlapping |

## 5. Models — VERIFIED

- Phase 11 implements the three documented models per store — naive,
  seasonal-naive and ARIMA(1,1,1) — on the training window ending 2024-02-10 and
  evaluates them over the 114-day validation period.
- Phase 12 evaluates nine candidate configurations per store (including a
  deterministic `feature_gbm` candidate over the 16 store-day feature families)
  across 90 expanding-window cross-validation folds, tuning all four stores.
- Selection uses training-period cross-validation only; the reserved test period
  is never read.
- The tuned portfolio reduces mean validation RMSE from 3,223.0630 to
  3,079.4286. Stores 1 and 2 improve; store 3 is 0.32 % worse than the weekly
  benchmark (recorded, not hidden); store 4 reproduces its Phase 11 forecast
  exactly on a single affordable fold.

## 6. Evaluation — PARTIAL

RMSE and MAPE are recomputed from stored predictions in Phase 12, Phase 13 and
independently in R (Phase 14) with `yardstick`, and reconcile to floating-point
precision. Time-aware splits and leakage guards are asserted.

**Gap:** the reserved final test-period evaluation named in the Phase 12 plan
still has no owning phase. It is recorded as an open item, not claimed.

## 7. Configuration & dependencies — VERIFIED

- `requirements.txt` is pinned to the verified environment.
- `.python-version`, `.streamlit/config.toml` and `pyproject.toml` pin the
  runtime and the pytest configuration.
- R, pandoc and package versions are recorded in `data/analysis/r/r_environment.csv`.
- No dependency was added without a documented purpose; `tidymodels`/`yardstick`
  are genuinely exercised by the Phase 14 reconciliation.

## 8. Git — VERIFIED (state recorded)

- Working tree: only the two root reference documents and `.freebuff/` are
  untracked, both by deliberate decision (see §13).
- HEAD at audit time: `fa2eed8` — *Phase 16 Audit*.
- The Phase 17 audits themselves performed no Git operations except the Phase 16
  deployment commit/push carried out under its approved deployment plan.
- The owner has since performed the end-of-phase commit and push: verified
  2026-09-19, `HEAD` = `origin/main` = `e5a750f` (*Final Audit*), and the
  `phase-17-testing-documentation-final-audit` branch exists on `origin`.

## 9. Documentation — VERIFIED

All sixteen preceding phases carry a re-audit record. This review synchronized
the cross-phase records that had drifted:

- `docs/phase-0/curriculum-mapping.md` — the top mapping tables reconciled to
  verified phase evidence, and the `Holidays` row corrected to **Not
  Applicable** (no holiday field exists in the dataset).
- `docs/phase-1/requirements-traceability.md` — BR-003, BR-004, BR-013, BR-014,
  BR-015 and the `Share`/`Act` stages advanced to their evidenced status.
- `docs/phase-0/project-state.md` — HEAD/branch corrected, Phase 17 closed.
- `README.md` — status table updated and final artifacts linked.
- `docs/project-file-update-register.md` — Phase 17 files recorded.

## 10. README — VERIFIED

The README's status table, repository-structure section and reproducibility
commands were checked against the scripts. The cheap local command
`scripts/sync_tableau_workbook_schema.py --check` was re-run and reported
"Workbook schema already matches its sources."

## 11. Deployment — PARTIAL

- Local deployment is verified end to end: the Streamlit application starts
  headless and answers HTTP 200; a seven-file artifact bundle is committed so a
  repository build can start.
- **Gap:** the hosted public deployment has not been executed. Streamlit
  Community Cloud requires a one-time interactive authorisation tied to the
  project owner's account, so no public URL exists and none is claimed.
- The published Tableau Public dashboard resolves (HTTP 200) but reflects the
  extract built on 8 September 2026; refreshing it requires Tableau Desktop.

## 12. Security — VERIFIED

- No secrets are committed. A scan of tracked files returns only empty
  `password=''` Tableau connection attributes and the test file's own pattern
  list; `test_application_source_contains_no_secrets` asserts the application
  source contains none.
- `.gitignore` excludes `.env`, key material, credentials and generated
  databases.
- The application requires no secrets (asserted by test).

## 13. Reproducibility — PARTIAL (verified in process, one interactive step open)

- Every pipeline stage is re-runnable from the documented commands and is
  deterministic; generated artifacts reconcile on rows, quantity and (where
  asserted) bytes.
- Random seeds are fixed where stochastic behaviour exists; the feature-based
  candidate is deterministic.
- **Gap (owner decision):** the two root reference documents
  (`AI_Phase_Based_Project_Development_Instructions(1).md` and
  `Internship Course Content Authority — Eight-Video Curriculum Guide.md`)
  remain untracked by the project owner's decision. A fresh clone therefore does
  not include them; the project does not depend on them to run.

## 14. Course-content coverage — VERIFIED

The curriculum mapping now reflects only verified evidence. The eight course
videos are covered through the six-stage methodology, with these honest
exceptions:

| Row | Status | Reason |
|---|---|---|
| Holidays | **Not Applicable** | No holiday field exists in the dataset (Phase 2: "VERIFIED ABSENT"); the requirement was conditional on availability |
| RStudio | Not evidenced | The workflow runs through `Rscript`; no `.Rproj` is committed |
| Prophet / LSTM | Not Applicable (as implementation) | Assessed and deliberately not implemented; the deferral is documented |
| Temporary tables (SQL) | Not Applicable | The analysis uses CTEs rather than explicit temporary tables |
| Annotations / Accessibility | Partial | No in-chart annotation objects; no human usability or screen-reader review performed |
| Presentation / Q&A | Verified by this review | `docs/phase-17/final-presentation.md` |

## 15. Outstanding items (recorded, not hidden)

1. **Hosted Streamlit deployment** — needs a one-time owner authorisation; no
   public URL observed.
2. **Tableau Public refresh** — the published dashboard shows the 8 September
   2026 extract; refreshing requires Tableau Desktop.
3. **Human usability / accessibility review** of the rendered interface — not
   performed.
4. **Reserved final test-period evaluation** — no owning phase; remains deferred.
5. **RStudio** — installed but unevidenced.
6. **Tableau workbook** — uses an absolute local data-source path and the
   Reorder-Point Scenarios worksheet has a fixed axis whose lead-time minimum
   sits slightly below zero.
7. **Reference documents** — intentionally untracked.

## 16. Future improvements

- Add the reserved test-period evaluation once the project owner wants a
  genuinely unseen forecast assessment.
- Refresh and re-publish the Tableau dashboard against the post-audit extracts.
- Replace the Tableau workbook's absolute path with a relative/parameterised
  connection for portability.
- Complete a human usability and accessibility pass on the interface.
- Source-control the two reference documents if the owner later decides the
  internship evaluator should see them.

## Final Audit Verdict

The project is **complete and audit-safe as an internship/portfolio deliverable**.
Every phase 0–16 is individually re-audited; the cross-phase records now match
the implementation; the full test suite passes; no secrets are committed; and
every remaining gap is named above rather than presented as finished work.
