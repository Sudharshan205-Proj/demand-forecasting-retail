# Phase 9 — Time-Series Preparation Methodology

## Source

The integrated retail dataset from Phase 6 is used as the source.

## Aggregation

Sales records are aggregated to:

`date + item_id + store_id`

with:

`quantity = sum(quantity)`

This produces a forecasting-oriented daily demand series.

## Chronology

Dates are explicitly parsed as datetime values.

Each item-store series is sorted chronologically.

## Duplicate handling

The date-item-store key must be unique after aggregation.

Any remaining duplicate keys indicate an implementation error and stop the
workflow.

## Temporal gaps

The difference between consecutive observed dates is calculated within each
item-store series.

A gap greater than one day indicates one or more missing intermediate
calendar dates.

The workflow reports these gaps instead of silently filling them.

## Train/validation/test split

The complete observed date range is ordered chronologically.

The first 70% of unique dates forms training data.

The next 15% forms validation data.

The final 15% forms test data.

## Leakage control

No random sampling is performed.

No future date can be assigned to training or validation when it belongs to
a later chronological partition.

## Online channel

Online demand remains separate from physical-store demand.

It is not added to the physical demand target.

## Forecasting boundary

This phase prepares the temporal dataset only.

Feature engineering and model development are subsequent stages.