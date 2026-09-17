# Phase 8 — Statistical & Analytical Analysis Checklist

## Objective

Quantify demand relationships, variability, trends and statistical evidence
that can inform later demand-forecasting decisions.

## Analysis

- [x] Define statistical questions.
- [x] Calculate descriptive statistics.
- [x] Calculate coefficient of variation.
- [x] Calculate demand trend (ordinary least squares plus Newey-West robust
      inference).
- [x] Calculate Pearson correlations.
- [x] Calculate sample covariance.
- [x] Calculate price-demand relationship (correlation and simple regression).
- [x] Analyse promotional relationships (presence comparison and rate-sign
      breakdown, each with a Mann-Whitney U test).
- [x] Calculate demand autocorrelation.
- [x] Perform statistical significance testing.
- [x] Interpret practical significance separately from statistical
      significance (p-value floor and magnitude commentary in
      `statistical_findings.txt`).
- [x] Document correlation-versus-causation limitations.
- [x] Diagnose the 2023-11 to 2023-12 level shift
      (`statistical_monthly_activity.csv`; coverage change confirmed against
      `data/raw/sales.csv`).

## Engineering

- [x] Process the integrated dataset in chunks (100,000 rows; measured 483.4 MB
      peak for the aggregation, no retained analysis frame).
- [x] Preserve the source dataset.
- [x] Preserve chronological ordering.
- [x] Use deterministic analysis.
- [x] Avoid unnecessary dependencies (`numpy`, `pandas`, `scipy`,
      `matplotlib` and the already-declared `statsmodels`).
- [x] Add unit tests (46 tests; 10 replaced).
- [x] Validate generated outputs (`statistical_quality_report.csv`, 56 metrics).

## Documentation

- [x] Statistical analysis plan.
- [x] Statistical methodology.
- [x] Statistical quality framework.
- [x] Statistical results (verified values recorded).
- [x] Course-content coverage.
- [x] README update.
- [x] Project-state update.
- [x] Project-file update register update.
- [x] Cross-phase synchronisation (curriculum mapping, requirements
      traceability, dataset inventory, Phase 6 and Phase 7 records,
      `requirements.txt`).

## Git

- [ ] Create Phase 8 branch.
- [ ] Review changes.
- [ ] Stage intended files.
- [ ] Commit once at phase completion.
- [ ] Push branch.
- [ ] Verify remote branch.
- [ ] Verify clean working tree.

The Git section is not exercised by the Phase 17 audit workflow: this
repository is audited in place and the audit runs no Git commands, so no
branch, commit or push is created for the re-audit. The section is left
unticked deliberately rather than claimed.
