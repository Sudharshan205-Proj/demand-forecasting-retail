# Phase 8 — Statistical & Analytical Results

## Source

`data/processed/integrated_retail_data.csv` (produced by Phase 6).

Every reported statistic is calculated from the complete dataset; no reported
value comes from a sample. The integrated dataset guards both derived-rate
denominators, so it contains no infinite value in `promo_discount_rate` or
`markdown_discount` ([`../phase-6/integration-results.md`](../phase-6/integration-results.md)).

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

## Results

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
daily grain covers every calendar day in the range with no gap.

### Descriptive statistics of daily demand

| Metric | Result |
|---|---:|
| Mean daily quantity | 55,124.218 |
| Median daily quantity | 44,753.823 |
| Standard deviation | 19,326.148 |
| Minimum | 19,345.758 |
| Maximum | 154,068.882 |
| Coefficient of variation | 0.351 |

The coefficient of variation of 0.35 means daily demand varies by roughly a third
of its mean, and the mean sits well above the median: the distribution is
right-skewed by high-demand days.

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

The only strong linear association with physical demand is `markdown_quantity`
(r = 0.698 over 8,709 rows that carry a markdown record). Online quantity
correlates moderately (r = 0.303), but online demand is a separate channel and is
never added to physical demand. All remaining coefficients are weak — below
|0.07| — which means price, promotion and assortment-change counts explain very
little of row-level demand variation.

These values agree with the Phase 7 EDA correlation matrix to 15 significant
figures, which cross-validates both implementations.

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
variation. This is an analytical association, **not** a causal price elasticity,
and it is not estimated on a controlled price experiment.

### Promotion comparison

The primary comparison follows the phase plan: records with a discount record are
compared with records without one. The secondary breakdown splits the promoted
records by the sign of the finite discount rate.

| Comparison | Group | Observations | Mean quantity | Median quantity | Mean discount rate |
|---|---|---:|---:|---:|---:|
| Presence | `promotion_record_present` | 1,518,622 | 5.951 | 2 | 0.187495 |
| Presence | `promotion_record_absent` | 5,912,404 | 5.567 | 2 | — |
| Rate sign | `promotion_rate_positive` | 1,215,172 | 5.364 | 2 | 0.233879 |
| Rate sign | `promotion_rate_non_positive` | 296,668 | 8.362 | 3 | -0.002495 |

- Presence comparison: Mann-Whitney U = 4.959047e+12, p < 1e-300.
- Rate-sign comparison: Mann-Whitney U = 1.675299e+11, p < 1e-300.

Demand is higher on promoted rows (mean 5.951 versus 5.567; median equal at 2),
but the difference is small relative to the spread of the data. Within the
promoted rows the pattern reverses: rows whose discount rate is positive have
*lower* mean demand (5.364) than rows with a non-positive rate (8.362).

This is not evidence that promotions reduce demand. Promotion selection is not
random: discounts are placed on fast-selling or clearance items, and rows with a
non-positive rate mostly carry a markdown rather than a promotion. Both
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

Aggregate daily demand trends upwards by about 67 quantity units per day, and a
linear trend explains 58% of daily variation. Because daily demand is strongly
autocorrelated, the naive OLS standard error (2.07) understates uncertainty; the
Newey-West (HAC) standard error is 4.30, roughly double. The trend remains
statistically significant under the robust measure, but it is not purely organic
demand growth — see the level-shift finding below.

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

Store 1 carries 55% of demand, and store 4, active only from 2023-12, already
carries 22%. The department table covers 182 groups, led by Auxiliary Group
(3,111,278) and Bread (2,735,210); the 36,580 rows with no catalog match form
their own unmatched group (319,500 quantity, 0.76% of demand).

Store and department comparisons are reported descriptively. They are not tested
for significance because the store groups contain only four units and because
department rows are far from independent; with millions of observations a
significance test would add no information beyond the magnitudes shown here.

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
- distinct items per month rise from about 12,500–13,700 (2023) to about
  14,500–15,400 (2024);
- monthly rows rise from about 228,000 to about 350,000–425,000, while quantity
  per row stays near 5.5–6.0 throughout.

The change is present in the raw source data, not created by the pipeline:
`data/raw/sales.csv` contains store 4 only from **2023-12-13** onward, while
stores 1-3 span the full range 2022-08-28 to 2024-09-26.

### Quality report

`statistical_quality_report.csv` contains 56 metrics and evidences the checks the
quality framework requires. All reconciliation flags are true:

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

The interpretations distinguish:

- statistical significance from practical significance — with 7.43 million rows,
  p < 1e-300 is reached by coefficients as small as 0.0015, so magnitude, not
  significance, decides importance;
- association from causation — the price and promotion results are observational
  group differences that selection effects can explain;
- an underflowed p-value from a meaningful one — probabilities below 1e-300 are
  reported as `< 1e-300`, because a probability of exactly zero is not a valid
  statistical statement.

## Forecasting implications

- **Weekly seasonality is the strongest signal.** Lag 7 and lag 14
  autocorrelation (0.874 / 0.885) is comparable to lag 1 (0.882) and much higher
  than lag 5-6, so the Phase 9–12 models need weekly terms.
- **Strong short-run autocorrelation** means naive random train/test splits would
  leak; temporal splits and differencing are required.
- **The trend must not be read as organic growth.** Because store 4 enters on
  2023-12-13 and assortment grows, any model trained across the break can learn
  coverage as trend.
- **Price and promotions are weak row-level predictors.** They contribute little
  to explaining row-level quantity, so the forecasting design relies on temporal
  structure rather than these covariates.
- **Assortment items differ enormously in magnitude**, so aggregate error metrics
  should be complemented by per-item evaluation. The forecasting phases operate
  at the store-day grain, so no per-item evaluation exists; this is a recorded
  limitation.
- The Phase 9 time-series preparation quantified the gap structure: 55,122 of
  58,022 item-store series contain intermediate date gaps (12,553,017 missing
  intermediate days), so the temporal splits are contiguous by date while
  individual series remain sparse.

## Limitations

- The dataset is observational; no causal price elasticity can be estimated.
- The trend is described by a linear fit, which is a summary and not a forecast.
- Trend significance is autocorrelation-robust (Newey-West), but the fit itself
  is not a time-series model.
- The price/demand scatter figure uses a deterministic systematic sample (1 per
  37 eligible rows, 200,839 points) so that it spans the whole date range; every
  reported statistic uses the complete dataset.
- Department and store differences are descriptive only.
