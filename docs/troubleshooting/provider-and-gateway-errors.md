---
title: "Provider and Gateway Errors"
slug: "provider-and-gateway-errors"
category: "troubleshooting"
tags: ["troubleshooting", "providers", "gemini", "openrouter", "zai", "systemd", "gateway", "mcp", "codex"]
sources:
  - "sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md"
  - "sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md"
  - "sessions/2026-05-27-hermes-pull-105-commits-codex-fix-tts-cornelia.md"
  - "sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md"
  - "sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md"
last_updated: "2026-06-05"
version: 4
hermes_version_min: "0.14.0"
---

# Provider and Gateway Errors

This page collects exact errors and fixes from a Hermes runtime investigation involving scheduled jobs, provider fallback behavior, and profile gateway path resolution.

## Codex `NoneType` stream crash and no-first-byte timeouts

Codex `gpt-5.5` failures split into two patterns:

- `TypeError: 'NoneType' object is not iterable` was fixed upstream by changing how Hermes consumes Codex response streams. Update Hermes and restart gateways.
- `no first byte after 45s` can still occur intermittently when the ChatGPT Codex backend silently rejects or gates a request. Keep the fallback chain healthy.

See [Codex gpt-5.5 Errors](codex-gpt55-errors.md) for the full diagnostic flow.

## `Gemini HTTP 400: Function call is missing a thought_signature`

Exact observed error:

```text
Gemini HTTP 400: Function call is missing a thought_signature in functionCall parts. Additional data, function call default_api:skill_view, position 2
```

### Cause

Gemini 3.x tightened validation around `thought_signature` fields for multi-function-call histories. The source investigation found that the documented sentinel bypass was not enough for the parallel/multiple function-call case.

### Fix

Use `gemini-2.5-flash` instead of Gemini 3.x in the fallback chain until the adapter behavior is verified for the newer model family.

```yaml
fallback_providers:
- provider: google-gemini-cli
  model: gemini-2.5-flash
```

## `Gemini HTTP 429 RESOURCE_EXHAUSTED`

Exact observed error:

```text
Gemini HTTP 429 RESOURCE_EXHAUSTED, paid_tier_input_token_count limit 2000000, retry in 10.7s
```

### Cause

The workload saturated a paid-tier input-token rate limit. In the source session this happened because the primary provider was failing and Gemini became the hot fallback path.

### Fix

Do not make Gemini the only practical fallback. Use a broader provider chain so traffic can continue through additional providers:

```yaml
fallback_providers:
- provider: google-gemini-cli
  model: gemini-2.5-flash
- provider: zai-coding
  model: glm-5.1
- provider: anthropic
  model: claude-sonnet-4-7
- provider: openrouter
  model: z-ai/glm-4.5-air:free
```

## `OpenRouter HTTP 402` max-token preauthorization

Exact observed error:

```text
You requested up to 65536 tokens, but can only afford 60042. Add more credits
```

### Cause

OpenRouter can pre-authorize against the maximum requested output tokens. A request with a large `max_tokens` can fail even when average usage would be inexpensive.

### Fix

For subscription-first setups, move the primary model to an OAuth-backed provider such as `openai-codex`, and keep OpenRouter as a lower-priority fallback.

```yaml
model:
  default: gpt-5.5
  provider: openai-codex
```

If you intentionally want OpenRouter primary, reduce requested max output tokens or add credits.

## `Z.AI 1113 Insufficient balance`

Exact observed error:

```text
1113 Insufficient balance
```

### Cause

The request used the Z.AI pay-as-you-go endpoint while the account had Z.AI Coding Pro subscription access.

### Fix

Configure a user-defined provider pointed at the Coding Pro endpoint:

```yaml
providers:
  zai-coding:
    name: Z.AI Coding Pro
    base_url: https://api.z.ai/api/coding/paas/v4
    key_env: ZAI_API_KEY
    default_model: glm-5.1
```

## `Hermes AuthError: No Codex credentials stored`

### Cause

The Codex CLI and Hermes do not share OAuth sessions. Running `codex login` does not create Hermes credentials.

### Fix

```bash
hermes auth add openai-codex --type oauth --no-browser --manual-paste
```

## `File not found: .../procedures/capture-protocol.md`

Exact observed log pattern:

```text
Tool read_file returned error: "File not found:
/home/kos/.hermes/hermes-agent/procedures/capture-protocol.md"
```

### Cause

The profile's `SOUL.md` referenced a procedure with a relative path:

```text
procedures/capture-protocol.md
```

But the systemd unit's `WorkingDirectory` was the Hermes source/runtime directory:

```text
/home/kos/.hermes/hermes-agent/
```

not the profile directory:

```text
/home/kos/.hermes/profiles/mc/
```

Hermes resolved the relative path against the process working directory, so the file lookup failed.

### Fix

Use absolute paths in profile instructions for procedure files:

```text
/home/kos/.hermes/profiles/mc/procedures/capture-protocol.md
```

Add an explicit comment in the profile instructions so future edits do not reintroduce relative paths.

## `hermes -z` with `--base-url`

### Cause

The source session attempted to pass a base URL as a chat CLI flag, but that flag was not exposed by `hermes chat`.

### Fix

Use a named provider in `config.yaml` instead of a one-off CLI flag:

```yaml
providers:
  my-provider:
    name: My Provider
    base_url: https://example.invalid/v1
    key_env: MY_PROVIDER_API_KEY
    default_model: my-model
```

## Provider exhaustion cooldown

Observed pattern:

```text
OPENROUTER_API_KEY exhausted (402) (17m 59s left)
```

Hermes may mark exhausted providers with a cooldown. If the condition is temporary, let the cooldown expire. If it is persistent, fix the provider balance or move it lower in the fallback chain.

## `hermes login` removed

`hermes login` is no longer a command (the help text may still mention it). Use:

```bash
hermes auth add <provider> --type oauth
```

For OAuth flows that have gone sideways (state mismatch, abandoned mid-flow), reset before retrying:

```bash
hermes auth reset <provider>
```

For xAI OAuth on a remote SSH session specifically — loopback callback handling, SSH tunnel, `--manual-paste` with the full URL — see [xAI OAuth on Remote SSH Sessions](xai-oauth-remote-session.md).

## Related docs

- [Provider authentication reference](../reference/provider-authentication.md)
- [Provider chain guide](../guides/provider-chain-subscription-oauth.md)
- [MCP errors troubleshooting](mcp-errors.md)
- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [xAI OAuth on Remote SSH Sessions](xai-oauth-remote-session.md)
