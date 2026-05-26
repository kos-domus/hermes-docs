---
title: "Provider Authentication Reference"
slug: "provider-authentication"
category: "reference"
tags: ["providers", "authentication", "configuration", "oauth", "api-keys"]
sources: ["sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md"]
last_updated: "2026-05-26"
version: 1
hermes_version_min: "0.14.0"
---

# Provider Authentication Reference

This reference summarizes provider names, authentication modes, endpoints, and observed edge cases from the source session.

## Provider matrix

| Provider name | Auth mode | Endpoint / backend | Notes |
|---|---:|---|---|
| `openai-codex` | OAuth | Codex/OpenAI subscription path | Requires `hermes auth add openai-codex --type oauth`; separate from Codex CLI login. |
| `google-gemini-cli` | OAuth | `cloudcode-pa://google` / Cloud Code backend | Distinct from the `gemini` API-key provider. |
| `gemini` | API key | `generativelanguage.googleapis.com` | Uses `GEMINI_API_KEY`; Gemini 3.x produced a `thought_signature` error in the source session. |
| `zai-coding` | API key | `https://api.z.ai/api/coding/paas/v4` | User-defined provider for Z.AI Coding Pro subscription. |
| `zai` / default Z.AI endpoint | API key | `https://api.z.ai/api/paas/v4` | Pay-as-you-go path; may return `1113 Insufficient balance` for subscription-only accounts. |
| `anthropic` | OAuth/API key depending config | Anthropic provider | Used as a high-quality fallback in the validated chain. |
| `openrouter` | API key | OpenRouter | Useful as final safety fallback; credit balance can pre-authorize max-token requests. |

## User-defined Z.AI Coding provider

```yaml
providers:
  zai-coding:
    name: Z.AI Coding Pro
    base_url: https://api.z.ai/api/coding/paas/v4
    key_env: ZAI_API_KEY
    default_model: glm-5.1
```

Confirmed model family in the source session:

- `glm-5.1`
- `glm-4.7`
- `glm-4.6`
- `glm-4.5`
- `glm-4.5-air`
- `glm-4.5-flash`

> ⚠️ **Unverified**: The source session confirmed chat completions and Anthropic-wire compatibility for the Coding Pro endpoint. Embeddings, vision, and audio coverage were not verified.

## Gemini provider distinction

Hermes has two Gemini integration paths:

```text
provider: gemini             # Native API-key adapter
provider: google-gemini-cli  # OAuth / Cloud Code adapter
```

Choose `google-gemini-cli` when you want to use Gemini CLI / Gemini Advanced-style OAuth credentials. Choose `gemini` when you explicitly want API-key billing through `GEMINI_API_KEY`.

## OAuth commands

```bash
hermes auth add openai-codex --type oauth --no-browser --manual-paste
hermes auth add google-gemini-cli --type oauth --no-browser --manual-paste
```

Older instructions may mention `hermes login`. In current Hermes versions represented by this repository baseline, use `hermes auth add`.

## Inspect configured fallbacks

```bash
hermes fallback list
hermes -p <profile> fallback list
```

## Profile fleet checklist

When running multiple Hermes profiles, keep provider configuration aligned across the profiles that can receive scheduled or gateway work:

```text
~/.hermes/config.yaml
~/.hermes/profiles/mc/config.yaml
~/.hermes/profiles/backend/config.yaml
~/.hermes/profiles/cso/config.yaml
~/.hermes/profiles/frontend/config.yaml
~/.hermes/profiles/orcharch/config.yaml
```

Restart the relevant gateway services after editing profile configs.
