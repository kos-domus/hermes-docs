---
title: "Hermes Agent 0.19–0.20 Release Wave Reference"
slug: "hermes-019-020-release-wave"
category: "reference"
tags: ["release-notes", "voice", "a2a", "webhooks", "secrets", "performance", "providers", "desktop", "cli"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20"
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3"
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.27"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-01"
version: 2
hermes_version_min: "0.19.0"
---

# Hermes Agent 0.19–0.20 Release Wave Reference

This reference covers the operator-facing changes from Hermes Agent **v0.19.0 (2026.7.20, "Quicksilver")** through **v0.20.6 (v2026.8.27)**. It extracts what a fleet operator needs to know when planning an upgrade from 0.16/0.17/0.18-era installs. It is not a replacement for the upstream changelogs.

## Release timeline

| Version | Tag | Date | Theme |
|---|---|---|---|
| 0.19.0 | v2026.7.20 | 2026-07-20 | Quicksilver — speed, secrets, subscriptions |
| 0.19.1 | v2026.7.30 | 2026-07-30 | Infrastructure patch rollup (~1,000 PRs of fixes) |
| 0.20.0 | v2026.8.3 | 2026-08-03 | Herald — voice, A2A, webhooks, grounded citations |
| 0.20.1 | v2026.8.13 | 2026-08-13 | Stabilization rollup (656 PRs, ~481 issues closed) |
| 0.20.2 | v2026.8.16 | 2026-08-16 | Desktop Connections registry, persisted model routes |
| 0.20.3 | v2026.8.16.2 | 2026-08-17 | MCP 2.x SDK, Bot Mode plugin, runtime hardening |
| 0.20.4 | v2026.8.18 | 2026-08-18 | Desktop glass UI, SkillEvaluator scanning, cron media hardening |
| 0.20.5 | v2026.8.19 | 2026-08-21 | Keyless web tier, CLI polish, Bot Mode group threads |
| 0.20.6 | v2026.8.27 | 2026-08-27 | Consent-gated real-profile browsing, MCP catalog, TTL caching |

> **Distribution channel note**: as of 2026-08-31, PyPI's `hermes-agent` latest is still **0.19.0** (uploaded 2026-07-20). The 0.20.x line is distributed via `hermes update` from an existing install or the GitHub installer one-liner (`curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`). If you install via `pip install hermes-agent`, you get 0.19.0, not 0.20.6.

## v0.19.0 Quicksilver — operator highlights

### Performance

- **First-turn time-to-first-token dropped ~80%** across CLI, gateway, TUI, desktop, and cron. Cold-start "Initializing agent..." went from ~4.3s to ~0.9s.
- Reasoning models **stream their thinking live by default** — no more 30-second spinner while a thinking model works.
- Desktop app got a ~20-PR speed overhaul (14× faster streaming markdown, virtualized diffs, snappy session switching).

### Secrets: the `SecretSource` interface

API keys no longer need to live in a plaintext `~/.hermes/.env`. A pluggable `SecretSource` interface fetches secrets from **Bitwarden Secrets Manager** and **1Password** (`op://` references) at load time. Multiple vaults can be enabled simultaneously with deterministic precedence. See [Secrets Vault Integration](../guides/secrets-vault-integration.md) for configuration.

This supersedes the manual `op inject` template + render-script + systemd `ExecStartPre=` pattern documented for older versions — the render script becomes unnecessary when the native source handles resolution at startup.

### Nous subscription management from the terminal

- `/subscription` — full plan management flow in TUI/CLI: see plan and remaining allowance, preview upgrade cost, apply changes with scheduled-change banners and undo.
- `/topup` — top up allowance without leaving the keyboard.
- Desktop app got a matching billing settings tab.

### Smart approvals default-on

An LLM reviewer independently assesses flagged commands instead of prompting for each one. Each verdict covers only that exact command instance. Paired with:

- **User-defined deny rules** — block commands even under yolo mode.
- `/deny <reason>` — tell the agent why you refused so it course-corrects.

### Delegation and delivery durability

- `delegate_task` dispatches return **live transcript files** you can `tail -f` per child subagent.
- Background delegation completions are **durable** — process restarts mid-run restore results through an ownership-checked ledger.
- **Delivery-obligation ledger**: final responses are recorded in `state.db` around the platform send and redelivered on next boot. Closes the P1 silent-loss window where a gateway crash between generation and delivery ate a paid turn.

### Profile-based message routing (one gateway, many profiles)

A single multiplexed gateway sharing one bot token can route specific guilds, channels, or threads to different profiles — each with isolated config, skills, memory, and secrets. One bot, work server → `work` profile, hobby server → `personal`.

### New providers and models

Fireworks AI and DeepInfra as first-class providers; Upstage Solar via salvage. Catalog additions: GPT-5.6 family (Sol/Terra/Luna + Pro), grok-4.5 GA, kimi-k3, claude-fable-5 / claude-sonnet-5, tencent/hy3 GA. LM Studio JIT model loading for local setups.

### Reasoning effort tiers

`max` and `ultra` levels added (GPT-5.6 and Codex top tiers), with per-model overrides in config, per-slot effort in MoA presets, and per-task effort for auxiliary models.

### Session export

`hermes sessions export` writes Markdown, Quarto, HTML, prompt-only, and Hugging Face-ready trace formats with full filters (age, workspace, platform), opt-in `--redact` secret scrubbing, and compacted-session lineage stitching.

## v0.20.x Herald — operator highlights

### Voice: streaming conversational with barge-in

- Hermes speaks **clause-by-clause as the response streams**; you can interrupt mid-sentence by talking (it stops, listens, and the model is told you cut in). Busy-aware silence detection avoids talking over you.
- **Wake words**: open-vocabulary on-device detection ("hey Hermes" or any phrase), multi-profile voice routing (different wake words reach different profiles), "stop" ends voice chat everywhere.
- **Voice on every platform**: WhatsApp, Feishu, DingTalk, LINE, QQ, Photon, Weixin voice notes transcribed and answered; auto-TTS replies are platform-aware (opus where wanted).
- STT became a first-class `hermes tools` category with GUI toggles, unified language resolution, and OpenAI gpt-transcribe support.

### Agent-to-Agent (A2A v1.0)

A bundled plugin implements the A2A protocol: Hermes can discover, talk to, and be driven by other A2A-compatible agents. Closes one of the repo's oldest feature requests (#514).

### Outbound webhooks (signed)

Hermes pushes **signed lifecycle events** (session activity, turn completions, tool events) to registered HTTP endpoints with HMAC signatures for receiver-side verification. Wire Hermes into CI, home automation, or dashboards without polling.

### Grounded citations

The `grounded-citations` skill produces research where every claim is backed by a verifiable source: quotes matched against actual page text, citations linking to exact evidence, and a fact-checking mode for arbitrary documents.

### Desktop as a platform

- **Artifacts**: versioned cards with sandboxed live preview in a right-rail viewer.
- **Plugin SDK** with Kanban as founding plugin; `ctx.download` for handing users files.
- Global-hotkey **quick-entry window**; multiple GUI windows.
- (0.20.6) Desktop Browser gets its own OS window, managed SSH remote-update engine, fleet profile rail.

### CLI power-user wave

- `!command` — run a shell command without spending a model turn.
- `/init` — scan project, generate/update `AGENTS.md`.
- `/diff` — staged/all/session changes from any surface.
- `/context` — breakdown of what fills the context window.
- `/focus` — reduced-output view with hidden-line recovery.
- `hermes import-agent` — migrate Claude Code or Codex CLI setup into Hermes.
- (0.20.5) Fuzzy `/model` picker, Ctrl+P command palette, richer `/status`.
- (0.20.5) `hermes worktree list/prune`.

### Mid-turn redirects

Type a correction while Hermes works: the active turn is redirected, in-flight work preserved, original prompt kept. No more `/stop` + re-explain.

### Self-recovering tools

Truncated terminal output spills to a readable file; `patch` detects already-applied edits; `write_file` verifies on-disk content; empty searches probe near-misses. **Default tool-calling iteration limit jumped 90 → 500.**

### Compression overhaul

Proactive tool-result pruning for large-window models, per-turn micro-compaction, guaranteed N-user-message tail, progress-aware timeouts, ghost-skill defense. Thresholds configurable per-model and in absolute tokens. (0.20.6) **Lean-tail compression is now the default.**

### Keyless web tier (0.20.5)

5-vendor free rotation with ring failover for web search — **fresh installs get working web search with zero API keys**.

### Other notable 0.20.x items

- **MCP 2.x SDK migration** + stateless protocol support (0.20.3); remote MCP catalog expansion with 50+ live-verified vendor-hosted servers (0.20.6).
- **Bot Mode** bundled plugin (`hermes-bots`) with teammate protocol; group-room threads (0.20.5).
- **Skill install security scanning** — NVIDIA SkillEvaluator Tier 1 advisory license + security checks (0.20.4).
- **Opt-in OS-keychain encryption** for stored secrets (0.20.6).
- **TTL result caching** for `web_search`/`web_extract` (0.20.6).
- Updaters pause gateways over the control socket instead of tree-killing them (0.20.6).
- Consent-gated **real-profile browsing** — use your default Chromium profile with a Windows close-with-approval flow (0.20.6).
- Cron jobs gained **persistent memory and per-job reasoning effort** (0.20.5), media-send hardening (0.20.4), durable-incident acks (0.20.6).

## Upgrade attention points

1. **Approvals behavior change**: smart approvals became the default in 0.19.0. If you relied on manual prompts for every flagged command, review the [smart approvals config](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#smart-approvals) and set deny rules for hard blocks.
2. **Compression defaults changed**: lean-tail compression became default in 0.20.6. Long-session behavior differs from 0.18-era compaction.
3. **Tool iteration limit 90 → 500**: long autonomous runs no longer stop at 90 tool calls. If you had cron guardrails assuming that ceiling, revisit them.
4. **PyPI lag**: `pip install -U hermes-agent` yields 0.19.0 as of 2026-08-31. Use `hermes update` or the GitHub installer for 0.20.x.
5. **MCP SDK 2.x** (0.20.3): custom MCP server configs written against the 1.x SDK protocol should be re-validated after upgrade.
6. **Secrets**: if you run a manual 1Password render-script pipeline (systemd `ExecStartPre=` + `op inject`), the native `secrets.onepassword` source can replace it — see [Secrets Vault Integration](../guides/secrets-vault-integration.md).

## Related docs

- [Hermes Agent 0.21.0 Pantheon Release Reference](hermes-021-pantheon-release.md) — v0.21.0 rolls up the v0.20.1–v0.20.6 windows documented on this page and adds Bot Mode, `hermes peer`, and cron memory on top.
- [Quick Setup via Nous Portal](../getting-started/quick-setup-nous-portal.md)
- [Secrets Vault Integration](../guides/secrets-vault-integration.md)
- [Provider Authentication Reference](provider-authentication.md)
- [Hermes Agent 0.16.0 Surface Release Reference](hermes-016-surface-release.md)
