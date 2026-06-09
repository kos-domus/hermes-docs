---
title: OAuth Credential Separation in Hermes
slug: oauth-credential-separation
category: concepts
tags:
- oauth
- credentials
- providers
- codex
- gemini
- mcp
- profiles
- gws
sources:
- sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md
- sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md
- sessions/2026-06-09-fleet-outage-codex401-gws-reauth.md
last_updated: '2026-06-09'
version: 3
hermes_version_min: 0.14.0
---
# OAuth Credential Separation in Hermes

Hermes intentionally keeps provider OAuth sessions separate from adjacent CLI tools such as Codex CLI, Gemini CLI, and editor extensions.

## Why separation exists

The practical reason is refresh-token safety. If multiple apps share the same refresh token, one app's refresh can invalidate another app's session. Hermes avoids this by storing its own credentials instead of reusing another tool's token file.

This is especially relevant for:

- `openai-codex`
- `google-gemini-cli`
- provider integrations backed by local CLI/OAuth workflows

## Consequence for setup

Logging into the vendor CLI does not automatically authenticate Hermes.

For Codex, this is insufficient by itself:

```bash
codex login --device-auth
```

You still need the Hermes credential:

```bash
hermes auth add openai-codex --type oauth --no-browser --manual-paste
```

For Gemini CLI OAuth, you may already have a file such as:

```text
~/.gemini/oauth_creds.json
```

Hermes still needs its own provider credential:

```bash
hermes auth add google-gemini-cli --type oauth --no-browser --manual-paste
```

## Headless OAuth pattern

On a remote SSH machine:

1. Start the Hermes OAuth command on the remote host.
2. Open the printed URL in your local browser.
3. Authorize the account.
4. If the browser lands on a failed `127.0.0.1` redirect, copy the full redirected URL.
5. Paste that URL back into the remote terminal prompt.

The local redirect failure is normal in headless/SSH setups because the browser is not running on the same machine as Hermes.

## Snap-installed Codex CLI quirk

When Codex CLI is installed as a snap package, its auth file may live under:

```text
~/snap/codex/current/auth.json
```

instead of the traditional:

```text
~/.codex/auth.json
```

Do not build Hermes automation that assumes the traditional Codex CLI path. Prefer `hermes auth` for Hermes-owned credentials.

## MCP server OAuth: same principle applies

The per-profile separation also applies to MCP server OAuth tokens. Hermes stores MCP OAuth credentials in:

```text
~/.hermes/mcp-tokens/<server>.json                              # default profile
~/.hermes/profiles/<profile>/mcp-tokens/<server>.json            # named profile
```

If three profiles (e.g., `mc`, `cso`, `frontend`) all use the Sentry MCP server, each requires its own OAuth login:

```bash
hermes -p mc mcp login sentry
hermes -p cso mcp login sentry
hermes -p frontend mcp login sentry
```

The anti-rotation rationale is identical to provider OAuth: if profiles shared a token file, one profile's refresh could invalidate another's session. The source code in `credential_sources.py` explicitly documents this as preventing "refresh token rotation conflicts where one app's refresh invalidates the other's session."

## Profile HOME overrides and external CLI credentials

Named Hermes profiles can run automation with a profile-local HOME, for example:

```text
~/.hermes/profiles/<profile>/home
```

External CLIs launched from that profile inherit the same separation. For Google Workspace CLI, a profile HOME may contain:

```text
client_secret.json
.encryption_key
credentials.enc
```

`credentials.enc` is encrypted by the `.encryption_key` in that HOME. Do not copy `credentials.enc` from the default HOME into a profile HOME. Re-authenticate in place instead:

```bash
HOME=$HOME/.hermes/profiles/<profile>/home \
GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file \
gws auth login
```

This is the same operational principle as Hermes provider and MCP OAuth: credential files are scoped to the runtime that owns their refresh and encryption context.

## Security rule

Store secrets in environment variables or Hermes credential storage, not in repository files.

Public docs may name provider keys such as `ZAI_API_KEY` or `GEMINI_API_KEY`, but must not include actual values.

## Related docs

- [MCP server setup reference](../reference/mcp-server-setup.md)
- [MCP fleet propagation guide](../guides/mcp-fleet-propagation.md)
- [Provider authentication reference](../reference/provider-authentication.md)
- [Profile-scoped Google Workspace credentials](../troubleshooting/gws-profile-credentials.md)
