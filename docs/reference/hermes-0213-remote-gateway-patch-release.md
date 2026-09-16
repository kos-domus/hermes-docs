---
title: "Hermes Agent 0.21.3 Remote-Gateway Patch Release Reference"
slug: "hermes-0213-remote-gateway-patch-release"
category: "reference"
tags: ["release-notes", "patch-release", "remote-gateway", "desktop", "oauth", "session-expiry", "state-db", "cloud", "json-rpc", "providers", "desktop", "cli"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.14"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v2026.9.11...v2026.9.14"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-16"
version: 1
hermes_version_min: "0.21.3"
---

# Hermes Agent 0.21.3 — Remote-Gateway Patch Release

**Release:** v0.21.3 (tag `v2026.9.14`), published September 14, 2026 (16:04 UTC).
**Window:** `v2026.9.11...v2026.9.14` — the three days since v0.21.2.
**Purpose:** roll up the ~338 PRs merged since v0.21.2 into a stable tagged release for downstream consumers (Docker images, Hermes Cloud, hosted deployments). The tag exists primarily so the remote-gateway sign-in fixes reach Cloud agents, which auto-update to the newest release tag.

## Release window statistics

Measured at commit `9b419a2d3c2657c192008e732149d61170b32c01`:

- **1,036 non-merge commits** across **2,642 changed files** (+131,690 / −37,096 lines).
- **338 merged PRs** in the release window.

## Remote dashboard sessions no longer expire on refresh bursts (the headline)

Symptom: a Desktop wake burst could replay an already-rotated refresh token into the Portal's reuse detection and revoke the whole session — remote dashboard sessions expired on refresh bursts (#110061, fixes #55712).

- Both refresh paths on the gateway — the cookie gate and the desktop's native bearer route — now **coalesce concurrent requests carrying the same rotating refresh token**.
- Refresh also runs **off the event loop**, so a slow identity provider no longer freezes `/api/status`.
- Pairs with Portal-side fix NousResearch/hermes-portal#1209: sliding 30-day idle horizon plus a 5-minute rotated-token grace window.
- Community salvage credit: #71548 (@Doud-FR), #55717 (@liuhao1022).

Relevant to any deployment where Hermes Desktop connects to a remote gateway over an OIDC-style rotating-token flow.

## Long-lived processes stop leaking duplicate state.db writer handles

Continuation of the v0.21.2 state.db reliability campaign (#110934, fixes #100896, #103339):

- Gateway, dashboard/Desktop backend, ACP, and CLI readers now **attach read-only**.
- **In-process writers share the registry handle**, so the `N live SessionDB handles` precursor stops firing on a healthy topology.

## Also in the window (undocumented upstream, listed for tracking)

- **Server→client JSON-RPC requests** and a Pydantic wire-contract registry with generated TS/OpenRPC for the TUI/Desktop gateway (#110521, #110522).
- **Reasoning-effort selection** on every model picker, a composer pill, and per-auxiliary control in Desktop.
- **OpenRouter OAuth PKCE login.**
- **HEIF/HEIC/AVIF image decoding.**
- **Honcho peer-model setup rework.**
- **MCP OAuth refresh tokens bound to their issuer** + a daily MCP re-auth nudge in Desktop.
- **FAL catalog additions**: Wan 3.0, Kling 3.0 / Kling Image v3, MiniMax H3 Max Turbo, Gemini Omni Flash 1.1, Meta Muse.
- **Slack pasted tables** and the **Agent Sessions API**.
- **Multiplexed-profile isolation** and gateway-liveness fixes.
- **state.db WAL refusal on cross-VM filesystems** (WAL mode is not safe there; the runtime now refuses rather than corrupts).

Full curated release notes for the whole post-v0.21.0 window ship with **v0.22.0** — nothing in the window is skipped there.

## Updating

- Existing install: `hermes update`
- Fresh install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- Docker / Hermes Cloud: images build from this tag (`nousresearch/hermes-agent:v2026.9.14`).

## Known caveats

1. **PyPI lag persists**: PyPI `latest` still resolves to **0.19.0** as of 2026-09-16. Use `hermes update` or the GitHub installer for 0.21.x; do not treat PyPI as current.
2. **Snapshot-vs-tag semantics**: a git-method install can carry a version label that understates its tree position. Real example from this repo's fleet runtime (2026-09-16): labeled v0.21.0 while sitting +5,322 commits past tag `v2026.8.31`, 1,659 behind tag `v2026.9.11` (v0.21.2), and 2,698 behind tag `v2026.9.14` (v0.21.3). Record version label and commit distances when describing an install.
3. **Release cadence still accelerating**: four stable tags in 14 days (v2026.8.31 → v2026.9.7 → v2026.9.11 → v2026.9.14). Curated notes for the post-0.21.0 window remain deferred to v0.22.0.

## Related docs

- [Hermes Agent 0.21.2 state.db Patch Release Reference](hermes-0212-state-db-patch-release.md) — the previous patch rollup whose reliability campaign this release extends.
- [Hermes Agent 0.21.1 Patch Release Reference](hermes-0211-patch-release.md)
- [Hermes Agent 0.21.0 Pantheon Release Reference](hermes-021-pantheon-release.md)
- [Connect Hermes Desktop to a Remote Gateway](../guides/desktop-remote-gateway.md) — the deployment pattern the headline fix protects.
