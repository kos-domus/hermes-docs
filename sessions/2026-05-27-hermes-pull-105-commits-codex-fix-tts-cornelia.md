---
title: "Hermes upstream pull 105 commit (Codex NoneType fix) + config v23→v24 migrate 7 profile + ElevenLabs Cornelia TTS setup"
date: "2026-05-27"
author: "kos-domus"
status: "ready"
tags: ["configuration", "troubleshooting", "automation", "api", "security"]
session_type: "hermes"
client: ""
openclaw_version: ""
environment:
  os: "Linux 6.17.0-29-generic"
  ide: "Claude Code (VSCode extension)"
  model: "claude-opus-4-7[1m]"
---

## Objective

1. Sbloccare il bug Codex `TypeError 'NoneType' object is not iterable` che da 24h forzava la chain v5 di Hermes a cascade su FB2 Z.AI (latency +1-2s) per ogni invocation che usava `openai-codex/gpt-5.5`.
2. Setup ElevenLabs Creator TTS sul profilo `family-staging` (assistente domestico Kai) per upgrade voice quality dal default Edge TTS gratuito.

## Context

**Stato in apertura (handoff dalla sessione precedente)**:
- Hermes HEAD: `2517917de` (25/05). 105 commit di ritardo rispetto a `origin/main` (scoperto solo dopo `git fetch` integrato in `git pull`, prima audit naive `git log HEAD..origin/main` riportava solo 8 commit perché origin/main era stale dalla precedente fetch).
- 3 daemon attivi: `hermes-gateway.service` (default), `hermes-gateway-mc.service` (mc), `hermes-gateway-family-staging.service` (family-staging — Kai shadow Fase 1).
- 4 specialist profile passive: backend, cso, frontend, orcharch (Work fleet).
- Chain v5 funzionante via FB2 cascade — primary Codex unable.
- ElevenLabs Creator $22/mo sub appena acquistata dall'utente, API key da generare.
- Voce Kai attuale: Edge TTS `it-IT-IsabellaNeural` o `it-IT-ElsaNeural` (iteration in corso).

**Open bug noti**:
- `TypeError 'NoneType' object is not iterable` su `openai-codex/gpt-5.x` qualunque modello. Documentato in memoria `feedback_hermes_provider_naming.md` come bug upstream sospettato.
- Gemini OAuth fallback layer warning ("OAuth provider not directly supported in fallback") — workaround chain salta a FB2 silenziosamente.
- OpenRouter FB5 credit error (account out of credit, FB5 last resort raramente chiamato).

## Steps Taken

### 1. Audit upstream Hermes — identificazione fix Codex

```bash
cd ~/.hermes/hermes-agent && git fetch
git log --oneline HEAD..origin/main
# 8 commit reported (stale fetch state)
git log --since="2026-05-15" --all | grep -iE "codex|gpt-5"
```

Trovato `43a3f119f fix(agent): recover Codex streams with null output` (26/05 17:15 PST) — commit message ESATTO descrive il nostro bug:
> "The OpenAI Python SDK's high-level `client.responses.stream(...)` helper does post-hoc typed reconstruction from the terminal `response.completed.response.output` field. The chatgpt.com Codex backend has been observed (today, gpt-5.5) to ship `response.output = null` on terminal frames, which crashes the SDK with `TypeError: 'NoneType' object is not iterable` mid-iteration."

Il fix introduce `_responses_null_output_iterable_error()` detector + backfill response da streamed events.

**Result**: bug confermato upstream, fix already merged. Pull necessario.

### 2. Pre-pull safety: stash local mod + sanity

Working tree aveva modifica locale `hermes_cli/mcp_config.py` (env override `HERMES_MCP_CONNECT_TIMEOUT` per MCP OAuth flows con SSH tunnel + browser interaction, es. Sentry MCP login). Check conflict potenziale:

```bash
git diff HEAD..origin/main -- hermes_cli/mcp_config.py
# Upstream change at line ~749 (mcp_command picker subcommands)
# Local change at line ~165 (_probe_single_server timeout)
# Different sections → 3-way merge clean expected
git stash push -m "local-mcp-oauth-timeout-override-20260527"
```

**Result**: stash creato, working tree clean per pull.

### 3. Git pull — sorpresa volume

```bash
git pull --ff-only
```

Output:
```
2a8d21741..f0de3cd0a  main       -> origin/main
Updating 2517917de..f0de3cd0a
Fast-forward
 245 files changed, 18509 insertions(+), 4554 deletions(-)
```

**Discovery**: il pull's internal fetch ha aggiornato origin/main da `2a8d21741` a `f0de3cd0a` mid-operation. **Audit pre-pull (8 commit) era stale** — actual pull portava **105 commit**.

```bash
git stash pop
# Auto-merging hermes_cli/mcp_config.py
# No conflicts → local mod re-applied clean
```

**Result**: HEAD `2517917de → f0de3cd0a`, 105 commit applied, local mod preserved.

### 4. Audit 105 commit per categoria

| Category | Count | Notable commits |
|---|---|---|
| Critical Codex fixes | 5 | `cb38ce28c` refactor(codex) drop SDK responses.stream() consume events directly — **THE FIX strutturale**, bypassa il bug; `43a3f119f` catch preventivo; `b6ca56f65` invalid_encrypted_content recovery; `9c69204d8` foreign-issuer reasoning drop; `b1a46b304` rs_tmp transient state cleanup |
| Reliability/perf | ~12 | `f0de3cd0a` switch_model() rollback robustness (snapshot+restore on rebuild fail — relevant per chain v5 fallback); `8601c4d44` Codex TTFB watchdog; `2bbd53493` credential_pool sync on Codex re-auth; `f1422ffd7` 429 quota classification; `b4eea187d` + `a699de83e` xAI OAuth slash-enum + service_tier sanitization (FB4 grok robust) |
| Telegram noise reduction | 4 | `0325e18f3` heartbeat in-place edit; `60f84c6c2` quiet operational chatter; `8807b1c72` hide compaction status; `efa952531` ignore start pings |
| Dashboard auth (new feature) | ~25 | OAuth gating per web dashboard: login page, cookies, WS tickets, audit log, plugin `dashboard_auth/nous` (Nous Portal provider built-in). Fail-closed on no providers. **Non usiamo web dashboard → impatto 0.** |
| security-guidance plugin (new opt-in) | 1 (`249534e47`) | 25 pattern-matched warnings su file writes pericolosi (pickle.load, yaml.load, eval, dangerouslySetInnerHTML, ECB, XXE, GHA injection, torch.load no weights_only=True). Default non-blocking, `SECURITY_GUIDANCE_BLOCK=1` per block. Candidate per CSO posture su Hermes-driven write_file. |
| Removals | 1 (`febc4cfec`) | Vercel AI Gateway + Vercel Sandbox removed. `vercel_runtime: node24` config key obsoleta ma ignorata silently. **No impact noi.** |
| API server features | 4 | `f7527b0fd` session controls; `25f43d38d` GET /v1/skills + /v1/toolsets; `464b51d45` media in session chat API; `96223265b` skills_api capability flag |
| MCP catalog | 1 (`8b69ec03a`) | Nous-approved MCP catalog + interactive picker `hermes mcp picker` |
| TUI session orchestrator | 1 (`0a83247e9`) | TUI-only feature |
| Docs + tests + chore | ~50 | Coverage per i fix + `hermes login` → `hermes auth add` rename refs |

### 5. Verifica fix presente nel working tree

```bash
grep -nE "responses\.stream|null output|NoneType" agent/auxiliary_client.py agent/codex_runtime.py agent/codex_responses_adapter.py
```

Conferma:
- `agent/codex_runtime.py:185` ha commento "`TypeError: 'NoneType' object is not iterable` mid-iteration" + bypass strutturale
- `agent/auxiliary_client.py:786,790` riferimenti al refactor (drop SDK helper)

### 6. Test Codex fix — direct provider invocation

```bash
hermes -p family-staging -z "Rispondi solo con: TEST OK" -m gpt-5.5 --provider openai-codex
# Output: "TEST OK"
```

✅ **Fix confirmed**. Nessun TypeError, nessuna cascata FB2.

### 7. Restart 3 daemon attivi per pickup nuovo codice

```bash
systemctl --user restart hermes-gateway-family-staging.service
systemctl --user restart hermes-gateway-mc.service hermes-gateway.service
# All active running, zero errors in journalctl
```

Test chain v5 primary (no `-m` override → chain v5 default):
```bash
hermes -p family-staging -z "Rispondi solo con: CHAIN OK"
# Output: "CHAIN OK"
```

✅ Primary `openai-codex/gpt-5.5` ritorna diretto, no FB2 cascade.

### 8. Verifica impatto Vercel removal + dashboard auth

```bash
grep -rE "vercel|VERCEL" ~/.hermes/config.yaml ~/.hermes/profiles/*/config.yaml
# 5 profile hanno `vercel_runtime: node24` (config key dentro blocco sandbox runtime)
grep -A 10 "^dashboard:" ~/.hermes/config.yaml
# Solo theme + show_token_analytics. No web dashboard attivo, no oauth provider configurato.
hermes -p family-staging doctor
# ✓ All packages, ✓ OAuth tutti loggati, ⚠ Config v23 → v24 outdated
# Nessun errore vercel_runtime → key obsoleta ignorata silently
```

**Result**: Vercel removal benign, dashboard auth non triggera fail-closed (non usiamo dashboard).

### 9. Config v23 → v24 migrate — 7 profile

Strategy: test su default profile first, audit diff completo, poi propagare.

```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.pre-v24-migrate.bak
hermes config migrate
diff ~/.hermes/config.yaml.pre-v24-migrate.bak ~/.hermes/config.yaml
```

**Diff analysis** (131 righe):
- ➕ `providers: {}` aggiunto (empty section, scaffolding canonical surface v24)
- 🔀 `mcp_servers:` block MOVED da top (line 16) a bottom (line 513). Content preserved (sentry + github + filesystem + codebase-memory).
- 🔀 `vercel_runtime: node24` MOVED da line 106 a line 115 (still present, legacy ignored).
- ✏️ Emoji system prompts (`kawaii`, `catgirl`, `surfer`, `hype`) re-encoded come unicode escapes (`◕`, `\U0001F525`) — cosmetic, less readable in editor, no functional change.
- ➕ Nuovi opt-in defaults: `resume_*` (5 keys), `gateway:` block (media_delivery_allow_dirs, trust_recent_files, trust_recent_files_seconds), `dashboard.oauth:` block (client_id, portal_url, public_url empty), `paste_collapse_threshold*` (3 keys), `fallback_model:` commented documentation block.

**Risk assessment**: false alarm su `mcp_servers` rimozione — solo spostato. `hermes mcp list` conferma tutti e 4 MCP server attivi.

Apply su 6 profile rimanenti:
```bash
for p in mc backend frontend cso orcharch family-staging openclaw-observer; do
  cp ~/.hermes/profiles/$p/config.yaml ~/.hermes/profiles/$p/config.yaml.pre-v24-migrate.bak
  hermes -p $p config migrate
done
# 7/7 → Config version 23 → 24
```

Restart 3 daemon attivi per pickup nuova config:
```bash
systemctl --user restart hermes-gateway.service hermes-gateway-mc.service hermes-gateway-family-staging.service
journalctl --user -u hermes-gateway*.service --since "1 minute ago" | grep -iE "error|exception|nonetype"
# Zero output → clean restart
```

Doctor verify v24 (default + mc + family-staging): `✓ Config version up to date (v24)`.

### 10. ElevenLabs Creator API key generation con least-privilege scoping

Brief utente su scoping ElevenLabs dashboard:
- **Usage Limit**: 50000 credits/mo (50% del plan 100k/mo, lascia margine future experiments). Hard cap previene runaway cost da bug Hermes (es. loop infinito che chiama TTS).
- **Endpoints granted**: Text to Speech (Access), Voices (Read), Models (Access), User (Read), History (Read opzionale). **Tutto il resto NO ACCESS** (Speech to Speech/Text, Sound Effects, Audio Isolation, Music Generation, Dubbing, ElevenAgents, Projects, Audio Native, Voice Generation, Forced Alignment, Pronunciation Dictionaries, Workspace*, Service Accounts, Webhooks, Group Members, Audit Log, ToS Accept).
- Rationale: se la key leak (es. .env accidental commit, lessoned learned dall'incident 25/05 OP_SERVICE_ACCOUNT_TOKEN), blast radius limitato a "genera TTS + lista voci" — non può modificare workspace, invitare members, vedere audit log, fare admin. Future: per Voice Cloning o Sound Effects → key separata scoped solo per quello, mai upgradare questa.

Utente generata + salvata in 1P vault Tech come API_CREDENTIAL item (field `credential`).

### 11. Lettura API key da 1P + scrittura in family-staging .env

```bash
unset OP_SERVICE_ACCOUNT_TOKEN  # evita stale env var conflict (gotcha noto)
export OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.op-service-account-token)

# Discovery item title (non era "ElevenLabs" diretto):
op item list --vault Tech | grep -iE "eleven|labs"
# Output: <REDACTED_OP_ITEM_ID>    Eleven Labs - Hermes OC stuff API Key   Tech

# Read field structure (con --vault esplicito, required per SA):
op item get "<REDACTED_OP_ITEM_ID>" --vault Tech
# Field: credential

# Write to .env senza esporre valore in shell history o tool output:
{
  grep -v "^ELEVENLABS_API_KEY=" ~/.hermes/profiles/family-staging/.env 2>/dev/null
  echo "ELEVENLABS_API_KEY=$(op read 'op://Tech/<REDACTED_OP_ITEM_ID>/credential')"
} > /tmp/env.new && mv /tmp/env.new ~/.hermes/profiles/family-staging/.env
chmod 600 ~/.hermes/profiles/family-staging/.env
```

Verify (senza printare valore):
- Mode: 600 ✓
- ELEVENLABS_API_KEY entries: 1 ✓
- Length: 51 chars (ElevenLabs format `sk_*` confermato)

### 12. ElevenLabs voice library exploration

```bash
KEY=$(grep "^ELEVENLABS_API_KEY=" ~/.hermes/profiles/family-staging/.env | cut -d= -f2-)

# User library (premade default voices):
curl -s -H "xi-api-key: $KEY" https://api.elevenlabs.io/v1/voices
# 21 voices, all labeled lang=en (Bella, Sarah, Alice, Matilda, Jessica, George, Brian...)
# Con eleven_multilingual_v2 model parlano IT fluente ma con leggero English-accented accent

# Shared library filtrato IT:
curl -s -H "xi-api-key: $KEY" "https://api.elevenlabs.io/v1/shared-voices?language=it&page_size=15"
# 15 voci IT-native (Cornelia, Aurora, Daniela Narrator, MVee, Hannalise, Marta, Paolo, ...)
```

**Discovery**: Voci shared library usabili **direttamente** via voice_id in `/v1/text-to-speech/{voice_id}` — non serve "add to library" preliminare (alcune voci richiedono add, le premade community-shared no).

### 13. Voice selection — 3 candidate per Kai

Profilo Kai (assistente domestico, femminile, warm + practical, decisione Q2 sessione precedente):

| Pick | Nome | voice_id | Accent | Cloned by | Note |
|---|---|---|---|---|---|
| 🥇 | Cornelia | `SKEVNjRKCergbPKum64u` | standard | **2135** | "Calming and warm, customer support or narration" — highest community social proof |
| 🥈 | Aurora | `3LTv5xMEHTJYUIMl1jBR` | milanese | 86 | Clear & Supportive, calm authority |
| 🥉 | Daniela Narrator | `VZOd9FMXDnXRZpGn0thg` | standard | 326 | Studio-quality professional narrator |

Test diretto Cornelia (8s, 25 parole, ~160 credits):
```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/SKEVNjRKCergbPKum64u" \
  -H "xi-api-key: $KEY" \
  -d '{"text": "...", "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "use_speaker_boost": true}}'
# HTTP 200, MP3 133KB / 128kbps / 44.1kHz / mono
```

### 14. Side-by-side delivery samples Cornelia (ElevenLabs) vs Isabella (Edge)

Generato Isabella Edge sample same text via `edge-tts --voice it-IT-IsabellaNeural`. Convert mp3 → opus per Telegram voice memo UX:

```bash
ffmpeg -i /tmp/cornelia-test.mp3 -c:a libopus -b:a 32k /tmp/cornelia-test.ogg
ffmpeg -i /tmp/isabella-edge.mp3 -c:a libopus -b:a 32k /tmp/isabella-edge.ogg
```

Delivery via Telegram Bot API `sendVoice` a `<KAI_STAGE_BOT_DM>`:
```bash
curl -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendVoice" \
  -F "chat_id=TG_USER_ID" \
  -F "voice=@/tmp/cornelia-test.ogg" \
  -F "caption=🥇 Cornelia ElevenLabs"
# Plus same per isabella-edge.ogg
```

**Verdict utente**: Cornelia vince ("straordinario / sensazionale").

### 15. Demo lungo per partner — sendAudio (forwardable WhatsApp)

Generato demo ~22s (~250 credits) con testo neutro family-context (introduzione capacità Kai con prosody naturale, stability 0.55 per delivery più calma).

Delivery via `sendAudio` (non `sendVoice` — formato mp3 playable + saveable + forwardable, non voice memo "throwaway"):
```bash
curl -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/sendAudio" \
  -F "chat_id=TG_USER_ID" \
  -F "audio=@/tmp/kai-demo.mp3" \
  -F "title=Kai - Presentazione" \
  -F "performer=Voce Cornelia (ElevenLabs IT)"
# msg_id 179, size 269.4KB
```

Utente può inoltrare via lungo-tap → Forward → WhatsApp.

## Configuration Changes

### Hermes core
- `~/.hermes/hermes-agent` HEAD: `2517917de` → `f0de3cd0a` (105 commit pulled, 245 file changed, 18509 insertions)
- Local mod preserved: `hermes_cli/mcp_config.py` (timeout env var override `HERMES_MCP_CONNECT_TIMEOUT` per MCP OAuth flows) — auto-mergiata clean via stash pop

### Config profiles (7 migrated v23 → v24)
- `~/.hermes/config.yaml` (default Kos)
- `~/.hermes/profiles/{mc,backend,frontend,cso,orcharch,family-staging,openclaw-observer}/config.yaml`
- Backup `.pre-v24-migrate.bak` salvato per ogni file (rollback path: `mv X.bak X`)

### .env update
- `~/.hermes/profiles/family-staging/.env`: aggiunto `ELEVENLABS_API_KEY=<REDACTED>` (mode 600)
- **No env_passthrough whitelist** — per memoria `feedback_hermes_env_passthrough.md`, le API key provider Hermes le legge dal main process env via `load_dotenv(.env)` at boot, NON via env_passthrough (che Hermes blocca per security GHSA-rhgp-j443-p4rf, sandbox credential scrubbing).

### Daemon restart (3)
- `hermes-gateway.service` (default Kos)
- `hermes-gateway-mc.service` (mc)
- `hermes-gateway-family-staging.service` (family-staging — Kai shadow)
- 4 passive specialist (backend, cso, frontend, orcharch) carico fresh next invocation (no restart needed)

### TTS config family-staging (PATCH READY, NON APPLICATA ANCORA)
Pending positive feedback partner before flipping. Patch:
```yaml
tts:
  provider: elevenlabs   # was: edge
  elevenlabs:
    voice_id: SKEVNjRKCergbPKum64u   # was: pNInz6obpgDQGcFmaJgB (default scaffold)
    model_id: eleven_multilingual_v2  # already set
```

## Key Discoveries

- **Hermes upstream è veloce**: same-day fix uploaded per Codex backend regression (43a3f119f il 26/05 17:15 PST, refactor strutturale cb38ce28c il 27/05 00:30 PST). Disciplina: weekly `cd ~/.hermes/hermes-agent && git fetch && git log HEAD..origin/main` minimum, monthly `git pull` review.
- **`git pull` può espandere lo scope mid-operation**: il `git fetch` interno aggiorna `origin/main` rispetto a una fetch precedente stale → audit pre-pull può sotto-stimare il volume. Mitigazione: `git fetch && git log HEAD..origin/main` IMMEDIATAMENTE prima di `git pull`.
- **ElevenLabs `/v1/shared-voices?language=it`** restituisce voci IT-native usabili **direttamente** via voice_id in `/v1/text-to-speech/{voice_id}` — no library-add preliminare per voci community-shared.
- **Hermes config v23 → v24 migrate è cosmetico**: muove `mcp_servers:` dal top al bottom del file (semantica preserved), re-encoda emoji prompts come unicode escapes (less readable, no functional change), aggiunge sezioni opt-in (resume, gateway, dashboard.oauth, paste_collapse, fallback_model commented). `vercel_runtime:` key obsoleta ma migrate la mantiene comunque (legacy compat).
- **Cornelia `SKEVNjRKCergbPKum64u`** (standard accent, "calming and warm, customer support or narration", 2135 community clones) = highest social proof su IT female voices. Stability 0.55 + similarity_boost 0.75 + use_speaker_boost = delivery naturale + steady per persona Kai.
- **Cost math ElevenLabs Creator $22/mo**: 100k credits/mo. Briefing Kai 15-30s ≈ 150-300 credits → ~333-666 briefings/mo. Hard cap 50k self-imposed (50% plan) → ~165-330 briefings, abbondante per use case daily briefing famiglia.
- **`op` CLI gotcha** (già noto da memoria `feedback_session_persistence.md`): biometric/desktop integration prompt dismissal causa "authorization prompt dismissed" anche quando SA token disponibile. Workaround: `unset OP_SERVICE_ACCOUNT_TOKEN` + `export OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.op-service-account-token)` + sempre `--vault <name>` quando usi SA (anche con item ID).
- **`hermes send` è text-only** — per delivery audio via Telegram serve direct Bot API `sendVoice` (opus + voice memo UX) o `sendAudio` (mp3 + playable+forwardable file). `sendDocument` come fallback se richiesto.

## Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `git log HEAD..origin/main` reportava 8 commit ma `git pull` ne portava 105 | Stale fetch state: `origin/main` aggiornato mid-pull dal fetch integrato | Run `git fetch` immediately before `git log` audit, OR audit `git log 2517917de..HEAD` post-pull |
| `op item get "ElevenLabs" --vault Tech` → "isn't an item" | Item title era "Eleven Labs - Hermes OC stuff API Key" (con spazi, descriptive), non "ElevenLabs" | `op item list --vault Tech | grep -i eleven` per discovery, poi usare ID o exact title |
| `op item get <ID>` → "vault query must be provided" | Service account richiede `--vault <name>` flag esplicito anche con item ID (a differenza di sessione interactive) | Sempre `--vault <name>` quando `OP_SERVICE_ACCOUNT_TOKEN` è set |
| `op item get ... --vault Tech` → "authorization prompt dismissed" | 1P desktop biometric prompt competeva con SA token (mode mix) | `unset OP_SERVICE_ACCOUNT_TOKEN` poi `export` esplicito da file |

## Final State

- ✅ Codex bug `'NoneType' not iterable` **RESOLVED upstream** via `cb38ce28c` refactor strutturale (drop SDK responses.stream() helper, consume events directly)
- ✅ Hermes HEAD `f0de3cd0a` (Wed 27/05 05:43 PST)
- ✅ 105 commit applied, 245 file changed
- ✅ 7 profile config @ v24
- ✅ 3 daemon restarted, healthy (zero error in journalctl)
- ✅ Chain v5 primary `openai-codex/gpt-5.5` returns direct, no FB2 cascade
- ✅ ElevenLabs Creator API key generata + scoped least-privilege (50k cap, TTS+Voices+Models only) + salvata 1P vault Tech + scritta in family-staging .env (mode 600)
- ✅ Cornelia (`SKEVNjRKCergbPKum64u`) test diretto API → MP3 generated successfully
- ✅ Side-by-side samples Cornelia vs Isabella Edge delivered via Telegram
- ✅ Demo file forwardable mp3 (~22s, Cornelia stability 0.55) delivered via `sendAudio` per family member preview
- ⏳ TTS config switch (`provider: edge → elevenlabs`, `voice_id: Cornelia`) **patch ready ma NON applicata** — pending partner feedback before flip

## Open Questions

1. **Apply Cornelia config + restart family-staging**: gating sul positive feedback da partner. Reversibile (config backup .bak presente).
2. **Estendere TTS Edge ai 2 profile work**: Q7 sessione precedente decise Kos + MC voce on-demand (`it-IT-ElsaNeural`, `it-IT-DiegoNeural`). Da applicare post-cutover Kai weekend.
3. **security-guidance plugin enable evaluation**: candidate CSO posture, 25 pattern-matched warnings su file writes pericolosi. Test su un caso reale per valutare noise vs valore prima di enable workspace-wide.
4. **Dashboard auth**: non usiamo web dashboard ora. Decisione future: skippare permanentemente o abilitare con Nous provider per future remote access scenarios.
5. **Audit Codex OAuth status su 4 specialist passive**: test 1 chat manuale ciascuno per confermare nessun side-effect del 337-commit pull (probable OK dato che il fix è strutturale, ma worth verifying prima del cutover Kai).
6. **MC morning todo persistenti**: tracked separately in client session logs (private repo) — non-public scope, omitted here.
