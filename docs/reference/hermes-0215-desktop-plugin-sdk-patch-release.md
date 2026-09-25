---
title: "Hermes Agent 0.21.5 Desktop Plugin SDK Patch Release Reference"
slug: "hermes-0215-desktop-plugin-sdk-patch-release"
category: "reference"
tags: ["release-notes", "patch-release", "desktop", "plugin-sdk", "connectors", "mcp", "plugins", "catalog", "i18n", "voice-shortcuts", "gateway-standalone", "multiplexer", "live-dock", "kanban", "webhooks", "models", "performance"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.24"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v2026.9.21...v2026.9.24"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-25"
version: 1
hermes_version_min: "0.21.5"
---

# Hermes Agent 0.21.5 — Desktop Plugin SDK Patch Release

**Release:** v0.21.5 (tag `v2026.9.24`), published September 24, 2026 (10:09 UTC).
**Window:** `v2026.9.21...v2026.9.24` — the three days since v0.21.4.
**Purpose:** patch release rolling up the ~460 PRs merged since v0.21.4 into a stable tagged release for downstream consumers (Docker images, Hermes Cloud, hosted deployments). Full curated notes for this window are deferred to v0.22.0.

## Release window statistics

Measured at commit `f97608f178d1ffeca59860195ab7da295f7c8e5f` (per the release body):

- **1,610 non-merge commits** across **4,828 changed files** (+164,132 / −149,440 lines).
- **460 merged PRs** and **475 closed issues** in the release window.

Note: the GitHub compare API reports `files: 300` for this window — that is the endpoint's hard truncation cap, not the real count. Always take file/commit totals from the release body verbatim (upstream's own measurement commit) or measure locally with `git rev-list` after fetching the tag. Local measurement: `git rev-list --count v2026.9.21..v2026.9.24` = 1,638 (includes merge commits; consistent with the body's 1,610 non-merge figure).

## Desktop plugin SDK wave (the headline for plugin authors)

A broad SDK surface for Desktop plugins, all landed in this window:

- **Composer draft API** — plugins can read/manipulate the message being composed.
- **Session-list and row-decoration slots** — custom rendering in session lists.
- **Sidebar nav preferences** and an **appearance-settings slot**.
- **Model-pill label providers** — plugins can relabel/annotate the model picker pill.
- **Typed bridges** for settings, skills, toolsets, and profiles.
- **Sandboxed embed primitive** — safely embed plugin UI.
- **Public event bridge** for plugin backends.

## Connectors page replaces the MCP tab

- The Desktop **Connectors page** replaces the old MCP tab.
- **"Connect now"** action for a freshly installed plugin's MCP servers.
- Installed plugins' **tools and skills go live in every open chat** without restart.
- Onboarding now offers **catalog plugins beside connectors**.

## Also in the window (undocumented upstream, listed for tracking)

- **Simple/Advanced interface mode** for Desktop.
- Complete **French, German, and Spanish Desktop catalogs** plus an **RTL/LTR text direction** setting.
- **Custom model entry** from the composer and Settings pickers.
- **Function-key and dictation voice shortcuts**.
- **Per-profile stop/start/restart** under the host multiplexer, with **`gateway.standalone`** to opt a profile out — relevant to multi-profile hosts.
- **Live dock** showing the standing `/goal` and queued prompts in the CLI and TUI.
- **Kanban design pass**: two-column ticket modal, markdown task text.
- **Webhook deliveries mirrored into the target chat session**.
- **Bot Screen** on hosted `-desktop` images.
- **GPT-6 Sol/Terra/Luna and Claude Opus 5.5** in the Nous and OpenRouter catalogs.
- An official **Blender Lab integration** and **NVIDIA app/Broadcast plugins**.
- A long run of **hot-path performance work**: config loading, tool registry, gateway message handling, model picker.
- Dozens of **new community plugins** in the catalog.

Full curated release notes for the whole post-v0.21.0 window ship with **v0.22.0** — nothing in the window is skipped there.

## Updating

- Existing install: `hermes update`
- Fresh install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- Docker / Hermes Cloud: images build from this tag (`nousresearch/hermes-agent:v2026.9.24`).

## Known caveats

1. **PyPI lag persists**: PyPI `latest` still resolves to **0.19.0** as of 2026-09-25. Use `hermes update` or the GitHub installer for 0.21.x; do not treat PyPI as current.
2. **Curated notes deferred**: this tag's release body is explicitly a rollup summary; feature-level documentation arrives with v0.22.0.
3. **Snapshot-vs-tag semantics**: a git-method install can carry a version label that understates its tree position. Real example from this repo's fleet runtime (2026-09-25): labeled v0.21.0 while sitting +5,322 commits past tag `v2026.8.31`, 9,509 behind tag `v2026.9.24` (v0.21.5), 11,610 behind main. Record version label and commit distances when describing an install.

## Security note

PyPI JSON lists 4 OSV advisory entries = 2 unique CVEs (GHSA-xq8w-9jvx-gm3v / CVE-2026-10221 injection in `_compress_context` ≤0.12.0; GHSA-pmqc-57g8-c22c / CVE-2026-10224 resource consumption in feishu webhook ≤2026.4.30), each mirrored as PYSEC entries. Affected ranges unchanged; local runtime v0.21.0 is newer than both — not vulnerable. GitHub repo security advisories: none published (0).

## Related docs

- [Hermes Agent 0.21.4 Fleet Rollup Patch Release Reference](hermes-0214-fleet-rollup-patch-release.md) — the previous patch rollup.
- [Hermes Agent 0.21.3 Remote-Gateway Patch Release Reference](hermes-0213-remote-gateway-patch-release.md)
- [Hermes Agent 0.21.0 Pantheon Release Reference](hermes-021-pantheon-release.md)
