# Security and Data Handling

## Principles

Security is a project-wide requirement.

## Secrets

Never commit:

- API keys
- Passwords
- Tokens
- Credentials
- Private keys
- Service-account credentials

## Environment Variables

Secrets required by tools or deployment infrastructure must be provided through appropriate environment configuration.

## Git

The repository must not contain secret credentials.

`.env` files containing secrets must remain excluded from Git.

## Data

Only appropriately sourced datasets will be used.

Public datasets are preferred where possible.

## Privacy

The project should avoid personally identifiable information.

If PII exists in a selected dataset, it must be assessed before use.

## Logs

Logs must not expose:

- Credentials
- Tokens
- Sensitive user information
- Private configuration

## Application

The deployed application should expose only the functionality required for forecasting.

## Data Integrity

Raw data should be preserved and treated as immutable.

Processing should occur through documented pipelines.

## Dependencies

Dependencies should be kept to a reasonable minimum and reviewed for necessity.

## Deployment

Production configuration must not contain hardcoded secrets.

## Final Security Audit

The final project audit will verify:

- No secrets in Git
- No credentials in documentation
- No sensitive values in logs
- Appropriate `.gitignore`
- Appropriate environment configuration
- Appropriate data handling