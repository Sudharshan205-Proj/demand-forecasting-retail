# Phase 7 — Exploratory Data Analysis Plan

## Purpose

Phase 7 explores the integrated retail dataset to identify demand patterns,
relationships, distributions, anomalies, and forecasting-relevant behaviour.

The analysis is descriptive and does not train forecasting models.

## Primary dataset

`data/processed/integrated_retail_data.csv`

## Analytical grain

The integrated dataset preserves:

`date + item_id + store_id`

as the canonical sales grain.

## EDA questions

### Overall demand

* How much demand is represented?
* What is the total revenue?
* How many stores and items are represented?
* What is the temporal coverage?

### Temporal behaviour

* How does demand change over time?
* Which months have higher or lower demand?
* Are there visible seasonal or trend-like patterns?

### Store behaviour

* Which stores generate the most demand?
* How different are store demand levels?

### Product behaviour

* Which departments contribute the most demand?
* Which products have the highest aggregate demand?
* Is demand concentrated among a small number of products?

### Price behaviour

* How does price vary?
* Is there an observable relationship between price and quantity?

### Promotion behaviour

* How frequently do promotion records occur?
* How does demand behave during promotion activity?

### Markdown behaviour

* How frequently are markdown records present?
* Is markdown activity associated with unusual demand patterns?

### Online channel

Online quantity and sales value are examined separately.

They are not added to the physical sales target.

## Analysis outputs

* Overall EDA summary
* Monthly demand summary
* Store summary
* Department summary
* Top-item summary
* Correlation summary
* Item-level distribution and concentration summary
* Promotion and markdown record frequency
* Descriptive findings
* Exploratory visualizations

## Interpretation rule

EDA findings describe associations and patterns.

They do not establish causation.

## Reproducibility

The complete analysis is executed by:

`scripts/exploratory_data_analysis.py`

The script uses no sampling and no random seed. Correlation is calculated
from the complete integrated dataset using chunked pairwise moments, so the
output is deterministic for a given input file and does not depend on the
random-number behaviour of the installed pandas version.

## Phase 17 Re-Audit Record

**Audit status:** AUDITED — COMPLETE

Changes applied during the re-audit, recorded against the sections above:

* **Analysis outputs** — the item-level distribution and concentration
  summary and the promotion/markdown record frequency are now produced as
  `eda_summary.csv` metrics and appear in `eda_findings.txt`. They answer the
  "Is demand concentrated among a small number of products?" and
  "How frequently do promotion/markdown records occur?" questions, which
  previously had no implemented output.
* **Reproducibility** — the original plan stated that the script "uses a
  fixed random seed when sampling data for correlation analysis". Sampling
  was removed, so that statement was replaced. The change was justified by
  measurement: the sample gave equal weight to every chunk regardless of its
  size and reused one seed per chunk, and its coefficients differed from the
  exact full-dataset values by up to 0.179, including a sign change on one
  pair.
* **Anomalies, distributions and relationships** — no EDA question was
  removed, added or reworded. Unusual demand is now identified at item level
  (interquartile-range upper fence) without removing any observation, which is
  how the phase purpose and the methodology already described it.

Verification: 34 Phase 7 tests and 193 tests overall pass; the pipeline ran
to completion in 61-63 seconds and every artifact was verified.
