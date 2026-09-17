# Phase 7 — Exploratory Data Analysis Results

## Status

VERIFIED

Verified during the Phase 17 re-audit by executing the pipeline against the
complete integrated dataset (`data/processed/integrated_retail_data.csv`,
7,431,026 rows) and inspecting every generated artifact.

## Dataset

| Metric | Result |
|---|---:|
| Rows analysed | 7,431,026 |
| Total quantity | 41,949,529.910 |
| Total revenue | 5,659,219,309.900 |
| Date start | 2022-08-28 |
| Date end | 2024-09-26 |
| Unique stores | 4 |
| Unique items | 28,180 |

Rows, quantity and revenue reconcile exactly with the Phase 6 integration
report and with the Phase 5 cleaned dataset. Every Phase 7 metric is
calculated from the complete integrated dataset; no sampled subset is used.

## Missingness

See:

`data/analysis/eda_summary.csv`

| Metric | Result |
|---|---:|
| Missing `dept_name` / `class_name` / `subclass_name` | 36,580 |
| Missing `markdown_quantity` | 7,422,317 |
| Missing `promo_discount_rate` | 5,912,426 |
| Rows with a discount record | 1,518,622 |
| Rows with a markdown record | 8,709 |
| Rows with non-finite values (`infinite_promo_discount_rate`) | 6,760 |

Missing promotion and markdown values mean that no matching auxiliary record
exists for that date, item and store after the Phase 6 left joins. They are
not cleaning failures.

Promotion and markdown frequency is reported from
`discount_record_count > 0` and `markdown_record_count > 0` rather than from
null values, so the counts stay correct even where an aggregated value is
itself unusable. The 22-row difference between the discount-record count
(1,518,622) and the non-missing rate count (1,518,600) is explained under
"Non-finite values" in the re-audit record.

## Temporal findings

26 months are covered, from 2022-08 to 2024-09.

| Month | Quantity | Records |
|---|---:|---:|
| 2022-08 (partial; dataset starts 2022-08-28) | 161,947.719 | 28,256 |
| 2023-11 | 1,257,658.749 | 228,071 |
| 2023-12 | 2,100,635.721 | 348,181 |
| 2024-05 (highest) | 2,456,964.945 | 425,279 |

- Highest-demand month: 2024-05 (2,456,964.945).
- Lowest-demand month: 2022-08 (161,947.719). The dataset begins on
  2022-08-28, so this month covers only four days (28,256 records against
  228,071-425,279 in a complete month). The low total reflects partial
  coverage, not a genuine demand trough.
- A structural level shift appears between 2023-11 and 2023-12: monthly
  quantity rises from 1,257,658.749 to 2,100,635.721 while monthly record
  counts rise from 228,071 to 348,181. The 2023-01 to 2023-11 average is
  1,260,084 quantity from 229,552 records per month; the 2024-01 to 2024-09
  average is 2,290,959 quantity from 402,726 records per month. Because
  record counts rise at the same time as quantity, the shift is at least
  partly a change in assortment or coverage rather than demand growth alone.
- Within 2024 demand is highest in the spring and summer months
  (2024-03 to 2024-08, between 2,324,241 and 2,456,964) and lower in
  January and September.
- Revenue follows quantity: the highest-revenue month is 2024-03
  (357,829,881.990).

Interpretation is descriptive only. Stationarity, autocorrelation and
decomposition belong to Phases 8 and 9.

## Store findings

| Store | Quantity | Share of demand | Revenue | Records |
|---|---:|---:|---:|---:|
| 1 | 23,074,468.588 | 55.0% | 3,106,803,486.10 | 3,682,576 |
| 4 | 9,220,435.304 | 22.0% | 1,446,502,879.36 | 1,580,284 |
| 2 | 4,898,960.559 | 11.7% | 492,114,006.09 | 1,337,723 |
| 3 | 4,755,665.459 | 11.3% | 613,798,938.35 | 830,443 |

Store 1 contributes 55.0% of demand and store 4 a further 22.0%. Store 4
generates 25.6% of revenue from 22.0% of demand, so its average selling price
is the highest of the four stores. Store heterogeneity of this magnitude
means store-level effects must be considered during feature engineering and
model comparison.

## Product findings

- 181 named departments plus one unmatched group: 36,580 rows with no
  catalog match, 319,499.611 quantity (0.76% of demand).
- Highest-demand departments: Auxiliary Group (3,111,278.0), Bread
  (2,735,210.334), Fruits (2,079,785.447).
- Highest-demand items: `b0d24502fb66` (2,023,140.0; 4.82% of demand),
  `9a7e315f3f42` (563,403.013) and `63161948a95a` (434,289.0).
- The leading item averages 889.3 units per record across only 2,275 records,
  and Auxiliary Group averages 203.9 units per record, against a dataset mean
  of 5.645 units per record. Both behave like bulk or aggregated lines rather
  than typical consumer products, so department and item rankings should be
  read with that composition in mind.
- Several departments carry source placeholders such as "Fresh Fish DO NOT
  USE" and "Loyalty Promotion (DO NOT USE)". Their demand is negligible and
  they are retained for fidelity to the source catalog.
- Demand is strongly concentrated: the top 10 items account for 11.14% of
  demand, and the top 1% of items (282 of 28,180) account for 40.89%.

## Price findings

- `quantity` vs `price_base`: -0.0444 (pairwise-complete Pearson, complete
  dataset). The row-level linear association between base price and quantity
  is negligible and very slightly negative.
- `price_base` vs `sum_total`: 0.1090. `price_base` vs `markdown_quantity`:
  -0.1828.
- Phase 8 fits the same relationship on the same 7,431,026 observations and
  reports r = -0.04442 with R² = 0.0020 in
  `data/analysis/statistical_price_demand.csv`, which confirms the
  correlation reported here.
- Row-level price spread is not summarised in Phase 7. The dedicated
  price/demand analysis belongs to Phase 8 and is not duplicated here.

## Promotion findings

- 1,518,622 rows (20.4% of the dataset) carry a discount record.
- `promo_discount_rate` vs `quantity`: -0.0654.
  `promo_discount_rate` vs `markdown_quantity`: -0.2182.
- Phase 8's promotion comparison over the same data reports a lower mean
  quantity on promoted rows (5.36, median 2, n = 1,215,172) than on
  non-promoted rows (8.30, median 3, n = 303,428), consistent with the weak
  negative association observed here.
- This is an association, not a causal effect. Promotion targeting is not
  random and item and store composition differ between the two groups.

## Markdown findings

- Markdown records exist for only 8,709 rows (0.12% of the dataset).
- `quantity` vs `markdown_quantity`: 0.6979 (pairwise complete over those
  8,709 rows). `markdown_quantity` vs `promo_discount_rate`: -0.2182 over the
  284 rows where both values exist.
- Because coverage is so sparse, these coefficients describe the marked-down
  subset only. They must not be read as general demand relationships.

## Correlation findings

Pairwise-complete Pearson coefficients calculated from the complete
7,431,026-row dataset. Non-finite values are excluded pairwise, so each
coefficient uses every row in which both variables are usable.

| variable | quantity | price_base | sum_total | online_quantity | markdown_quantity | promo_discount_rate | price_change_count |
|---|---:|---:|---:|---:|---:|---:|---:|
| quantity | 1.0 | -0.044422 | 0.407449 | 0.302598 | 0.697860 | -0.065396 | 0.011631 |
| price_base | -0.044422 | 1.0 | 0.108984 | -0.040614 | -0.182753 | -0.033751 | 0.005552 |
| sum_total | 0.407449 | 0.108984 | 1.0 | 0.125226 | 0.255225 | -0.048182 | 0.012712 |
| online_quantity | 0.302598 | -0.040614 | 0.125226 | 1.0 | 0.143980 | -0.007710 | 0.023298 |
| markdown_quantity | 0.697860 | -0.182753 | 0.255225 | 0.143980 | 1.0 | -0.218218 | 0.033127 |
| promo_discount_rate | -0.065396 | -0.033751 | -0.048182 | -0.007710 | -0.218218 | 1.0 | -0.009932 |
| price_change_count | 0.011631 | 0.005552 | 0.012712 | 0.023298 | 0.033127 | -0.009932 | 1.0 |

Readings:

- `quantity` is most strongly associated with `markdown_quantity` (0.6979,
  8,709 usable rows) and `sum_total` (0.4074), then `online_quantity`
  (0.3026).
- `price_base` has almost no linear relationship with `quantity` (-0.0444).
- `price_base` varies more with `markdown_quantity` (-0.1828) than with any
  other variable.
- All associations are weak to moderate. None of these variables alone
  explains demand.

### Change recorded during the Phase 17 re-audit

Phase 7 previously derived this table from a deterministic sample of 10,000
rows per 250,000-row chunk (300,000 rows, 4.0% of the dataset). That design
gave equal weight to every chunk regardless of its size and reused one seed
for each chunk, so the same positional offsets were drawn from every chunk
and the coefficients were biased relative to the population. The re-audit
replaced the sample with an exact chunked pairwise-moment calculation over
the complete dataset. The affected coefficients changed as follows.

| Pair | Previous (sampled) | Current (exact full dataset) | Difference |
|---|---:|---:|---:|
| quantity vs online_quantity | 0.3397 | 0.3026 | 0.0371 |
| quantity vs markdown_quantity | 0.7078 | 0.6979 | 0.0099 |
| quantity vs sum_total | 0.4038 | 0.4074 | 0.0036 |
| markdown_quantity vs promo_discount_rate | -0.3975 | -0.2182 | 0.1793 |
| markdown_quantity vs price_change_count | -0.0327 | 0.0331 | 0.0659 (sign change) |

Cause: removal of the unequal-weight deterministic sample. Downstream impact:
none. No later phase reads `data/analysis/eda_*.csv`; Phase 8 recalculates its
own statistics from the integrated dataset, and the price/demand coefficient
now agrees with Phase 8 to 15 significant digits.

## Outlier observations

Item-level descriptive outlier and concentration metrics were added during
the Phase 17 re-audit, because the phase purpose, the methodology and the
course-content coverage all require unusual demand to be identified for
investigation.

| Metric | Result |
|---|---:|
| Item-level demand Q1 | 21.0 |
| Item-level demand median | 122.974 |
| Item-level demand Q3 | 699.0 |
| Item-level upper fence (Q3 + 1.5 x IQR) | 1,716.0 |
| Items above the upper fence | 4,007 (14.2% of items) |
| Share of total demand held by those items | 85.27% |
| Top 1% of items (282) | 40.89% of demand |
| Top 10 items | 11.14% of demand |

These "outliers" are the commercially important assortment rather than
invalid records. Nothing is removed, filtered or modified by Phase 7.
Record-level validity outliers remain Phase 5's responsibility, where 73,507
potential quantity outlier rows were identified and retained.

## Visualizations

The following figures are generated by the Phase 7 analysis script. All five
were re-verified during the Phase 17 audit (existence, non-zero size,
dimensions, correspondence with the summary tables):

- `reports/figures/eda_demand_over_time.png` (1800x900)
- `reports/figures/eda_monthly_demand.png` (1800x900)
- `reports/figures/eda_store_demand.png` (1200x750)
- `reports/figures/eda_top_categories.png` (1800x1050)
- `reports/figures/eda_demand_distribution.png` (1500x900)

Chart categories without a catalog match now render an explicit "(unmatched)"
label instead of failing to plot; see the re-audit record below.

## Forecasting implications

- Only 26 months of history across 4 stores. The series is short, so simple
  regularised models are likely to be more reliable than complex ones.
- The level shift between 2023-11 and 2023-12 must be handled deliberately.
  If it reflects coverage or assortment change rather than demand, models
  trained across the break can learn a spurious trend.
- Item-level concentration means a handful of items dominate aggregate error
  metrics; forecast quality should be reported for representative items as
  well as for aggregate demand.
- Promotion and markdown coverage is sparse and only weakly associated with
  demand, so promotional flags are not automatically strong predictors.
- Demand differs materially by store, so store-level effects should be
  available to the modelling phases.
- Phase 7 introduces no temporal leakage: the phase is descriptive and
  creates no predictors or forward-looking features.

## Limitations

EDA identifies descriptive patterns. It does not establish causal
relationships or forecasting performance. The correlation matrix contains
row-level associations that mix item, store and period composition. The
markdown coefficients describe 0.12% of rows. Department and item rankings
are influenced by bulk or aggregated lines such as Auxiliary Group and the
leading item.

## Phase status

VERIFIED. Execution, testing, artifact validation and documentation are
complete for Phase 7.

## Phase 17 Re-Audit Record

**Audit status:** AUDITED — COMPLETE

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/exploratory_data_analysis.py` (664 to 1,059 lines) |
| Tests | `tests/test_exploratory_data_analysis.py` (214 to 775 lines, 10 to 34 tests) |
| Phase 7 documents | all six files in `docs/phase-7/` |
| Generated artifacts | `eda_summary.csv`, `eda_monthly_demand.csv`, `eda_store_summary.csv`, `eda_category_summary.csv`, `eda_top_items.csv`, `eda_correlation.csv`, `eda_findings.txt`, five `eda_*.png` figures |
| Inputs | `data/processed/integrated_retail_data.csv` (Phase 6), `data/raw/discounts_history.csv` (root-cause check) |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-6/integration-results.md`, `docs/project-file-update-register.md`, `README.md` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Phase 7 documentation was never updated after execution | every results section read "NOT YET VERIFIED"; the checklist was unchecked; the update register read "Not yet started" while `README.md` already listed Phase 7 as COMPLETE | Medium |
| F2 | Test quality: tests exercised pandas, not the module | only 4 of 10 tests imported the module; the temporal, store, item, correlation and sampling tests re-implemented pandas calls and could not fail if the script changed; `build_eda_summaries`, `create_figures` and `write_findings` were untested | Medium |
| F3 | Correlation output came from a biased, untraceable sample | equal 10,000 rows per chunk with the same seed in every chunk; measured deviations of up to 0.179 from the exact values, including a sign change; the sample size appeared in no artifact | High |
| F4 | Anomaly/outlier analysis was documented but not implemented | phase purpose ("anomalies"), methodology section 9, coverage "Concept: Outliers" and a dedicated results section, with no output to support them | High |
| F5 | "Is demand concentrated among a small number of products?" was never answered | plan question; only an unranked top-100 item list existed | Medium |
| F6 | Promotion/markdown frequency was only implied by null counts | plan questions; `missing_promo_discount_rate` cannot distinguish "no record" from "unusable record" | Medium |
| F7 | Chart labels fail when a category has no value under pandas 3 or later | `Series.astype(str)` preserves missing values as float NaN, which matplotlib's category converter rejects; reproduced with a fixture whose unmatched department ranks in the top 15 | High (latent) |
| F8 | Non-finite values reach the analytical columns | 6,760 `inf` in `promo_discount_rate` and 2 in `markdown_discount`; pandas 3.0.5 silently ignores non-finite values in `corr()` while pandas below 3 returns NaN, and `requirements.txt` is unpinned | Medium (cross-phase) |
| F9 | Findings file contained float artefacts | `Highest-demand store: 1.0`; `41949529.910000004`; `3111278.0` | Low |
| F10 | Missingness was counted with 16 separate passes per chunk | column-wise `isna()` loop inside the chunk loop | Low |
| F11 | The framework's "input file exists" check was not implemented | raw `FileNotFoundError` with no path or remediation hint | Low |
| F12 | `read_csv(..., nrows=0)` cannot infer dtypes | the header-only read classifies every column as `object`, so numeric integrity counters must not depend on it | Low |

**Leakage audit:** none, and none is possible — Phase 7 performs only
row-level aggregation and correlation over a completed dataset. No lag,
rolling, interpolation or forward-filling feature is created, and no
chronological split is altered.

**Full-data audit:** every aggregate already used the full dataset; the only
sampled calculation was the correlation matrix, which now uses the full
dataset as well.

**Efficiency audit:** the pipeline reads the integrated dataset three times
(one aggregation pass over the 16 analytical columns and two correlation
passes over the 7 numeric columns). Runtime was measured at 61-63 seconds
end to end on the complete dataset.

### Code changes

| File | Change | Reason | Benefit |
|---|---|---|---|
| `scripts/exploratory_data_analysis.py` | `build_correlation`, `correlation_offsets`, `accumulate_correlation`, `pearson_from_accumulators`: exact chunked pairwise-complete Pearson replacing the per-chunk sample and `random_state` | F3 | Exact, reproducible, version-independent coefficients at constant memory |
| same | `describe_item_demand`: item-level quartiles, IQR upper fence, outlier count and demand share, top-1% and top-10 concentration | F4, F5 | Closes two documented-but-unimplemented requirements |
| same | `rows_with_discount_record`, `rows_with_markdown_record` and an `infinite_<column>` block in `eda_summary.csv` | F6, F8 | Answers the promotion/markdown frequency questions and quantifies non-finite values |
| same | `chart_labels` used for every categorical chart axis | F7 | Charts render even when a category has no value; the unmatched department is shown explicitly |
| same | `validate_input_file` with an actionable message; `read_numeric_columns` from a 10,000-row sample | F11, F12 | Clear failure mode; reliable numeric integrity counters |
| same | vectorized missingness (`chunk[use_columns].isna().sum(axis=0)`) replacing the 16-pass loop | F10 | One pass per chunk instead of sixteen |
| same | `format_metric` and `format_identifier` for the findings text | F9 | No float artefacts in a user-facing artifact |
| `tests/test_exploratory_data_analysis.py` | 6 pandas-only tests replaced by 24 module tests (fixtures, monkeypatched paths, chunk independence, oracle comparison, non-finite handling, metric values, figures, findings) | F2 | The phase's core logic is covered by assertions that can fail |

### Testing

```text
Command: .venv\Scripts\python.exe -m pytest tests/test_exploratory_data_analysis.py -q
Result:  34 passed
Tests:   34
Passed:  34
Failed:  0
Skipped: 0
Warnings: 0

Command: .venv\Scripts\python.exe -m pytest -q
Result:  193 passed, 1 warning
Warnings: pre-existing UserWarning in scripts/clean_retail_data.py (Phase 5)
```

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/exploratory_data_analysis.py
Exit status: 0
Runtime:     61-63 seconds
Result:      "Exploratory data analysis completed successfully."
```

### Generated-file verification

| File | Exists | Size | Structure | Validation |
|---|---|---|---|---|
| `eda_summary.csv` | yes | 1,253 B | 45 metric rows | includes missing, non-finite, record-frequency and item-distribution metrics |
| `eda_monthly_demand.csv` | yes | 1,162 B | 26 months | matches the dataset totals; 2022-08 partial |
| `eda_store_summary.csv` | yes | 185 B | 4 stores | sorted by quantity; shares 55.0 / 22.0 / 11.7 / 11.3% |
| `eda_category_summary.csv` | yes | 7,714 B | 182 rows | 181 named departments plus one unmatched group (0.76% of demand) |
| `eda_top_items.csv` | yes | 3,948 B | 100 items | descending quantity; leader 4.82% of demand |
| `eda_correlation.csv` | yes | 1,158 B | 7x7 matrix | all 21 coefficients match an independent chunked calculation; diagonal exactly 1.0 |
| `eda_findings.txt` | yes | 1,595 B | 8 sections | no float artefacts; store rendered as "1" |
| 5 figures | yes | 21-67 KB | 1800x900 / 1500x900 / 1200x750 | dimensions match the configured figsize x dpi |

### Documentation changes

`eda-results.md` (this file), `eda-methodology.md`, `eda-plan.md`,
`eda-quality-framework.md`, `course-content-coverage.md`,
`phase-7-checklist.md`, plus the cross-phase records listed under
"Files reviewed".

### Remaining issues

- **Flagged for Phase 6:** `promo_discount_rate` contains 6,760 `inf` values
  and `markdown_discount` 2, because 21,419 of the 3,746,744 raw discount
  records have `sale_price_before_promo == 0`, so `1 - during/before` divides
  by zero. A further 28 records have both prices equal to zero, which yields a
  NaN rate for 22 integrated rows and explains the 22-row difference between
  the record count (1,518,622) and the usable rate count (1,518,600). Phase 7
  excludes non-finite values explicitly; guarding the division belongs to the
  Phase 6 script and was not changed during this audit.
- **Dependency pinning:** `requirements.txt` lists unpinned packages. Chart
  and correlation behaviour differs between pandas 2 and pandas 3, so pinning
  would improve reproducibility. Not changed here.
- **Deferred:** row-level price spread statistics are not produced by Phase 7;
  Phase 8 owns the price/demand analysis. The 2023-12 level shift is
  documented but not diagnosed, because Phase 7 has no data-source lineage
  beyond the raw files.
