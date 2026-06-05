---
title: "xAI OAuth on Remote SSH Sessions"
slug: "xai-oauth-remote-session"
category: "troubleshooting"
tags: ["troubleshooting", "providers", "xai", "oauth", "ssh", "remote"]
sources:
  - "sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md"
last_updated: "2026-06-05"
version: 1
hermes_version_min: "0.14.0"
---

# xAI OAuth on Remote SSH Sessions

Hermes uses OAuth for `xai-oauth` (Grok) and a handful of other providers. On a remote machine reached over SSH, the OAuth loopback callback (`127.0.0.1:<port>/callback`) fires against the remote host's loopback — not your laptop's. The browser on your laptop cannot reach it directly.

This page collects the failure modes and the two working flows.

## `hermes login` is deprecated

Older documentation may still reference `hermes login`. The command has been removed. Use:

```bash
hermes auth add <provider> --type oauth
```

For xAI specifically:

```bash
hermes auth add xai-oauth --type oauth
```

If you previously attempted an OAuth flow and want to retry cleanly, reset the stored state first:

```bash
hermes auth reset xai-oauth
```

## Flow A: SSH tunnel (recommended when you control both ends)

The cleanest path is to forward the loopback port from your laptop to the remote machine. When the OAuth callback fires against `127.0.0.1:<port>` on the remote, your browser hits the laptop-side tunnel and the response is forwarded back.

```bash
# On your laptop, in a separate terminal:
ssh -N -L <port>:127.0.0.1:<port> kos@<remote-host>
```

`<port>` is whatever loopback port Hermes reported when it started the OAuth flow. Keep this tunnel open for the duration of the flow.

Then on the remote:

```bash
hermes auth add xai-oauth --type oauth
```

Hermes opens (or prints) the authorization URL. Open it in your laptop's browser. The callback auto-completes through the tunnel. You should see the success message in the remote terminal within seconds.

### Why this is preferred

- No copy-paste of URLs or codes.
- The `state` parameter reaches the callback intact.
- Works for any OAuth provider that uses loopback redirect URIs.

## Flow B: `--manual-paste` with the full callback URL

If you cannot tunnel the port (NAT, firewall, jump host), use manual paste:

```bash
hermes auth add xai-oauth --type oauth --manual-paste
```

Hermes prints the authorization URL. Open it in your laptop's browser. After you authorize, the browser will be redirected to a loopback URL that **does not load** — that is expected.

### What to copy

Copy the **entire URL** from the browser's address bar, including query parameters:

```text
http://127.0.0.1:<port>/callback?code=<long-string>&state=<state-string>
```

Paste this entire URL into the Hermes prompt.

### What NOT to copy

Do not paste only the `code` value. The flow needs both `code` and `state`, and Hermes parses them out of the URL. A bare code produces:

```text
Error: missing authorization code
```

## `state mismatch`

Exact observed error after multiple interleaved OAuth attempts:

```text
Error: state mismatch
```

### Cause

Each `hermes auth add` generates a fresh `state` nonce. If you start a flow, abandon it, start another, and then paste a callback URL from the first attempt, the `state` value no longer matches what Hermes has in memory.

### Fix

```bash
hermes auth reset xai-oauth
hermes auth add xai-oauth --type oauth     # one clean attempt
```

Do not interleave attempts. Start one flow, finish it. If it fails, reset before retrying.

## `hermes proxy` only fronts `nous` and `xai`

While investigating xAI auth, it is worth knowing the current scope of `hermes proxy`. As of 0.14.x, the proxy that bridges OpenAI-compatible clients to OAuth-backed providers fronts **only `nous` and `xai`** — not the full provider chain.

This matters if you are trying to A/B-test a model served by a different provider (e.g., routing OpenAI-compatible traffic to Anthropic or Z.AI via the proxy). It will not work today. Use the provider's native endpoint directly, or wait for the proxy to be extended.

## Related docs

- [Provider and Gateway Errors](provider-and-gateway-errors.md)
- [Provider Authentication](../reference/provider-authentication.md)
- [OAuth Credential Separation](../concepts/oauth-credential-separation.md)
- [Provider Chain Subscription/OAuth](../guides/provider-chain-subscription-oauth.md)
