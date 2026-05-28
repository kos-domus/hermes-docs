---
title: "Codex gpt-5.5 Errors"
slug: "codex-gpt55-errors"
category: "troubleshooting"
tags: ["codex", "gpt-5.5", "providers", "fallback", "troubleshooting", "openai-codex"]
sources:
  - "sessions/2026-05-27-hermes-pull-105-commits-codex-fix-tts-cornelia.md"
  - "sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md"
last_updated: "2026-05-28"
version: 1
hermes_version_min: "0.14.0"
---

# Codex gpt-5.5 Errors

Hermes can use the ChatGPT Codex backend through the `openai-codex` provider. In late May 2026, two separate failure modes appeared around `gpt-5.5`. They look similar in user experience because both can cause fallback, but their causes and fixes are different.

## Quick decision table

| Pattern | User-visible symptom | Root cause | Best response |
|---|---|---|---|
| Pattern A: `NoneType` stream crash | `TypeError: 'NoneType' object is not iterable` | Codex terminal stream frame returned `response.output = null`; older Hermes code consumed it through the OpenAI SDK helper | Pull Hermes upstream containing the structural stream-consumption fix, then restart active gateways |
| Pattern B: no first byte / silent reject | `no first byte after 45s` or timeout before any model token | ChatGPT Codex backend silently drops or gates some `gpt-5.5` request payloads intermittently | Keep a fallback chain; treat as provider-side intermittency unless it becomes constant |

## Pattern A: `TypeError: 'NoneType' object is not iterable`

### Exact symptom

```text
TypeError: 'NoneType' object is not iterable
```

The upstream fix was described as recovery from Codex streams with null output. The failure happened because the OpenAI Python SDK's high-level `client.responses.stream(...)` helper reconstructed the final response from `response.completed.response.output`, but the ChatGPT Codex backend could send `response.output = null` on terminal frames.

### Fix

Update Hermes Agent to a revision that consumes Codex response events directly instead of depending on the SDK terminal-frame reconstruction.

```bash
cd ~/.hermes/hermes-agent
git fetch origin
git log --oneline HEAD..origin/main --grep='Codex\|null output\|responses.stream' --all
git pull --ff-only
```

Then restart any long-running gateway daemons so they load the new code:

```bash
systemctl --user restart hermes-gateway.service
systemctl --user restart hermes-gateway-mc.service
systemctl --user restart hermes-gateway-family-staging.service
```

Adjust the unit names to the profiles actually running on your host.

### Verification

Run a direct provider invocation that bypasses the fallback chain:

```bash
hermes -p <profile> -z "Reply only with: TEST OK" -m gpt-5.5 --provider openai-codex
```

Expected output:

```text
TEST OK
```

If this succeeds without `NoneType`, Pattern A is fixed for that profile.

## Pattern B: no first byte / silent reject

### Exact symptom examples

```text
no first byte after 45s
APIConnectionError
```

This can still happen after Pattern A is fixed. The observed behavior is intermittent: the same profile and same provider can accept a simple smoke test one minute and silently reject another request later.

### Likely cause

The ChatGPT Codex backend for `gpt-5.5` is stricter than the public OpenAI API. The source investigation linked silent drops to payload fields such as:

- `reasoning: {effort: "xhigh", summary: "auto"}`
- `include: ["reasoning.encrypted_content"]`
- `store: false`
- stricter tool-schema validation for some `gpt-5.5` requests

> ⚠️ **Unverified upstream detail**: these fields came from a live field investigation and linked ecosystem issues. Treat them as diagnostic clues, not a stable public API contract.

### Mitigation

Keep `openai-codex/gpt-5.5` as primary only if your fallback chain is healthy. A subscription-first chain can self-heal when Codex silently rejects a request:

```yaml
model:
  default: gpt-5.5
  provider: openai-codex

fallback_providers:
  - provider: google-gemini-cli
    model: gemini-2.5-flash
  - provider: zai-coding
    model: glm-5.1
  - provider: anthropic
    model: claude-sonnet-4-7
```

For user-facing gateways, prefer a chain that trades a small latency penalty for completion reliability.

## Debug checklist

1. Check whether the error is Pattern A or Pattern B:
   ```bash
   journalctl --user -u 'hermes-gateway*.service' --since '1 day ago' | grep -iE 'NoneType|no first byte|APIConnectionError|codex'
   ```
2. If `NoneType` appears post-update, pull upstream again and retest direct provider invocation.
3. If only no-first-byte errors appear, verify fallback health rather than repeatedly re-authing Codex.
4. Restart active gateway services after code or config changes.
5. Test the profile directly:
   ```bash
   hermes -p <profile> -z "Reply only with: TEST OK" -m gpt-5.5 --provider openai-codex
   ```

## Related docs

- [Build a Subscription-First Provider Chain](../guides/provider-chain-subscription-oauth.md)
- [Provider Authentication Reference](../reference/provider-authentication.md)
- [Provider and Gateway Errors](provider-and-gateway-errors.md)
