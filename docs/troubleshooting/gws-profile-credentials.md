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
- secret-rotation
sources:
- sessions/2026-06-09-fleet-outage-codex401-gws-reauth.md
- sessions/2026-10-26-posta-agent-quick-commands-codex-entitlement.md
last_updated: '2026-10-27'
version: 2
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

## Rotating an OAuth client secret (without killing every login)

When a client secret has been exposed and must be rotated, the trap is in what `gws` does with the secret:

- `gws` stores the `client_secret` **inside `credentials.enc`** (the authorized-user file) at login time and never re-reads `client_secret.json` on refresh.
- There is no `gws auth import` — you cannot inject a new secret into existing tokens.
- Deactivating the old secret therefore breaks **every existing login** at once, with:

```text
invalid_client
```

Also: rotate by adding a secret to the **existing** client (Edit → Add secret). Do **not** use "Add client" — that creates a new `client_id` and invalidates all logins and consent grants.

Correct order:

1. In the Google Cloud Console, add a **new secret** to the existing OAuth client (keep the old one active for now).
2. Update `client_secret.json` in **every** `gws` config location (each profile HOME that uses it).
3. Re-run `gws auth login` for every account (per profile HOME, as above).
4. Verify each login (`encryption_valid: true`, `token_valid: true` and a working read call).
5. Only then deactivate and delete the old secret.

After any new login, also delete `token_cache.json` in that HOME — it can still hold a token minted under the old secret/scope set and keep serving stale credentials.

## Consent-screen and project-membership 403s

Two Google-side traps that surface as 403s **after** a login that reports success:

- **Gmail scope checkbox unchecked.** For an unverified app, the consent screen can show the Gmail permission checkbox **unchecked by default**. The user approves without noticing, and the login succeeds — but the grant only contains `openid`/`email`. Symptom: `Gmail 403 insufficient scopes` on the first mail call. Fix: redo the consent flow with the Gmail box checked, then delete `token_cache.json` (see above).
- **`403 serviceusage.services.use`.** The account logging in is not a member of the GCP project that owns the OAuth client. Fix: grant the IAM role **Service Usage Consumer** on the project to that account (no conditions needed).

## Related docs

- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [Provider and Gateway Errors](provider-and-gateway-errors.md)
- [Provider Authentication Reference](../reference/provider-authentication.md)
