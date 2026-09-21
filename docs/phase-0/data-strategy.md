# Data Strategy

## Objective

Identify the data required to forecast retail demand and investigate demand
drivers, and record what the selected dataset provides.

## Required core data

### Sales

The sales data provides:

- Date
- Product identifier
- Store identifier
- Quantity sold (the demand target)
- Price
- Revenue

### Promotions

The dataset provides promotion and markdown records (`markdowns.csv`,
`discounts_history.csv`): promotion type, discount amounts and dates.

### Holidays

No holiday field exists in the dataset. Holiday analysis is recorded as not
applicable, and the requirement was conditional on availability.

## Optional supporting variables

The selected dataset provides store characteristics (`stores.csv`), product
category and type (`catalog.csv`), and an online sales channel (`online.csv`).
Weather, events and season indicators are not present and were not used.

Additional variables are used only where they are relevant and appropriately
sourced.

## Data source requirements

The source is assessed against:

- Reliability
- Originality
- Comprehensiveness
- Currency
- Citation

These correspond to the course's ROCCC data-quality framework and are recorded
in [`../phase-2/data-source-assessment.md`](../phase-2/data-source-assessment.md).

## Dataset selection criteria

The selected dataset:

1. Contains meaningful temporal coverage (2022-08-28 → 2024-09-26).
2. Contains sufficient observations for time-series analysis (7,432,685 raw
   sales rows).
3. Provides a clear demand target (`quantity`).
4. Allows aggregation at a meaningful retail level (date × item × store).
5. Supports historical/future separation through chronological splits.
6. Is legally and ethically appropriate to use (CC BY-NC-SA 4.0).
7. Has sufficient documentation.
8. Allows reproducible analysis.

## Data privacy

The project uses a public dataset. It contains no personally identifiable
information; the data-handling rules are recorded in
[`../phase-2/data-ethics-and-privacy.md`](../phase-2/data-ethics-and-privacy.md).

## Data versioning

The project documents the source, download date, dataset version where
available, file names, file sizes, license and known limitations in
[`../phase-2/dataset-inventory.md`](../phase-2/dataset-inventory.md) and
[`../phase-2/data-dictionary.md`](../phase-2/data-dictionary.md).

## Data storage

Raw data remains immutable. Processed datasets are generated through the
documented processing pipelines. Large datasets are not committed to Git; the
only committed data is the seven-file `deploy/artifacts/` bundle that lets the
application start.

## Data quality

The project inspects dimensions, columns, data types, missing values, duplicate
records, date range, chronological ordering, target distribution, invalid values
and outliers in Phases 2, 5 and 7.

## Data leakage

Time-series data preserves temporal order. Future information is never allowed
to influence historical training observations; lag and rolling features are
shifted, and the reserved test period is never read.
