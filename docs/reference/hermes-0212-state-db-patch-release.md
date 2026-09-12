---
title: "Hermes Agent 0.21.2 state.db Patch Release Reference"
slug: "hermes-0212-state-db-patch-release"
category: "reference"
tags: ["release-notes", "patch-release", "state-db", "sqlite", "session-store", "multi-profile", "security", "plugins", "cron", "desktop", "providers", "cli"]
sources:
  - "upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.11"
  - "upstream:https://github.com/NousResearch/hermes-agent/compare/v2026.9.7...v2026.9.11"
  - "upstream:https://pypi.org/pypi/hermes-agent/json"
last_updated: "2026-09-12"
version: 1
hermes_version_min: "0.21.2"
---

# Hermes Agent 0.21.2 — The state.db Patch Release

**Release:** v0.21.2 (tag `v2026.9.11`), published September 11, 2026.
**Window:** `v2026.9.7...v2026.9.11` — the four days since v0.21.1.
**Purpose:** close the `state.db` reliability regression class introduced by the v0.21.0 session-store connection rewrite, and roll up main since v0.21.1. For installs whose `state.db` broke after 0.21.0, this is the target release.

## Release window statistics

Measured at commit `04dd80a977f40b05e5b2054111747af07a61886a`:

- **947 non-merge commits** across **1,869 changed files** (+182,504 / −15,564 lines).
- **312 merged PRs** in the release window.
- **140 contributors** across commits, co-author trailers, and salvage credits.

## state.db reliability campaign (the headline)

Six PRs closing 44 issues fix root causes rather than symptoms:

1. **No more second writers.** Four independent writers were corrupting the root `state.db`: profile gateways writing hosted-room state every 5 s, the dashboard opening a writable handle on startup, cron's lifecycle guard doing a raw `open()` on a live database (which cancels the gateway's POSIX locks), and `doctor --fix` checkpointing under a live holder. Fixes: hosted rooms moved to `shared-state.db`, dashboard opens read-only first, the guard goes through the tracked connection registry, `doctor --fix` refuses an unprovable checkpoint. (#108076)
2. **Healthy WAL databases stop wedging.** OpenZFS `(deleted)` dentries and a `close()` racing `append_message` produced a sticky `DeletedWalGenerationError` on healthy stores; the read pool was handed out under an unconfirmed journal mode; a transient `disk I/O error` on WSL2 killed `get_session` on first attempt; a stale "state.db locked" banner persisted after the lock cleared. (#108082)
3. **FTS damage no longer kills the turn.** Full-text-search index errors were misclassified as whole-file corruption and fail-closed the conversation. Now scoped as `fts_index`: search degrades, the index rebuilds later, the transcript store is untouched. Also: honest `doctor` damage naming, FTS write probe catching the stale-index shape, `.recover` tolerating orphan FTS5 shadow tables, header-zeroed databases recoverable, dashboard analytics poller returning 503 instead of tracebacks. (#108130)
4. **One corrupt row no longer kills `sessions list`/export/insights.** A TEXT timestamp or `1e30` epoch crashed the whole listing; malformed marker JSON crashed `json_extract`; >999 ids crashed bulk delete/prune. Fixes: a `coerce_epoch()` helper on every reader (bad rows render `?` plus a WARNING naming the session), `json_valid` guard, IN-list chunking, batched export hydration. (#108086)
5. **Sessions never bind to another profile's database.** Desktop launch backend could pin the wrong profile's `state.db` under a `HERMES_HOME` override race; `session_search` by bare ID silently scanned every profile and could return another profile's transcript; profile delete kept a handle open (WinError 32). (#108074)
6. **Opening state.db no longer takes the write lock when nothing needs writing.** A one-shot `hermes` process behind a busy gateway stalled 4–20 s then failed with `database is locked`; now 0.01 s. (#108067)

Adjacent hardening in the same subsystem: fresh `state.db` no longer publishes FTS tables before owning the rebuild lock (#106311), WAL-generation-lost handles no longer checkpoint stale frames (#106315, #106840), clobbered first pages quarantined with their WAL (#106587), quarantined handles refuse VACUUM/FTS optimize (#106343, #106349).

## Multi-profile isolation hardening

For multi-profile (multiplex) installs: secondary-profile bots no longer inherit the default profile's allow-lists (#107616); adapters no longer send credentials to the default profile's host (#107617); stdio MCP servers no longer receive the default profile's vault secrets (#107630); `MEDIA:` delivery can no longer attach another profile's `.env` / `auth.json` / `state.db` (#107609); Feishu drive callbacks and `/p/<profile>/` webhook replies stay on the routed profile (#107620, #107626); secondary profiles no longer get a sibling's Nous bearer from per-process memos (#107611).

## Other highlights

- **Desktop backend spawn storms fixed** — Bot Mode spawned/dialed one backend per profile per roster tick; roster hover spawned one per row; profile switches could duplicate the primary. (#108069 et al.)
- **Password-blind credential vault** — sign-in, payment, and address fill from 1Password/Bitwarden/local vault without the agent seeing a secret; 2FA from a saved authenticator key or via the user's UI. Private git plugins install with stored credentials. (#106480, #107585, #106981)
- **Plugin catalog** — curated SHA-pinned plugin index with CLI, admission CI, docs, dashboard; one Desktop Plugins page with per-commit pinning; Radio as opt-in SDK plugin.
- **Nous free tier + guided first launch** — free inference/connectors, one-command sign-in, `/login` from chat, connector tools via `tool_search`, `HERMES_GUEST_ONBOARDING=1`.
- **Cron & Kanban fixes** — off-tick "run now" no longer cancels the next scheduled run (#106306); killed manual run no longer blocks the next for 5 min (#106733); one-shot → recurring keeps firing (#106532); unpinned jobs run on creation-snapshot model (#106499); `--clone-all` no longer copies cron jobs (#106478); `kanban promote` refuses undone parents (#106550).
- **Provider routing** — `/model` and auxiliary auto never bill an unselected provider (#107366); never auto-switch to a credential-less provider (#107281); MCP OAuth refresh no longer erases the refresh token (#106185); Anthropic clients send exactly one credential (#107978).
- **CLI** — `hermes -z --resume` continues the session (#106313); update checks poll GitHub API once daily instead of git-fetching every 30 min (#107648); `hermes update` names the real cause and can't hang on a stalled fetch (#108053).

## Updating

- Existing install: `hermes update`
- Fresh install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- **If `state.db` was already damaged by 0.21.0/0.21.1**: run `hermes doctor` first — it now distinguishes structural vs index damage and points at `hermes sessions recover --inspect-only` (profile-pinned) when a rebuild isn't enough.

## Known caveats

1. **PyPI lag persists**: PyPI `latest` still resolves to **0.19.0** as of 2026-09-12. Use `hermes update` or the GitHub installer for 0.21.x; do not treat PyPI as current.
2. **Snapshot-vs-tag semantics**: a git-method install can carry a version label that understates its tree position. Real example from this repo's fleet runtime (2026-09-12): labeled v0.21.0 while sitting +5,322 commits past tag `v2026.8.31`, 673 behind tag `v2026.9.7` (v0.21.1), and 1,659 behind tag `v2026.9.11` (v0.21.2). After v0.21.2 the local install is behind **both** stable tags — record version label and commit distances when describing an install.
3. **Release cadence accelerating**: three stable tags in 11 days (v2026.8.31 → v2026.9.7 → v2026.9.11). Curated notes for the post-0.21.0 window are still deferred to v0.22.0.

## Related docs

- [Hermes Agent 0.21.1 Patch Release Reference](hermes-0211-patch-release.md) — the previous patch rollup.
- [Hermes Agent 0.21.0 Pantheon Release Reference](hermes-021-pantheon-release.md) — the minor release whose session-store rewrite this patch repairs.
- [MCP Server Setup Reference](mcp-server-setup.md)
- [Provider Authentication Reference](provider-authentication.md)
