# Security and data handling

These examples call a real video API and can expose credentials, account data,
device identifiers and recordings if configured carelessly.

## Before using a sample

- Copy the relevant `baseaaa.example.json` to `baseaaa.json` locally.
- Never commit the populated file. `baseaaa.json` is git-ignored.
- Use only accounts, devices and recordings you are authorized to access.
- Do not include credentials, customer identifiers or unredacted logs in issues.
- Confirm the current endpoint, API version and authentication method with the
  provider documentation.

## Repository history

The current example configuration files contain empty credential fields. Older
commits and previously tracked local-history files must still be reviewed before
this repository is promoted as a security example. If a real credential was ever
committed, revoke or rotate it first. Removing a file or making a repository
private does not invalidate copies that may already exist.

## Transport security

TLS certificate verification must remain enabled. Do not add `verify=False`,
`ssl.CERT_NONE` or equivalent bypasses to make a connection appear to work.
Diagnose certificate, proxy and trust-store problems instead.
