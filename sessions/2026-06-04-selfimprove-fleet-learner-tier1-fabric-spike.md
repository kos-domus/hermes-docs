---
title: "Self-improver da idle a Fleet Learner (pattern Quarq) + deploy Tier-1 gated CSO + deep-dive gate + spike Fabric Docker-MCP + alpha intake"
date: "2026-06-04"
author: "kos-domus"
status: "processed"
tags: ["multi-agent", "security", "memory", "configuration", "automation", "cron", "mcp", "agent-sdk"]
session_type: "openclaw"
client: ""
openclaw_version: ""
environment:
  os: "Linux (mini-PC kos-domus)"
  ide: "Claude Code (VSCode extension)"
  model: "claude-opus-4-8"
---

## Objective
Trasformare il profilo Hermes `hermes-selfimprove` da **idle** (girava ma skippava sempre) a **Learner della fleet**; deployare Tier-1 (kos) sotto gate CSO; approfondire il gate di validazione T+14; valutare l'integrazione di Fabric come MCP Docker; filtrare 5 drop di "alpha" AI-tooling.

## Context
Profilo `hermes-selfimprove` (advisory-shadow) leggeva solo le proprie sessioni (vuote) → 0 input → skip perpetuo. Driver: due articoli memory condivisi — **Quarq Agent** (continual-learning, 3 layer + targeted-edit learner + Temporal-Truth) e **Mem0** (token-efficient, ADD-only). Più una serie di tool di terzi da valutare col lente `/alpha`.

## Steps Taken

### 1. Re-architettura: self-improver = Learner della fleet (pattern Quarq)
Mappatura anatomia profilo Hermes ↔ 3 layer Quarq: `sessions/`+`memory/` = semantic; **`SOUL.md`+`procedures/`+`skills/` = procedural** (target dell'edit); episodic = runtime. Il self-improver diventa il **ruolo learning separato** della fleet (gli agent fanno generation; lui impara su di loro). Pattern rubati: targeted-edit (add/update-outdated/dedup/delete-contradiction) + **Temporal-Truth 4 regole** (storage-date ≠ event-date) + **cross-layer dedup**. NON adottato il software Quarq (= ennesimo RAG, contro la decisione convergenza-substrato).
**Result**: piano `hermes/plans/PLAN-selfimprove-repoint-real-corpus.md` riscritto; skill `self-improvement` §9 "Learner mode" aggiunta.

### 2. Pilot manuale su kos
Letti 15 session log recenti del corpus pubblico di kos. Filtro Learner: 15 sessioni dense → **1 sola proposta high-confidence** applicata (kos SOUL Core Principle #6 "Ground-truth prima del report"). 2 borderline scartati. **Il filtro è il valore**: temporal-truth scarta ~60% di lezioni di era deprecata (pre-migrazione OpenClaw→Hermes), cross-layer dedup scarta ~80% già migrato.
**Result**: proof-of-value; conferma che corpus vecchio/coperto → yield basso = corretto.

### 3. Deploy Tier-1 (kos) — gate CSO GO-with-conditions (C1–C9)
Threat-model CSO (STRIDE + lente AI) → verdetto a 3 tier: **Tier-1 (kos, corpus pubblico + file procedural root) GO**; Tier-2 (corpus PRIVATE clienti) + Tier-3 (family) **HOLD**.
- **C1 deroga read** = allowlist `read_roots` in `state/capability-matrix.yaml` (0444 deploy-only, NON prosa) per i 3 path procedural root di kos (`~/.hermes/SOUL.md`/`procedures`/`skills`).
- **C2** deny-glob `request_dump_*.json` (vedi finding sotto).
- **SOUL §26/§31** → wording-puntatore alla matrix (read governata da allowlist, **write_deny cross-profilo invariato**). La deroga è **dati**, non prosa modificabile → §33 Non-Drift intatto.
- **C3 re-baseline**: `immutable-check.sh --profile hermes-selfimprove --init --force` → `--verify` VERDE (5 sezioni; le 2 modificate cambiano hash, le 3 non toccate invariate = edit chirurgico).
- **U4 cadenza**: nuovo cron `hermes-learner-kos` `0 20 * * 0` (settimanale).
**Result**: Tier-1 live. Smoke-test: 1 sessione → 4 cluster → 3 dedup-skip (la deroga legge il procedural di kos) → 0 patch = filtro corretto.

### 4. Codex OAuth re-auth
Smoke-test girato su fallback `glm-5.1` perché il primary `gpt-5.5` (openai-codex) aveva il **token OAuth scaduto** (chain v5 fallback ha salvato il run). Re-auth via `hermes auth add openai-codex --type oauth --manual-paste` (fatto da Rakki, TTY+browser). Verifica: micro-call sul primary risponde OK → gpt-5.5 di nuovo attivo.

### 5. Deep-dive gate T+14 + finding di sicurezza
- **C5 NON implementato (gap)**: non esiste un read-gate/audit. La deroga read è solo **istruita nel SOUL**, non enforced né loggata → la KPI "0 read fuori allowlist" non è misurabile a basso costo.
- **Finding strutturale**: il MCP `filesystem` del profilo era sandboxato a tutto `~/job-desk` → includeva i **client folder**. Sandbox più largo dell'allowlist.
- **Seed di validazione** (30 sessioni corpus pieno, primary gpt-5.5): 9 cluster → 0 survivor, **5 temporal-scartati + 4 dedup-skip** → i filtri sparano davvero. Conferma: corpus kos pubblico troppo vecchio/coperto → valore **forward-looking**, non dimostrabile sul backlog.
- **C5-lite inconcludente**: il transcript dei tool-call vive in `state.db` (SQLite lockato dal gateway + sqlite3 non installato) → non estraibile.
- **Igiene fatta**: ristretto il sandbox MCP filesystem a 11 dir non-client (esclusi i client folder + quarantine). config.yaml backup + YAML valido + corpus kos intatto.
- Decisione Rakki: **"prima il valore su kos"** → Tier-2 (clienti/family) resta HOLD finché il learner non prova valore su sessioni nuove. Hard read-gate (C5-full) = prerequisito Tier-2, non di questo gate.

### 6. Spike Fabric come MCP Docker — CSO precheck GO, poi bloccato su auth
Proposta Rakki: integrare Fabric (danielmiessler) come **MCP isolato in Docker on-demand** per benchmarkare i pattern. CSO precheck → **GO-with-conditions**:
- Immagine `kayvan/fabric` pinnata per digest (`sha256:8ed2f056...292e`; maintainer = top contributor upstream; trivy 0 CRITICAL).
- Bridge `fabric-mcp` (PyPI) — **zero auto-sync** (vettore prompt-injection chiuso). `brneto/fabric-mcp-server` respinto (auto-sync core).
- Powering **(A) `hermes proxy`** (OpenAI-compat → provider OAuth, key dummy, zero costo, rete Docker isolata).
- C1-C10 + keep/kill.
**Blocker**: `hermes proxy` fronta solo `nous`+`xai`, ed entrambi NON autenticati. Tentato re-auth `xai-oauth`: loopback su sessione remota richiede SSH tunnel o `--manual-paste`; 3 tentativi falliti (state mismatch / device-code-vs-url confusion / missing-code). **Pausa** decisa: spike ripreso quando l'auth Grok è pulita (via SSH tunnel `ssh -N -L <port>:127.0.0.1:<port>`, che auto-completa). Immagine già pinnata, conditions pronte.

### 7. Alpha intake (5 drop filtrati col lente steal/skip)
- **Quarq** → STEAL applicato (self-improver, vedi sopra).
- **Mem0** → 1 idea rubata ("agent-generated facts first-class" → §9 skill) + 1 principio salvato: **ADD-only (facts) vs targeted-edit (rules/procedural) dipende dal layer** (un SOUL ADD-only sfonda il limite char). Software SKIP.
- **mattpocock/skills** → SKIP (duplica /plan+AskUserQuestion+karpathy; il core "griglia su ogni modifica" confligge con la preferenza "procedi con assunzioni dichiarate").
- **models.dev** → reference-only / WATCH; trappola: i model-ID sono convenzione AI-SDK ≠ nomi built-in Hermes (non usarli per il config chain).
- **Docmd** → WATCH (sito statico da markdown; fit sui repo docs pubblici ma non prioritizzato).
- **Fabric** → spike gated (sopra).
Tutto archiviato nel MOC `Agentic-Engineering` con il *perché* di ogni no.

## Configuration Changes
- `state/capability-matrix.yaml`: `read_roots` += 3 path procedural root kos; `read_deny` += deny-glob `request_dump_*.json`; chmod 0444. Backup.
- `~/.hermes/profiles/hermes-selfimprove/SOUL.md` §26/§31: wording-puntatore matrix (deroga read governata da allowlist). Backup.
- `state/immutable-hashes-hermes-selfimprove.yaml`: re-baseline (5 sezioni).
- `skills/self-improvement/SKILL.md`: §9 Learner mode + agent-generated-facts. Backup.
- `config.yaml`: MCP `filesystem` allowed-dir ristretto da `~/job-desk` a 11 dir non-client. Backup.
- Nuovo cron `hermes-learner-kos` (settimanale dom 20:00).
- Memorie: `project_hermes_selfimprove_validation` riscritta (fleet learner Tier-1); nuova `reference_memory_edit_strategy_by_layer`; MOC `Agentic-Engineering` esteso.

## Key Discoveries
- **La deroga di sicurezza come DATI (allowlist matrix 0444 deploy-only), non prosa** → l'agente non può allargarsi (hash-protected), il re-baseline è operazione deploy umana. È ciò che tiene §33 Non-Drift intatto.
- **Read enforcement parziale**: il MCP filesystem hard-sandboxa `job-desk`; le letture `~/.hermes`/`~/.claude` passano dal file-tool nativo, governato solo da SOUL-instruction. Hard read-gate (PreToolUse hook + audit) = lavoro Tier-2.
- **`hermes proxy` fronta solo `nous` + `xai`** (non l'intera chain v5) → per un A/B equo con Fabric serve lo stesso modello su entrambi i lati.
- **xAI OAuth su sessione remota**: loopback (`_xai_oauth_loopback_login`) → serve SSH tunnel (auto-completa) o `--manual-paste` (incollare l'URL `127.0.0.1/callback?code=...&state=...` dalla barra, NON il codice mostrato). Tentativi multipli → "state mismatch": serve `hermes auth reset` + UN tentativo pulito.
- **Bearer token a riposo** nei `request_dump_*.json` (dump di richieste fallite `max_retries_exhausted`): finding HIGH, ticket aperto separato (scrub+rotate). I token erano davvero scaduti (confermato dal 401 Codex).
- **Yield del learner = forward-looking**: su backlog vecchio/coperto rende ~0 (corretto); il valore emerge su sessioni nuove.

## Errors & Solutions
| Error | Cause | Solution |
|-------|-------|----------|
| Smoke-test learner su fallback glm-5.1, non primary | Codex OAuth token scaduto (refresh morto) | chain v5 fallback ha retto; re-auth `hermes auth add openai-codex --type oauth --manual-paste` |
| `hermes login` removed | comando deprecato (help stale) | usare `hermes auth add <provider> --type oauth` |
| xAI auth `state mismatch` | tentativi OAuth incrociati | `hermes auth reset xai-oauth` + 1 tentativo pulito |
| xAI auth `missing authorization code` | incollato il contenuto sbagliato (non l'URL callback con `?code=`) | su remoto: SSH tunnel (auto-completa) o copiare l'URL `127.0.0.1/callback?...` intero dalla barra |
| C5-lite non verificabile | transcript in `state.db` (SQLite lockato) + no sqlite3 | igiene MCP-narrow come mitigazione Tier-1; hard read-gate rinviato a Tier-2 |

## Final State
- Self-improver Tier-1 (kos) **live, gated, igienizzato**; cron settimanale; primo run reale 2026-06-07 20:00. Gate T+14 ~21/06 con KPI sicurezza+valore (checklist in `hermes/decisions/`).
- Tier-2/3 (clienti/family) HOLD CSO finché valore provato + controlli R6 + hard read-gate.
- Fabric Docker-MCP: CSO GO + immagine pinnata, **in pausa** su auth Grok (riprende a SSH sistemato).
- 5 alpha filtrati + archiviati; 1 principio nuovo salvato.

## Open Questions
- Valore del learner: re-assess a ~4 settimane di sessioni fresche.
- Fabric: completare auth xAI via SSH tunnel → finire build + A/B.
- Ticket HIGH: scrub+rotate dei `request_dump_*.json` con Bearer a riposo.
- Tier-2 (futuro): costruire R6 (output segregato + tagging + denylist) + hard read-gate prima di abilitare corpus clienti.
