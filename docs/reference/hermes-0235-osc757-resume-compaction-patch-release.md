---
title: "Hermes Agent 0.23.5 OSC-757 Resume & Compaction Patch Release Reference"
slug: "hermes-0235-osc757-resume-compaction-patch-release"
category: "reference"
tags:
  - release-notes
  - patch-release
  - rollup
  - osc757
  - terminal-resume
  - compaction
  - read-file
  - search-files
  - plugins
  - oauth
  - solstice
  - plugin-api
  - profiles
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.5"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v0.23.4...v0.23.5"
last_updated: "2026-11-28"
version: 1
hermes_version_min: "0.23.5"
---

# Hermes Agent 0.23.5 OSC-757 Resume & Compaction Patch Release Reference

Patch release **v0.23.5** (tag `v0.23.5`, published 2026-11-28T03:20:13Z, release date November 27, 2026 per the release body). It rolls up the window since v0.23.4 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker, and Hermes Cloud. **Full curated notes for this window ship with v0.24.0** — this patch deliberately ships abbreviated notes. Like v0.23.3 and v0.23.4, the release body carries no per-issue fix list; it is a pure rollup plus a deliberately-undocumented feature inventory.

## Window measured at commit `a428f5344f77`

- **338 merged PRs**, 92 closed issues
- **1,262 non-merge commits** across **1,146 changed files** (+57,989 / −5,346)

Cross-check: the compare API reports 1,277 total commits for `v0.23.4...v0.23.5` (1,262 non-merge + 15 merge commits). The compare API's `files` array returns 300 entries (truncated) — the 1,146 changed-files figure is upstream's own measurement and authoritative. At roughly 147% of the v0.23.4 window's merged-PR count (338 vs 229), this window is materially larger than the previous patch's.

## Features shipped in the window but undocumented on purpose

The release body lists these explicitly as "undocumented here on purpose" — full curation deferred to v0.24.0. Treat this list as a feature inventory, not usage documentation:

- **OSC 7577 program resume protocol** support in the CLI and TUI.
- **Idle gateway chats compact in the background on every route.**
- **`read_file` tails with a negative offset and lists directories.**
- **`search_files` says when a content search is the whole answer** (no follow-up read step needed).
- **A bounded default-plugins preflight before the local gateway starts** (Desktop, Docker, and CLI).
- **Plugin OAuth entries that can pin their redirect URI.**
- **The Solstice provider moved to the stateless Interactions API.**
- **New plugin API surfaces**: turn origin, how a session was created, cron scheduling, and gateway silence helpers.
- **The dashboard's "your dashboard is moving" notice.**
- **Raw arrow keys working in the sessions and plugins pickers.**
- **A long series of fixes that keep plugin work bound to the right profile when a profile is renamed, moved, or removed.**

## Updating

- Microsoft Store app: updates through the Store.
- Desktop app installed from the installer (.exe / .dmg): no change in this release; it updates with the next bundled release.
- CLI: `hermes update`, or re-run the installer one-liner.
- Docker / Hermes Cloud: `nousresearch/hermes-agent:stable` (or `:latest`).

## Operational advisory

With no per-issue fix list in the body, the practical upgrade drivers for operators are the profile rename/move/remove binding fixes for plugin work (directly relevant to multi-profile fleets), the bounded default-plugins preflight (safer local-gateway boots on Desktop, Docker, and CLI), and plugin OAuth redirect-URI pinning (security-relevant hardening for plugin OAuth flows). The `read_file` negative-offset tails and directory listing change tool behavior that skills and scripts may rely on. The body mentions no dependency security bumps comparable to v0.23.3's oauthlib/opentelemetry/tornado set. An install left on v0.23.3 is now two stables behind (v0.23.4, v0.23.5) — see the [0.23.4 release reference](hermes-0234-gemini4-models-patch-release.md) for the previous window. Full curated notes and contributor credits arrive with v0.24.0.
