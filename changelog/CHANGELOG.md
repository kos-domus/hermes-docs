# Hermes Docs Changelog

Log of every Kos elaboration run on this repository.

## 2026-09-12

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check — STABLE ADVANCE**: GitHub stable moved v0.21.1 → **v0.21.2 (tag `v2026.9.11`, published 2026-09-11T19:20:31Z, prerelease=false)** — "The state.db Patch Release". Window since v0.21.1: 947 non-merge commits, 1,869 files, 312 merged PRs, 140 contributors. Headline: state.db reliability campaign (six PRs, 44 issues closed) fixing the second-writer/WAL-wedge/FTS-misclassification/corrupt-row regressions from the v0.21.0 session-store rewrite; plus multi-profile isolation hardening, Desktop spawn-storm fixes, password-blind credential vault, SHA-pinned plugin catalog, Nous free tier. Verified against the paginated releases list. PyPI still lags at 0.19.0. GitHub security advisories for the repo: none published.
- **Added**: `hermes-0212-state-db-patch-release` — new reference doc for the v0.21.2 patch release (upstream-sourced ingestion pattern; `docs/index.yaml` regenerated with doc_count 27, entry inserted adjacent to the other release references, no reordering churn).
- **Updated**: `hermes-0211-patch-release` — version 2: cross-link to the new 0.21.2 doc (successor patch), `last_updated` bump.
- **Repo hygiene recovery**: removed stray root `.elaboration.log` — a mis-pathed artifact committed by the 2026-09-10 run (`eefcac0`) that bypassed `logs/daily-elaboration.log`; now gitignored. Also noted: the 2026-09-11 run (`5eaf0bf`) committed empty (log+changelog missing) — this block restores changelog continuity; both anomalies called out here rather than silently papered over.
- **Local runtime**: still v0.21.0 snapshot (+5,322 past tag `v2026.8.31`), now 1,752 commits behind upstream main per `hermes --version` (rev-list cross-check post-fetch: 1,752, zero drift; was 942-972 on 09-09 — upstream burst ~780/24h). Behind both stable tags: 673 behind `v2026.9.7` (v0.21.1), 1,659 behind `v2026.9.11` (v0.21.2). v0.21.2 upgrade available via `hermes update`; not applied by this docs run (docs cycle does not upgrade the runtime).
- **Self-assessment**: upstream-sourced ingestion run — robust session discovery (`grep -E 'status:\s*["']?ready'` over all 8 session files), release verified against the paginated releases list (not the single `latest` endpoint), gitleaks passed before commit, staged set limited to the new doc + 0211 update + index + log + changelog + hygiene removal (`.elaboration.log` deletion + `.gitignore`). One cron-guard hit: `python3 -c` inline in a validation one-liner blocked (known); redone with sed+grep only.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.11, https://github.com/NousResearch/hermes-agent/compare/v2026.9.7...v2026.9.11, https://pypi.org/pypi/hermes-agent/json


## 2026-09-09

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: GitHub stable unchanged at v0.21.1 (tag `v2026.9.7`, published 2026-09-07T22:17:01Z, already ingested 2026-09-08 as `hermes-0211-patch-release`); verified against the paginated releases list. No new prereleases/tags beyond v2026.9.7. PyPI still lags at 0.19.0. No docs or index changes (skip contract: zero churn).
- **Local runtime**: still v0.21.0 snapshot, now 942 commits behind upstream main per `hermes --version` (rev-list cross-check post-fetch: 972; spread from concurrent upstream pushes during the two measurements; was 697 yesterday — upstream burst ~245-275/24h). v0.21.1 upgrade available via `hermes update`; not applied by this docs run.
- **Self-assessment**: clean skip run — robust session discovery (`grep -E 'status:\s*["']?ready'` over all 8 session files, statuses enumerated individually), zero docs/index churn, gitleaks passed before commit, only `logs/daily-elaboration.log` + this changelog block staged.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.7, https://pypi.org/pypi/hermes-agent/json

## 2026-09-08

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check — STABLE ADVANCE**: GitHub stable moved v0.21.0 → **v0.21.1 (tag `v2026.9.7`, published 2026-09-07T22:17:01Z, prerelease=false)**. Patch rollup of main since v0.21.0: 5,139 non-merge commits, 4,364 files, 632 merged PRs; areas: modularization, file-op/startup perf, provider updates, desktop session controls + browser annotations, MCP auth, cron scheduling/delivery fixes, delegation reliability. Full curated notes deferred to v0.22.0. PyPI still lags at 0.19.0. No new prereleases/tags beyond v2026.9.7.
- **Added**: `hermes-0211-patch-release` — new reference doc for the v0.21.1 patch release (upstream-sourced, per the stable-release-ingestion pattern; `docs/index.yaml` regenerated with doc_count 26, new entry inserted adjacent to the other release references, no reordering churn).
- **Local runtime**: still v0.21.0 snapshot, now 697 commits behind upstream main (`hermes --version`; rev-list cross-check: 698, drift of 1 from concurrent pushes; was 265 yesterday — upstream burst ~430/24h). v0.21.1 upgrade available via `hermes update`; not applied by this docs run (docs cycle does not upgrade the runtime).
- **Self-assessment**: upstream-sourced ingestion run — robust session discovery (`grep -E 'status:\s*["']?ready'`), release verified against the **paginated releases list** (not the single `latest` endpoint, which can lag hours after a stable advance), zero session churn, gitleaks passed before commit, only the new doc + index + log + this changelog block staged.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.7, https://github.com/NousResearch/hermes-agent/compare/v2026.8.31...v2026.9.7, https://pypi.org/pypi/hermes-agent/json

## 2026-09-07

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: GitHub stable unchanged at v0.21.0 "Pantheon" (v2026.8.31, published 2026-08-31T19:29:49Z); no new prereleases/tags since. PyPI still lags at 0.19.0. Local runtime v0.21.0, now 265 commits behind upstream main (rev-list cross-check: 266; was 18 yesterday — upstream burst ~250 commits/24h, no new tag yet). GitHub security advisories for the repo: none published. Direct OSV API query blocked by cron security scanner (lookalike-TLD heuristic on `.dev`); previous OSV snapshot (2026-09-05) had both advisories in ranges ≤0.12.0 / ≤2026.4.30, local v0.21.0 not affected. No docs or index changes (skip contract: zero churn).
- **Self-assessment**: clean skip run — robust session discovery (`grep -E 'status:\s*["'\'']?ready'`), zero docs/index churn, gitleaks passed before commit, only `logs/daily-elaboration.log` + this changelog block staged. Behind-count cross-checked via `hermes --version` (265) vs `git fetch` + `rev-list --count HEAD..origin/main` (266, drift of 1 from concurrent upstream pushes during measurement) — recorded both, semantics: local-behind-main-tip.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31, https://pypi.org/pypi/hermes-agent/json

## 2026-09-02

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: GitHub stable unchanged at v0.21.0 "Pantheon" (v2026.8.31, published 2026-08-31T19:29:49Z); no new prereleases/tags since. PyPI still lags at 0.19.0. No docs or index changes (skip contract: zero churn).
- **Self-assessment**: clean skip run — robust session discovery (`grep -E 'status:\s*["\']?ready'`), zero docs/index churn, gitleaks passed before commit, only `logs/daily-elaboration.log` + this changelog block staged. Approval-guard quirks hit (curl|python3 and `python3 -c` both blocked in cron): fell back to `gh --jq` + `grep -o` on a saved JSON file, per skill guidance.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31, https://pypi.org/pypi/hermes-agent/json

## 2026-05-24 — Repo bootstrap

- **Created**: repo scaffold mirroring `openclaw-docs` structure (Diátaxis docs/, sessions/, changelog/, strategy/, skill-draft/, assets/)
- **Added**: `README.md`, `CLAUDE.md` (Kos elaboration instructions), `CONTRIBUTING.md`, `LICENSE` (MIT), `index.yaml`
- **Sources**: bootstrap, no sessions processed yet
- **Hermes baseline**: 0.14.0 (installed via PyPI on 2026-05-23 Step 1 Kos personal migration)
- **Next**: first sessions to ingest will be Step 2 fleet migration (2026-05-24) and Step 1 Kos personal migration (2026-05-23)

## 2026-05-26
- **Added**: provider-chain-subscription-oauth — Guide for configuring a five-tier subscription-first OAuth fallback chain.
- **Added**: oauth-credential-separation — Concept doc explaining why Hermes keeps OAuth sessions separate from vendor CLIs.
- **Added**: provider-authentication — Reference matrix for provider names, auth modes, endpoints, and profile-fleet config targets.
- **Added**: provider-and-gateway-errors — Troubleshooting page for Gemini, OpenRouter, Z.AI, Codex OAuth, and profile procedure path errors.
- **Sources**: sessions/2026-05-25-hermes-provider-chain-v4-sub-oauth-capture-fix.md

## 2026-05-27
- **Added**: mcp-fleet-propagation — Guide for propagating MCP servers across a multi-profile Hermes fleet with per-profile domain mapping.
- **Added**: mcp-server-setup — Reference for MCP config syntax, CLI commands, OAuth token persistence, and validated server catalog.
- **Added**: mcp-errors — Troubleshooting page for MCP CLI argparse bug, OAuth timeout, SSH tunnel callback failures, and per-profile auth issues.
- **Updated**: oauth-credential-separation — Added MCP OAuth section explaining per-profile token separation for MCP servers (same anti-rotation rationale as provider OAuth).
- **Updated**: provider-and-gateway-errors — Added MCP tag and cross-links to new MCP troubleshooting docs.
- **Sources**: sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md

## 2026-05-28
- **Added**: codex-gpt55-errors — Troubleshooting flow for Codex `gpt-5.5` `NoneType` stream crashes versus no-first-byte silent rejects.
- **Added**: config-migration-v24 — Reference for Hermes config v23→v24 migration, moved sections, daemon restarts, and rollback.
- **Added**: elevenlabs-tts — Guide for least-privilege ElevenLabs TTS setup, Italian voice discovery, and Telegram sample delivery.
- **Added**: skill-consolidation-pattern — Concept doc for turning scattered workflow prompts into a single lazy-loaded skill source of truth.
- **Added**: self-improvement-agent-safety — Concept doc for safely designing a self-improvement Hermes profile with deterministic gates.
- **Updated**: provider-and-gateway-errors — Added Codex error routing and cross-link to the dedicated Codex troubleshooting page.
- **Sources**: sessions/2026-05-27-hermes-pull-105-commits-codex-fix-tts-cornelia.md, sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md

## 2026-06-02
- **Added**: cron-script-execution — Reference for profile-local cron script resolution, containment, wrapper execution, and immediate test commands.
- **Added**: cron-script-wrapper-pattern — Guide for using real profile-local wrapper files that exec external canonical scripts without copy drift.
- **Added**: cron-script-errors — Troubleshooting page for `Script not found` and `Blocked: script path resolves outside the scripts directory`.
- **Updated**: self-improvement-agent-safety — Added cron script containment as a self-improvement profile safety control.
- **Sources**: sessions/2026-06-01-cron-script-containment-fix.md

## 2026-06-05
- **Added**: fleet-learner-architecture — Concept doc for the Fleet Learner pattern: 3-layer memory model, targeted-edit operations, Temporal-Truth rules, ADD-only vs targeted-edit by layer, cross-layer dedup, forward-looking yield.
- **Added**: capability-matrix-allowlist — Guide for data-not-prosa read derogations: 0444 deploy-only YAML allowlist, deny-glob patterns, MCP sandbox parity, re-baseline flow, partial read enforcement caveats.
- **Added**: xai-oauth-remote-session — Troubleshooting for xAI OAuth over SSH: SSH tunnel flow, `--manual-paste` with full callback URL, `hermes auth reset` for state mismatch, `hermes proxy` scope note.
- **Updated**: self-improvement-agent-safety — Added Fleet Learner mode section, CSO tiered gating (Tier-1/2/3), capability-matrix cross-link, MCP filesystem sandbox narrowing, bearer-at-rest in `request_dump_*.json`, re-baseline flow, partial enforcement note.
- **Updated**: provider-and-gateway-errors — Added `hermes login` deprecation note + cross-link to new xAI OAuth troubleshooting page.
- **Sources**: sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md
## 2026-06-09
- **Added**: gws-profile-credentials — Troubleshooting flow for profile-local Google Workspace CLI credentials, `credentials.enc`, and HOME-scoped re-authentication.
- **Updated**: codex-gpt55-errors — Added the `HTTP 401 token_expired` Codex outage pattern and auth-error non-fallback mitigation.
- **Updated**: provider-authentication — Added credential-pool inspection with `hermes auth list`, reset guidance, and auth-error fallback notes.
- **Updated**: provider-and-gateway-errors — Added Codex 401 cascade and profile HOME Google Workspace credential errors.
- **Updated**: oauth-credential-separation — Added external CLI credential separation for profile HOME overrides.
- **Updated**: provider-chain-subscription-oauth — Added operational warning that auth errors may not trigger fallback in Hermes Agent 0.14.0.
- **Sources**: sessions/2026-06-09-fleet-outage-codex401-gws-reauth.md

## 2026-06-10
- **Added**: quick-setup-nous-portal — Getting-started page for Hermes 0.16.0 Quick Setup via Nous Portal and the `hermes portal` alias.
- **Added**: desktop-remote-gateway — Guide for connecting the native desktop app to an OAuth or username/password protected remote Hermes gateway.
- **Added**: hermes-016-surface-release — Reference summary of the 0.16.0 Surface Release: desktop app, dashboard admin panel, setup, skills, CLI/TUI, and security notes.
- **Sources**: no ready session files; upstream release https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5; PyPI https://pypi.org/project/hermes-agent/0.16.0/

## 2026-06-25
- **No sessions to process** — zero sessions with status: ready found.
- **Sources**: none

## 2026-06-28
- **No sessions to process** — zero sessions with status: ready found (all 8 sessions status: processed; last session 2026-06-09).
- **Sources**: none

## 2026-06-30
- **No sessions to process** — zero sessions with status: ready found (all 8 sessions status: processed; last session 2026-06-09).
- **Sources**: none

No sessions with status: ready found on 2026-08-14. Skipping elaboration cycle.
No sessions with status: ready found on 2026-08-25. Skipping elaboration cycle.

## 2026-08-31
- **Added**: hermes-019-020-release-wave — Reference for the v0.19.0 Quicksilver through v0.20.6 release wave: voice/barge-in, A2A v1.0, signed outbound webhooks, grounded citations, SecretSource interface, delivery-obligation ledger, keyless web tier, MCP 2.x, upgrade attention points, PyPI distribution lag note.
- **Added**: secrets-vault-integration — Guide for the `secrets:` block and SecretSource backends: 1Password (`op://` refs, setup/CLI/config), Bitwarden Secrets Manager (machine accounts, bws auto-install), command helper, multi-source precedence ladder, `preserve_existing` + profile aliasing, plugin contract.
- **Updated**: quick-setup-nous-portal — v2: added Tool Gateway coverage, `/subscription` `/topup` terminal flows (0.19.0), and keyless web tier on fresh installs (0.20.5).
- **Sources**: no ready session files (all 8 sessions status: processed); upstream sync — https://github.com/NousResearch/hermes-agent/releases (v2026.7.20 → v2026.8.27), https://hermes-agent.nousresearch.com/docs/user-guide/secrets/, https://pypi.org/pypi/hermes-agent/json

## 2026-09-01
- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Added**: hermes-021-pantheon-release — Reference for v0.21.0 "Pantheon" (v2026.8.31): Bot Mode built into desktop, `hermes peer` bot-to-bot DMs, cron memory/continuity/notepads, live subagent steering with output schemas, MCP command center, agent-driven desktop browser, provider wave + `model_overrides`, protected instruction files, redaction sweep, Blender MCP removal, reverted features list, upgrade attention points, PyPI lag note (still 0.19.0).
- **Updated**: hermes-019-020-release-wave — v2: cross-link to the new 0.21.0 Pantheon reference (which rolls up the 0.20.1–0.20.6 windows documented there).
- **Sources**: no ready session files; upstream sync — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31, https://pypi.org/pypi/hermes-agent/json

## 2026-09-03
- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: stable unchanged — GitHub latest release still v0.21.0 "Pantheon" (v2026.8.31, published 2026-08-31, not a prerelease); PyPI hermes-agent still 0.19.0 (distribution lag). Local CLI at v0.20.6 (2026.8.27), reports 1184 commits behind upstream tip — upgrade candidate noted, not acted on (docs cycle does not upgrade the runtime).
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases, https://pypi.org/pypi/hermes-agent/json

## 2026-09-04

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: GitHub stable unchanged at v0.21.0 "Pantheon" (v2026.8.31, published 2026-08-31T19:29:49Z); no new tags/prereleases since (latest tags: v2026.8.31, v2026.8.27, v2026.8.19). PyPI still lags at 0.19.0. No docs or index changes (skip contract: zero churn).
- **Environment note**: local install v0.20.6 now 1293 commits behind upstream main (was 1184 yesterday) — main branch active (~109 commits) but no tagged release yet; upgrade deferred until a stable tag lands.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31, https://pypi.org/pypi/hermes-agent/json

## 2026-09-05

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: GitHub stable unchanged at v0.21.0 "Pantheon" (v2026.8.31, published 2026-08-31T19:29:49Z); no new tags/prereleases since (latest tags: v2026.8.31, v2026.8.27, v2026.8.19). PyPI still lags at 0.19.0. No docs or index changes (skip contract: zero churn).
- **Environment note**: upstream main is in a heavy burst — local install v0.20.6 now 5600 commits behind origin/main (was 1293 yesterday; ~1330 commits in the last 48h, 5785 in 7d; tip 1e69c12b64 feat(slack): interactive Block Kit model picker for /model). No stable tag has landed yet; upgrade remains deferred until a tagged release ships.
- **Security note**: PyPI JSON lists 4 OSV advisories (GHSA-xq8w-9jvx-gm3v / CVE-2026-10221 injection in _compress_context ≤0.12.0; GHSA-pmqc-57g8-c22c / CVE-2026-10224 resource consumption in feishu webhook ≤2026.4.30). Local runtime v0.20.6 is newer than both affected ranges — not vulnerable.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31, https://pypi.org/pypi/hermes-agent/json

## 2026-09-06

- **No sessions to process** — zero sessions with status: ready (all 8 sessions status: processed; last session 2026-06-09).
- **Upstream check**: GitHub stable unchanged at v0.21.0 "Pantheon" (v2026.8.31, published 2026-08-31T19:29:49Z); no new tags/prereleases since (latest tags: v2026.8.31, v2026.8.27, v2026.8.19). PyPI still lags at 0.19.0. No docs or index changes (skip contract: zero churn).
- **Environment note — external upgrade detected**: local runtime upgraded outside the docs cycle from v0.20.6 to v0.21.0 between runs. Evidence: `git reflog` fast-forward to `006b1beb00` on 2026-09-05 15:53:25 +0200, gateway restart at 15:54:38 (`systemctl --user show hermes-gateway -p ActiveEnterTimestamp`), `hermes --version` now reporting v0.21.0 (upstream 245e4800). Semantics: local HEAD sits +5322 commits past the v2026.8.31 stable tag and 18 commits behind origin/main tip — the v0.21.0 label is the package version; the installed tree is a post-tag main snapshot, not the tagged release itself.
- **Security note**: PyPI JSON still lists 4 OSV advisory entries = 2 unique CVEs (GHSA-xq8w-9jvx-gm3v / CVE-2026-10221, GHSA-pmqc-57g8-c22c / CVE-2026-10224, each mirrored as PYSEC entries). Affected ranges unchanged (≤0.12.0 / ≤2026.4.30); local runtime v0.21.0 is newer than both — not vulnerable.
- **Sources**: no ready session files; upstream check — https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.31, https://pypi.org/pypi/hermes-agent/json
