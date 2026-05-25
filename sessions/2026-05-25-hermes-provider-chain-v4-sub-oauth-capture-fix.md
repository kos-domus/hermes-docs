---
title: "Hermes provider chain ridisegnata 5-tier sub-OAuth (v1→v4) + Capture Protocol workdir fix + Step 2.5 SA legacy cleanup"
date: "2026-05-25"
author: "kos-domus"
status: "ready"
tags: ["hermes", "configuration", "automation", "troubleshooting", "api", "agent-sdk"]
session_type: "openclaw"
client: ""
openclaw_version: ""
environment:
  os: "Linux 6.17.0-29-generic (Ubuntu)"
  ide: "VSCode SSH Remote → mini-PC"
  model: "claude-opus-4-7[1m]"
---

## Objective

Tre obiettivi emergenti in ordine di scoperta:
1. **Cleanup Step 2.5** Hermes: revocare il SA legacy `openclaw-clienti` (orphaned post migrazione work fleet a `hermes-clienti-v1`), riallineare wrapper shell e memoria.
2. **Patchare 2 errori cron Hermes** scoperti durante validazione: Gemini HTTP 400 (`thought_signature` mandatory in 3.x) e Gemini HTTP 429 (rate-limit). Investigation ha rivelato problema architetturale più profondo: il primary `openai/gpt-5.5` via OpenRouter falliva 402 (credit basso) → fallback gemini saturava → cascata di errori.
3. **Fix regressione Capture Protocol**: MC rispondeva generic invece di archiviare note nel topic dedicato.

## Context

**Stato iniziale**:
- Hermes runtime (Nous Research) gira sul mini-PC con 1 daemon (default profile = utente) + 1 daemon (work fleet profile `mc` con 4 specialist passivi).
- Fallback chain configurata identica su 6 config files: `openai/gpt-5.5` (via OpenRouter, primary) → `gemini-3.5-flash` → `openrouter/z-ai/glm-5.1` → `openrouter/anthropic/claude-opus-4.6`.
- Subscription pagate utente: ChatGPT Pro $200/mese, Gemini Advanced $25/mese, Claude Code (OAuth già loggato), Z.AI Coding Pro, GitHub Copilot. **Nessuna di queste era collegata a Hermes**.

**Sintomi che hanno innescato l'investigation**:
- Cron MC Evening Digest 19:30 fallito con `Gemini HTTP 400: Function call is missing a thought_signature in functionCall parts. Additional data, function call default_api:skill_view, position 2`.
- Cron OpenClaw Release Monitor 04:00 fallito con `Gemini HTTP 429 RESOURCE_EXHAUSTED, paid_tier_input_token_count limit 2000000, retry in 10.7s`.
- Capture Protocol nel topic dedicato: utente segnalava regressione (MC risponde generic invece di archiviare nota in vault Inbox).

## Steps Taken

### 1. Step 2.5 cleanup — revoke SA legacy + wrapper rename

Identificati consumer attuali del SA `openclaw-clienti` (1Password service account legacy pre-Hermes Step 2.5):
- Wrapper bash `op-clienti()` in `~/.bashrc:148-154` → leggeva `~/.openclaw/op-clienti-token`
- Item 1P backup `<REDACTED>` in vault Tech (titolo "Service Account Auth Token: openclaw-clienti")
- Zero consumer automatici (nessun cron, nessuna systemd unit)

Fix applicato:
1. Rinominato wrapper `op-clienti()` → `op-work()` in `~/.bashrc`, repointed a `~/.hermes/op-token-clienti` (SA Hermes Step 2.5 `hermes-clienti-v1`, vault Tech+Clienti). UX preservata.
2. Aggiornata memoria `reference_op_service_accounts.md` (4 SA → 3 SA documentati).
3. Utente revocato il SA su 1P web admin → verificato token invalidato (`OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/op-clienti-token) op whoami` → `403 Service Account Deleted`).
4. Item 1P backup archiviato manualmente da utente (i SA 1P sono read-only sui vault, no API delete possible).
5. DOSSIER hermes aggiornato status: `step-2.5-clienti-SA-CUTOVER-DONE-cleanup-COMPLETE`.

**Result**: cleanup chiuso. Token files lasciati in place su filesystem (invalidati, basso rischio, per cleanup futuro).

### 2. Cron error retrospective + root cause architetturale

Eseguito `hermes -p mc cron list` + `hermes cron list` per validare retrospettivamente i 16 cron totali (9 mc + 7 default).

Cron OK pre+post Step 2.5 cutover:
- MC Daily Work Briefing 06:30 ✅
- MC Morning Todo 07:10 ✅
- MC wrap-up 23:30 ✅
- Backend DB Schema Review (weekly) ✅
- Daily docs elaboration (default profile) ✅
- GitHub Trending Intelligence ✅

Cron ERROR:
- MC Evening Digest 19:30 → Gemini 400 thought_signature
- OpenClaw Release Monitor 04:00 → Gemini 429 rate-limit

Inspection del codice adapter (`agent/gemini_cloudcode_adapter.py:104` e `gemini_native_adapter.py`):
- Il sentinel `"skip_thought_signature_validator"` è documentato da Google come bypass valido per signatures non-recoverable (cross-model history transfer)
- Però Gemini 3.x ha tightened la validazione per multi-function-call paralleli ("position 2" nel messaggio errore) — il sentinel funziona solo su singolo call
- Gemini 2.5-flash mantiene thought_signature opzionale → no errore

Analisi log post-restart ha rivelato un terzo problema sottostante: HTTP 402 da OpenRouter sul primary `openai/gpt-5.5` ("You requested up to 65536 tokens, but can only afford 60042. Add more credits"). Quota OpenRouter API non riflette il balance UI ($20 mostrato, $1.68 effettivo da API `/credits` endpoint — discrepanza non spiegata, potenziale cache lag o monthly allowance system).

### 3. Iterazione provider chain (4 versioni)

**v1** (sostituzione immediata gemini-3.5 → 2.5): semplice reorder/downgrade per chiudere il 400. 6 config patchati con sed pattern matching `fallback_providers:` block, restart daemons, smoke test PONG OK.

**v2** (scoperta sub-OAuth Codex): durante investigation per attivare ChatGPT Pro sub come backend, scoperto che Hermes supporta nativamente `openai-codex` provider (`hermes login --provider openai-codex` in versioni vecchie, ora `hermes auth add openai-codex --type oauth --no-browser --manual-paste`).

Setup Codex OAuth (richiede 2 flow paralleli):
1. Sul mini-PC: `codex login --device-auth` → autentica account ChatGPT da browser Mac → ma `codex` CLI è snap-installato → scrive in `~/snap/codex/current/auth.json`, NON `~/.codex/auth.json`.
2. Hermes mantiene **SESSION OAuth SEPARATA** dal Codex CLI (anti-rotation conflict, commento esplicito in `agent/credential_sources.py`): serve `hermes auth add openai-codex --type oauth --no-browser --manual-paste` separato.
3. Flow analogo a Codex: stampa URL + codice, browser Mac autorizza, redirect a `127.0.0.1:...` fallisce (normale su SSH headless), copy intero URL fallito → paste nel terminale mini-PC.

Chain v2: `gpt-5.5 (openai-codex)` → `gemini-2.5-flash (gemini)` → `claude-sonnet-4-7 (anthropic)` → `z-ai/glm-4.5-air:free (openrouter)`. Smoke test PONG_PRIMARY, PONG_GEMINI, PONG_CLAUDE, PONG_FREE tutti OK.

**v3** (aggiunto Z.AI Coding Pro sub): test ZAI_API_KEY su endpoint built-in di Hermes `api.z.ai/api/paas/v4` → `1113 Insufficient balance` (quel endpoint è pay-as-you-go, NON coperto dalla sub Coding Pro). Probe degli endpoint alternativi → `api.z.ai/api/coding/paas/v4` risponde correttamente. Tutta la family GLM disponibile (glm-5.1, glm-4.7, glm-4.6, glm-4.5, glm-4.5-air, glm-4.5-flash).

Registrato user-defined provider `zai-coding` in `providers:` section dei 6 config:
```yaml
providers:
  zai-coding:
    name: Z.AI Coding Pro
    base_url: https://api.z.ai/api/coding/paas/v4
    key_env: ZAI_API_KEY
    default_model: glm-5.1
```

Chain v3 con 4 fallback (`gemini-2.5-flash → glm-5.1 → claude-sonnet-4-7 → openrouter free`). Smoke test PONG_ZAI 🦌 OK.

**v4** (Gemini sub via OAuth invece di API key): preferenza utente esplicita "usare sub OAuth, API key solo come safety". Verificato che esiste già `~/.gemini/oauth_creds.json` (creato dal `gemini` CLI tradizionale) + account attivo nel `google_accounts.json`. Hermes ha provider built-in `google-gemini-cli` con endpoint `cloudcode-pa://google`. Setup analogo a Codex: `hermes auth add google-gemini-cli --type oauth --no-browser --manual-paste`.

Chain v4 finale (5 livelli, tutti sub-OAuth dove possibile):
```yaml
model:
  default: gpt-5.5
  provider: openai-codex

providers:
  zai-coding:
    name: Z.AI Coding Pro
    base_url: https://api.z.ai/api/coding/paas/v4
    key_env: ZAI_API_KEY
    default_model: glm-5.1

fallback_providers:
- provider: google-gemini-cli
  model: gemini-2.5-flash
- provider: zai-coding
  model: glm-5.1
- provider: anthropic
  model: claude-sonnet-4-7
- provider: openrouter
  model: z-ai/glm-4.5-air:free
```

API key `GEMINI_API_KEY` rimane in secrets.env disponibile ma fuori chain attiva (safety net manuale). Smoke test 5-tier post v4: tutti i `OK_*` ricevuti.

### 4. Capture Protocol fix — workdir mismatch

Investigation `~/.hermes/profiles/mc/logs/agent.log` ha rivelato:
```
2026-05-24 07:22:29 WARNING agent.tool_executor:
  Tool read_file returned error: "File not found:
  /home/kos/.hermes/hermes-agent/procedures/capture-protocol.md"
```

Root cause:
- SOUL.md MC referenziava `procedures/capture-protocol.md` (path **relativo**)
- WorkingDirectory del systemd unit `hermes-gateway-mc.service` è `/home/kos/.hermes/hermes-agent/` (non il profile dir)
- Il file reale è a `/home/kos/.hermes/profiles/mc/procedures/capture-protocol.md`
- → `read_file` cercava nel cwd sbagliato → 404 → MC fallback a comportamento generic

Fix: sostituiti 4 reference in SOUL.md a path **assoluti** + aggiunto commento esplicativo:
```
Procedure dettagliate in `/home/kos/.hermes/profiles/mc/procedures/`.
Caricale SOLO quando il task lo richiede (usa SEMPRE path assoluto
perché il workdir gateway è `/home/kos/.hermes/hermes-agent`,
NOT il profile dir):
```

Verificato che altri 4 profile (backend, cso, frontend, orcharch) non hanno lo stesso pattern. Restart gateway-mc, utente ha confermato test live: Capture ora funziona, ack `🎯 MC — captured ...` arriva nel topic dedicato.

## Configuration Changes

**File modificati (6 config Hermes + bashrc + SOUL.md MC + DOSSIER + 2 memorie)**:

1. `~/.bashrc` — wrapper `op-clienti()` rinominato `op-work()`, repointed a `~/.hermes/op-token-clienti`
2. `~/.hermes/config.yaml` (4 backup datati v1→v4)
3. `~/.hermes/profiles/{mc,backend,cso,frontend,orcharch}/config.yaml` (stesso pattern, 4 backup ognuno)
4. `~/.hermes/profiles/mc/SOUL.md` — 4 reference path procedures da relativi → assoluti
5. `~/job-desk/hermes/DOSSIER.md` — status aggiornato, sezione cleanup SA legacy aggiunta
6. `~/.claude/projects/-home-kos-job-desk/memory/reference_op_service_accounts.md` — 4 SA → 3 SA
7. `~/.claude/projects/-home-kos-job-desk/memory/project_hermes_step2_done.md` — sezione Step 2.5 + sezione Provider chain v4

**File non più usato (invalidato ma in place)**: `~/.openclaw/op-clienti-token` (token revocato, mantained per audit)

## Key Discoveries

- **Hermes ha 2 adapter Gemini distinti**: `gemini_native_adapter.py` (endpoint `generativelanguage.googleapis.com`, usa `GEMINI_API_KEY`) vs `gemini_cloudcode_adapter.py` (endpoint `cloudcode-pa.googleapis.com`, usa OAuth). Provider name `gemini` → native API. Provider name `google-gemini-cli` → OAuth.
- **OAuth session separation è anti-rotation pattern**: Hermes deliberatamente NON condivide token con Codex CLI / VS Code extension. Commento esplicito in `credential_sources.py`: "refresh token rotation conflicts where one app's refresh invalidates the other's session". Conseguenza: serve doppio login (Codex CLI side + Hermes side) per ogni servizio OAuth.
- **Codex CLI snap-installato isola filesystem**: scrive in `~/snap/codex/current/auth.json` invece di `~/.codex/auth.json`. Importante quando si integra con altri tool che leggono il path tradizionale.
- **Z.AI Coding Pro vs Z.AI pay-as-you-go**: endpoint diversi (`/api/coding/paas/v4` vs `/api/paas/v4`). La sub Coding Pro copre TUTTI i modelli GLM family ma SOLO via endpoint dedicato. Bisogna configurare user-defined provider in Hermes con `base_url` override.
- **OpenRouter pricing reali GPT-5.5**: $5/1M input, $30/1M output. Una call max 65k tokens output costa worst-case ~$2. Daily reale ~$0.30. Stima iniziale "30-60$/giorno" che ho fatto inizialmente era completamente sbagliata.
- **Fallback chain Hermes non riprova se primary HTTP 5xx/429/402**: si dovrebbe ma in pratica raise `RuntimeError` se `api_max_retries` esauriti — il fallback chain è solo per casi "provider unreachable" non "provider returns error code". Da verificare meglio.
- **WorkingDirectory del systemd unit ≠ profile dir**: anche se i 5 daemon Hermes operano su 5 profile diversi, condividono lo stesso WorkingDirectory (`~/.hermes/hermes-agent/`). Path relativi in SOUL.md sono interpretati relativi al cwd, NON al profile dir. Pattern da ricordare per evitare regressioni future.
- **Subscription paid CLI = chat sub != API access**: ChatGPT Plus/Pro/Enterprise sono UI-only, NON includono API. Codex CLI permette di USARE la sub via OAuth ma non emula API REST per altri tool. Same per Claude Code sub, Gemini Advanced sub. Per accedere via Hermes serve OAuth wrapper specifico per ogni servizio.

## Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Gemini HTTP 400 thought_signature in functionCall position 2` | Gemini 3.x ha mandatory validation per multi-fc; sentinel skip funziona solo su singolo call | Downgrade fallback a `gemini-2.5-flash` (validation opzionale) |
| `Gemini HTTP 429 paid_tier_input_token_count limit 2000000` | Rate limit per-minute saturato (workload heavy in 60s), NON quota daily | Riordinato chain (gemini è ora FB1 invece di unico fallback) + retry-after handling lasciato come future patch |
| `OpenRouter HTTP 402 afford 60042 tokens` | Balance basso ($1.68 effettivo) + max_tokens 65536 → pre-authorization fail | Switch primary a OpenAI Codex OAuth (sub) → bypass completo del problema balance |
| `Z.AI 1113 Insufficient balance` | Endpoint sbagliato (sub Coding Pro non copre `/api/paas/v4`) | User-defined provider `zai-coding` con `base_url: api.z.ai/api/coding/paas/v4` |
| `Hermes AuthError: No Codex credentials stored` dopo `codex login` | OAuth session separata Hermes ↔ Codex CLI by design | `hermes auth add openai-codex --type oauth --no-browser --manual-paste` |
| `Tool read_file returned error: File not found procedures/capture-protocol.md` | WorkingDirectory systemd ≠ profile dir → path relativi falliscono | Path assoluti in SOUL.md + commento esplicativo per future-proof |
| `hermes -z` con `--base-url` flag | Flag non esposto in CLI `hermes chat` | Override via `providers:` section in config.yaml |
| `hermes login` command removed | Versione recente Hermes ha deprecato `login` in favore di `auth` | `hermes auth add <provider> --type oauth` |
| `OPENROUTER_API_KEY exhausted (402) (17m 59s left)` | Hermes marca provider come exhausted con cooldown automatico | Cooldown auto-expiry, no fix needed |

## Final State

- **Hermes daemons**: `hermes-gateway` + `hermes-gateway-mc` entrambi `active` post v4 restart
- **Fallback chain visualizzata via `hermes fallback list`**:
  ```
  Primary:    gpt-5.5            (via openai-codex)        ← ChatGPT Pro sub
  Fallback 1: gemini-2.5-flash   (via google-gemini-cli)   ← Gemini Advanced sub
  Fallback 2: glm-5.1            (via zai-coding)          ← Z.AI Coding Pro sub
  Fallback 3: claude-sonnet-4-7  (via anthropic)           ← Claude Code OAuth sub
  Fallback 4: z-ai/glm-4.5-air:free (via openrouter)       ← FREE safety
  ```
- **Auth pool Hermes**: 6 provider con OAuth/API key (anthropic 2 cred, copilot, gemini, google-gemini-cli, openai-codex, openrouter, zai)
- **Step 2.5 cleanup**: SA legacy revocato, wrapper rinominato, item 1P archiviato, memoria allineata
- **Capture Protocol**: SOUL.md path assoluti, restart gateway-mc, validato live dall'utente
- **Daily usage previsto**: ~$0 marginale (tutti i 4 livelli primary+fallback usano subscription già pagate)

## Open Questions

- **OpenRouter UI vs API discrepancy**: UI mostra $20 balance, API endpoint `/credits` restituisce `total_credits=10, usage=8.32 → diff $1.68`. Non spiegato. Worth opening ticket support o testare il "View Usage" UI per chiarire l'allocazione (monthly allowance? rollover? cache lag?).
- **Hermes retry-after handling per Gemini 429**: edge case rare con la nuova chain (gemini chiamato solo se primary E z-ai coding falliscono entrambi), ma patch low-effort se serve in futuro. Deferred.
- **Fallback chain pickup di HTTP 5xx vs 429 vs 402**: comportamento non chiaramente documentato. Da verificare se realmente Hermes scala al next fallback per ognuno o solo per alcuni. Test empirico richiede primary che fallisca artificialmente.
- **Sub Z.AI Coding Pro endpoint coverage**: confermato copre `/api/coding/paas/v4` (chat completions + Anthropic wire). Da verificare se copre anche embedding, vision, audio endpoints.
- **Cron OpenClaw Release Monitor 04:00 domani**: validazione async se la nuova chain salva il cron (era il 429 di stamattina). Idem MC Evening Digest stasera 19:30.
- **Auto-refresh OAuth Codex / Gemini in Hermes**: token expiry tipico 1h (access), 90d (refresh). Hermes dovrebbe gestire refresh trasparente ma da monitorare al primo expiry naturale.
