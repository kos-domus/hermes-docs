---
title: "OAuth Credential Separation in Hermes"
slug: "oauth-credential-separation"
category: "concepts"
tags: ["oauth", "credentials", "providers", "codex", "gemini"]
sources: ["sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md"]
last_updated: "2026-05-26"
version: 1
hermes_version_min: "0.14.0"
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

## Security rule

Store secrets in environment variables or Hermes credential storage, not in repository files.

Public docs may name provider keys such as `ZAI_API_KEY` or `GEMINI_API_KEY`, but must not include actual values.
