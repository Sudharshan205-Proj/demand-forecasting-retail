# Phase 12 — Model Evaluation & Tuning Checklist

## Objective

Evaluate and tune the Phase 11 forecasting approaches without using
the test period for model selection or tuning.

## Checklist

- [ ] Create Phase 12 Git branch.
- [ ] Verify Phase 11 state.
- [ ] Verify chronological train/validation/test boundaries.
- [ ] Implement time-series cross-validation.
- [ ] Tune Naive baseline.
- [ ] Tune Seasonal Naive season length.
- [ ] Tune ARIMA order configurations.
- [ ] Record all candidate configurations.
- [ ] Record cross-validation metrics.
- [ ] Select configurations using training-period CV.
- [ ] Evaluate selected configurations on validation.
- [ ] Perform store-level error analysis.
- [ ] Preserve the test period as unseen data.
- [ ] Create automated tests.
- [ ] Execute the evaluation script.
- [ ] Validate generated artifacts.
- [ ] Update Phase 12 documentation.
- [ ] Update README.
- [ ] Update project state.
- [ ] Update file-update register.
- [ ] Update course-content coverage.
- [ ] Verify generated artifacts are ignored.
- [ ] Review Git changes.
- [ ] Commit Phase 12.
- [ ] Push Phase 12 branch.
- [ ] Verify clean repository state.

## Completion Criteria

Phase 12 is complete only when:

1. All required tests pass.
2. Cross-validation executes successfully.
3. Configurations are selected without using test data.
4. Validation results are produced.
5. Error analysis is produced.
6. Documentation matches the implementation.
7. Git status is clean after the phase commit.
8. The Phase 12 branch is pushed successfully.