# Phase 8 — Statistical Quality Framework

## Data integrity

The analysis must preserve:

- row counts;
- total quantity;
- total revenue;
- date coverage.

The source integrated dataset must not be modified.

All four are now asserted by `data/analysis/statistical_quality_report.csv`:
`rows_read`, `daily_record_rows`, `total_quantity`, `total_revenue`,
`date_min`, `date_max`, `calendar_days` and `missing_calendar_days`, together
with `monthly_records_reconciled`, `quantity_reconciled` and
`revenue_reconciled`. The verified execution reports 7,431,026 rows,
41,949,529.910 quantity, 5,659,219,309.900 revenue, 2022-08-28 to 2024-09-26
and 0 missing calendar days.

## Schema validation

The following fields are mandatory:

- date
- item_id
- quantity
- price_base
- sum_total
- store_id

Optional analytical variables are used only when present. Each analytical
variable is coerced to numeric, and values that cannot be coerced become
missing rather than silently removing the variable from the analysis.

## Numerical validation

The analysis must check:

- finite numerical results;
- absence of unexpected division-by-zero behaviour;
- sufficient observations for statistical tests;
- valid correlation ranges;
- valid p-values;
- valid regression outputs.

These checks are recorded as `regression_outputs_finite`,
`autocorrelation_outputs_finite`, `trend_outputs_finite`,
`correlations_in_valid_range`, `correlations_not_computed`,
`minimum_observations_required` and `p_values_underflowed`. The verified
execution reports all output-finiteness flags true, 9 of 9 correlations in
range and 5 underflowed p-values, which the findings file and the
documentation report as `< 1e-300`.

Division by zero in derived rates is guarded at its source in Phase 6: the
integration report records `undefined_markdown_discount_records` and
`undefined_promo_discount_rate_records`, and the integrated dataset contains
0 infinite values in `promo_discount_rate` and `markdown_discount`.

## Statistical validity

Tests must only be calculated where sufficient observations exist.

Statistical significance must not be confused with practical significance.

Correlation must not be presented as causation.

Additional rules applied and documented:

- a variable with no usable variation (variance indistinguishable from zero
  relative to its own scale) yields an undefined correlation rather than a
  meaningless coefficient;
- the trend is reported with autocorrelation-robust (Newey-West) standard
  errors because OLS inference is invalid for autocorrelated daily demand;
- store and department comparisons are descriptive only, with the reason
  stated;
- both promotion comparisons are labelled, and their groups are asserted to
  partition the eligible rows.

## Temporal validation

Dates must be parsed successfully and sorted chronologically before
temporal analysis.

No random shuffling is performed.

Invalid dates are counted (`invalid_date_rows`, verified as 0) and excluded
from the temporal grains. The daily grain covers 761 of 761 calendar days in
the range, so the series has no gap.

## Reproducibility

The statistical workflow must be deterministic and executable from the
repository root.

Dependencies are pinned in `requirements.txt` to the verified environment so
that version-dependent statistical behaviour is reproducible.

## Output validation

Generated CSV files must:

- contain column headers;
- contain valid records;
- use consistent naming;
- be reproducible from the source dataset.

Generated figures must correspond to the documented analysis.

Verified for 10 CSVs, the findings file and 4 figures. Every reported
statistic uses the complete dataset; the only sampled output is the
price/demand figure, whose deterministic systematic sample (1 per 37 eligible
rows, 200,839 points) is recorded in the quality report and stated in the
figure.

## Limitations

The dataset does not establish causal relationships between price,
promotions and demand.

Observed relationships may be affected by unobserved variables,
assortment changes, store differences and temporal effects.

A documented example is the 2023-12 level shift, which
`statistical_monthly_activity.csv` and the raw source data show to be a
coverage and assortment change (store 4 first appears on 2023-12-13) rather
than demand growth.

## Phase 17 re-audit record

The framework was written before the analysis existed and was not evidenced by
any artifact. During the Phase 17 re-audit:

- `data/analysis/statistical_quality_report.csv` was added and now evidences
  every check listed above (56 metrics);
- the promotion definition was corrected so that the labelled groups match the
  documented comparison;
- non-finite handling was made consistent across all statistics;
- the p-value underflow rule was documented and applied to the findings file;
- dependency pinning closed the reproducibility gap.
