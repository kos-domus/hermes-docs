# Hermes Docs Changelog

Log of every Kos elaboration run on this repository.

## 2026-05-24 — Repo bootstrap

- **Created**: repo scaffold mirroring `openclaw-docs` structure (Diátaxis docs/, sessions/, changelog/, strategy/, skill-draft/, assets/)
- **Added**: `README.md`, `CLAUDE.md` (Kos elaboration instructions), `CONTRIBUTING.md`, `LICENSE` (MIT), `index.yaml`
- **Sources**: bootstrap, no sessions processed yet
- **Hermes baseline**: 0.14.0 (installed via PyPI on 2026-05-23 Step 1 Kos personal migration)
- **Next**: first sessions to ingest will be Step 2 fleet migration (2026-05-24) and Step 1 Kos personal migration (2026-05-23)

## 2026-05-26
- **Added**: provider-chain-subscription-oauth — Guide for configuring a five-tier subscription-first OAuth fallback chain.
- **Added**: oauth-credential-separation — Concept doc explaining why Hermes keeps OAuth sessions separate from vendor CLIs.
- **Added**: provider-authentication — Reference matrix for provider names, auth modes, endpoints, and profile-fleet config targets.
- **Added**: provider-and-gateway-errors — Troubleshooting page for Gemini, OpenRouter, Z.AI, Codex OAuth, and profile procedure path errors.
- **Sources**: sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md

