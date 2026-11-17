---
title: "Hermes Agent 0.23.2 Desktop-Streaming Patch Release Reference"
slug: "hermes-0232-desktop-streaming-patch-release"
category: "reference"
tags:
  - release-notes
  - patch-release
  - rollup
  - desktop
  - telegram
  - streaming
  - tui
  - cli
  - webapp
  - plugin-api
  - cron
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.2"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v0.23.1...v0.23.2"
last_updated: "2026-11-17"
version: 1
hermes_version_min: "0.23.2"
---

# Hermes Agent 0.23.2 Desktop-Streaming Patch Release Reference

Patch release **v0.23.2** (tag `v0.23.2`, published 2026-11-16T20:59:18Z, release date November 16, 2026). It rolls up the window since v0.23.1 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker, and Hermes Cloud. **Full curated notes for this window ship with v0.24.0** — this patch deliberately ships abbreviated notes.

## Window measured at commit `ae2a81ccc00`

- **1,989 merged PRs**, 940 closed issues
- **7,918 non-merge commits** across **5,211 changed files** (+239,733 / −22,788)

The window is roughly three times the size of the v0.23.0→v0.23.1 window (618 PRs), so v0.23.2 is a large rollup masquerading as a patch.

## Fixed in the release candidate

Desktop / Telegram reply-streaming and input handling dominate the fix list:

- Desktop chats created by an August build with a bare `custom` provider can send again after updating ([#156545](https://github.com/NousResearch/hermes-agent/issues/156545)).
- A Desktop or TUI reply that streamed beside a todo or memory call now settles instead of leaving the Stop button up ([#156553](https://github.com/NousResearch/hermes-agent/issues/156553)).
- A crash mid-stream on Telegram and other edit-streaming chats no longer shows a duplicate "Recovered reply"; a word holding a key prefix mid-word (`program_id`) is shown on time again ([#156546](https://github.com/NousResearch/hermes-agent/issues/156546)).
- Desktop no longer loses or scrambles typed input while it starts and resumes the last chat ([#156615](https://github.com/NousResearch/hermes-agent/issues/156615), [#156642](https://github.com/NousResearch/hermes-agent/issues/156642)).
- After a reconnect mid-reply, Desktop shows the reply once and in full, attachments included ([#156611](https://github.com/NousResearch/hermes-agent/issues/156611)).
- In the Webapp, opening Hermes Cloud agents while this install is not signed in to Nous Portal now tells you to sign in to Nous Portal instead of redirecting to the Webapp login ([#156652](https://github.com/NousResearch/hermes-agent/issues/156652)).
- Exiting the CLI while its startup update check is waiting on GitHub no longer leaves a `git` process running ([#156616](https://github.com/NousResearch/hermes-agent/issues/156616)).

## Features shipped in the window but undocumented on purpose

The release body lists these explicitly as "undocumented here on purpose" — full curation deferred to v0.24.0. Treat this list as a feature inventory, not usage documentation:

- **Durable subagents** that survive a gateway restart or crash and can be continued on their own conversation.
- **One prompt-cache clock per session.**
- **`hermes fallback check`** — readiness check for the fallback chain.
- **`hermes update --force`** — stops gateways at once instead of draining.
- **One-time `browser_vault` codes** entered from Telegram and Discord.
- **Opt-in shared Telegram DM threads.**
- **Gemini Interactions API by default** for Gemini 3 and later, plus Gemini 4 Carbon.
- **Fast mode for Claude Mythos 5.2.**
- **Per-job cron options**: `wrap_response`, and a fresh thread per run.
- **New plugin APIs**: `ctx.fork_session`, `ctx.redact_text()`, `ctx.register_idle_task`.
- **Compatibility shims** so updates work across module moves.
- **Slimmer macOS bundle** that installs Chromium on first use.
- **A large batch of new plugin-catalog entries.**

## Updating

- Microsoft Store app: updates through the Store.
- Desktop app installed from the installer (.exe / .dmg): no change in this release; it updates with the next bundled release.
- CLI: `hermes update`, or re-run the installer one-liner.
- Docker / Hermes Cloud: `nousresearch/hermes-agent:stable` (or `:latest`).

## Operational advisory

An install left on v0.23.1 or older keeps every bug above. Nothing in the fix list is security-critical or affects a headless gateway's core loop, but [#156616](https://github.com/NousResearch/hermes-agent/issues/156616) (orphaned `git` process on CLI exit during the startup update check) directly affects CLI-driven workflows like scheduled docs jobs that invoke the CLI. Since the window also rolls up module moves with compatibility shims, updating sooner reduces exposure to shim-edge cases. Full curated notes and contributor credits arrive with v0.24.0.
