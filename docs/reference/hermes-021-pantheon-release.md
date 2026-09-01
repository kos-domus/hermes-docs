---
title: "Hermes Agent 0.21.0 Pantheon Release Reference"
slug: "hermes-021-pantheon-release"
category: "reference"
tags: ["release-notes", "bot-mode", "multi-agent", "cron", "delegation", "mcp", "desktop", "security", "providers", "cli"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-01"
version: 1
hermes_version_min: "0.21.0"
---

# Hermes Agent 0.21.0 — The Pantheon Release

**Release:** v0.21.0 (tag `v2026.8.31`), published August 31, 2026.
**Window:** since v0.20.0 (`v2026.8.3`) — ~5,800 commits, ~2,475 merged PRs, ~2,100 issues closed, 760+ contributors.
**Rollup:** this minor fully documents the v0.20.1–v0.20.6 patch-tag windows (Aug 13–27) per the rollup-release policy.

The theme: v0.20.0 made Hermes *the herald* (he spoke to other agents); v0.21.0 assembles the pantheon — a society of named agents that talk to each other and to you, plus the operational machinery (cron memory, live subagent steering, an MCP command center) that makes a fleet governable.

## Bot Mode (desktop, default-on)

Multi-agent stopped being plumbing and became a chat app. Bot Mode is bundled and enabled by default in the desktop app:

- **Every agent profile gets a name and a deterministic avatar face** (with randomize/lock controls) and a slot in a shared roster.
- **Group chats** — Discord-style rooms where multiple bots and the human talk together; @-mention any bot from the composer; rooms have editable names and pictures.
- **Attributed agent-to-agent message cards** and sender-side delivery notices make bot conversations readable in the room.
- **Routines pane** for scheduled bot behavior.
- **Paint-first hydration** for instant wakes on room open.

This replaces the "plumb your own multi-agent" pattern (profiles + `hermes -p` CLI fan-out) with a first-class UI surface — the CLI patterns still work, but group coordination now has a native home.

## `hermes peer` — bot-to-bot DMs

Any Hermes agent can message any other **by handle**, across profiles and across gateways:

- Invoke from the CLI or from inside a conversation ("ask the research bot to hand findings to the coding bot").
- **Replies land in each agent's canonical Bot Chat** — conversations between agents are durable and inspectable, not fire-and-forget.
- Cross-gateway routing means the peers do not need to live on the same machine or profile tree.

## Cron jobs that remember

Scheduled agents stopped being goldfish. The cron subsystem gained:

- **Persistent memory load/update** — cron agents read and write memory like any interactive agent.
- **`continuity=true`** — each run's output carries into the next, so a monitor can dedupe against what it already reported.
- **Per-job durable notepads** — a scratchpad that survives across runs.
- **Monitor-mode hash-suppressed change detection** — skip the LLM entirely when nothing changed.
- **Bot Chat delivery** — cron output can land in a bot's canonical chat, where the bot actually responds to it.
- Per-job **reasoning-effort pinning**, pre-dispatch config validation, **acked failure signatures** (a known failure stops re-pinging), "Trigger now" for immediate safe execution, and model-drift impact surfaced in Desktop.

Practical effect: a 9am briefing job knows what it told you yesterday. Combined with Bot Chat delivery, scheduled reports become conversational.

## Live subagent orchestration

`delegate_task` went from fire-and-pray to managed parallel work:

- **List** running children, **steer** one mid-flight with a course correction, **stop** early keeping the partial result.
- **Optional JSON-schema validation** on child outputs (per-delegation `output_schema`).
- **Per-delegation cost** surfaced in results.
- **Raised defaults:** 250 iterations, 10 concurrent children.
- **Batch-quality validation before spawning** and truncation markers on capped children.
- Subagent work protection: delegate no longer deletes a child's uncommitted work when git inspection fails.

## MCP command center

MCP servers and the catalog merged into one desktop page:

- **Drag-in "paste anything" import** — paste JSON, a URL, or a config blob and it imports.
- **Background health checks** that nudge re-authentication *before* a tool call fails.
- **Fleet cost/usage overlay** — schema token estimates and 30-day usage per server.
- **`hermes://` deep links** that install an MCP server with explicit confirmation.
- Per-profile MCP lifecycle RPCs over the gateway.

Managing twenty MCP servers is now a dashboard instead of config-file archaeology. See [MCP Server Setup Reference](mcp-server-setup.md).

## The agent drives the desktop's browser

The in-app browser became an actuator, not a viewport: Hermes **navigates, clicks, and reads** the desktop's own browser tab, and pages can be popped out to the system browser with full link context menus. Ask it to walk a docs site or debug a web app and watch it happen inside your app.

## CLI & TUI power wave

- **Ctrl+P fuzzy command palette**; `/model` picker filters as you type.
- **`/status`** shows reasoning mode, pending approvals, and context usage.
- **Status bar live metrics**: cache-hit %, latency, tokens/sec with per-field toggles; session titles in the bar.
- **Global emergency stop**; **session pin/unpin** from the CLI.
- **`hermes approval-check`** — dry-run approval verdicts for a command without executing it.
- Ctrl+C interrupt fix (Kitty keyboard protocol no longer pushed).
- Rotating task-oriented composer placeholders — and terminal pets, because a companion should have a companion.

## Providers and models

- **Six new providers:** Meta Model API (Muse Spark) as a built-in provider plugin, CommandCode (GOAT/Pro/Max plans), Tencent TokenPlan, Nebius Token Factory, Ramp Router, Actual Computer.
- **`model_overrides`** — patch any model's context window, pricing, or capabilities in config without waiting on a catalog release.
- **Entry-point provider discovery** — third parties can ship pip-installable model providers.
- **Data-training-tier warnings** — a unified selection-guard warns across every picker surface when a model trains on your data.
- **Catalog wave:** GLM-5.3-Flash, qwen3.8-max/flash, Gemini 3.7 Flash, MiniMax M3 free SKUs, Nemotron 3.5 Lightning, Meta Muse Spark 1.2.
- Prompt caching engaged for LiteLLM Claude on the OpenAI wire; Codex GPT context defaults back to the verified 272K with explicit -900k picker variants.

See [Provider Authentication Reference](provider-authentication.md).

## Security hardening

- **Protected instruction files** — writes to AGENTS.md, skills, and memory stores **always require write approval**, so a prompt-injected agent can't quietly rewrite its own standing orders.
- **Deep redaction sweep** — secret-leak gaps closed across terminal error results, `.env` file reads (via file-read detection), checkpoints, ACP stderr, env-name variants, control-splits, `process(list)`, and SSH target logging.
- **Windows approval coverage** — destructive Windows commands and paths now trip the approval system.
- **macOS TCC signing identity** — permission grants survive every update via `hermes desktop --setup-tcc-identity`.
- **Supply-chain response** — the Blender MCP catalog entry and skill were **removed after an upstream compromise**; plugin installs get Tier-1 security scanning.
- **PKCE cookie fix** — SameSite=None over HTTPS with a matching clear path.

## Sessions & state

- Resumed transcripts **never re-append** (`_db_persisted` stamped at row load).
- Instant session naming from the opening message, sticky across resume.
- Oversized tool results spill to cache instead of being truncated in sandbox-less sessions.

## Gateway & messaging

- **Slack native live cards** (streaming via `chat.startStream`, opt-in plan/task cards) with outbound link-preview suppression.
- **Telegram inline picker** — every command and skill searchable via @botname, bypassing Telegram's command-menu cap.
- **Gateway control socket** — fleet consumers query the gateway (identify/status); updaters pause gateways gracefully instead of tree-killing them.
- **Turn-reaper stack dumps** — when the watchdog fires, wedged worker stacks are captured for diagnosis.
- Split-delivery bug class closed (swallowed finals, split deliveries).
- Relay matured: native plugin init, live-card ops, session-span segmentation, voice-note STT restored.

## Reverted in this window (not shipping)

Do **not** rely on these — they landed and were reverted:

- **Model Council mode (`/council`)**
- **DCP context engine**
- **WS-only gateway server** (#94245, reverted by #96118) — FastAPI remains on the desktop boot path; the seq-stamped event replay (#94219) *did* ship.
- Electron rolled back to 40.10.2.

## Upgrade attention points

1. **Protected instruction files break silent automation**: any cron job, skill, or script that writes to AGENTS.md, skill files, or memory stores now requires write approval. Unattended runs that self-edit their instructions will block — pre-approve via the approval config or restructure the workflow.
2. **Delegation defaults raised** (250 iterations, 10 concurrent children): fleet cost and parallelism behavior changes on upgrade if you relied on the old lower ceilings as guardrails.
3. **Cron continuity**: existing monitors that assumed goldfish memory (no dedupe) will start deduplicating once memory/`continuity=true` is on — review job prompts if output patterns change.
4. **Blender MCP removed**: if you had the Blender MCP server installed from the catalog, remove it and audit anything it touched.
5. **PyPI lag persists**: `pip install -U hermes-agent` yields **0.19.0** as of 2026-09-01 (0.20.x/0.21.0 not yet published). Use `hermes update` or the GitHub installer for 0.21.0. Do not treat PyPI `latest` as the current release.
6. **macOS**: re-run `hermes desktop --setup-tcc-identity` after upgrading so permission grants survive future updates.

## Related docs

- [Hermes Agent 0.19–0.20 Release Wave Reference](hermes-019-020-release-wave.md) — the wave this release rolls up (0.20.1–0.20.6 windows are documented here in full).
- [Hermes Agent 0.16.0 Surface Release Reference](hermes-016-surface-release.md)
- [Quick Setup via Nous Portal](../getting-started/quick-setup-nous-portal.md)
- [MCP Server Setup Reference](mcp-server-setup.md)
- [Provider Authentication Reference](provider-authentication.md)
