# Phase 6 — Data Integration

## Purpose

Phase 6 integrates the cleaned sales dataset with the seven supporting sources on
the canonical `date + item_id + store_id` grain, producing the 34-column
analytical matrix the later phases consume.

## What the phase delivered

| Deliverable | Content |
|---|---|
| Integrated dataset | `data/processed/integrated_retail_data.csv` — 7,431,026 rows, 34 columns, 1,283,859,491 bytes, byte-identical on re-execution |
| Quality report | `data/processed/integration_quality_report.csv` |
| Pipeline | `scripts/integrate_retail_data.py` |
| Tests | `tests/test_integrate_retail_data.py` — 24 tests |

## Integration decisions

- Store and catalog dimensions are joined many-to-one; catalog uses a left join so
  unmatched sales rows survive.
- Price, markdown, promotion and online records are aggregated to the canonical
  grain before joining.
- Online demand is carried in separate columns and never added to physical demand.
- The actual matrix becomes an exact-key indicator.
- Both derived rate columns guard their denominators, so no rate is infinite.

## Key results

| Metric | Result |
|---|---:|
| Integrated rows | 7,431,026 |
| Row-count difference | 0 |
| Duplicate canonical-grain rows | 0 |
| Unknown store rows | 0 |
| Unmatched catalog rows | 36,580 (948 distinct items, retained) |
| Unique items / stores | 28,180 / 4 |
| Total demand quantity | 41,949,529.91 |
| Total sales revenue | 5,659,219,309.90 |
| Undefined promo discount rates (reported) | 6,782 promoted rows |

## Course coverage

Phase 6 carries the **Process** stage's integration half: multi-source
integration, joins, join cardinality, aggregation and data validation
([`course-content-coverage.md`](course-content-coverage.md)).

## Related documents

- [`integration-methodology.md`](integration-methodology.md) — method
- [`integration-quality-framework.md`](integration-quality-framework.md) — quality practices
- [`integration-results.md`](integration-results.md) — results
