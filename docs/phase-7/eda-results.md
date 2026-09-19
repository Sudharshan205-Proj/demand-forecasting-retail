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
| Missing `promo_discount_rate` | 5,919,186 |
| Rows with a discount record | 1,518,622 |
| Rows with a markdown record | 8,709 |
| Rows with non-finite values (`infinite_promo_discount_rate`) | 0 |

Missing promotion and markdown values mean that no matching auxiliary record
exists for that date, item and store after the Phase 6 left joins. They are
not cleaning failures.

Both counters changed when the Phase 8 re-audit guarded the two zero
denominators in Phase 6: 6,760 values that were infinite are now missing, so
`missing_promo_discount_rate` moved from 5,912,426 to 5,919,186 and
`infinite_promo_discount_rate` from 6,760 to 0. Two `markdown_discount` values
changed in the same way. No other metric in this document is affected.

Promotion and markdown frequency is reported from
`discount_record_count > 0` and `markdown_record_count > 0` rather than from
null values, so the counts stay correct even where an aggregated value is
itself unusable. The 22-row difference between the discount-record count
(1,518,622) and the non-missing rate count (1,518,600) is explained under
"Non-finite values" in the Phase 7 record at
`docs/phase-17/re-audit-record.md`.

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
- Phase 8's promotion comparison over the same data reports a slightly higher
  mean quantity on rows that carry a discount record (5.95, median 2,
  n = 1,518,622) than on rows without one (5.57, median 2, n = 5,912,404), and
  within the promoted rows a lower mean on rows with a positive discount rate
  (5.36, median 2, n = 1,215,172) than on rows with a non-positive rate (8.36,
  median 3, n = 296,668). The rate-sign figures are the ones consistent with
  the weak negative association observed here; the presence comparison shows
  that the difference between promoted and unpromoted rows is small relative
  to the spread of the data.
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
label instead of failing to plot; see the Phase 7 record in
`docs/phase-17/re-audit-record.md`.

## Forecasting implications

- Only 26 months of history across 4 stores. The series is short, so simple
  regularised models are likely to be more reliable than complex ones.
- The level shift between 2023-11 and 2023-12 is a **documented coverage and
  assortment change rather than demand growth**, as the Phase 8 re-audit
  established: `data/raw/sales.csv` contains store 4 only from 2023-12-13,
  distinct stores per month rise from 3 to 4 in 2023-12, distinct items per
  month rise from about 12,600 to about 15,400, and quantity per row stays near
  5.5-6.0 throughout. Models trained across the break can still learn the
  coverage change as a spurious trend, so it must be handled deliberately.
- Item-level concentration means a handful of items dominate aggregate error
  metrics; forecast quality should be reported for representative items as
  well as for aggregate demand.
- Promotion and markdown coverage is sparse and only weakly associated with
  demand, so promotional flags are not automatically strong predictors.
- Demand differs materially by store, so store-level effects should be
  available to the modelling phases.
- Phase 7 introduces no temporal leakage: the phase is descriptive and
  creates no predictors or forward-looking features.

- **Phase 9 quantified the temporal gap structure.** The prepared
  time-series dataset keeps 7,431,026 observed date-item-store records across
  58,022 item-store series, of which 55,122 contain at least one intermediate
  date gap (12,553,017 missing intermediate days). Calendar-based lag windows
  therefore need an explicit densification decision before they can be used.

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

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
