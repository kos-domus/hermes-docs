---
title: "Hermes MCP fleet propagation (5 profile) + Sentry OAuth setup 3 profile + Claude Code chrome-devtools/sentry MCP + HERMES_MCP_CONNECT_TIMEOUT patch"
date: "2026-05-26"
author: "kos-domus"
status: "processed"
tags: ["hermes", "mcp", "mcp-servers", "configuration", "automation", "api", "agent-sdk", "remote"]
session_type: "hermes"
client: ""
openclaw_version: ""
environment:
  os: "Linux 6.17.0-29-generic (Ubuntu mini-PC)"
  ide: "VSCode SSH Remote → mini-PC"
  model: "claude-opus-4-7[1m]"
---

## Objective

Estendere la copertura MCP del work fleet Hermes propagando i provider rilevanti a tutti i 5 profile (default Kos + mc + backend + cso + frontend + orcharch), completare il setup Sentry OAuth sui 3 profile che lo usano (mc + cso + frontend), installare i 2 nuovi MCP server su Claude Code (chrome-devtools-mcp + sentry-mcp). Risolvere lungo il flow il bug del timeout fisso 30s su `hermes mcp login` che rendeva impossibile completare OAuth flow interattivo con SSH tunnel.

## Context

**Stato pre-sessione**:
- Hermes work fleet già operativo post Step 2.5 (1 daemon `hermes-gateway-mc` + 4 profile specialist passivi + default profile Kos). Provider chain v4 attiva (gpt-5.5 codex → gemini-2.5-flash → glm-5.1 zai-coding → claude-sonnet-4-7 → openrouter free).
- MCP support nativo Hermes via `mcp_servers` section nel `config.yaml` per profile. CLI `hermes [-p <profile>] mcp {add,remove,list,test,configure,login}`.
- Zero MCP configurati su Hermes prima della sessione (work fleet usa solo `toolsets: hermes-cli` built-in).
- Claude Code (versione npm-global su mini-PC, accessibile da VSCode SSH) ha 14 MCP attivi (codebase-memory + obsidian + context7 + playwright + firecrawl + github + filesystem + deep-research + postgres + semgrep + trivy + 3 Google OAuth-pending).
- Rakki ha account Sentry attivo con organizzazione appena creata (`alessandrobenedetti90@gmail.com`).

**Trigger sessione**: Rakki ha chiesto se possiamo integrare Chrome DevTools MCP + Sentry MCP. Poi ha esteso a propagation cross-fleet per gli agent Hermes (mapping diverso per dominio: backend → postgres, cso → semgrep+trivy, frontend → chrome+playwright, orcharch → deep-research).

## Steps Taken

### 1. Verifica + install MCP nuovi su Claude Code

```bash
# Chrome DevTools MCP (Google official, ChromeDevTools/chrome-devtools-mcp)
claude mcp add chrome-devtools --scope user -- npx -y chrome-devtools-mcp@latest --isolated --headless

# Sentry MCP (hosted, OAuth, mcp.sentry.dev)
claude mcp add --transport http --scope user sentry https://mcp.sentry.dev/mcp
```

Verify:
```
chrome-devtools: ✓ Connected
sentry: ! Needs authentication
```

**Result**: Claude Code passa da 14 → 16 MCP attivi (12 stdio + 2 HTTP + Google OAuth). Sentry richiede OAuth flow al primo uso.

### 2. Propagation MCP a Hermes mc profile (4 MCP)

Edit diretto YAML `~/.hermes/profiles/mc/config.yaml` (CLI `hermes mcp add` ha bug con args che iniziano per `-` tipo `-y` perché argparse li interpreta come flag):

```yaml
mcp_servers:
  sentry:
    url: https://mcp.sentry.dev/mcp
    auth: oauth
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/kos/job-desk"]
  codebase-memory:
    command: codebase-memory-mcp
    args: ["--ui=true", "--port=9749"]
```

`systemctl --user restart hermes-gateway-mc.service`. Verify: `hermes -p mc mcp list` → tutti 4 ✓ enabled.

**Decisione esplicita**: **obsidian NON propagato**. Il vault file system esiste sul mini-PC (Hermes legge/scrive direttamente), ma l'app Obsidian che espone la REST API su `127.0.0.1:27124` gira sul Mac di Rakki, NON sul mini-PC. Hermes mc su mini-PC non può collegarsi. Per Capture Protocol MC usa `Write` diretto sui file via filesystem MCP — è sufficiente.

### 3. Propagation MCP ai 4 profile specialist (17 MCP slot totali)

Mapping per dominio (raccomandato Co-CEO precedente + memoria reference community resources):

| Profile | MCP propagati |
|---|---|
| **backend** | postgres (DB Spesabot read) + github + filesystem + codebase-memory |
| **cso** | semgrep + trivy + github + sentry + filesystem |
| **frontend** | chrome-devtools (isolated+headless) + playwright + sentry + filesystem |
| **orcharch** | deep-research + github + codebase-memory + filesystem |

Backup config files con suffix `.bak.pre-mcp.<timestamp>` prima di edit. No restart necessario per i profile specialist (sono passivi, config letto on-demand al subprocess invocation).

`hermes -p {backend,cso,frontend,orcharch} mcp list` → tutti enabled.

### 4. Propagation MCP a Kos hermes profile (default)

Rakki ha chiesto di estendere anche al profile default Kos personal (per domande non-work tipo gestione personale, query Sentry su progetti suoi). Stesso pattern di mc profile: sentry + github + filesystem + codebase-memory.

`systemctl --user restart hermes-gateway.service` (default profile è daemon attivo).

**Total Hermes setup**: 21 slot MCP attivi tra 5 profile.

### 5. Patch `_probe_single_server` per HERMES_MCP_CONNECT_TIMEOUT env var

Bug scoperto: `hermes -p <profile> mcp login sentry` ha timeout fisso 30s (40s con buffer). Sentry MCP usa OAuth 2.1 PKCE che richiede browser flow → user deve aprire URL, fare login Sentry, autorizzare, e il callback torna al listener Hermes su `127.0.0.1:<random_port>/callback`. Quando SSH tunnel + browser flow + Sentry auth richiedono >40s, timeout scatta e callback è perso.

Sintomo: i token OAuth `<provider>.json` (access_token + refresh_token) NON erano scritti su disco. Solo il `<provider>.client.json` (client metadata) restava lì.

Patch chirurgica in `~/.hermes/hermes-agent/hermes_cli/mcp_config.py:167-180`:
```python
def _probe_single_server(
    name: str, config: dict, connect_timeout: float = None
) -> List[Tuple[str, str]]:
    """...
    Override default 30s connect timeout via env var ``HERMES_MCP_CONNECT_TIMEOUT``
    (in seconds). Useful for OAuth flows that require SSH tunnel + browser
    interaction (e.g. ``HERMES_MCP_CONNECT_TIMEOUT=300 hermes mcp login sentry``).
    """
    import os as _os
    if connect_timeout is None:
        connect_timeout = float(_os.getenv("HERMES_MCP_CONNECT_TIMEOUT", "30"))
```

Default 30s fallback (no behavior change per user esistenti). Override esplicito via env var.

**Caveat upstream-safe**: la modifica è in `~/.hermes/hermes-agent/` che è il source vendored di Hermes. **Verrà persa al prossimo update Hermes via pip/installer**. Pattern fix da preparare come patch riapplicabile (TBD).

### 6. Sentry OAuth setup — 3 OAuth flow distinti

Hermes mantiene **session OAuth SEPARATA per profile** (anti-rotation conflict, stesso pattern visto per Codex/Anthropic OAuth). Sentry usato da 3 profile (mc + cso + frontend) → 3 login distinti:

```bash
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p mc mcp login sentry
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p cso mcp login sentry
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p frontend mcp login sentry
```

**Flow originariamente proposto** (SSH tunnel da Mac al mini-PC):
1. Terminale A (VSCode SSH al mini-PC): lancia `hermes mcp login sentry` → stampa URL OAuth + porta random `<PORT>`
2. Terminale B (locale Mac, NON SSH): `ssh -N -L <PORT>:127.0.0.1:<PORT> spesify-mini` per forward callback
3. Browser Mac: apri URL Sentry → autorizza → redirect a `127.0.0.1:<PORT>/callback` → tunnel SSH forwarda al mini-PC → listener Hermes riceve code

**Flow effettivamente usato** (Rakki ha browser sul mini-PC fisico): zero tunnel necessario, browser sul mini-PC chiama direttamente `127.0.0.1:<PORT>/callback`. Decisamente più semplice.

Risultato post 3 login:
```
~/.hermes/profiles/{mc,cso,frontend}/mcp-tokens/
├── sentry.client.json    (OAuth client metadata, 319B)
├── sentry.json           (access_token + refresh_token + expires_at, 305B, mode 600)
└── sentry.meta.json      (tool discovery cache, 812B)
```

Auto-refresh trasparente via `refresh_token` (TTL access_token 1h, refresh_token weeks).

### 7. Setup propagation Kos hermes profile + Claude Code

Anche Kos hermes profile riceve Sentry OAuth (separato, 4° OAuth flow distinto):
```bash
HERMES_MCP_CONNECT_TIMEOUT=300 hermes mcp login sentry
```

Claude Code Sentry OAuth: NON c'è `claude mcp login` (deprecato). Auth via slash command `/mcp` dentro sessione interactive `claude` OR auto al primo uso di un tool `mcp__sentry__*`.

### 8. Memoria aggiornata

`reference_community_claude_resources.md` esteso con:
- Tabella per-profile Hermes con MCP propagati (5 profile, 21 slot)
- Pattern OAuth setup Sentry (decisioni timeout, SSH tunnel vs browser fisico mini-PC, file persistence layout `mcp-tokens/`)
- Nota su patch HERMES_MCP_CONNECT_TIMEOUT (env var override)

## Configuration Changes

### Hermes config.yaml per 5 profile

Aggiunto `mcp_servers:` block prima di `toolsets:` in:
- `~/.hermes/config.yaml` (default Kos profile)
- `~/.hermes/profiles/mc/config.yaml`
- `~/.hermes/profiles/backend/config.yaml`
- `~/.hermes/profiles/cso/config.yaml`
- `~/.hermes/profiles/frontend/config.yaml`
- `~/.hermes/profiles/orcharch/config.yaml`

Backup files: `*.bak.pre-mcp.<timestamp>` per ognuno.

### Hermes patch source code

- `~/.hermes/hermes-agent/hermes_cli/mcp_config.py:167-180` — env var `HERMES_MCP_CONNECT_TIMEOUT` override per `_probe_single_server` (default 30s fallback).

### Hermes auth pool

4 nuove OAuth credentials registrate (1 per profile):
- `~/.hermes/mcp-tokens/sentry.{client.json,json,meta.json}` (default Kos)
- `~/.hermes/profiles/{mc,cso,frontend}/mcp-tokens/sentry.{client.json,json,meta.json}`

Tutti i `sentry.json` mode 600. Auto-refresh trasparente.

### Claude Code

2 nuovi MCP in `~/.claude.json`:
- `chrome-devtools` (stdio npx, isolated+headless)
- `sentry` (HTTP, OAuth-pending — auth tramite slash `/mcp` o auto al primo tool use)

### Filesystem extra

`npx playwright install firefox` (~100MB in `~/.cache/ms-playwright/firefox-1522/`) — installato durante sessione cliente parallela per Excalidraw PNG export, ma riusabile per qualsiasi headless rendering futuro.

## Key Discoveries

- **Hermes OAuth session è separata per profile by design** (anti-rotation conflict pattern). Implicazione: ogni nuovo profile che usa lo stesso MCP server OAuth (es. Sentry) richiede login OAuth distinto. Nessun sharing di token cross-profile. Verifica esplicita in `~/.hermes/hermes-agent/agent/credential_sources.py` (commenti riferiscono `refresh token rotation conflicts where one app's refresh invalidates the other's session`).
- **CLI `hermes mcp add` bug con args che iniziano per `-`**: argparse interpreta `-y` come flag. Workaround: edit YAML diretto. Future fix: usare `--args=-y` con `=` o `--` separator nel CLI Hermes.
- **Timeout default 30s `_probe_single_server` troppo corto per OAuth interactive**: pattern usato in 2 code path (mcp test + mcp login). Patch env var-aware `HERMES_MCP_CONNECT_TIMEOUT` retain backward compatibility + sblocca OAuth flow lunghi. Da preparare come PR upstream o re-patch automatico post update.
- **Mini-PC fisico bypass SSH tunnel**: quando Rakki ha accesso fisico al mini-PC con monitor + tastiera + browser (Firefox installato per Playwright), il flow OAuth è massimamente semplificato — browser sul mini-PC chiama direttamente `127.0.0.1:<PORT>/callback`. SSH tunnel è solo workaround per scenario completamente headless.
- **Obsidian MCP NON propagabile su Hermes mini-PC** finché l'app Obsidian gira solo sul Mac. La REST API `127.0.0.1:27124` è local-only del processo Obsidian. Mock alternative: filesystem MCP (basta per Write/Read sui file vault) — sufficiente per Capture Protocol e ops vault. Re-evaluation se mai Rakki installa Obsidian anche sul mini-PC (improbabile).
- **Sentry MCP project-per-cliente** è pattern raccomandato (tag-based segmentation per agent/env/phase) — NO project-per-agent (alert fatigue + quota frammentata). Best practice per agentic systems con <10 agent.
- **Patch source code upstream-safe è anti-pattern**: ogni update Hermes via pip/installer perde la modifica. Preparare patch file riapplicabile + check post-update OR contribute upstream PR. Per ora: documentato in memoria + nota in DOSSIER hermes per re-application.
- **3 OAuth flow per Sentry stesso provider** è correct by design (anti-rotation). Tempo totale ~10-15 min con browser fisico mini-PC (5 min per flow). Con SSH tunnel sarebbero ~20-30 min (overhead tunnel per ogni porta random).

## Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `hermes mcp add github --command npx --args -y @mcp/server-github` → `error: unrecognized arguments: -y @...` | argparse interpreta `-y` come flag invece che come arg di `--args` (che ha nargs `[ARGS ...]`) | Edit YAML diretto in `mcp_servers:` section (skip CLI per args complessi con prefisso `-`) |
| `MCP call timed out after 40.0s (configured timeout: 40.0s)` su `hermes mcp login sentry` | Default `connect_timeout=30` in `_probe_single_server` + 10s buffer = totale 40s, troppo corto per OAuth interactive con SSH tunnel + browser auth | Patch `~/.hermes/hermes-agent/hermes_cli/mcp_config.py` con env var `HERMES_MCP_CONNECT_TIMEOUT` override (default 30s, override 300s per OAuth) |
| `sentry.json non trovato` post-login apparente success | OAuth callback ricevuto, ma listener Hermes già scaduto (40s) → code perso → token exchange mai eseguito | Re-launch login con timeout esteso 300s |
| `npx playwright install firefox` necessario per `excalidraw-brute-export-cli` | Tool richiede browser headless | Install one-time ~100MB, riusabile per altri Playwright use case |

## Final State

- **Hermes**: 5 profile con MCP propagati (21 slot totali). Sentry OAuth attivo su 4 profile (mc + cso + frontend + default Kos). Patch HERMES_MCP_CONNECT_TIMEOUT env var attiva.
- **Claude Code**: 16 MCP (14 esistenti + chrome-devtools + sentry). Sentry pending OAuth al primo uso interactive.
- **Memoria**: `reference_community_claude_resources.md` aggiornata con setup MCP per-profile + pattern OAuth Sentry + nota patch timeout.
- **File OAuth token**: persistiti in `~/.hermes/{mcp-tokens,profiles/<name>/mcp-tokens}/sentry.json` (mode 600, auto-refresh trasparente).
- **Setup riusabile**: pattern `mcp_servers` YAML edit + restart gateway è documentato. Future cliente può ereditare pattern.

## Open Questions

- **Patch HERMES_MCP_CONNECT_TIMEOUT upstream contribution**: vale la pena fare PR a Nous Research repo o preparare patch riapplicabile post-update locale? Volume use case OAuth interactive cresce → contribution upstream è ROI alto.
- **Z.AI MCP direct** (vs aggregator OpenRouter): provider chain attuale ha `zai-coding` user-defined provider, ma c'è anche MCP server Z.AI? Da indagare se vale la pena per use case specifici.
- **Obsidian MCP via SSH tunnel reverse**: se Rakki vuole davvero, si potrebbe fare reverse tunnel dal Mac (dove gira Obsidian) al mini-PC per esporre `127.0.0.1:27124`. Complessità setup + flakiness sync → probabilmente non vale.
- **Sentry MCP project structure per nuovo cliente**: 1 project tag-based o multi-project? Pattern raccomandato 1 project (`<client>-multi-agent`) con tag `agent={1..N}` + `phase` + `env`. Da implementare quando l'app cliente sarà instrumentata.
- **Auto-refresh OAuth Codex/Gemini/Sentry**: token expiry tipico 1h access, weeks refresh. Hermes gestisce refresh trasparente ma da monitorare al primo expiry naturale di Sentry (4 profile = 4 refresh independents). Setup alert se refresh fail.
- **Sentry monitoring weekly cron per nuovi clienti**: pattern struttura pendente (script + cron disabled). Attivazione post-deploy quando app cliente sarà instrumentata. Documentato in memoria per riferimento futuro.
