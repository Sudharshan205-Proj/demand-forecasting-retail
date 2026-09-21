# Phase 15 — Visualization & Tableau Results

## Environment

| Tool | Version | Evidence |
|---|---|---|
| Python | 3.12 (project virtual environment) | `.venv` |
| matplotlib | 3.11.1 | `pip show matplotlib` |
| pandas | 3.0.5 | `pip show pandas` |
| numpy | 2.5.2 | `pip show numpy` |
| scipy | 1.18.1 | `pip show scipy` |
| Tableau | 2026.2.2 (build 20262.26.0819.2015) | `.twb` `source-build` attribute |

Tableau Public is a hosted service; its client version is not recorded in the
environment document.

## Workflow Execution

| Item | Value |
|---|---|
| Workflow | `scripts/create_visualizations.py` |
| Inputs consumed | 5 analytical files |
| Validation checks | 55 — all passing |
| Quality report | `data/analysis/visualization_quality_report.csv` |
| Manifest | `data/analysis/visualization_manifest.csv` |
| Figures written | 4 |
| Exit code | 0 |

Inputs (all produced by Phase 13):

- `inventory_demand_summary.csv` — 4 rows
- `inventory_variability_summary.csv` — 4 rows
- `inventory_scenarios.csv` — 36 rows
- `forecast_inventory_insights.csv` — 13 rows
- `tuned_validation_results.csv` — 4 rows

The workflow gates on its checks: if any check fails it writes the failing report,
prints `FAILED` to stderr, returns exit code 1 and draws no figure. The figures
and both reports are written only after every input check passes, and the reports
are rewritten afterwards to include the four figure checks.

## Static Outputs

| Figure | Bytes | SHA-256 | Source | Source rows |
|---|---|---|---|---|
| `store_average_daily_demand.png` | 32,067 | `33d5a9d4…65f588a7` | demand | 4 |
| `store_demand_variability.png` | 36,079 | `58a0b7d4…fc5c5416` | variability | 4 |
| `reorder_point_by_lead_time.png` | 103,628 | `64d17cb4…2b3d20b7` | scenarios | 36 |
| `lowest_validation_rmse.png` | 43,048 | `b868be45…0ab7ba69` | insights | 13 |

The full digests are recorded in `visualization_manifest.csv`, which the test
suite verifies against the files on disk. Every figure post-dates the inputs it
describes, and the digests are reproduced identically across repeated runs.

Each figure carries direct value labels and explicit units:

| Figure | Title | Axis label |
|---|---|---|
| Average demand | Average Daily Physical Demand by Store | Mean Daily Demand (demand units, training period) |
| Variability | Relative Demand Variability by Store | Coefficient of Variation (std / mean, training period) |
| Scenarios | Scenario Reorder Points at an Assumed 95% Service Level | Assumed Lead Time (days) — a planning assumption, not a requirement |
| Forecast evidence | Lowest Validation RMSE Among Validated Models, by Store | Validation RMSE (demand units — not comparable across stores) |

## Values

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
row-by-row against `inventory_scenarios.csv` and against the Phase 13 insights:
Store 1 = 448,302.491763; Store 2 = 95,240.141608; Store 3 = 91,617.640793;
Store 4 = 476,010.139796.

The 55 checks cover, in addition to presence and type checks: the coefficient of
variation equals std / mean; the variance equals the squared standard deviation;
percentile ordering; z values equal the standard-normal quantile of the service
level; expected lead-time demand, safety stock and reorder point each reconcile
with their formula; reorder points are monotonic in both service level and lead
time; every store covers the full 3 × 3 scenario grid; scenario demand levels
match the demand summary; every store set is identical across inputs; and all
five insight families reconcile to their sources.

## Tableau Workbook

| Property | Value |
|---|---|
| File | `tableau/Retail_Demand_Forecasting.twb` |
| Authored with | Tableau 2026.2.2 (20262.26.0819.2015), `source-platform='win'`, `license-type='public'` |
| Repository id | present — `id='Retail_Demand_Forecasting'`, `path='/workbooks'`, `revision='1.0'` |
| Data sources | `inventory_scenarios.csv`, `inventory_variability_summary.csv`, `tuned_validation_results.csv` |
| Worksheets | 6 — Average Demand by Store; Relative Demand Variability; Forecast Evidence; Reorder-Point Scenarios; Safety Stock Scenarios; `KPI Summary` (all fully built) |
| Dashboard | 1 — *Retail Demand Forecasting & Inventory Planning*, fixed 1600 × 900 |
| Filters | 11 `<filter>` elements across the sheets for the six intended cards (the sixth is the `KPI Summary` `Measure Names` filter); 6 filter zones in the desktop layout over 5 field/source combinations |
| Layout zones | 41 `<zone>` elements — 23 in the desktop layout, 18 in the auto-generated phone layout |
| Field instances | 46 `<column-instance>` elements |
| Marks | 3 Bar, 2 Line, 1 Text (the `KPI Summary` tiles) |
| Hidden fields | 5 — `order`, `season_length` (Validation Results); `p90`, `p95`, `p99_daily_demand` (Store Variability) |

The workbook is well-formed XML and the test suite asserts its six worksheets by
name, its dashboard, data sources, hidden fields and repository id.

### Worksheet behaviour

| Worksheet | Encoding |
|---|---|
| Average Demand by Store | Bar chart of mean daily demand per store |
| Relative Demand Variability | Bar chart of the coefficient of variation per store |
| Forecast Evidence | Cross-store comparison on MAPE, with validation RMSE carried in the tooltip together with its scale-bound caveat in the field name |
| Reorder-Point Scenarios | Line chart of `AVG(reorder_point)` filtered to the 95 % baseline service level, lead-time axis fixed to 7 → 28 days so it cannot imply lead times outside the scenario set |
| Safety Stock Scenarios | Grouped by service level for a single store, so each sheet carries one grouping variable and one constant |
| `KPI Summary` | Text-mark KPI tiles under `Measure Names` on Columns |

**`KPI Summary` is the sixth worksheet and it is built.** It blends Store
Variability and Validation Results on `Store`, computes three measures —
`MAX([mean_daily_demand])`, `MAX([std_daily_demand] / [mean_daily_demand])` and
`MIN([mape_percent])` — into `Measure Values` on a Text mark with `Measure Names`
on Columns. The tiles read the extreme values `29,711 units/day`, `0.3801` and
`8.14%` under their KPI-name headers. Two shapes are recorded rather than hidden:
the evidence tile is MAPE rather than RMSE, and the sheet's tooltip definition is
one literal sentence covering all three tiles because Tableau does not permit
`[Measure Names]` inside a calculation. The tooltip carries the KPI name, its
value, a plain-text definition and the source CSV.

### Schema reconciliation

The workbook's cached textscan schema is rebuilt from the current CSV headers by
`scripts/sync_tableau_workbook_schema.py`, which writes the workbook back only
when something changed. The reconciliation:

- lists the current headers in order with contiguous ordinals in each `<columns>`
  block;
- corrects each column `<metadata-record>` ordinal and includes `season_length`
  and `order`;
- **preserves declared datatypes** — `validation_start` and `validation_end`
  remain `date` rather than being downgraded to text;
- clones newly added records from the block's own record of the same datatype, so
  the extract flavour (which carries `<family>` and `<approx-count>`) is
  reproduced exactly;
- reads the workbook's own `hidden='true'` declarations, checks the live blocks
  against the full header order and the extract blocks against the visible
  subset, and preserves any cached record outside the expected schema instead of
  deleting it.

The reconciliation is idempotent: a second run reports no change. It is covered by
the test suite, including a drift case in which a new column is added to a source
copy, and a case asserting that a hidden field is never re-introduced into an
extract's metadata.

## Tableau Public

| Property | Value |
|---|---|
| URL | `https://public.tableau.com/views/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |
| Canonical URL | `https://public.tableau.com/app/profile/sudharshan.moodley/viz/Retail_Demand_Forecasting/RetailDemandForecastingInventoryPlanning` |
| Workbook match | URL workbook id = `Retail_Demand_Forecasting` = `repository-location/@id`; URL view slug = `RetailDemandForecastingInventoryPlanning` = the dashboard name with non-alphanumerics removed |

The dashboard is publicly reachable and its URL names this workbook and this
dashboard. The `<repository-location>` stamp in the workbook on disk confirms that
the committed copy is the published one.

## Tests

`tests/test_create_visualizations.py` — 34 tests, all passing:

- the workflow driven end-to-end as a subprocess over synthetic CSV fixtures, run
  from a directory that is not the project root, asserting all four figures, both
  reports and the manifest;
- the manifest digest and byte size re-verified against the files on disk;
- a failing gate proven to withhold every figure and mark the report FAIL;
- 14 unit tests over `validate_inputs` and `validate_leakage_guard`, covering
  missing columns, empty inputs, negative demand, negative variability, a broken
  variance identity, negative reorder points, invalid service levels, mismatched
  store sets, duplicate store ids, missing insight types, unreconciled insight
  values and a test-period metric;
- 6 parametrized subprocess failure paths, each asserting a non-zero exit, a
  `FAILED` message and no figure written;
- 9 workbook, hidden-field and URL tests — well-formedness, worksheets and
  dashboard, full schema agreement with the current CSV headers, preserved date
  datatypes, idempotent reconciliation, drift detection, unknown-source
  rejection, the published URL match, the five hidden fields being exactly those
  declared, and a hidden field never appearing in an extract's metadata.

## Assumptions and Limitations

- **The published dashboard reflects its publish-time extract.** The workbook
  embeds three extracts whose `update-time` is 2026-09-20 and which point at
  transient `#TableauTemp_*.hyper` files created by the publish. Their values
  match the current CSVs — re-deriving the plotted reorder points from
  `inventory_scenarios.csv` reproduces what the sheet shows — but a later
  pipeline re-run would change the repository's figures and not the live view
  until the workbook is re-published, which needs Tableau Desktop.
- **The workbook's data-source directory is an absolute local path.** Opening the
  workbook on another machine requires re-pointing the three CSV connections.
  Publishing from an extract makes the *published view* independent of that path;
  it does not make the committed `.twb` portable.
- The Tableau Public client version is not recorded.
- Scenario lead times and service levels are planning assumptions, not
  operational requirements.
- Validation RMSE is scale-bound and is not comparable across stores; the figure
  says so on its axis.
- Store 4's history covers 60 training days against 532 for the others, so its
  variability estimate rests on fewer observations.
- A distribution or correlation visualization is not part of the delivered
  figure set; the course-coverage rows for those concepts are marked accordingly
  rather than claimed.

The workbook's structure and specification are recorded in
`tableau/tableau-dashboard-specification.md` and
`tableau/tableau-data-dictionary.md`.
