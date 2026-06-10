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

## 2026-05-27
- **Added**: mcp-fleet-propagation — Guide for propagating MCP servers across a multi-profile Hermes fleet with per-profile domain mapping.
- **Added**: mcp-server-setup — Reference for MCP config syntax, CLI commands, OAuth token persistence, and validated server catalog.
- **Added**: mcp-errors — Troubleshooting page for MCP CLI argparse bug, OAuth timeout, SSH tunnel callback failures, and per-profile auth issues.
- **Updated**: oauth-credential-separation — Added MCP OAuth section explaining per-profile token separation for MCP servers (same anti-rotation rationale as provider OAuth).
- **Updated**: provider-and-gateway-errors — Added MCP tag and cross-links to new MCP troubleshooting docs.
- **Sources**: sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md

## 2026-05-28
- **Added**: codex-gpt55-errors — Troubleshooting flow for Codex `gpt-5.5` `NoneType` stream crashes versus no-first-byte silent rejects.
- **Added**: config-migration-v24 — Reference for Hermes config v23→v24 migration, moved sections, daemon restarts, and rollback.
- **Added**: elevenlabs-tts — Guide for least-privilege ElevenLabs TTS setup, Italian voice discovery, and Telegram sample delivery.
- **Added**: skill-consolidation-pattern — Concept doc for turning scattered workflow prompts into a single lazy-loaded skill source of truth.
- **Added**: self-improvement-agent-safety — Concept doc for safely designing a self-improvement Hermes profile with deterministic gates.
- **Updated**: provider-and-gateway-errors — Added Codex error routing and cross-link to the dedicated Codex troubleshooting page.
- **Sources**: sessions/2026-05-27-hermes-pull-105-commits-codex-fix-tts-cornelia.md, sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md

## 2026-06-02
- **Added**: cron-script-execution — Reference for profile-local cron script resolution, containment, wrapper execution, and immediate test commands.
- **Added**: cron-script-wrapper-pattern — Guide for using real profile-local wrapper files that exec external canonical scripts without copy drift.
- **Added**: cron-script-errors — Troubleshooting page for `Script not found` and `Blocked: script path resolves outside the scripts directory`.
- **Updated**: self-improvement-agent-safety — Added cron script containment as a self-improvement profile safety control.
- **Sources**: sessions/2026-06-01-cron-script-containment-fix.md

## 2026-06-05
- **Added**: fleet-learner-architecture — Concept doc for the Fleet Learner pattern: 3-layer memory model, targeted-edit operations, Temporal-Truth rules, ADD-only vs targeted-edit by layer, cross-layer dedup, forward-looking yield.
- **Added**: capability-matrix-allowlist — Guide for data-not-prosa read derogations: 0444 deploy-only YAML allowlist, deny-glob patterns, MCP sandbox parity, re-baseline flow, partial read enforcement caveats.
- **Added**: xai-oauth-remote-session — Troubleshooting for xAI OAuth over SSH: SSH tunnel flow, `--manual-paste` with full callback URL, `hermes auth reset` for state mismatch, `hermes proxy` scope note.
- **Updated**: self-improvement-agent-safety — Added Fleet Learner mode section, CSO tiered gating (Tier-1/2/3), capability-matrix cross-link, MCP filesystem sandbox narrowing, bearer-at-rest in `request_dump_*.json`, re-baseline flow, partial enforcement note.
- **Updated**: provider-and-gateway-errors — Added `hermes login` deprecation note + cross-link to new xAI OAuth troubleshooting page.
- **Sources**: sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md
## 2026-06-09
- **Added**: gws-profile-credentials — Troubleshooting flow for profile-local Google Workspace CLI credentials, `credentials.enc`, and HOME-scoped re-authentication.
- **Updated**: codex-gpt55-errors — Added the `HTTP 401 token_expired` Codex outage pattern and auth-error non-fallback mitigation.
- **Updated**: provider-authentication — Added credential-pool inspection with `hermes auth list`, reset guidance, and auth-error fallback notes.
- **Updated**: provider-and-gateway-errors — Added Codex 401 cascade and profile HOME Google Workspace credential errors.
- **Updated**: oauth-credential-separation — Added external CLI credential separation for profile HOME overrides.
- **Updated**: provider-chain-subscription-oauth — Added operational warning that auth errors may not trigger fallback in Hermes Agent 0.14.0.
- **Sources**: sessions/2026-06-09-fleet-outage-codex401-gws-reauth.md

## 2026-06-10
- **Added**: quick-setup-nous-portal — Getting-started page for Hermes 0.16.0 Quick Setup via Nous Portal and the `hermes portal` alias.
- **Added**: desktop-remote-gateway — Guide for connecting the native desktop app to an OAuth or username/password protected remote Hermes gateway.
- **Added**: hermes-016-surface-release — Reference summary of the 0.16.0 Surface Release: desktop app, dashboard admin panel, setup, skills, CLI/TUI, and security notes.
- **Sources**: no ready session files; upstream release https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5; PyPI https://pypi.org/project/hermes-agent/0.16.0/
