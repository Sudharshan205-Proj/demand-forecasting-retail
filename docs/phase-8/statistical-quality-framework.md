# Phase 8 — Statistical Quality Framework

## Data integrity

The analysis must preserve:

- row counts;
- total quantity;
- total revenue;
- date coverage.

The source integrated dataset must not be modified.

## Schema validation

The following fields are mandatory:

- date
- item_id
- quantity
- price_base
- sum_total
- store_id

Optional analytical variables are used only when present.

## Numerical validation

The analysis must check:

- finite numerical results;
- absence of unexpected division-by-zero behaviour;
- sufficient observations for statistical tests;
- valid correlation ranges;
- valid p-values;
- valid regression outputs.

## Temporal validation

Dates must be parsed successfully and sorted chronologically before
temporal analysis.

No random shuffling is performed.

## Statistical validity

Tests must only be calculated where sufficient observations exist.

Statistical significance must not be confused with practical significance.

Correlation must not be presented as causation.

## Reproducibility

The statistical workflow must be deterministic and executable from the
repository root.

## Output validation

Generated CSV files must:

- contain column headers;
- contain valid records;
- use consistent naming;
- be reproducible from the source dataset.

Generated figures must correspond to the documented analysis.

## Limitations

The dataset does not establish causal relationships between price,
promotions and demand.

Observed relationships may be affected by unobserved variables,
assortment changes, store differences and temporal effects.