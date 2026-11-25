---
title: "Hermes Agent 0.23.4 Gemini-4 Models Patch Release Reference"
slug: "hermes-0234-gemini4-models-patch-release"
category: "reference"
tags:
  - release-notes
  - patch-release
  - rollup
  - models
  - gemini
  - gateway-migration
  - plugins
  - desktop
  - sandbox-approvals
  - skills-config
  - plugin-catalog
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.4"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v0.23.3...v0.23.4"
last_updated: "2026-11-25"
version: 1
hermes_version_min: "0.23.4"
---

# Hermes Agent 0.23.4 Gemini-4 Models Patch Release Reference

Patch release **v0.23.4** (tag `v0.23.4`, published 2026-11-24T08:17:06Z, release date November 23, 2026 per the release body). It rolls up the window since v0.23.3 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker, and Hermes Cloud. **Full curated notes for this window ship with v0.24.0** — this patch deliberately ships abbreviated notes. Like v0.23.3, the release body carries no per-issue fix list; it is a pure rollup plus a deliberately-undocumented feature inventory.

## Window measured at commit `8fc03744473`

- **229 merged PRs**, 281 closed issues
- **1,122 non-merge commits** across **1,316 changed files** (+96,873 / −6,703)

Cross-check: the compare API reports 1,143 total commits for `v0.23.3...v0.23.4` (1,122 non-merge + 21 merge commits). The compare API's `files` array returns 300 entries (truncated) — the 1,316 changed-files figure is upstream's own measurement and authoritative. At roughly 62% of the v0.23.3 window's PR count (229 vs 370 merged PRs), this is a genuine patch, not a rollup masquerading as one.

## Features shipped in the window but undocumented on purpose

The release body lists these explicitly as "undocumented here on purpose" — full curation deferred to v0.24.0. Treat this list as a feature inventory, not usage documentation:

- **Gemini 4 Hydrogen, Neon, and Carbon** available on Nous Portal, OpenRouter, and Vertex.
- **`hermes gateway migrate --backends`** — moves an old serve/dashboard backend onto the gateway, surfaced with a System page card in the dashboard.
- **`hermes plugins config`** — edit a plugin's settings from the terminal.
- **Approval cards in Desktop for a sandbox's folder and site requests.**
- **Gateway clients announce who they are** so plugins can see which client sent a turn.
- **Desktop streaming and transcript performance work** (long run).
- **Retryable indicator for slow profile switches.**
- **`hermes dashboard password` without a TTY prompt.**
- **Configurable skill index description length** via the `skills.index_desc_limit` setting.
- **Managed-scope config honored by security and URL-safety reads.**
- **A large batch of new plugin-catalog entries.**

## Updating

- Microsoft Store app: updates through the Store.
- Desktop app installed from the installer (.exe / .dmg): no change in this release; it updates with the next bundled release.
- CLI: `hermes update`, or re-run the installer one-liner.
- Docker / Hermes Cloud: `nousresearch/hermes-agent:stable` (or `:latest`).

## Operational advisory

With no per-issue fix list in the body, the practical upgrade drivers for operators are the gateway backend migration path (`hermes gateway migrate --backends`) and the managed-scope alignment for security and URL-safety reads. The body mentions no dependency security bumps comparable to v0.23.3's oauthlib/opentelemetry/tornado set, so this is a lower-urgency patch: an install left on v0.23.3 misses only this window. Full curated notes and contributor credits arrive with v0.24.0.
