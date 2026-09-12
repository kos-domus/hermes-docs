---
title: "Hermes Agent 0.21.1 Patch Release Reference"
slug: "hermes-0211-patch-release"
category: "reference"
tags: ["release-notes", "patch-release", "rollup", "performance", "modularization", "mcp", "cron", "delegation", "desktop", "providers", "cli"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.7"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v2026.8.31...v2026.9.7"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-12"
version: 2
hermes_version_min: "0.21.1"
---

# Hermes Agent 0.21.1 — Patch Rollup Release

**Release:** v0.21.1 (tag `v2026.9.7`), published September 7, 2026.
**Window:** `v2026.8.31...v2026.9.7` — since v0.21.0 "Pantheon".
**Purpose:** a patch tag that rolls up current main since v0.21.0 for tagged deployments and downstream consumers. It is **not** a feature-announcement release — full curated release notes for this window ship with v0.22.0.

## Release window statistics

Measured at commit `6178e9f4eed8d99f4fc550add939d58c7bed6206`:

- **5,139 non-merge commits** across **4,364 changed files** (+601,014 / −768,419 lines).
- **632 merged PRs** in the release window at preparation time.
- Figures exclude the release-version commit.

The large negative line delta (net −167K lines) reflects the codebase **modularization** work — this window restructured the tree rather than growing it.

## What the rollup contains

The release does not enumerate every change, but names these areas:

- **Codebase modularization** — the internal tree was reorganized into modules.
- **File-operation and startup performance** — faster file ops and cold starts.
- **Provider and model updates** — catalog and provider refreshes.
- **Desktop session controls and browser annotations** — session management plus annotation capability in the desktop browser surface.
- **MCP authorization improvements** — hardened MCP auth flows.
- **Cron scheduling and delivery fixes** — reliability fixes in the scheduler and message delivery path.
- **Delegation reliability improvements** — `delegate_task`/subagent robustness.

When v0.22.0 ships its curated notes, this doc should link them and absorb feature-level detail.

## Upgrade paths

- Existing install: `hermes update`
- Fresh install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- Managed deployments: update through your deployment tooling using the new tag.

## Known caveats

1. **PyPI lag persists**: `pip install -U hermes-agent` still yields **0.19.0** as of 2026-09-08. Use `hermes update` or the GitHub installer for 0.21.x. Do not treat PyPI `latest` as the current release.
2. **Full release notes deferred**: do not expect a feature-by-feature changelog at this tag — v0.22.0 will carry the curated notes for the whole window since v0.21.0.
3. **Snapshot-vs-tag semantics**: if your install tracks main (git method), the version label can understate tree position. Example from this repo's own fleet runtime on 2026-09-08: labeled v0.21.0 while sitting +5,322 commits past tag `v2026.8.31` and ~698 behind main tip. Always record version label **and** commit distance when describing an install.

## Related docs

- [Hermes Agent 0.21.2 state.db Patch Release Reference](hermes-0212-state-db-patch-release.md) — the follow-up patch that repairs the state.db reliability regressions from the v0.21.0 session-store rewrite.
- [Hermes Agent 0.21.0 Pantheon Release Reference](hermes-021-pantheon-release.md) — the minor release this patch rolls up.
- [Hermes Agent 0.19–0.20 Release Wave Reference](hermes-019-020-release-wave.md)
- [MCP Server Setup Reference](mcp-server-setup.md)
- [Provider Authentication Reference](provider-authentication.md)
