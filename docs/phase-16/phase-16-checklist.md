# Phase 16 — Application Development & Deployment Checklist

## Status

**COMPLETE (local)** — application development, testing, documentation and
local deployment validation are done. The three unticked boxes below are all
part of one outstanding workstream: the hosted public deployment, which
remains pending owner authorisation.

Every ticked box is backed by a named test, a recorded command or an
inspection whose result is recorded in `application-results.md`,
`deployment-validation.md` or `docs/phase-17/re-audit-record.md`.

## Application Development

- [x] Application architecture reviewed
- [x] Streamlit application implemented
- [x] Application configuration implemented
- [x] Data loading separated from presentation
- [x] Formatting helpers implemented
- [x] Logging implemented
- [x] Store selection implemented
- [x] Inventory scenario controls implemented
- [x] Forecast evaluation displayed
- [x] Model configuration displayed
- [x] Per-store model evidence derived from the Phase 12 tables
- [x] Store 4's single-fold model evidence displayed as a caveat
- [x] Scenario assumptions displayed

## Testing

- [x] Application support tests pass (36 of 36)
- [x] Application imports successfully without a Streamlit runtime
- [x] No Streamlit call runs at module scope
- [x] Streamlit starts successfully (headless, HTTP 200)
- [x] Required artifacts load successfully
- [x] Store selection works
- [x] Scenario filtering works
- [x] Error handling works (missing artifacts named before failing)
- [x] Artifact resolution order covered, including the bundle fallback
- [x] Deployment bundle reconciled against the pipeline output
- [x] Full project suite passes (530 tests, 1 warning)

## Deployment

- [x] Deployment target selected (Streamlit Community Cloud)
- [x] Deployment configuration documented
- [x] Deployment configuration committed (`.streamlit/config.toml`,
      `.python-version`, `requirements.txt`)
- [x] Runtime artifacts committed so a repository build can start
      (`deploy/artifacts/`, 14,977 bytes)
- [x] Secrets review completed (none required; asserted by a test)
- [x] Local deployment executed and validated
- [ ] Hosted deployment executed
- [ ] Deployment URL verified
- [ ] Deployed application validated

## Documentation

- [x] Application development plan
- [x] Application architecture
- [x] Application quality framework
- [x] Deployment plan
- [x] Deployment validation
- [x] Course-content coverage
- [x] Application results
- [x] Deployment bundle README
- [x] README updated
- [x] Persistent project state updated — that running state log was later
      consolidated into `docs/project-status.md`
- [x] Project file-update register updated — that register was later
      consolidated into `docs/project-status.md`

## Git

- [x] Phase branch created
- [x] Changes reviewed
- [x] Correct files staged
- [x] Phase commit created
- [x] Branch pushed
- [x] Remote branch verified
- [x] Audit changes committed and pushed
- [x] `git status` reviewed: no unintended files staged; the two root
      reference documents remain untracked by design, and `.freebuff/` is
      gitignored

## Phase 17 Re-Audit Record

Moved to the consolidated [Phase 17 Re-Audit Record](../phase-17/re-audit-record.md).
