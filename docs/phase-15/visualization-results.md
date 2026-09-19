# Phase 15 — Visualization & Tableau Results

## Status

VERIFIED — the static workflow was re-executed against the current Phase 13
outputs on 19 September 2026, its 55 checks pass, the Tableau workbook's
cached schema has been reconciled with its current CSV sources, and the
published dashboard was confirmed to resolve.

Every figure, hash and value below was produced by the workflow or read from
the committed workbook. Nothing in this document was entered by hand.

## Environment

| Tool | Version | Evidence |
|---|---|---|
| Python | 3.12 (project virtual environment) | `.venv` |
| matplotlib | 3.11.1 | `pip show matplotlib` |
| pandas | 3.0.5 | `pip show pandas` |
| numpy | 2.5.2 | `pip show numpy` |
| scipy | 1.18.1 | `pip show scipy` |
| Tableau | 2026.2.2 (build 20262.26.0819.2015) | `.twb` `source-build` attribute |

Tableau Public is a hosted service; its client version is not recorded, which
is why `docs/phase-0/environment.md` still marks the *client version* as not
recorded even though the published workbook is now evidenced.

## Workflow Execution

| Item | Value |
|---|---|
| Workflow | `scripts/create_visualizations.py` |
| Inputs consumed | 5 analytical files |
| Validation checks | 55 — 55 PASS, 0 FAIL |
| Quality report | `data/analysis/visualization_quality_report.csv` |
| Manifest | `data/analysis/visualization_manifest.csv` |
| Figures written | 4 |
| Exit code | 0 |

Inputs (all generated 19 September 2026 01:27 by Phase 13):

- `inventory_demand_summary.csv` — 4 rows
- `inventory_variability_summary.csv` — 4 rows
- `inventory_scenarios.csv` — 36 rows
- `forecast_inventory_insights.csv` — 13 rows
- `tuned_validation_results.csv` — 4 rows

The workflow gates on its checks: if any check fails it writes the failing
report, prints `FAILED` to stderr, returns exit code 1 and draws no figure.
The figures and both reports are written only after every input check passes,
and the reports are rewritten afterwards to include the four figure checks.

## Static Outputs

| Figure | Bytes | SHA-256 | Source | Source rows |
|---|---|---|---|---|
| `store_average_daily_demand.png` | 32,067 | `33d5a9d4…65f588a7` | demand | 4 |
| `store_demand_variability.png` | 36,079 | `58a0b7d4…fc5c5416` | variability | 4 |
| `reorder_point_by_lead_time.png` | 103,628 | `64d17cb4…2b3d20b7` | scenarios | 36 |
| `lowest_validation_rmse.png` | 43,048 | `b868be45…0ab7ba69` | insights | 13 |

The full digests are recorded in `visualization_manifest.csv`, which the test
suite verifies against the files on disk. All four figures post-date the
inputs they describe: the inputs were written at 01:27 on 19 September 2026
and the figures were regenerated afterwards. The digests above were reproduced
identically across repeated runs.

Each figure carries direct value labels and explicit units:

| Figure | Title | Axis label |
|---|---|---|
| Average demand | Average Daily Physical Demand by Store | Mean Daily Demand (demand units, training period) |
| Variability | Relative Demand Variability by Store | Coefficient of Variation (std / mean, training period) |
| Scenarios | Scenario Reorder Points at an Assumed 95% Service Level | Assumed Lead Time (days) — a planning assumption, not a requirement |
| Forecast evidence | Lowest Validation RMSE Among Validated Models, by Store | Validation RMSE (demand units — not comparable across stores) |

## Verified Values

Store-level demand, as charted and as reconciled against
`inventory_demand_summary.csv`:

| Store | Mean daily demand | Coefficient of variation | Training days |
|---|---|---|---|
| 1 | 29,711.253352 | 0.176886 | 532 |
| 2 | 6,355.192286 | 0.160240 | 532 |
| 3 | 5,832.890242 | 0.277371 | 532 |
| 4 | 29,132.823483 | 0.380098 | 60 |

Charted insight values, each reconciled to its source:

| Insight | Store | Value | Reconciled against |
|---|---|---|---|
| Highest average demand | 1 | 29,711.253352 | demand summary (difference 0) |
| Highest relative variability | 4 | 0.380098 | demand summary (difference 0) |
| Lowest validation RMSE | 2 | 711.206677 | `tuned_validation_results.csv` (difference 0) |
| Lowest relative validation error | 2 | 8.141356 % | `tuned_validation_results.csv` (difference 0) |

Scenario reorder points at the charted 14-day / 95 % assumption, reconciled
row-by-row against `inventory_scenarios.csv` and against the Phase 13
insights: Store 1 = 448,302.491763; Store 2 = 95,240.141608;
Store 3 = 91,617.640793; Store 4 = 476,010.139796.

The 55 checks cover, in addition to presence and type checks: the coefficient
of variation equals std / mean; the variance equals the squared standard
deviation; percentile ordering; z values equal the standard-normal quantile
of the service level; expected lead-time demand, safety stock and reorder
point each reconcile with their formula; reorder points are monotonic in both
service level and lead time; every store covers the full 3 × 3 scenario grid;
scenario demand levels match the demand summary; every store set is identical
across inputs; and all five insight families reconcile to their sources.

## Tableau Workbook

| Property | Value |
|---|---|
| File | `tableau/Retail_Demand_Forecasting.twb` (171,074 bytes) |
| Authored with | Tableau 2026.2.2, `source-platform='win'`, `license-type='public'` |
| Repository id | `Retail_Demand_Forecasting` |
| Data sources | `inventory_scenarios.csv`, `inventory_variability_summary.csv`, `tuned_validation_results.csv` |
| Worksheets | 5 — Average Demand by Store; Relative Demand Variability; Reorder-Point Scenarios; Forecast Evidence; Safety Stock Scenarios |
| Dashboard | 1 — *Retail Demand Forecasting & Inventory Planning* |
| Filters | 6 quantitative/categorical filters |
| Field instances | 27 |

The workbook is well-formed XML and the test suite asserts its worksheets,
dashboard, data sources and repository id.

### Schema reconciliation

The workbook was authored on 8 September 2026. The Phase 13 audit later
regenerated the analytical CSVs and added `season_length` and `order`, which
shifted the position of every later column. The workbook's cached textscan
schema therefore no longer matched the files it points at — a mis-mapping
risk, because Tableau's textscan connector reads the cached field order.

`scripts/sync_tableau_workbook_schema.py` rebuilds every cached schema block
from the current CSV headers and writes the workbook back only when something
changed. Applied once, it produced 170 insertions and 52 deletions across the
three data sources and their extracts:

- each `<columns>` block now lists the current headers in order with
  contiguous ordinals;
- each column `<metadata-record>` carries the corrected ordinal, and
  `season_length` / `order` were added;
- **declared datatypes are preserved** — `validation_start` and
  `validation_end` remain `date` rather than being downgraded to text;
- newly added records are cloned from the block's own record of the same
  datatype, so the extract flavour (which carries `<family>` and
  `<approx-count>`) is reproduced exactly.

The reconciliation is idempotent: a second run reports no change. It is
covered by the test suite, including a drift case in which a new column is
added to a source copy.

## Tableau Public

| Property | Value |
|---|---|
| URL | `https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |
| Verification | HTTP 200 on 19 September 2026 |
| Canonical URL | `https://public.tableau.com/app/profile/sudharshan.moodley/viz/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |
| Workbook match | URL workbook id = `Retail_Demand_Forecasting` = `repository-location/@id`; URL view slug = `RetailDemandForecastingInventoryPlanning` = the dashboard name with non-alphanumerics removed |

The dashboard is publicly reachable and its URL names this workbook and this
dashboard. The publication itself predates the Phase 17 audit, so the URL is
recorded as verified evidence of publication — not as an audit action.

## Tests

`tests/test_create_visualizations.py` — 32 tests, all passing:

- the workflow driven end-to-end as a subprocess over synthetic CSV fixtures,
  run from a directory that is not the project root, asserting all four
  figures, both reports and the manifest;
- the manifest digest and byte size re-verified against the files on disk;
- a failing gate proven to withhold every figure and mark the report FAIL;
- 14 unit tests over `validate_inputs` and `validate_leakage_guard`, covering
  missing columns, empty inputs, negative demand, negative variability, a
  broken variance identity, negative reorder points, invalid service levels,
  mismatched store sets, duplicate store ids, missing insight types,
  unreconciled insight values and a test-period metric;
- 6 parametrized subprocess failure paths, each asserting a non-zero exit, a
  `FAILED` message and no figure written;
- 7 workbook and URL tests — well-formedness, worksheets and dashboard, full
  schema agreement with the current CSV headers, preserved date datatypes,
  idempotent reconciliation, drift detection, unknown-source rejection and the
  published URL match.

## Phase 17 Re-Audit Record

Defects found and corrected:

| # | Defect | Resolution |
|---|---|---|
| F1 | All four figures were dated 8 Sep while every input was regenerated 19 Sep — the phase had never run against its own inputs | Workflow re-executed; figures now post-date their inputs |
| F2 | `visualization-results.md` said NOT YET EXECUTED and all 49 checklist boxes were unticked, while commit `f1146d8` existed and four figures had been produced | This document rewritten; checklist corrected |
| F3 | The `.twb` cached textscan schema no longer matched the CSVs after `season_length` and `order` were added | Reconciled in place; drift now tested |
| F4 | The workbook's data sources use the machine-absolute path `C:/Users/User/demand-forecasting-retail/data/analysis` | Documented as a portability note (see Limitations) |
| F5 | `forecast_inventory_insights.csv` was read but never validated, and the forecast-evidence chart silently returned when its insight was absent, letting a run report success with three of four charts | Fourth input validated; a missing insight now raises and fails the run |
| F6 | No quality report, manifest or results record; `main()` always printed success | 55-check gating report, manifest with digests, and a non-zero exit on failure |
| F7 | The 10 tests exercised only `validate_inputs` and never ran the workflow | 32 tests, including end-to-end and 6 failure paths |
| F8 | The plan listed Phase 14 as an input while nothing consumed R output | Corrected in `visualization-and-tableau-plan.md` |
| F9 | 16 course-coverage rows still read TO BE VERIFIED | Resolved in `course-content-coverage.md` |
| F10 | README said COMPLETE while the register said "Not yet started" | Both corrected |
| F11 | No Tableau Public URL was recorded anywhere | Published URL recorded and verified |

## Assumptions and Limitations

- **The published dashboard reflects its publish-time extract.** The workbook
  embeds three extracts built on 8 September 2026 that point at transient
  `#TableauTemp_*.hyper` files. The schema has been reconciled, but the
  extract *data* still predates the Phase 13 and Phase 14 audits. Refreshing
  or re-publishing it requires Tableau Desktop and cannot be performed from
  the command line, so the published dashboard may display pre-audit values.
- **The workbook's data-source directory is an absolute local path.** Opening
  the workbook on another machine requires re-pointing the three CSV
  connections.
- The Tableau Public client version is not recorded.
- Scenario lead times and service levels are planning assumptions, not
  operational requirements.
- Validation RMSE is scale-bound and is not comparable across stores; the
  figure says so on its axis.
- Store 4's history covers 60 training days against 532 for the others, so its
  variability estimate rests on fewer observations.

## Remaining Issues

- Refreshing the workbook's extracts and re-publishing the dashboard, so the
  live view reflects the post-audit data.
- A distribution or correlation visualization remains unimplemented; the
  course-coverage rows for those concepts are marked accordingly rather than
  claimed.
