---
title: "Hermes Agent 0.23.0 Hearth Release Reference"
slug: "hermes-023-hearth-release"
category: "reference"
tags: ["release-notes", "minor-release", "gateway", "webapp", "browser-tools", "delegation", "plugins", "skills", "mcp", "group-chats", "cron", "security", "performance"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.0"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v0.22.0...v0.23.0"
last_updated: "2026-11-06"
version: 1
hermes_version_min: "0.23.0"
---

# Hermes Agent 0.23.0 — The Hearth Release

**Release:** v0.23.0 (tag `v0.23.0`), published November 5, 2026 (21:32 UTC).
**Window:** `v0.22.0...v0.23.0` — rolls up and fully documents the v0.22.1–v0.22.7 patch releases (Oct 14 – Nov 3), whose notes were deferred to this minor.
**Theme:** "The Hearth Release" — v0.22.0 got newcomers through the door; v0.23.0 builds the fire they gather around. One gateway owns every conversation; every surface (CLI, TUI, Desktop, editors, bots, cron) is a client of it.

## Release window statistics

Per the release body (upstream's own measurement):

- **~10,080 commits** since v0.22.0, **~1,950 merged PRs**, **~850 issues closed**, 666 contributors.
- **~8,720 files changed** (+~725,200 / −~201,400 lines).

## Breaking changes and upgrade notes

Verify each of these before upgrading a fleet profile:

1. **The old built-in browser tools are gone.** Browser automation runs on `browser_exec` only; agent-browser and the ten `browser_*` tools (`browser_navigate`, `browser_click`, …) were removed. Homes that used Camofox get the `camofox` plugin installed automatically. **Any prompt, skill, or toolset list naming the old tools must be rewritten to `browser_exec`.** (#143146)
2. **Desktop requires macOS 13+ and 64-bit Windows.** Electron 44 no longer runs on macOS 11, macOS 12, or 32-bit Windows. (#142727)
3. **`hermes mcp serve` is now `hermes mcp-serve`** (moved into a plugin, adds a `--tools` mode). MCP clients that launch Hermes as a server must update their launch command; nothing rewrites it for you.
4. **Word, PowerPoint and Excel skills merge into one `microsoft-office` skill.** Built-in skills drop from 58 to 44; old copies stay on disk until removed manually. 12 niche skills become optional installs.
5. **The Webapp is off by default.** Nothing is served to a browser until `webapp.enabled: true` or Web Access is turned on in Settings.
6. **GitHub Copilot moved to a labs plugin** (`github-copilot`); profiles using Copilot install it automatically. Camofox, `mcp-serve`, agent importers and Singularity also left core for plugins (auto-installed for existing homes except MCP clients, see #3).

## Headline features

### One gateway owns every conversation

Since v0.22.0 the classic CLI, TUI, Desktop, API server, ACP editors, messaging bots and cron all run their sessions through **one gateway per profile** instead of each running its own agent copy against the same chat. v0.23.0 fixed what that broke (slash commands, `/retry`, clarify cards, usage, ACP sessions) and made config changes reach resumed sessions. A chat opened anywhere is the same chat: one queue, one history, one writer. (#106742, #138717, #141105)

### The Webapp: Desktop in a browser tab

With `webapp.enabled: true` the gateway serves the full Desktop workspace (chats, Group Chats, plugins, settings) on its own listener. `hermes webapp` opens it; Desktop's Settings → Web Access exposes it on the LAN or a public URL behind sign-in. Single-user by design: a signed-in tab acts as you. Ships in the Docker image and Nix package. Hardened: launch links are private, CSP sent, loopback-only CORS/WebSocket trust. (#141864, #145598)

### Terminal pictures and rewind

- Inline images in CLI/TUI: real pixels in kitty/Ghostty (CLI+TUI) and iTerm2/WezTerm/Konsole (CLI), coloured blocks elsewhere. Pasted images and tool screenshots render in-chat instead of printing a path. (#147293)
- `/rewind` (or Esc Esc on an empty prompt) in TUI/classic CLI lists earlier prompts; edit and resend one, or fork a new session from that point. The original session is untouched. (#144937)
- `/new` while a turn is running keeps the old session working in the background (Ctrl+X switches back). (#148880)

### Multi-gateway Desktop

Desktop keeps every registered gateway (This device, SSH hosts, URLs) connected at once with instant switching; terminal tabs run on the host they were opened on; Group Chats can mix bots from different machines. (#147681)

### Bot Mode Group Chats that run themselves

Rooms get an opt-in lead bot or `auto` router for messages naming nobody; cron jobs can post into a room via `deliver: room:<id>@<profile>`, waking only @mentioned bots; rooms carry a purpose and shared notes; bot-to-bot exchanges cap at `max_hops` (default 4). `hermes peer dm <peer>/hermes` reaches a peer's default bot. (#144833, #148903)

### Plugins keep themselves current

`hermes plugins update` updates everything at once; opt-in Auto-update (`plugins.auto_apply`, off by default) in CLI/TUI/Desktop/dashboard; updates that would break the setup (e.g. disabling the memory provider) are held back. Catalog grew ~600 → 1,050+ entries; new **Verified** tier for vendor-built integrations. (#141513, #85794)

### Price tags and spend limits on paid MCP tools

MCP servers can declare per-tool cost and a per-chat spend limit; approval prompts show the price and running total, and Hermes asks before exceeding the limit — even in YOLO mode or on trusted servers. (#142470, #143787)

### Pluggable delegation

`delegation.backend` selects how `delegate_task` tasks become child runs; the default strategy is a bundled plugin; the official `advanced-delegation` plugin adds model-map and per-profile routing. `/delegation <mode>` persists, `--now` applies immediately; opt-in `delegation.prefix_stagger_seconds` improves prompt-cache reuse for batch subagents. (#142563, #142564)

### Cron control

`hermes cron cancel` (plus Desktop Stop button, API, `cronjob_manage`) stops a live run; deleting a job cancels it; per-job missed-run policy (`--catch-up on|off`); prompts carry the fire time. (#144801)

### Skills: leaner and lockable

58 → 44 built-in skills; `microsoft-office` merges Word/PowerPoint/Excel; `hermes curator lock <skill>` stops the agent from rewriting a hand-curated skill through **any** tool, even under `--yolo`. Skills leave reload markers through compaction; plugin skills load as `plugin:skill`. (#147557, #146333)

### Security and reliability

- **Secret masking**: quoted secrets, connection strings, glued/flag-passed secrets, Azure keys, non-PEM private keys, SMB passwords. (#149435)
- **Approval gate**: catches `curl … | sudo bash` pipes, delayed/abbreviated PowerShell deletes, credential uploads hidden behind an approved rule; a stale approval card can't approve the next request. (#87362)
- **Network boundaries**: host-parsing-mismatch URLs refused; A2A refuses browser/foreign-Host requests without a token. (#145578)
- **Browser vault**: password-manager plugins register logins via `ctx.register_login_backend` (each sees only its own entries); vault key can live in the OS keychain (`vault.key_storage: keychain`). (#143964)

## Performance (long-lived gateways)

- Recurring cron jobs share one prompt-cache key; one-shot runs send ~1,570 fewer prompt tokens; four tool schemas 319 tokens shorter.
- `patch`/`write_file` return in milliseconds with LSP on (10.1 s → ~0.06 s on a clean TypeScript edit).
- The ~once-a-minute freeze during memory trims is gone; closed sessions release memory; glibc malloc arenas capped at 4.
- Desktop sidebar stays instant with tens of thousands of sessions (one store with ~35k cron runs: 121 s refresh → instant).
- Startup ~1 s faster from git checkouts (git calls 15 → 2).

## New and changed models

- **GLM-5.3 is the silent default** (was GLM-5.2); same price, 1M context on Nous Portal and OpenRouter. (#144810)
- New: GPT-6.1 Terra, DeepSeek V4.1 Flash 1017, Gemini 4 Argon; Claude Mythos treated as always-thinking; Nemotron 3.5 Super VL default parameters.
- `/model reset` un-pins a session without losing the conversation. (#80448)
- Usage-window plans: `/usage` shows one bar per allowance with reset time; pickers tag Large/Free. (#142308)
- Opt-in `agent.daybreak` enables OpenAI Trusted Access for Cyber on account-approved models only. (#148056)
- Local runtime on llama.cpp b11671 (one-slot DFlash drafts, opt-in Nemotron 3.5 Bolt).

## Agent loop and sessions

- **Opt-in prepared compaction** (`compression.prepare_ahead: true`): the next summary is written in the background as the trigger nears; compaction no longer pauses the turn. (#144684)
- **Compaction honesty**: summaries mark uncertain claims on `UNVERIFIED:` lines; `/stop` closes a summary stream; queued messages and `/steer` survive context-exhaustion resets. (#86019)
- **`hermes sessions refresh-prompts`**: continuing sessions pick up edited `SOUL.md`/skills/context on the next turn without `/new` (one cache miss each). (#143581)
- **Opt-in stream lifetime cap** (`agent.stream_max_lifetime`, off by default); timeout errors name the failing phase and the setting to raise. (#80701)
- Session storage: auto-prune opt-in again; `hermes sessions optimize-storage` ~18× faster; `hermes sessions` failures exit 1.

## Messaging platforms

- Every messaging adapter (Signal, Weixin, BlueBubbles, QQ Bot, Yuanbao, WhatsApp Cloud) now ships as a bundled platform plugin — no user-visible change. (#139843)
- Telegram: opt-in `dm_topic_auto_transfer`; video notes; group messages not addressed to the bot can stay silent. (#141347)
- Slack: emoji reactions in thread context; opt-in `thread_followup_silence`. Feishu clarify cards + tap picker. Discord: longer approval timeouts, plain audio attachments. (#80882, #139586)
- Gateway lifecycle safety: `hermes gateway stop`/`restart` refuse while sessions are live and never act on another home's service. (#142041)

## Plugin APIs (for plugin authors)

- `ctx.post_message` (post + edit in place), `ctx.side_question` (ask the session's agent post-turn, consent required), `pre_llm_call` block, `hold_stream`, new hooks `post_compaction` and `on_session_delete`; slash commands receive the calling session.
- Plugin-declared OAuth: `hermes auth add <plugin>:<id>` runs browser sign-in; the token is attached only to the hosts the plugin declared. (#141510)
- Desktop SDK: `ctx.files` (plugin data folder + user-granted folders only), Kanban card badge slot, composer context-menu rows, spell-check words, scriptable preview browser, Settings ▸ Plugins forms.
- Catalog floors: `requires_hermes` blocks installs on too-old Hermes; unknown manifest keys warn instead of fail. (#143468)
- Remote config backend for fleets (opt-in `HERMES_CONFIG_BACKEND=remote`): per-profile `config.yaml` from a central service with admin-locked keys. (#122509)

## MCP

- Tool costs + per-chat spend limits (see headline); Allow-for-session/Always choices actually stick; prompts show arguments with secrets masked. (#143780)
- Live progress for long MCP calls (Desktop tool row, CLI spinner, `tool.progress` events); servers declaring longer deadlines are not cut off. (#141985)
- Experimental MCP events over webhooks: `mcp_servers.<name>.events: true` lets a server notify Hermes; each event starts an agent run through the gateway webhook listener. (#140121)
- Streamable HTTP handles results/tool lists over 1 MiB; client name is `hermes-agent/<version>`.

## Install and update

- `install.sh`/`install.ps1`/Hermes-Setup now check out the **latest stable release**, not `main` tip. (#139311)
- `hermes update`: no longer stashes untracked folders it never touches (asks before stashing anything), reclaims git locks from killed updates, names CDN firewall blocks instead of bare 403s. (#147632)
- First-time `hermes setup` offers import from OpenClaw, Claude Code, Codex CLI or Cursor (agent-importers plugin). (#142556)
- `hermes pm install --without EXTRA` keeps a dropped extra dropped; corrupt cached packages no longer block installs.
- Docker: Webapp bundle ships in the image (plus tmux, Office/PDF libs); root-sandbox files are handed back to the user with setuid/caps stripped. (#145153)
- `hermes --cpu-profile PATH` writes a CPU profile + top-functions summary for any run. (#87545)
- Classic CLI layout is new (resize-surviving transcript); `display.cli_layout: classic` restores the old look. (#139241)

## Notable fixes

- Background completions on Discord/Telegram reach the agent instead of requeueing forever (#139026).
- `/retry` from messaging works again on multi-profile gateways (#139149).
- Gateway whose pid was recycled after SIGKILL no longer exits 75 forever (#139855).
- Long Claude DirectSDK answers no longer cancelled by the stall timer (#142905).
- Edge TTS works again after Microsoft's token change (#140896).
- Stdio MCP servers on multi-profile gateways use their own profile's home (#148129).

## Sources

- Release body (read in full, 81 KB): https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.0
- Compare window: https://github.com/NousResearch/hermes-agent/compare/v0.22.0...v0.23.0
