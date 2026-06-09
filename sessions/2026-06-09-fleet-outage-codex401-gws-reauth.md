---
title: 'Fleet outage triage: Codex-401 cascade, gws mc re-auth, fallback-non-cattura-auth-error'
date: '2026-06-09'
author: kos-domus
status: processed
tags:
- troubleshooting
- configuration
- automation
- cron
- security
- cli
session_type: hermes
client: ''
openclaw_version: ''
environment:
  os: Linux (mini-PC kos-domus)
  ide: VSCode + Claude Code
  model: claude-opus-4-8[1m]
---
## Objective
Triage dell'outage del work fleet (profile `mc` + specialisti): il wrap serale MC riportava "🔴 OUTAGE DAY —
zero scheduled work completed", tutti i 6 cron window falliti. Capire la causa-radice e ripristinare.

## Context
- Hermes Agent v0.14.0. Gateway attivi: `hermes-gateway.service` (default), `hermes-gateway-mc.service` (work fleet),
  `hermes-gateway-family-staging.service`. Cron MC: Daily Briefing 06:30, Morning Todo 07:10, Inbox Triage 09:00,
  Sentry Weekly 09:30, Evening Digest 19:30, + i weekly trigger degli specialisti (backend/cso/frontend/orcharch).
- Sintomi dal wrap: `HTTP 401 token_expired` su `openai-codex` (gpt-5.5) ×12; `Fallback to google-gemini-cli failed:
  provider not configured` ×8; `hermes send: Platform 'telegram' is not configured` ×10; `Drive auth failed: No
  credentials found` (gws); Evening Digest in retry-loop (21 auth errors).

## Steps Taken

### 1. Diagnosi read-only (stato runtime)
`hermes status` / `hermes -p mc status` → Provider primario gpt-5.5 via OpenAI Codex, "logged in". `hermes auth list`
→ pool credenziali: openai-codex (2 oauth device_code), google-gemini-cli (oauth), xai-oauth (2), anthropic/openrouter/
gemini (api-key). `hermes fallback list` → chain v5: gemini-2.5-flash(google-gemini-cli) → glm-5.1(zai) →
claude-sonnet-4-5(anthropic) → grok(xai-oauth) → z-ai/glm-4.5-air:free(openrouter).
**Result**: contraddizione — status dice "logged in" ma i cron prendevano 401. Brain testato live (`hermes -p mc -z`) →
**risponde** (PONG/READY): l'outage acuto era già rientrato (token auto-refreshato alle 04:00 del giorno dopo).

### 2. Root cause vera
**L'outage era una CASCATA da Codex-401**: l'access token OAuth scade (TTL breve) e il refresh nel contesto cron
fallisce in modo intermittente → 401. **Gap strutturale Hermes**: la doc fallback dice "tried when the primary fails
with rate-limit, overload, or connection errors" → **il 401 (auth error) NON triggera il fallback** → quando Codex
muore di auth, niente failover, solo retry sul primario → il retry-loop dell'Evening Digest. Gli altri errori
(telegram, drive) erano **collaterali** della cascata, non guasti indipendenti.

### 3. Fix Codex (durabilità)
`hermes auth add openai-codex --type oauth` (device flow, autorizzato da Rakki al mini-PC) → cred fresca aggiunta al
pool (ora 3, fresca attiva). Nota: `hermes login` è stato RIMOSSO in v0.14 → si usa `hermes auth add`.
**Result**: token fresco con refresh nuovo → riduce la ricorrenza del 401.

### 4. Fix gws profilo mc (Drive sbloccato dopo 13 giorni)
Causa: il profilo `mc` ha HOME override `~/.hermes/profiles/mc/home`; lì c'era `client_secret.json`+`.encryption_key`
ma MANCAVA `credentials.enc`. `credentials.enc` è cifrato con la `.encryption_key` per-profilo → non copiabile dal
default. Fix = re-auth sotto l'HOME del profilo:
`HOME=/home/kos/.hermes/profiles/mc/home GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND=file gws auth login` (OAuth Google,
autorizzato da Rakki).
**Result**: `credentials.enc` rigenerato, `encryption_valid:true`, `token_valid:true` → `gws drive +upload` dei cron funzionerà.

### 5. Telegram — falso allarme
Sospetto iniziale (`platforms:{}` vuoto, TELEGRAM_BOT_TOKEN "commentato") → entrambi SBAGLIATI: `platforms:{}` vuoto è
normale (anche nel default; il gateway usa la sezione `telegram:` + `TELEGRAM_BOT_TOKEN` da secrets.env, presente e
attivo). Il quirk reale: `hermes send` standalone CLI non stabilisce la connessione telegram come il gateway → gli
specialisti già aggirano usando la Bot API dal gateway. **Non criticamente rotto**: i cron consegnano via `Deliver:
telegram:...` con last-run "ok". Era collaterale dell'outage Codex.

## Configuration Changes
- Codex: cred OAuth fresca aggiunta al pool (`hermes auth add openai-codex --type oauth`).
- gws profilo mc: `credentials.enc` rigenerato via re-auth sotto HOME del profilo.
- Nessuna modifica a config.yaml/chain (i fix sono auth-level, non config).

## Key Discoveries
- **Il fallback Hermes non fa failover sugli auth-error (401)** — solo rate-limit/overload/connection. È IL motivo per
  cui un Codex-401 tira giù tutto invece di cadere su un fallback. Mitigazione durevole: tenere il token Codex "caldo"
  (refresh proattivo prima della scadenza) — candidato per un mini-cron token-warmth.
- `hermes login` rimosso in v0.14 → `hermes auth {add,list,remove,reset,status,logout}`. `hermes auth reset <provider>`
  pulisce lo stato di exhaustion.
- I profili con HOME override (`profiles/<p>/home`) hanno gws/credenziali ISOLATE per-profilo: `credentials.enc` è
  cifrato con la `.encryption_key` di quell'HOME → mai copiare tra profili, sempre re-auth in loco.
- `hermes status` (single-cred view) può dire "logged in" mentre il pool ha cred scadute/exhausted → `hermes auth list`
  è la vista autoritativa.

## Errors & Solutions
| Error | Cause | Solution |
|-------|-------|----------|
| `HTTP 401 token_expired` openai-codex ×12 | Access token OAuth scade, refresh fallisce nel cron | `hermes auth add openai-codex --type oauth` (re-auth fresca) |
| `Fallback ... provider not configured` / retry-loop | Il 401 non triggera il fallback (solo rate-limit/5xx/conn) | Gap strutturale Hermes → mitigare con token-warmth (TODO) |
| `Drive auth failed: No credentials found` (gws mc) | `credentials.enc` mancante nell'HOME del profilo mc | re-auth gws sotto `HOME=.../profiles/mc/home` |
| `hermes send: telegram not configured` | quirk CLI standalone (gateway funziona) | non-issue; specialisti usano Bot API dal gateway |

## Final State
Brain mc risponde READY. Codex re-authed (token durevole). gws mc re-authed (Drive sbloccato). Fleet operativo.
Residuo non urgente: il gap fallback-non-cattura-401 → opzionale mini-cron token-warmth.

## Open Questions
- Perché il refresh OAuth Codex fallisce intermittentemente nel contesto cron (contesa `auth.lock` cross-profilo? TTL
  refresh token? rigidità backend ChatGPT-Codex su gpt-5.5)? Da osservare se ricapita post re-auth.
- Vale la pena un mini-cron "token-warmth" (ping/refresh proattivo Codex pre-scadenza) per chiudere il gap del 401?
