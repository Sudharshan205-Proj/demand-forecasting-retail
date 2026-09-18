# Phase 8 — Statistical & Analytical Results

## Status

VERIFIED

Verified during the Phase 17 re-audit by executing the complete statistical
pipeline against the full integrated dataset (7,431,026 rows) and inspecting
every generated artifact. Every reported statistic is calculated from the
complete dataset; no reported value comes from a sample.

## Source

`data/processed/integrated_retail_data.csv`

Produced by Phase 6. The re-audit was executed after a Phase 6 fix that
guarded two zero denominators, so the source no longer contains any infinite
value in `promo_discount_rate` or `markdown_discount` (see
`docs/phase-6/integration-results.md`).

## Outputs

Analysis tables in `data/analysis/`:

- `statistical_summary.csv`
- `statistical_correlations.csv`
- `statistical_store_analysis.csv`
- `statistical_category_analysis.csv`
- `statistical_price_demand.csv`
- `statistical_promotion_analysis.csv`
- `statistical_autocorrelation.csv`
- `statistical_trend.csv`
- `statistical_monthly_activity.csv`
- `statistical_quality_report.csv`
- `statistical_findings.txt`

Figures in `reports/figures/`:

- `statistical_demand_trend.png`
- `statistical_price_demand.png`
- `statistical_store_variability.png`
- `statistical_demand_autocorrelation.png`

## Verified results

### Dataset and reconciliation

| Metric | Result |
|---|---:|
| Rows read | 7,431,026 |
| Daily observations | 761 |
| Calendar days covered | 761 |
| Missing calendar days | 0 |
| Date range | 2022-08-28 to 2024-09-26 |
| Total quantity demand | 41,949,529.910 |
| Total revenue | 5,659,219,309.900 |
| Stores | 4 |
| Months covered | 26 |
| Invalid dates | 0 |
| Non-finite quantities | 0 |

Row counts, quantity, revenue, stores, items and date coverage all reconcile
exactly with the Phase 6 integration report and the Phase 7 EDA results. The
daily grain covers every calendar day in the range with no gap, so the time
series is complete.

### Descriptive statistics of daily demand

| Metric | Result |
|---|---:|
| Mean daily quantity | 55,124.218 |
| Median daily quantity | 44,753.823 |
| Standard deviation | 19,326.148 |
| Minimum | 19,345.758 |
| Maximum | 154,068.882 |
| Coefficient of variation | 0.351 |

The coefficient of variation of 0.35 means daily demand varies by roughly a
third of its mean, and the mean sits well above the median: the distribution
is right-skewed by high-demand days.

### Relationships with demand

Pearson correlation is calculated pairwise-complete over the full dataset,
together with the sample covariance. Correlations describe association only.

| Variable | Observations | Pearson r | Covariance | p-value |
|---|---:|---:|---:|---:|
| `markdown_quantity` | 8,709 | 0.697860 | 22.394135 | < 1e-300 |
| `online_quantity` | 7,431,026 | 0.302598 | 13.563874 | < 1e-300 |
| `online_sales_value` | 7,431,026 | 0.189301 | 898.230735 | < 1e-300 |
| `promo_discount_rate` | 1,511,840 | -0.065396 | -0.141416 | < 1e-300 |
| `markdown_discount` | 8,707 | 0.052884 | 0.058512 | 7.91e-07 |
| `price_base` | 7,431,026 | -0.044422 | -410.078383 | < 1e-300 |
| `price_change_count` | 7,431,026 | 0.011631 | 0.062967 | 1.21e-220 |
| `discount_record_count` | 7,431,026 | 0.005654 | 0.062470 | 1.37e-53 |
| `markdown_record_count` | 7,431,026 | 0.001510 | 0.001479 | 3.87e-05 |

The only strong linear association with physical demand is
`markdown_quantity` (r = 0.698 over 8,709 rows that carry a markdown record).
Online quantity correlates moderately (r = 0.303) but online demand is a
separate channel and is never added to physical demand. All remaining
coefficients are weak: below |0.07|, which means price, promotion and
assortment-change counts explain very little of row-level demand variation.

These independent full-dataset values agree with the Phase 7 EDA correlation
matrix to 15 significant figures, which cross-validates both implementations.

### Price-demand relationship

| Metric | Result |
|---|---:|
| Observations | 7,431,026 |
| Pearson r | -0.044422 |
| p-value | < 1e-300 |
| Regression slope (quantity per price unit) | -0.003613 |
| Intercept | 6.395124 |
| R-squared | 0.001973 |

Demand and price are negatively associated, in the expected direction, but the
relationship is extremely weak: price explains 0.2% of row-level quantity
variation. This is an analytical association, **not** a causal price
elasticity, and it is not estimated on a controlled price experiment.

### Promotion comparison

The primary comparison follows the phase plan: records with a discount record
are compared with records without one. The secondary breakdown splits the
promoted records by the sign of the finite discount rate.

| Comparison | Group | Observations | Mean quantity | Median quantity | Mean discount rate |
|---|---|---:|---:|---:|---:|
| Presence | `promotion_record_present` | 1,518,622 | 5.951 | 2 | 0.187495 |
| Presence | `promotion_record_absent` | 5,912,404 | 5.567 | 2 | — |
| Rate sign | `promotion_rate_positive` | 1,215,172 | 5.364 | 2 | 0.233879 |
| Rate sign | `promotion_rate_non_positive` | 296,668 | 8.362 | 3 | -0.002495 |

- Presence comparison: Mann-Whitney U = 4.959047e+12, p < 1e-300.
- Rate-sign comparison: Mann-Whitney U = 1.675299e+11, p < 1e-300.

Demand is higher on promoted rows (mean 5.951 versus 5.567; median equal at
2), but the difference is small relative to the spread of the data. Within the
promoted rows, the pattern reverses: rows whose discount rate is positive have
*lower* mean demand (5.364) than rows with a non-positive rate (8.362).

This is not evidence that promotions reduce demand. Promotion selection is not
random: discounts are placed on fast-selling or clearance items, and rows with
a non-positive rate mostly carry a markdown rather than a promotion. Both
comparisons are group differences in observational data.

### Trend

| Metric | Result |
|---|---:|
| Observations | 761 |
| Slope per day | 66.979443 |
| Intercept | 29,672.030 |
| R-squared | 0.580431 |
| p-value (OLS) | 2.71e-145 |
| Standard error (OLS) | 2.067030 |
| Newey-West standard error | 4.301785 |
| Newey-West p-value | 1.21e-47 |
| HAC maximum lags | 14 |

Aggregate daily demand trends upwards by about 67 quantity units per day, and
a linear trend explains 58% of daily variation. Because daily demand is
strongly autocorrelated, the naive OLS standard error (2.07) understates
uncertainty; the Newey-West (HAC) standard error is 4.30, roughly double. The
trend remains statistically significant under the robust measure, but the
trend itself is not purely organic demand growth — see the level-shift finding
below.

### Autocorrelation

| Lag (days) | Autocorrelation |
|---:|---:|
| 1 | 0.882016 |
| 2 | 0.755541 |
| 3 | 0.720710 |
| 4 | 0.718364 |
| 5 | 0.733122 |
| 6 | 0.807726 |
| 7 | 0.873946 |
| 8 | 0.806308 |
| 9 | 0.724339 |
| 10 | 0.700074 |
| 11 | 0.698572 |
| 12 | 0.717093 |
| 13 | 0.809650 |
| 14 | 0.885024 |

Demand is strongly autocorrelated, and the pattern is not a monotone decay:
autocorrelation is highest at lag 14 (0.885), lag 1 (0.882) and lag 7 (0.874).
This weekly periodicity is the single most important structural finding for
forecasting.

### Store and department comparison

| Store | Quantity | Revenue | Records | Share of demand |
|---|---:|---:|---:|---:|
| 1 | 23,074,468.588 | 3,106,803,486.10 | 3,682,576 | 0.5501 |
| 2 | 4,898,960.559 | 492,114,006.09 | 1,337,723 | 0.1168 |
| 3 | 4,755,665.459 | 613,798,938.35 | 830,443 | 0.1134 |
| 4 | 9,220,435.304 | 1,446,502,879.36 | 1,580,284 | 0.2198 |

Store 1 carries 55% of demand and store 4, active only from 2023-12, already
carries 22%. The department table covers 182 groups, led by Auxiliary Group
(3,111,278) and Bread (2,735,210); the 36,580 rows with no catalog match form
their own unmatched group (319,500 quantity, 0.76% of demand).

Store and department comparisons are reported descriptively. They are not
tested for significance because the store groups contain only four units and
because department rows are far from independent; with millions of
observations a significance test would add no information beyond the
magnitudes shown here.

### Monthly activity and the 2023-11 to 2023-12 level shift

`statistical_monthly_activity.csv` records, for all 26 months, the row count,
distinct items, distinct stores, quantity and revenue.

| Month | Records | Distinct items | Distinct stores | Quantity | Revenue |
|---|---:|---:|---:|---:|---:|
| 2023-10 | 234,022 | 12,544 | 3 | 1,280,277.961 | 164,498,564.62 |
| 2023-11 | 228,071 | 12,577 | 3 | 1,257,658.749 | 164,759,463.37 |
| 2023-12 | 348,181 | 15,041 | 4 | 2,100,635.721 | 338,187,860.55 |
| 2024-01 | 377,757 | 14,731 | 4 | 1,983,902.447 | 285,956,261.75 |
| 2024-07 | 422,055 | 15,399 | 4 | 2,449,969.778 | 340,370,226.96 |

The level shift is a **coverage and assortment change, not demand growth**:

- the number of stores reporting rises from 3 to 4 in 2023-12;
- distinct items per month rise from about 12,500-13,700 (2023) to about
  14,500-15,400 (2024);
- monthly rows rise from about 228,000 to about 350,000-425,000, while
  quantity per row stays near 5.5-6.0 throughout.

The change is present in the raw source data, not created by the pipeline:
`data/raw/sales.csv` contains store 4 only from **2023-12-13** onward, while
stores 1-3 span the full range 2022-08-28 to 2024-09-26. This resolves the
level shift that Phase 7 documented and deferred.

The consequences are recorded under Forecasting implications: the first and
last months are partial (2022-08 starts on the 28th, 2024-09 ends on the 26th)
and models fitted across the break can learn the coverage change as trend.

### Quality report

`statistical_quality_report.csv` contains 56 metrics and evidences the checks
the quality framework requires. All reconciliation flags are true:

| Check | Result |
|---|---|
| `monthly_records_reconciled` | True (7,431,026) |
| `quantity_reconciled` | True (41,949,529.910) |
| `revenue_reconciled` | True (5,659,219,309.900) |
| `promotion_records_reconciled` | True (1,518,622 + 5,912,404) |
| `promotion_rate_rows_reconciled` | True (1,511,840 + 6,782) |
| `correlations_in_valid_range` | 9 of 9 |
| `correlations_not_computed` | 0 |
| `regression_outputs_finite` | True |
| `autocorrelation_outputs_finite` | True |
| `trend_outputs_finite` | True |
| `p_values_underflowed` | 5 |
| `scatter_sample_points` | 200,839 (systematic, 1 per 37 eligible rows) |
| `figures_written` | 4 |

## Interpretation requirements

Final interpretations must distinguish:

- statistical significance from practical significance — with 7.43 million
  rows, p < 1e-300 is reached by coefficients as small as 0.0015, so
  magnitude, not significance, decides importance;
- association from causation — the price and promotion results are
  observational group differences that selection effects can explain;
- an underflowed p-value from a meaningful one — probabilities below 1e-300
  are reported as `< 1e-300`, because a probability of exactly zero is not a
  valid statistical statement.

## Forecasting implications

- **Weekly seasonality is the strongest signal.** Lag 7 and lag 14
  autocorrelation (0.874 / 0.885) is higher than lag 1 (0.882) only marginally
  and much higher than lag 5-6, so phase 9-12 models need weekly terms.
- **Strong short-run autocorrelation** means naive random train/test splits
  would leak; temporal splits and differencing are required.
- **The trend must not be read as organic growth.** Because store 4 enters on
  2023-12-13 and assortment grows, any model trained across the break can
  learn coverage as trend. Either the series must be made comparable (for
  example store 1-3 basis) or the break must be modelled explicitly.
- **Price and promotions are weak row-level predictors.** They contribute
  little to explaining row-level quantity, so a forecasting design should not
  expect them to carry the main signal.
- **Assortment items differ enormously in magnitude**, so aggregate error
  metrics should be complemented by per-item evaluation in Phase 12.

- **Phase 9 quantified the gap structure.** 55,122 of 58,022 item-store
  series contain intermediate date gaps (12,553,017 missing intermediate
  days), so the temporal splits established in Phase 9 are contiguous by date
  while individual series remain sparse.

## Limitations

- The dataset is observational; no causal price elasticity can be estimated.
- The trend is described by a linear fit, which is a summary and not a
  forecast.
- The trend significance is autocorrelation-robust (Newey-West) but the fit
  itself is still not a time-series model; phase 9 does the modelling.
- The price/demand scatter figure uses a deterministic systematic sample
  (1 per 37 eligible rows, 200,839 points) so that it spans the whole date
  range; every reported statistic uses the complete dataset.
- Department and store differences are descriptive only.

## Phase status

Phase 8 is implemented, executed and verified.

## Phase 17 Re-Audit Record

### Files reviewed

| Type | Files |
|---|---|
| Script | `scripts/statistical_analytical_analysis.py` |
| Tests | `tests/test_statistical_analytical_analysis.py` |
| Phase 8 documents | all six files in `docs/phase-8/` |
| Generated artifacts | 10 CSVs and `statistical_findings.txt` in `data/analysis/`, 4 figures in `reports/figures/` |
| Inputs | `data/processed/integrated_retail_data.csv`, `data/raw/sales.csv` (independent verification), `data/raw/discounts_history.csv` |
| Downstream | `scripts/prepare_time_series.py`, `scripts/feature_engineering.py` (consumers of the analysis grain) |
| Cross-phase | `docs/phase-0/project-state.md`, `docs/phase-0/curriculum-mapping.md`, `docs/phase-1/requirements-traceability.md`, `docs/phase-2/dataset-inventory.md`, `docs/phase-6/integration-results.md`, `docs/phase-7/eda-results.md`, `docs/phase-7/eda-methodology.md`, `docs/phase-7/eda-quality-framework.md`, `docs/project-file-update-register.md`, `README.md`, `requirements.txt` |

### Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | Documentation never updated after execution | `statistical-results.md` said "Not yet executed"; the checklist was entirely unchecked; the register said "Files will be determined at Phase 8 start." while the README reported COMPLETE | Medium |
| F2 | **Promotion comparison was not what the plan specifies** | The plan requires "Promotion versus non-promotion". The code dropped rows with a missing rate and split the remainder by rate sign, so the group labelled `no_promotion_discount` (303,428 rows) excluded the 5,912,426 rows with no discount record at all | High |
| F3 | **Documented memory strategy was not honoured** | The methodology states the complete source is never loaded into memory, but `relationship_parts` retained 10 columns x 7,431,026 rows: 594.5 MB retained and about 1,189 MB peak at the concatenation, followed by nine further full-frame copies inside `calculate_correlations` | Medium |
| F4 | The scatter figure plotted an arbitrary 2.7% block | `create_figures` re-read the file with `nrows=200,000`, covering about 50 of 761 days in file order, presented as "Price and Demand Relationship" with no note | Medium |
| F5 | Framework validation was unimplemented | The framework requires finite results, no unexpected division by zero, sufficient observations, valid correlation ranges, valid p-values, valid regression outputs and output validation; only `validate_columns` existed and no artifact recorded any of it | Medium |
| F6 | p-values were reported as exactly `0.0` | Four correlation rows, the price regression and both promotion tests printed `p_value = 0.0` (float underflow), and the findings text printed "p=0.0" | Medium |
| F7 | Trend significance was not defensible as reported | OLS on 761 autocorrelated daily observations (lag-1 autocorrelation 0.882) gave a standard error of 2.067 and p = 2.7e-145, both invalid under OLS assumptions | Medium |
| F8 | The plan's "covariance where applicable" was never implemented | No covariance appeared in any artifact | Low |
| F9 | Non-finite handling was inconsistent | `clean_pair` dropped ±inf, but the promotion path used `.dropna()` only, so infinite rates were classified as promotions | Low |
| F10 | Two of the plan's three group comparisons had no test or justification | Store and department tables were raw aggregates with no stated reason | Low |
| F11 | Dead code | `RANDOM_SEED = 42` was unused; `year_month` was computed per chunk and never consumed; `average_price` was aggregated per chunk, re-averaged as a mean-of-chunk-means and never used | Low |
| F12 | Findings text contained float artefacts and float-formatted identifiers | `daily_quantity_max: 154068.88199999998`, `lag_days: 14.0` | Low |
| F13 | Test coverage missed the core | 10 tests covered six pure functions; `aggregate_chunks`, `clean_pair`, `create_figures`, `write_findings` and `main` were untested, and one test locked in the F2 mislabelling | Medium |
| F14 | Cross-phase records were stale | `requirements-traceability.md` left Promotions and Quantitative analysis unmarked; `project-state.md` carried two contradictory "next audit target" lines (Phase 8 and Phase 7); `requirements.txt` was unpinned | Low |

**Leakage audit:** none. The pipeline performs row-level aggregation and
pairwise statistics only; no forward or backward fill, no windowing, and the
daily series is sorted chronologically before temporal analysis.

**Positive validation:** Phase 8's independent full-dataset values match the
Phase 7 exact correlation matrix to 15 significant figures, and
`statistical_category_analysis.csv` is byte-identical to Phase 7's
`eda_category_summary.csv`.

### Code changes

1. **Streaming statistics (F3, F4, F8, F9, F10).** The retained relationship
   frame was replaced by a `PairMoments` accumulator that merges chunk-level
   centered sums with the parallel-accumulation formula. Correlations,
   covariance, the price regression and the scatter sample are now computed in
   the single existing chunked pass, so no full frame is materialised and no
   per-column full-frame copies are made. The second file read disappeared.
2. **Promotion comparison corrected (F2, F9).** The primary comparison is now
   presence-based (`discount_record_count > 0`, 1,518,622 rows, versus
   5,912,404 rows with no record), with the rate-sign breakdown retained as a
   secondary, clearly labelled comparison over finite rates only. The two
   presence groups partition the rows with a finite demand value, and that
   partition is asserted by the quality report.
3. **New quality report (F5).** `statistical_quality_report.csv` records 56
   metrics: row, quantity, revenue, date and monthly reconciliation; per
   variable observation and exclusion counts; correlation-range validity;
   observation sufficiency; output finiteness; promotion partition
   reconciliation; p-value underflow count; scatter sample size and figure
   count.
4. **New monthly activity diagnostic (F11).** `statistical_monthly_activity.csv`
   gives the previously unused `year_month` column a purpose and answers the
   level-shift question Phase 7 deferred.
5. **Robust trend inference (F7).** Newey-West (HAC, 14 lags) standard error
   and p-value were added next to the OLS values, using the already-declared
   `statsmodels` dependency.
6. **Degenerate-variance rule.** A variable whose variance is indistinguishable
   from zero relative to its own scale now yields an undefined correlation
   instead of a meaningless coefficient.
7. **Dead code removed (F11).** `RANDOM_SEED`, the unused `average_price`
   aggregation and the retired relationship-frame machinery.
8. **Chunk size reduced (F3).** `CHUNK_SIZE` changed from 250,000 to 100,000:
   measured 483.4 MB peak versus 659.7 MB for the aggregation at identical
   runtime.
9. **Findings formatting (F6, F12).** Underflowed p-values print as
   `< 1e-300`, identifiers and counts print as integers, and magnitudes print
   without floating-point artefacts. Raw values remain in the CSVs.

### Testing

| Test | Result |
|---|---|
| Phase 8 test file | 46 tests, all passing (was 10) |
| Full suite | 231 tests, all passing (10 of them replaced by 46 Phase 8 tests; 2 Phase 6 tests added) |

Coverage added: streaming moments against whole-array scipy reference values,
chunk-size independence, NaN and ±inf exclusion, degenerate variance,
promotion presence semantics and rate-sign partition, manual verification of
group statistics and the Mann-Whitney values, correlation schema and ordering,
price regression response/predictor orientation, integer lags, OLS and HAC
trend values, store shares, quality-report reconciliation including two
deliberate failure cases, findings formatting, figure generation and the
complete `main()` workflow.

### Script execution

```text
Command:     .venv\Scripts\python.exe scripts/statistical_analytical_analysis.py
Exit status: 0
Runtime:     40.8 seconds
Peak memory: 736.1 MB
Result:      "Statistical and analytical analysis completed successfully."
```

The peak is dominated by the rank-based Mann-Whitney test over the corrected,
much larger unpromoted group; the aggregation alone peaks at 483.4 MB
(imports included) and the previously retained 594.5 MB analysis frame no
longer exists.

### Verification of the rewrite

The streaming implementation was run against the unmodified dataset and
compared with the previous artifacts before any source fix:

| Artifact | Comparison with the previous implementation |
|---|---|
| `statistical_summary.csv` | identical |
| `statistical_store_analysis.csv` | identical |
| `statistical_autocorrelation.csv` | identical |
| `statistical_category_analysis.csv` | identical (182 rows) |
| `statistical_correlations.csv` | observation counts identical; r agrees to 1.3e-13 relative |
| `statistical_price_demand.csv` | slope identical; intercept agrees to 9.7e-16 relative |
| `statistical_trend.csv` | identical (plus new HAC columns) |
| `statistical_promotion_analysis.csv` | changed deliberately (F2) |

After the Phase 6 source fix the pipeline was re-run: the promotion artifact is
byte-identical, the correlation and aggregate values differ only in the 15th
to 16th significant digit (summation order), and the only quality-report
changes are the two guard counters, which moved from 22 missing / 6,760
infinite to 6,782 missing / 0 infinite with reconciliation still true.

### Generated-file verification

| File | Exists | Size | Structure | Validation |
|---|---|---|---|---|
| `statistical_summary.csv` | yes | 376 B | 12 metric rows | values reconcile with Phase 6 and Phase 7 |
| `statistical_correlations.csv` | yes | 959 B | 9 rows, 6 columns | sorted by absolute correlation; covariance added; 9 of 9 in range |
| `statistical_store_analysis.csv` | yes | 273 B | 4 stores | shares sum to 1.0 |
| `statistical_category_analysis.csv` | yes | 7,711 B | 182 rows | matches Phase 7's category summary |
| `statistical_price_demand.csv` | yes | 151 B | 1 row | slope, intercept and R-squared verified against scipy `linregress` |
| `statistical_promotion_analysis.csv` | yes | 575 B | 4 rows, 8 columns | both comparisons and their tests |
| `statistical_autocorrelation.csv` | yes | 338 B | 14 integer lags | matches pandas `autocorr` |
| `statistical_trend.csv` | yes | 259 B | 1 row, 9 columns | OLS values match `linregress`; HAC values finite |
| `statistical_monthly_activity.csv` | yes | 1,516 B | 26 months | monthly records and totals reconcile with the daily grain |
| `statistical_quality_report.csv` | yes | 1,740 B | 56 metric rows | all reconciliation flags true |
| `statistical_findings.txt` | yes | 2,913 B | 6 sections | no `p=0.0`, no float artefacts, integer lags |
| 4 figures | yes | 21-140 KB | 1800x900 / 1500x900 | regenerated; scatter labelled as a systematic sample |

### Documentation changes

All six Phase 8 documents were rewritten under their existing headings, and the
cross-phase records listed under "Files reviewed" were synchronised, including
the two numbers in the Phase 7 documents that the Phase 6 fix changed.

### Remaining issues

- None open for Phase 8. The Phase 6 zero-denominator issue flagged by Phase 7
  was fixed at source in this pass and verified analytically neutral.
- `requirements.txt` is now pinned to the verified environment, closing the
  reproducibility issue Phase 7 raised.
- The 2023-11 to 2023-12 level shift is now diagnosed as a coverage and
  assortment change; handling it in forecasting is Phase 9-12 work and is
  recorded under Forecasting implications.
