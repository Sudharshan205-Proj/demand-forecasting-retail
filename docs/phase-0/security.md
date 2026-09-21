# Security and Data Handling

## Principles

Security and data handling are project-wide requirements.

## Secrets

The repository does not contain:

- API keys
- Passwords
- Tokens
- Credentials
- Private keys
- Service-account credentials

A scan of tracked files returns only empty `password=''` Tableau connection
attributes, and a test asserts that the application source contains no secrets.

## Environment variables

Secrets required by tools or deployment infrastructure are provided through
environment configuration. The application requires no secrets; its artifact
directory is read from `APP_ANALYSIS_DIR` when set.

## Git

`.gitignore` excludes `.env`, key material, credentials and generated databases
while retaining the data-directory placeholders.

## Data

The project uses a single appropriately sourced public dataset (CC BY-NC-SA
4.0). Raw data is treated as immutable.

## Privacy

The dataset contains no personally identifiable information, so no PII handling
is required. The data-handling rationale is recorded in
[`../phase-2/data-ethics-and-privacy.md`](../phase-2/data-ethics-and-privacy.md).

## Logs

Logs do not expose credentials, tokens, sensitive user information or private
configuration.

## Application

The deployed application exposes only the functionality required for
forecasting and inventory scenario review.

## Data integrity

Raw data is preserved and treated as immutable; all processing runs through the
documented pipelines.

## Dependencies

Dependencies are kept to the set the project actually uses and are pinned in
`requirements.txt`.

## Deployment

Deployment configuration contains no hardcoded secrets.
