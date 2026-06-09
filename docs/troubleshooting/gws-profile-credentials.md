---
title: Profile-scoped Google Workspace Credentials
slug: gws-profile-credentials
category: troubleshooting
tags:
- troubleshooting
- gws
- google-workspace
- profiles
- oauth
- credentials
- cron
sources:
- sessions/2026-06-09-fleet-outage-codex401-gws-reauth.md
last_updated: '2026-06-09'
version: 1
hermes_version_min: 0.14.0
---
# Profile-scoped Google Workspace Credentials

Use this troubleshooting flow when a Hermes cron job or profile-local automation calls the Google Workspace CLI (`gws`) and reports missing Drive or Workspace credentials even though the default shell user is authenticated.

## Symptom

```text
Drive auth failed: No credentials found
```

This often appears in scheduled jobs that upload artifacts to Google Drive after an agent run. Other jobs in the same outage window may also report provider errors; fix the primary provider outage first, then verify whether the Drive error remains.

## Cause

A named Hermes profile can run with a profile-local HOME:

```text
~/.hermes/profiles/<profile>/home
```

External CLIs launched from that runtime read credentials from that HOME, not from the default user's normal home directory. For Google Workspace CLI with file-backed encryption, the important files are:

```text
~/.hermes/profiles/<profile>/home/client_secret.json
~/.hermes/profiles/<profile>/home/.encryption_key
~/.hermes/profiles/<profile>/home/credentials.enc
```

If `client_secret.json` and `.encryption_key` exist but `credentials.enc` is missing, the CLI has the OAuth client material and encryption key but no user token.

Do **not** copy `credentials.enc` from another profile or from the default HOME. It is encrypted for the HOME that created it and can fail validation when moved.

## Fix: re-authenticate inside the profile HOME

Run the Google Workspace login with `HOME` pointed at the profile's HOME and the file keyring backend enabled:

```bash
HOME=$HOME/.hermes/profiles/<profile>/home \
GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
gws auth login
```

Complete the browser OAuth flow for the intended Google account. The result should be a new profile-local `credentials.enc`.

## Verify

Use the auth/status command provided by your installed `gws` CLI. The expected state is equivalent to:

```text
encryption_valid: true
token_valid: true
```

Then run a harmless Drive read/list or a small upload in the same profile HOME to confirm that the scheduled job will see the same credential context.

## Operational checklist

1. Confirm which profile owns the failing cron job.
2. Check whether that profile overrides `HOME`.
3. Inspect the profile HOME for `credentials.enc`; do not inspect or copy token contents.
4. Re-authenticate in place with the profile HOME.
5. Re-run the failed cron job or its upload step.

## Related docs

- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [Provider and Gateway Errors](provider-and-gateway-errors.md)
- [Provider Authentication Reference](../reference/provider-authentication.md)
