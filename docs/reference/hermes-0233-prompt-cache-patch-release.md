---
title: "Hermes Agent 0.23.3 Prompt-Cache Patch Release Reference"
slug: "hermes-0233-prompt-cache-patch-release"
category: "reference"
tags:
  - release-notes
  - patch-release
  - rollup
  - prompt-caching
  - compaction
  - storage
  - sqlite
  - first-run
  - models
  - appimage
  - security-bumps
  - plugin-catalog
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.3"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v0.23.2...v0.23.3"
last_updated: "2026-11-20"
version: 1
hermes_version_min: "0.23.3"
---

# Hermes Agent 0.23.3 Prompt-Cache Patch Release Reference

Patch release **v0.23.3** (tag `v0.23.3`, published 2026-11-20T00:34:38Z, release date November 19, 2026 per the release body). It rolls up the window since v0.23.2 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker, and Hermes Cloud. **Full curated notes for this window ship with v0.24.0** — this patch deliberately ships abbreviated notes. Unlike v0.23.2, the release body carries no per-issue fix list; it is a pure rollup plus a deliberately-undocumented feature inventory.

## Window measured at commit `caafe5389ae`

- **370 merged PRs**, 60 closed issues
- **1,657 non-merge commits** across **3,948 changed files** (+222,379 / −96,154)

Cross-check: the compare API reports 1,675 total commits for `v0.23.2...v0.23.3` (1,657 non-merge + 18 merge commits). The compare API's `files` array returns 300 entries (truncated) — the 3,948 changed-files figure is upstream's own measurement and authoritative. The window is roughly one fifth the size of the v0.23.1→v0.23.2 window (1,989 PRs), so v0.23.3 is a genuine patch, not a rollup masquerading as one.

## Features shipped in the window but undocumented on purpose

The release body lists these explicitly as "undocumented here on purpose" — full curation deferred to v0.24.0. Treat this list as a feature inventory, not usage documentation:

- **Prompt-cache lifecycle controller** — warming through long tool runs, compaction of idle chats before the 1h cache expires, Nous Portal support for the full 1h lifecycle, and a `prompt_caching.cache_ttl` setting defaulting to `auto`.
- **Compaction archives the tool results it drops** instead of discarding them outright.
- **Proactive tool-result prune on by default.**
- **One-question first-run CLI setup** with the free tier included.
- **GPT-6.2 Astra and GPT-6.2 Sol (+ Pro)** available on OpenRouter and Nous Portal.
- **"Waiting on teammates" strip** above Bot Chat composers.
- **Linux AppImage agent payload run from a stable per-build copy.**
- **Storage layer split** behind a persistence interface with its SQLite backend.
- **Dependency security bumps**: oauthlib, opentelemetry, tornado.
- **A large batch of new plugin-catalog entries.**

## Updating

- Microsoft Store app: updates through the Store.
- Desktop app installed from the installer (.exe / .dmg): no change in this release; it updates with the next bundled release.
- CLI: `hermes update`, or re-run the installer one-liner.
- Docker / Hermes Cloud: `nousresearch/hermes-agent:stable` (or `:latest`).

## Operational advisory

With no per-issue fix list in the body, the practical upgrade drivers for operators are the dependency security bumps (oauthlib, opentelemetry, tornado) and the storage-layer split — a lower-urgency patch than v0.23.2 unless you rely on the affected dependencies. An install left on v0.23.2 misses only this window; an install on v0.23.1 or older also keeps every v0.23.2 bug, including the orphaned-`git`-process-on-CLI-exit issue ([#156616](https://github.com/NousResearch/hermes-agent/issues/156616)) that affects CLI-driven scheduled workflows. Full curated notes and contributor credits arrive with v0.24.0.
