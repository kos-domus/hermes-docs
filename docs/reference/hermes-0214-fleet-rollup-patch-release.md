---
title: "Hermes Agent 0.21.4 Fleet Rollup Patch Release Reference"
slug: "hermes-0214-fleet-rollup-patch-release"
category: "reference"
tags: ["release-notes", "patch-release", "gateway", "singleton-lock", "desktop", "cli", "stream-json", "skills", "auto-load", "mcp", "discovery-concurrency", "session-search", "security", "unauthorized-dm", "plugins", "cron", "kanban", "state-db"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.21"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v2026.9.14...v2026.9.21"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-22"
version: 1
hermes_version_min: "0.21.4"
---

# Hermes Agent 0.21.4 — Fleet Rollup Patch Release

**Release:** v0.21.4 (tag `v2026.9.21`), published September 21, 2026 (18:10 UTC).
**Window:** `v2026.9.14...v2026.9.21` — the seven days since v0.21.3.
**Purpose:** patch release rolling up the ~1,800 PRs merged since v0.21.3 into a stable tagged release for downstream consumers (Docker images, Hermes Cloud, hosted deployments). Full curated notes for this window are deferred to v0.22.0.

## Release window statistics

Measured at commit `4b8a8134009a8727a289bcabeb0019fedd353128`:

- **5,071 non-merge commits** across **5,169 changed files** (+312,961 / −62,855 lines).
- **1,812 merged PRs** and **2,116 closed issues** in the release window.

The largest patch window since the post-0.21.0 rollup series began — nearly 5.4× the v0.21.3 window's commit count.

## Gateway singleton lock + Desktop attach (the headline for multi-process hosts)

- A **host-wide gateway singleton lock with a rendezvous record** prevents two gateway backends from running concurrently on the same host.
- **Desktop now attaches to the running host backend** instead of spawning a second one — the classic "Desktop opened a parallel gateway and split my sessions" failure mode.

Relevant to any host where Hermes Desktop and a systemd/CLI gateway coexist (this fleet's exact topology: `hermes-gateway.service` + Desktop).

## Also in the window (undocumented upstream, listed for tracking)

- **Backend-owned connector operation** with a setup card on Desktop, TUI, and CLI.
- **`--format stream-json`** — structured JSONL output for the CLI (machine-readable agent runs).
- **`skills.auto_load`** — pin skills into every new session's prompt without per-session loading.
- **Desktop**: chat/UI font picker, one-click local engine updates, plugin uninstall from the Plugins hub.
- **`decline` unauthorized-DM behavior** for the gateway — a security posture option for unsolicited DMs.
- **`mcp.discovery_concurrency`** — configurable MCP discovery connect cap (bounds fan-out at startup).
- **`session_search` after/before bounds** plus an OR-relaxed recall retry.
- **`hermes sessions set-journal-mode`** — journal-mode control per sessions store.
- **Video catalog additions**: LTX 2.5 and Kling O3.
- **Catalog website**: a page for every plugin and author, pinned-commit READMEs, added/updated sorting.
- **~12 new community plugins**: tailscale, ssh, shodan, terminal, rss, resetwatch, done-bell, kiwi, cognee, Octen.
- A large run of **profile/multiplex isolation, cron, kanban, Desktop, and state.db fixes**.

Full curated release notes for the whole post-v0.21.0 window ship with **v0.22.0** — nothing in the window is skipped there.

## Updating

- Existing install: `hermes update`
- Fresh install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- Docker / Hermes Cloud: images build from this tag (`nousresearch/hermes-agent:v2026.9.21`).

## Known caveats

1. **PyPI lag persists**: PyPI `latest` still resolves to **0.19.0** as of 2026-09-22. Use `hermes update` or the GitHub installer for 0.21.x; do not treat PyPI as current.
2. **Curated notes deferred**: this tag's release body is explicitly a rollup summary; feature-level documentation arrives with v0.22.0.
3. **Snapshot-vs-tag semantics**: a git-method install can carry a version label that understates its tree position. Real example from this repo's fleet runtime (2026-09-22): labeled v0.21.0 while sitting +5,322 commits past tag `v2026.8.31`, 7,871 behind tag `v2026.9.21` (v0.21.4), 7,977 behind main. Record version label and commit distances when describing an install.

## Security note

PyPI JSON still lists 4 OSV advisory entries = 2 unique CVEs (GHSA-xq8w-9jvx-gm3v / CVE-2026-10221 injection in `_compress_context` ≤0.12.0; GHSA-pmqc-57g8-c22c / CVE-2026-10224 resource consumption in feishu webhook ≤2026.4.30), each mirrored as PYSEC entries. Affected ranges unchanged; local runtime v0.21.0 is newer than both — not vulnerable. GitHub repo security advisories: none published.

## Related docs

- [Hermes Agent 0.21.5 Desktop Plugin SDK Patch Release Reference](hermes-0215-desktop-plugin-sdk-patch-release.md) — the next patch rollup.
- [Hermes Agent 0.21.3 Remote-Gateway Patch Release Reference](hermes-0213-remote-gateway-patch-release.md) — the previous patch rollup.
- [Hermes Agent 0.21.2 state.db Patch Release Reference](hermes-0212-state-db-patch-release.md)
- [Hermes Agent 0.21.0 Pantheon Release Reference](hermes-021-pantheon-release.md)
