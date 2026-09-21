# Phase 8 — Statistical Quality Framework

## Data integrity

The analysis preserves row counts, total quantity, total revenue and date
coverage, and never modifies the source integrated dataset.

These are asserted by `data/analysis/statistical_quality_report.csv`
(`rows_read`, `daily_record_rows`, `total_quantity`, `total_revenue`,
`date_min`, `date_max`, `calendar_days`, `missing_calendar_days`, together with
`monthly_records_reconciled`, `quantity_reconciled` and `revenue_reconciled`).
The execution reports 7,431,026 rows, 41,949,529.910 quantity,
5,659,219,309.900 revenue, 2022-08-28 to 2024-09-26 and 0 missing calendar days.

That file is a **metric/value validation report** (56 rows, no `passed` column)
rather than a run gate: it records what was measured so the figures in
[`statistical-results.md`](statistical-results.md) are reproducible from a single
file, while the assertions themselves are enforced by
`tests/test_statistical_analytical_analysis.py`. It is excluded from the
run-gating quality total, which counts only the reports that gate a run.

## Schema validation

The mandatory fields are date, item_id, quantity, price_base, sum_total and
store_id. Optional analytical variables are used only when present. Each
analytical variable is coerced to numeric, and values that cannot be coerced
become missing rather than silently removing the variable from the analysis.

## Numerical validation

The analysis checks finite numerical results, the absence of unexpected
division-by-zero behaviour, sufficient observations for statistical tests, valid
correlation ranges, valid p-values and valid regression outputs.

These checks are recorded as `regression_outputs_finite`,
`autocorrelation_outputs_finite`, `trend_outputs_finite`,
`correlations_in_valid_range`, `correlations_not_computed`,
`minimum_observations_required` and `p_values_underflowed`. The execution reports
all output-finiteness flags true, 9 of 9 correlations in range and 5 underflowed
p-values, which the findings file and the documentation report as `< 1e-300`.

Division by zero in derived rates is guarded at its source in Phase 6: the
integration report records `undefined_markdown_discount_records` and
`undefined_promo_discount_rate_records`, and the integrated dataset contains 0
infinite values in `promo_discount_rate` and `markdown_discount`.

## Statistical validity

Tests are calculated only where sufficient observations exist. Statistical
significance is not confused with practical significance, and correlation is not
presented as causation.

Additional rules:

- a variable with no usable variation (variance indistinguishable from zero
  relative to its own scale) yields an undefined correlation rather than a
  meaningless coefficient;
- the trend is reported with autocorrelation-robust (Newey-West) standard errors
  because OLS inference is invalid for autocorrelated daily demand;
- store and department comparisons are descriptive only, with the reason stated;
- both promotion comparisons are labelled, and their groups are asserted to
  partition the eligible rows.

## Temporal validation

Dates are parsed successfully and sorted chronologically before temporal
analysis, and no random shuffling is performed.

Invalid dates are counted (`invalid_date_rows`, 0) and excluded from the temporal
grains. The daily grain covers 761 of 761 calendar days in the range, so the
series has no gap.

## Reproducibility

The statistical workflow is deterministic and executable from the repository
root. Dependencies are pinned in `requirements.txt` to the verified environment so
that version-dependent statistical behaviour is reproducible.

## Output validation

Generated CSV files contain column headers, valid records, consistent naming and
are reproducible from the source dataset. Generated figures correspond to the
documented analysis.

This holds for 10 CSVs, the findings file and 4 figures. Every reported statistic
uses the complete dataset; the only sampled output is the price/demand figure,
whose deterministic systematic sample (1 per 37 eligible rows, 200,839 points) is
recorded in the quality report and stated in the figure.

## Limitations

The dataset does not establish causal relationships between price, promotions and
demand. Observed relationships may be affected by unobserved variables,
assortment changes, store differences and temporal effects. A documented example
is the 2023-12 level shift, which `statistical_monthly_activity.csv` and the raw
source data show to be a coverage and assortment change (store 4 first appears on
2023-12-13) rather than demand growth.
