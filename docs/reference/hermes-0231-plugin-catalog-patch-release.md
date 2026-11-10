---
title: "Hermes Agent 0.23.1 Plugin-Catalog Patch Release Reference"
slug: "hermes-0231-plugin-catalog-patch-release"
category: "reference"
tags:
  - release-notes
  - patch-release
  - plugins
  - plugin-catalog
  - rollup
  - tui
  - group-chats
  - webapp
  - plugin-api
  - cli
  - security
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.1"
  - "upstream:https://github.com/NousResearch/hermes-agent/pull/151860"
  - "upstream:https://github.com/NousResearch/hermes-agent/issues/151856"
last_updated: "2026-11-10"
version: 1
hermes_version_min: "0.23.1"
---

# Hermes Agent 0.23.1 Plugin-Catalog Patch Release Reference

Patch release **v0.23.1** (tag `v0.23.1`, published 2026-11-10T01:42:15Z, release date November 9, 2026). It rolls up the window since v0.23.0 "The Hearth Release" into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker, and Hermes Cloud. Full curated notes for this window ship with v0.24.0.

## Window measured at commit `3b421578588`

- **618 merged PRs**, 409 closed issues
- **2,578 non-merge commits** across **2,781 changed files** (+151,690 / −62,595)

## Headline fix: plugin catalog silently falling back (2 MiB cap)

Since the plugin catalog's site deploy on November 9, 2026, the published `plugin-catalog.json` exceeded the **2 MiB cap** that clients accept — so every install **silently fell back to the catalog it shipped with**. Symptoms on affected installs:

- `hermes plugins install <name>` cannot find plugins added since your last update.
- Installing resolves to the **pinned version your release shipped**, not the current one.
- Newer `removed` entries are missed (uninstalled/renamed plugins keep resolving).

v0.23.1 raises the cap to **16 MiB**, so the live catalog is used again ([#151860](https://github.com/NousResearch/hermes-agent/pull/151860), fixes [#151856](https://github.com/NousResearch/hermes-agent/issues/151856)).

**Operational advisory:** installs that stay on v0.23.0 or older keep falling back until they update. If you are on v0.23.0 and a plugin install "can't find" a newly published plugin or installs an old pin, this is why — update the runtime rather than working around the catalog.

## Features in the window, documented here as a watch list only

The release body intentionally defers these to the v0.24.0 curated notes; they are listed to set expectations for what a v0.23.0 → v0.23.1 (or later) jump includes:

- **Esc backtrack in the TUI and classic CLI** — replaces the rewind list picker.
- **Group chats without Desktop** — group chats that run on a gateway without Desktop, seating bots from other computers.
- **Saved gateway connections shared by Desktop and the Webapp.**
- **In-app browser sign-in with your real browser profile**, filling saved logins from its address bar.
- **`hermes gateway attach`** for local clients.
- **`hermes clipboard image --json`.**
- **Plugin API additions**: session-scoped environment values, plugin JSON-RPC methods and events, `llm.oneshot` auxiliary tasks, a compression-stable `conversation_id`, an `on_session_open` hook in the gateway, and a `post_curator_run` hook.
- Faster transcript and handoff reads.
- A large batch of new plugin-catalog entries.

## Updating

- **Microsoft Store app**: updates through the Store.
- **Desktop app from installer** (.exe / .dmg): no change in this release; updates with the next bundled release.
- **CLI**: `hermes update`, or re-run the installer one-liner.
- **Docker / Hermes Cloud**: `nousresearch/hermes-agent:stable` (or `:latest`).

Full changelog: [v0.23.0...v0.23.1](https://github.com/NousResearch/hermes-agent/compare/v0.23.0...v0.23.1)

## Related docs

- [Hermes Agent 0.23.0 Hearth Release Reference](hermes-023-hearth-release.md)
- [Hermes Agent 0.21.5 Desktop Plugin SDK Patch Release Reference](hermes-0215-desktop-plugin-sdk-patch-release.md)
