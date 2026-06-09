---
title: Build a Subscription-First Provider Chain
slug: provider-chain-subscription-oauth
category: guides
tags:
- providers
- oauth
- fallback
- configuration
- subscriptions
sources:
- sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md
- sessions/2026-06-09-fleet-outage-codex401-gws-reauth.md
last_updated: '2026-06-09'
version: 2
hermes_version_min: 0.14.0
---
# Build a Subscription-First Provider Chain

This guide describes a practical Hermes provider chain that prefers paid subscription-backed OAuth providers before falling back to API-key or free endpoints.

Use it when API billing or rate limits are making scheduled jobs fragile, but you already pay for ChatGPT Pro, Gemini Advanced, Claude/Codex, Z.AI Coding Pro, or similar CLI-backed subscriptions.

## Target chain

The validated five-level chain from the source session was:

```yaml
model:
  default: gpt-5.5
  provider: openai-codex

providers:
  zai-coding:
    name: Z.AI Coding Pro
    base_url: https://api.z.ai/api/coding/paas/v4
    key_env: ZAI_API_KEY
    default_model: glm-5.1

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

Rationale:

1. **Primary: `openai-codex` + `gpt-5.5`** — uses OpenAI/Codex OAuth instead of OpenRouter credit balance.
2. **Fallback 1: `google-gemini-cli` + `gemini-2.5-flash`** — uses Gemini CLI OAuth and avoids Gemini 3.x `thought_signature` regressions observed with parallel tool calls.
3. **Fallback 2: user-defined `zai-coding` + `glm-5.1`** — uses the Z.AI Coding Pro endpoint, not the pay-as-you-go endpoint.
4. **Fallback 3: `anthropic` + `claude-sonnet-4-7`** — paid high-quality fallback.
5. **Fallback 4: `openrouter` + free GLM model** — last-resort safety net.

## Prerequisites

- Hermes Agent installed and at least `0.14.0`.
- OAuth credentials added to Hermes for each OAuth provider you want to use.
- API keys available via environment variables only; never hard-code keys in `config.yaml`.
- For profile fleets, apply the same chain to every active profile config:
  - `~/.hermes/config.yaml`
  - `~/.hermes/profiles/<profile>/config.yaml`

## Add OpenAI Codex OAuth

Hermes keeps its own OAuth session. Logging in with the Codex CLI is not enough.

```bash
hermes auth add openai-codex --type oauth --no-browser --manual-paste
```

On an SSH/headless machine the browser redirect to `127.0.0.1` may fail locally. That is expected: copy the full redirected URL from the browser and paste it into the terminal prompt.

## Add Google Gemini CLI OAuth

The Gemini API-key provider and Gemini CLI OAuth provider are distinct:

- `gemini` → native Gemini API, `generativelanguage.googleapis.com`, uses `GEMINI_API_KEY`.
- `google-gemini-cli` → Cloud Code / Gemini CLI OAuth path, uses OAuth credentials.

Add the OAuth credential to Hermes:

```bash
hermes auth add google-gemini-cli --type oauth --no-browser --manual-paste
```

Keep `GEMINI_API_KEY` available as a manual safety net if you want, but leave it outside the active chain when the objective is subscription-first routing.

## Add Z.AI Coding Pro as a user-defined provider

Z.AI Coding Pro uses a different endpoint from the pay-as-you-go API.

```yaml
providers:
  zai-coding:
    name: Z.AI Coding Pro
    base_url: https://api.z.ai/api/coding/paas/v4
    key_env: ZAI_API_KEY
    default_model: glm-5.1
```

Do not use `https://api.z.ai/api/paas/v4` for Coding Pro subscription traffic; the source session observed `1113 Insufficient balance` on that endpoint.

## Verify the chain

Use the built-in fallback inspection command:

```bash
hermes fallback list
```

For profile fleets, inspect each profile:

```bash
hermes -p mc fallback list
hermes -p backend fallback list
hermes -p cso fallback list
hermes -p frontend fallback list
hermes -p orcharch fallback list
```

Then run small smoke prompts against the default and important profiles:

```bash
hermes chat -q 'Reply with PONG_PRIMARY only.'
hermes -p mc chat -q 'Reply with PONG_MC only.'
```

## Operational notes

- API subscriptions and chat subscriptions are not the same thing. ChatGPT Pro, Gemini Advanced, Claude Code, and Z.AI Coding Pro do not automatically grant normal REST API access.
- Hermes needs a provider-specific OAuth wrapper to use subscription-backed CLI access.
- OAuth access tokens expire; Hermes should refresh them transparently, but monitor the first natural expiry after setup.
- Authentication errors are different from rate limits. In Hermes Agent `0.14.0`, an `openai-codex` `HTTP 401 token_expired` was observed to retry the primary instead of cleanly falling through the fallback chain. Keep a direct auth-pool check (`hermes auth list`) in your scheduled-job diagnostics.
- When applying the chain across profiles, restart relevant gateway/systemd services after config changes.

## Related docs

- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [Provider authentication reference](../reference/provider-authentication.md)
- [Provider and gateway troubleshooting](../troubleshooting/provider-and-gateway-errors.md)
