---
title: "110-strategies fleet optimization campaign (15 patches, 9 IMMUTABLE manifest) + n8n+Discord+Claude Code POC end-to-end + Hermes scheduler bug discovery"
date: "2026-05-29"
author: "kos-domus"
status: "processed"
tags: ["agent-sdk", "configuration", "multi-agent", "security", "automation", "troubleshooting", "prompt-engineering"]
session_type: "hermes"
client: ""
openclaw_version: ""
environment:
  os: "Linux 6.17.0-29-generic"
  ide: "Claude Code (VSCode extension)"
  model: "claude-opus-4-7"
---

## Objective

Sessione single-day epica (~16h wall-clock attivo) con 3 macro-obiettivi indipendenti consolidati:

1. **Campaign 110-strategies optimization** — applicare il framework statutory dei 110 pattern di prompt engineering ai SOUL/skill/procedures degli 8 profile Hermes attivi (+ hermes-selfimprove production), producendo patches reversibili gated da CSO + Pattern A.
2. **understand-anything + MempPalace investigations** — Co-CEO Pattern A review di 2 candidate KM tool esterni per il knowledge management layer di Rakki, con verdict + roadmap 14gg integrata.
3. **n8n + Discord + Claude Code POC** — costruire end-to-end un bridge mobile pattern NetworkChuck-style (Discord channel → workflow n8n → SSH localhost → Claude Code subscription → reply) sul mini-PC, hardened CSO con ForceCommand SSH wrapper + Docker isolation.

Tutto in single session, tutto reversibile, tutto auditato.

## Context

- Setup Rakki post-Hermes-Step-3 (Kai shadow phase 1 attiva 2026-05-26)
- 8 profile Hermes attivi + hermes-selfimprove in shadow Day 0/14 (deploy 2026-05-28)
- Pre-existing: hermes-selfimprove con 5 IMMUTABLE markers + 110-strategies framework appena adottato come statutory rule
- 1Password vault Tech disponibile, MCP server ecosystem completo, Claude Code subscription Pro/Max
- Mini-PC Ubuntu 24 GB RAM + 468 GB disk, Hermes daemon attivo, no Docker pre-installato

## Major deliverables (timeline)

### A) Campaign 110-strategies optimization — 4 batches Pattern A

**Phase 0 — Function inventory baseline**
Script `~/job-desk/hermes/scripts/profile-inventory.sh` cattura snapshot pre-batch di 9 profile: 9 SOUL.md (81,856 chars totali), 327 skill files, 5 procedures, 54 cron jobs. Output JSON `~/job-desk/hermes/audit/baseline-inventory-2026-05-28.json` come gate verification post-batch.

**Batch 1 — default (Kos personale)**
Pattern A: Co-CEO + Backend + CSO + Frontend + OrchArch (4 lens synchronously, parallel spawn limitazione context). Output: memo `2026-05-28-co-ceo-batch1-default.md` + 2 patches:
- Patch 01 default SOUL: 19,519 → ~11,800 chars (-39%), 3 IMMUTABLE markers (`kos-identity`, `rakki-contact-data`, `security-rules`), 4 procedure NEW (`fleet-state`, `scope-and-drive-archive`, `youtube-pipeline`, `migration-openclaw-legacy`)
- Patch 02 troubleshooting.md split: 58,429 chars (1 file 60 entries) → 46,449 chars (1 main 37 entries Hermes-current) + 10,654 chars (`_archive/troubleshooting-openclaw-legacy.md` 12 OpenClaw entries). Cluster A-H structure, D cluster WhatsApp 11 entries → 1 consolidata, H cluster path-resolution 5 → 1

**Batch 2 — mc (Master Control)**
Memo `2026-05-28-co-ceo-batch2-mc.md` + 6 patches: SOUL 10,503 → 7,108 chars (-32%, 4 IMMUTABLE), audio-and-meet frontmatter, capture-protocol deprecated stub, project-dossier live-discovery, youtube anti-pattern table, capture skill 110-strategies re-baseline. 3 procedure NEW.

**Batch 3 — 4 work specialists in parallelo**
Memo `2026-05-28-co-ceo-batch3-specialists.md` + 4 patches: backend (5,184→5,485, 2 markers), cso (7,341→10,028, **4 markers policy-heavy**), frontend (5,151→6,409, 2 markers Mini App + DO/DON'T + WCAG), orcharch (6,318→8,340, 3 markers + §Conflicts schema). Decisione strategica: NO procedure introdotte (passive on-demand profile = self-contained SOUL preferred).

**Batch 4 — family-staging (Kai) + openclaw-observer**
Memo `2026-05-28-co-ceo-batch4-family-observer.md` + 3 patches: Kai SOUL 7,536→6,821 + 1 procedure NEW (drive-family-folders), Kai AGENTS 2,897→2,842, observer SOUL 8,077→7,603. CSP critical preservato: 3 numeri `<Rakki-tg-id> / <Rakki-wa> / <Katia-wa>` IMMUTABLE protected in `kai-privacy-boundary`. Shadow phase mandate "output LOCALE only durante Fase 1" IMMUTABLE.

**Fase A apply — 6/6 patches procedures + skill (low-risk)**
Applied 02 (troubleshooting split via Co-CEO respawn materialize), 04 (audio-and-meet), 05 (capture-protocol deprecated stub), 06 (project-dossier live-discovery), 07 (youtube), 08 (capture skill frontmatter refresh). Verification PASS: 17 audit entries, 15 backup files mode 0600, function inventory preserved.

**Fase B apply — 5/5 SOUL specialist (cold-start passive)**
Co-CEO respawn materialize ha riscritto tutti 5 SOUL specialist. Net delta: openclaw-observer -5.9%, backend +5.7%, frontend +24.4%, orcharch +32.0%, cso +36.6% — le 3 espansioni sono content schema richiesti dalle specs (DO/DON'T+WCAG frontend, §Conflicts schema orcharch, severity matrix cso). Tutti sotto safe ceiling 12K. 13 IMMUTABLE markers totali aggiunti.

**Fase C apply — 2/2 SOUL daemon-attivi (CRITICAL)**
Default Kos: 19,519 → 9,476 chars (**-51.5%**, sotto safe ceiling con margine 2,400 chars). 3 IMMUTABLE markers + 4 procedures NEW. Rimossi tool table 15-row, GWS skill enum 42-row, preamble "Step 1 in-corso" stale. MC: 10,503 → 7,108 chars (-32.3%), 4 IMMUTABLE markers + 3 procedures NEW. Function inventory preservation verified.

**Fase D apply — 2/2 SOUL family-staging (HIGH sensitivity)**
Kai SOUL 7,536 → 6,821 (-9.5%) + 4 IMMUTABLE markers (3 SOUL + 1 AGENTS). Kai AGENTS 2,897 → 2,842 (-1.9%). 1 procedure NEW. CSP boundary 3 numeri preservati verbatim. Shadow phase mandate confermato preservato. 33 cron DRY-RUN invariati.

**Test 7/7 profile post-apply PASS**
Default (Kos 🦌), MC (`🎯 MC —`), 4 specialist (incluso CSO con 4 IMMUTABLE markers citati), observer — tutti rispondono coerentemente a "chi sei + IMMUTABLE markers + prefisso Telegram". Identità preservata.

### B) Tasks post-campaign (1+2+5)

**Task 1 — client-sessions git fix v2**
Root cause: Hermes `terminal_tool` crea sandbox isolato che strippa HOME → `~/.git-credentials + helper store` (v1) non leggibile dal subprocess. **Fix v2**: URL embed token in `.git/config` mode 0600 del repo locale. Verified PASS sotto `env -i PATH=... HOME=/nonexistent bash -c "git pull"` (worst-case sandbox). Memoria `reference_git_credentials_setup.md` aggiornata.

**Task 2 — immutable-check.sh generalize multi-profile**
Script v2 con `--profile <name>` arg, manifest separato per profile in `~/job-desk/hermes/state/immutable-hashes-<profile>.yaml`. CSO NEW-1 (mode 0444) + NEW-2 (realpath canonicalization, reject symlinks) preservati. Init 9 manifest, total **29 IMMUTABLE markers** fleet-wide tracked. Roundtrip --init → --verify 9/9 PASS.

**Task 5 — TTL strategy 2026-06-04**
Sweep cron 03:00 skip patches `status: applied` by-design (zero rischio auto-revert). 15 backup files (~317 KB) mantenuti fino a 2026-06-11 (gate Day 14 hermes-selfimprove). Milestone calendar documentato.

### C) Co-CEO investigations 2 KM tool externals

**understand-anything (Lum1104, MIT, 43K stars)** — Karpathy LLM wiki + force-directed graph + community clustering + `/understand-knowledge` command. **Verdict: ADOPT PARTIAL** — pilota 14gg scope-strictly limitato a `/understand-knowledge` su vault `~/Obsidian-Personal/`. Niente install su Hermes profiles. Kill criteria T+14: (a) ≥2 candidati MOC validi, (b) zero drift wikilinks discipline, (c) zero tocchi IMMUTABLE. Memo `2026-05-29-co-ceo-understand-anything-investigation.md`.

**MempPalace (Milla Jovovich + Ben Sigman + igorls 511 commits, MIT, 53K stars 7 settimane)** — verbatim storage + ChromaDB + MCP 29 tools + Karpathy LLM wiki competitor. **Verdict: HOLD + spike read-only 2h post-pilot 2026-06-12**. 3 blocker: privacy (mining verbatim `~/.claude/projects/`), redundancy con `mcp__codebase-memory-mcp`, hype-curve 7-settimane + benchmark controversy (Penfield Labs flagged 100% LongMemEval teaching-to-test). Impostor domain `mempalace.tech` distribuisce malware. Memo `2026-05-29-co-ceo-mempalace-investigation.md`.

**Integrated 14d roadmap** memo: D1 understand-anything pilot first T+0→T+14, D2 n8n+Signal/Discord POC after T+14 (con scenario A/B/C/D chiaro). Concurrent only if Rakki has scenario explicit + 5h block libero. Memo `2026-05-29-co-ceo-integrated-14d-roadmap.md`.

### D) n8n + Discord + Claude Code POC end-to-end

Rakki override D2 sequencing: Discord scenario chiaro ("mobile Claude + 600 nodi + framework comunicazione + visual+monitoring") → go now.

**Pattern A specialist runbook** — CSO + Backend + OrchArch consultations. CSO verdict: **GO-with-conditions** con 8 mandatory hardening (MAND-1 pin digest, MAND-3 bind 127.0.0.1, MAND-7 ForceCommand wrapper allowlist, MAND-8 no workspace mount, MAND-4 token via 1P, MAND-5 minimum Discord intents, MAND-6 single channel allowlist, MAND-2 N8N_ENCRYPTION_KEY 32-byte random). Memo `2026-05-29-co-ceo-n8n-discord-poc-runbook.md`. Threat model 8 threats (T3 SSH bridge CRITICAL).

**Setup execution (~6h supervisionato)**:

| Step | Output |
|---|---|
| 0 prerequisiti | Docker install via apt sudo (Rakki), 1P CLI ok, hermes mc accessible, security tools (trivy/gitleaks/semgrep) presenti |
| 1 scaffolding | `~/job-desk/n8n-poc/{data,scripts,logs,.secrets,.security}` + .gitignore + secrets.env 0600 |
| 2 SSH key + ForceCommand wrapper | Ed25519 keypair dedicata + wrapper script con allowlist `claude -p` / `mc -z` / `hermes -p mc send/chat`. Anti-injection metachar check. Smoke 5/5 PASS (1 accept + 4 reject patterns) |
| 3 secrets via 1P | Discord bot token + server_id + channel_id pulled from 1P UUID. N8N_ENCRYPTION_KEY + basic_auth gen locale (op default vault Tech read-only, write blocked) |
| 4 docker-compose | n8n:2.23.1 digest pinned `sha256:a0aa401...` (vs runbook minimum 1.123.22 → **CVE riduce 143 HIGH/CRIT a 1 HIGH** accepted via `.security/cve-acceptance.md`). Bind 127.0.0.1:5678, no workspace mount, extra_hosts host.docker.internal, security_opt no-new-privileges, cap_drop ALL |
| 5 baseline scan | gitleaks clean + semgrep clean + trivy fs clean. n8n image upgrade discovery |
| 6 boot | Stack up healthy, n8n responde /healthz 200 OK |
| 7 workflow build | UI guidato 3-nodi (Webhook → SSH Execute → HTTP Request). Discord credential + SSH credential creati. Auth intents Discord Developer Portal abilitato + permission overwrites canale (post-diagnostic workflow) |
| 8 smoke E2E | Mobile Discord msg → bridge → n8n webhook → SSH → claude --model opus → HTTP /reply → bridge → Discord channel response = **PASS** |

**Custom Discord bridge Docker** (`~/job-desk/n8n-poc/discord-bridge/`):
- Node.js + discord.js + Express, 102 righe `index.js`
- Listens Discord Gateway, posts msg to n8n webhook, exposes `/reply` for n8n to call back
- Dockerfile multi-stage node:20-alpine, non-root user, security_opt no-new-privileges, cap_drop ALL, healthcheck wget
- Allowlist channel via DISCORD_CHANNEL_ID env, ignore bots (anti-loop)

**Wrapper SSH evolved v1 → v5** durante session (CSO + dev pragmatic balance):
- v1: base allowlist `mc -z` / `hermes`
- v2: bug grep PEM `-----` fix
- v3: add `claude -p` / `--resume` / `-c` patterns + cwd `/home/kos/job-desk`
- v4: handle n8n `cd /home/kos/job-desk && claude...` prepended pattern
- v5: handle n8n `cd /home/kos/job-desk ; claude...` (semicolon separator, n8n uses `;` not `&&`)

## Decisioni strategic

1. **Resta su mini-PC localhost vs Hostinger VPS** — Co-CEO recommendation accepted: localhost POC = security boundary semplice, footprint trascurabile (2.33 GB disk image + 289 MB RAM + 0.25% CPU su 468 GB / 15 GB / multi-core), zero esposizione internet. VPS Hostinger restate per fase 2 se vuole exposure pubblico.

2. **Custom Docker bridge vs community Discord-Trigger node** — n8n core NO Discord Trigger nativo. Audit 3 community candidates: solo katerlol/n8n-discord-trigger auditabile (86 stars + stale 10 mesi, n8n 2.x compat unknown). Decision: **custom Docker bot 102 lines node.js + discord.js** = supply-chain owned + future maintainability.

3. **V1 stateless vs V2 NetworkChuck multi-turn** — Build V1 first (Webhook → SSH → HTTP, ~20 min) to validate pipeline, V2 multi-turn pattern (UUID + Send-and-Wait + If "Done?" + Resume loop, ~30-40 min) deferred. Wrapper v3 già supporta `--resume <uuid>` quindi V2 è purely UI build, no backend change.

4. **Telegram vs Discord vs Signal** — User preference inversion mid-session:
   - First proposed Signal (E2E privacy, ma 4-5h setup signal-cli-rest-api Docker)
   - Switched to Discord (native n8n suggestions, ~30-45 min setup, separato da Telegram-Hermes identity)
   - Rejected Telegram fast-path nonostante zero overhead (vuole separazione hard da Hermes-thread workspace)

5. **Hermes vs Claude Code subscription** — User explicit: "lascia claude code, perche Hermes non ha accesso a anthropic via subscription". Confermato Claude Code CLI v2.1.85 con `--model opus` (Opus 4.6 fallback, Opus 4.8 explicit via `claude-opus-4-8`). Sessione persistente via `--session-id <uuid>` + `--resume <uuid>` confermati.

## Bug & issue rilevati + fix

1. **Discord intent disabled** → `discord login fail: Used disallowed intents` crash loop. Fix: Developer Portal → Bot → Privileged Intents → Message Content Intent ON.
2. **Discord channel permission insufficienti** → bot online ma solo VIEW_CHANNEL (1024) sul canale privato, mancano SEND_MESSAGES + READ_MESSAGE_HISTORY. Fix: Edit Channel → Permissions → bot → toggle entrambi.
3. **n8n SSH node prepend `cd <wd> ;` con semicolon** non `&&` — wrapper v4 rejecting metachar `;`. Fix v5: strip safe prefix con sia `&&` che `;`.
4. **n8n SSH node display name `Execute a command`** non `SSH` — HTTP Request expression `$('SSH')` ExpressionError. Fix: rename ref a `$('Execute a command')`.
5. **n8n JSON body content unescape** → Claude output multilinea con `\n` literali rompe parse "Bad control character at position 137". Fix: `{{ JSON.stringify(stdout) }}` invece di `"{{ stdout }}"` (JSON.stringify aggiunge quote + escape).
6. **n8n image 1.123.22 ha 143 HIGH/CRIT CVE** → CSO MAND-1 minimum non sufficient. Fix: upgrade pin a `2.23.1` (1 HIGH residuo CVE-2026-44705 `tmp` 0.2.4 path traversal, accepted log).
7. **op default service account no-write on Tech vault** → `op item edit/create` error 101. Workaround: secrets locali in `secrets.env` mode 0600, deferred move a 1P (Rakki userà UI manuale).
8. **op secret reference path con `&` carattere non parsabile** → use UUID instead of title in path `op://Tech/<UUID>/<field>`.
9. **n8n_bridge network subnet conflict** dopo compose rebuild — `name: n8n_bridge` override default `n8n-poc_n8n_bridge` causa "Pool overlaps". Fix: rimuovi `name:` field, lascia default project-prefixed.
10. **Hermes scheduler stuck next_run** (scoperto 03am 30/05) — `hermes-daily-review` next_run `2026-05-28T22:00:00` (30h passato). 2 Daily Reviews + 1 patch sweep missed. Diagnose deferred a session attuale.

## Learnings

**Pattern repetibili** (#79 prompt versioning):
- **Co-CEO respawn materialize**: Co-CEO produce patch description, separato Co-CEO respawn materialize il file finale. Riduce error rate vs single-pass write.
- **Wrapper SSH ForceCommand allowlist**: pattern reusable per qualsiasi bridge n8n→host. ~50 righe bash + smoke test 1 accept + N reject = security boundary trustable.
- **`{{ JSON.stringify(...) }}` per stdout multiline in n8n HTTP Request**: pattern universale per evitare body invalido.
- **Docker compose extra_hosts: ["host.docker.internal:host-gateway"]** per container→host SSH: works su Linux Docker Engine senza Docker Desktop.

**Anti-pattern noti**:
- Bash `SAFE_PREFIX=""` con prefix-match `[[ "$X" == "$PREFIX"* ]]` → empty prefix matcha sempre tutto, skip strip senza accorgersene (bug v5 prima del fix).
- n8n Working Directory empty = validation error rosso → setta a path che wrapper ignora (es. `/home/kos/job-desk` allineato a wrapper cwd).
- Spelling phonetic in nomi tool/persona (es. "Milla Yavovich" → "Milla Jovovich"): cercare varianti.

**Strategy IDs usate frequentemente questa session**:
- #1 obiettivo esplicito (decision memos)
- #5 output contract (memo struttura)
- #7 vincoli espliciti (CSO mandates)
- #14 counterexample (anti-pattern table)
- #28 assumption audit (multi-volte pre-action)
- #47 root-cause-first (debug Discord)
- #48 failure-mode prompting (pre-mortem)
- #50 verification loop (post-action)
- #62 ROI framing (sequencing decision)
- #65 decision memo (Co-CEO outputs)
- #66 pre-mortem (n8n+Discord risk)
- #94 safety boundary (CSO)
- #95 privacy minimization (no client data)
- #98 reversibility (backup pre-apply, rollback paths)
- #110 prompt-to-product transition (wrapper v1→v5 evolution)

## Memorie create / aggiornate

- `reference_git_credentials_setup.md` v2 (URL embed token repo-scoped, fix sandbox HOME stripped)
- `reference_prompt_engineering_110_strategies.md` (statutory framework)
- `reference_prompt_engineering_110_strategies_index.json` (machine-readable filter)
- `feedback_prompt_engineering_110_rule.md` (statutory application rule)

## File / artefatti creati (paths)

### Hermes optimization campaign
- 15 patch files in `~/job-desk/hermes/patches/2026-05-28-{01..15}-<profile>-<file>.md`
- 4 decision memos in `~/job-desk/hermes/decisions/2026-05-28-co-ceo-batch{1..4}*.md`
- 1 baseline inventory `~/job-desk/hermes/audit/baseline-inventory-2026-05-28.json`
- 9 IMMUTABLE manifest `~/job-desk/hermes/state/immutable-hashes-<profile>.yaml` (mode 0444)
- Script `~/job-desk/hermes/scripts/{profile-inventory,immutable-check}.sh` (multi-profile generalized)
- 15+ backup files `*.bak.pre-{patch,fase-c,fase-d,fase-b}-<timestamp>` (mode 0600)

### Co-CEO investigations
- `~/job-desk/hermes/decisions/2026-05-29-co-ceo-understand-anything-investigation.md`
- `~/job-desk/hermes/decisions/2026-05-29-co-ceo-mempalace-investigation.md`
- `~/job-desk/hermes/decisions/2026-05-29-co-ceo-integrated-14d-roadmap.md`

### n8n + Discord POC
- `~/job-desk/n8n-poc/{Dockerfile,docker-compose.yml,secrets.env,README.md,.gitignore}`
- `~/job-desk/n8n-poc/discord-bridge/{Dockerfile,index.js,package.json}`
- `~/job-desk/n8n-poc/scripts/hermes-ssh-gate.sh` (v5)
- `~/job-desk/n8n-poc/.security/cve-acceptance.md`
- `~/job-desk/n8n-poc/.secrets/n8n-ui-access.txt` (UI password reference)
- `~/.ssh/n8n_hermes_ed25519{,.pub}` (mode 600/644)
- `~/.ssh/authorized_keys` updated with ForceCommand entry (from "127.0.0.1,172.17.0.0/16,172.30.0.0/24")
- `~/job-desk/hermes/decisions/2026-05-29-co-ceo-n8n-discord-poc-runbook.md`
- 1P Tech vault: `Discord Kos_domus & n8n-MC config` updated (server_id + channel_id added)

## Open items + aperti per 30/05

1. **Hermes scheduler stuck bug** — recover via manual `cron run` o gateway restart (deferred)
2. **MC briefing 06:30 30/05** — first validation post-Fase-C apply (mc + default SOULs nuovi)
3. **Default Kos docs 07:30 30/05** — second validation cron
4. **understand-anything pilot start** (D1 integrated roadmap) — 4h scope `/understand-knowledge ~/Obsidian-Personal/`
5. **V2 multi-turn NetworkChuck pattern Discord** — UUID + Send-and-Wait + If + Resume loop, ~30-40 min UI build
6. **`--model opus` alias risolve a Opus 4.6** non 4.8. Fix esplicito `claude --model claude-opus-4-8 -p ...` nel SSH command per upgrade
7. **discord-bridge container `unhealthy`** (healthcheck wget non funziona ma bot risponde) — cosmetic da fixare
8. **LVY Cosmetics pre-kickoff** — deferred a quando Rakki ready
9. **Sacchitalia rc5.1 smoke test** — coordinazione Maurizio (NSSM restart + ESOLVER E2E)
10. **Enerj decision Auletta** wait

## Numbers giornata

- Patches scritte: **15** Co-CEO + 5 Co-CEO memos (4 batch + 1 integrated)
- Patches applicate: **15/15** + 1 git fix + 1 wrapper evolution v1→v5
- Backup files: **17+** mode 0600 (pre-apply safety net)
- Audit entries: **20+** JSONL append-only mode 0600
- IMMUTABLE markers fleet-wide: **29 nuovi** (4 default + 4 mc + 11 specialist + 4 family + 2 observer + 4 hermes-selfimprove pre-existing = **29 tracked**)
- CVE catalogati n8n image: **143 HIGH/CRIT → 1 HIGH** (99% riduzione via pin upgrade)
- Containers Docker: **2** (n8n + discord-bridge, both running 8h+)
- Smoke tests: **9+ patterns reject/accept** validated wrapper SSH
- Co-CEO Pattern A specialist consultations: **5 round** (Batch 1-4 + n8n runbook)
- Workflow Tool calls (background): **4** (understand-anything, mempalace, integrated-roadmap, diagnostic)
- Decisioni strategic deferred: 5 (V2 multi-turn, VPS migration, Hermes-in-chat dialog, hostinger 1P move, hardening webhook auth)

## Reference path memo + skill

- Hermes pattern Co-CEO Pattern A: memoria `feedback_co_ceo_consult_specialists.md`
- 110-strategies framework: memoria `reference_prompt_engineering_110_strategies.md` + JSON index
- Hermes selfimprove deploy precedente: `2026-05-28-hermes-selfimprove-deploy-day-zero.md` (logged 28/05)
- CSO default review by design: `feedback_cso_default_security_review.md`
- 5-maestri canonical (capture skill pattern): `feedback_hermes_skill_consolidation.md`
- Codex Pattern B OpenAI-side: `feedback_codex_gpt55_silent_reject.md` (reference cross-session)
