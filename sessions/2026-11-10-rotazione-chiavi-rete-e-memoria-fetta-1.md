---
title: "Rete di casa, rotazione chiavi Gemini/Z.AI, profili su glm-5.3, firecrawl con auto-update spento, memoria fetta 1 e doppioni SpesaBot"
date: "2026-11-10"
author: "kos-domus"
status: "processed"
tags: ["security", "configuration", "troubleshooting", "memory", "multi-agent", "automation", "testing"]
session_type: "hermes"
client: ""
openclaw_version: ""
environment:
  os: "Ubuntu 24.04 (mini PC kos-domus)"
  ide: "VS Code + Claude Code"
  model: "claude-opus-5-5"
---

## Objective
Giornata di manutenzione a più fili, con Rakki che studiava: rimettere in sesto la rete di casa, completare la rotazione delle chiavi Gemini e Z.AI usate dagli agenti Hermes, ripulire le copie dei segreti, portare gli specialisti a glm-5.3, aggiornare firecrawl-cli senza aggirare le regole sulle terze parti, chiudere la fetta 1 del piano «memoria: un solo flusso di scrittura» e ripulire le offerte doppie di SpesaBot.

## Context
- Dalla sera prima il gateway Hermes vedeva una «tempesta» di errori di rete verso Telegram e la pipeline notturna di SpesaBot era degradata.
- La rotazione delle chiavi era a metà: Gemini aggiornata nei file ma gateway non riavviato, Z.AI ancora da fare. Motivo: un backup del 31/10 conteneva le chiavi in chiaro.
- Il piano della memoria era alla v3, con le decisioni di Rakki ancora aperte.

## Steps Taken

### 1. Rete: un Deco ripiegato sul collegamento Wi-Fi
Dopo il riavvio del router e la ricollegatura dei cavi del Deco del garage: cavo del mini PC a 1 Gbit e senza errori, ma router e Deco lontani rispondevano tutti con la stessa latenza (min ~10 ms, media ~170, picchi 500) e internet tra 0,2 e 5 s. I Deco vicini restavano sotto 1 ms.
**Result**: valori identici su apparecchi diversi = un solo collegamento in comune lento, cioè il Deco del garage agganciato via radio. Riportati tutti i Deco in Ethernet: LAN ≤1,5 ms, internet ~21 ms, pagine 0,07–0,6 s. La «tempesta Telegram» (13:52 del giorno prima → 05:50) e il guasto notturno di SpesaBot (1Password irraggiungibile → segreti non caricati) coincidevano con quella finestra.

### 2. Rotazione Gemini e Z.AI
- Gemini: riavvio del gateway, chiave nuova attiva nel processo (controllata confrontando un'impronta dell'ambiente del processo, mai il valore).
- Z.AI, primo tentativo: la chiave nuova rispondeva 200 all'API normale ma **429 «Insufficient balance»** sull'endpoint del Coding Plan (`api/coding/paas/v4`). La vecchia rispondeva 200. Gli specialisti senza fallback si sono fermati, Kai ripiegava su Grok.
- Causa: dal 16/10 Z.AI separa le chiavi dell'API normale da quelle del Coding Plan, che si creano nella pagina del Coding Plan.
- Z.AI, secondo tentativo: chiave del Coding Plan nella stessa voce di 1Password (i template puntano a `op://Tech/<id>/credential`, quindi nessun template da toccare), render dei `secrets.env`, aggiornamento manuale di due copie fisse che nessuno script rigenera (`profiles/family-staging/.env` e `profiles/hermes-selfimprove/secrets.env`), riavvio.
**Result**: CSO e Kai rispondono su GLM. Nei log di Kai: `provider=zai model=glm-5.3`, senza fallback. Chiavi vecchie revocate (Z.AI → 401, Gemini → 400).

### 3. Bonifica delle copie dei segreti
- Tolte le chiavi revocate dalle fotografie dei profili; cancellati i backup del giorno, il `.env` del backup del 31/10 e una shell snapshot di Codex che conteneva l'ambiente.
- Trovata in `profiles/frontend/home/` una copia del token 1Password «clienti» e dei segreti di MC. Il 16/09 un cron del frontend, girando con la HOME del profilo, non trovava i file e l'agente li aveva copiati lì per far funzionare uno script.
**Result**: copie cancellate. I valori non compaiono in sessioni, log o `state.db`, quindi nessuna rotazione del token.

### 4. Profili e servizi
- Specialisti Z.AI (cso, backend, frontend, orcharch, selfimprove) da glm-5.1 a **glm-5.3**; verificato il CSO su glm-5.3.
- `hermes-selfimprove-cron`: sembrava rotto (il file base punta al vecchio venv dismesso), ma un drop-in lo fa partire con il nuovo lanciatore: 193 giri riusciti. Lezione: leggere sempre `systemctl --user cat`, drop-in compresi.
- Luci: aggiunta la lampadina «taverna 1.4» a Home Assistant (config flow REST), rinominate entità e dispositivi, aggiornati gruppo, plugin `kai-luci` (`/t`, `/t4`), menu e istruzioni di Kai. Spento di nuovo l'auto-update del firmware Tapo, tornato acceso dopo la riconfigurazione dall'app. Una striscia LED aveva cambiato indirizzo: il reconfigure flow di HA andava in timeout, mentre il flow «user» con il nuovo host si chiude con `already_configured` e aggiorna l'IP da solo.

### 5. firecrawl-cli 1.25.3 → 1.29.0
Controllo prima dell'aggiornamento: maintainer nuovo e una funzione nuova di **auto-update** (scarica la minor successiva in `~/.firecrawl/versions/` e la esegue al posto di quella installata, aggirando registro delle terze parti e regola dei 3 giorni). Revisione CSO: maintainer legittimo, nessuno script di installazione, Trivy pulito → GO con condizioni.
**Result**: `~/.firecrawl/auto-update.json` con `{"disabled":true}`, `FIRECRAWL_NO_UPDATE_CHECK=1` e `FIRECRAWL_NO_AUTO_UPDATE=1` in profilo shell e drop-in del gateway, installazione con `--ignore-scripts`, `~/.firecrawl/versions` assente, due voci nuove nel registro. Le modifiche ai file di avvio le ha autorizzate Rakki: il classificatore dei permessi le blocca come «persistenza non autorizzata».

### 6. Memoria, fetta 1 (piano con esecuzione a grafo)
- Round 2 di GPT sul piano v4: REVISE (15 rilievi di sicurezza, 11 di piano, 6 alternative). Il piano diventa v5 in **due fette** (alternativa GPT ALT-01, coincidente con la scelta di Rakki «in due tempi»).
- Fetta 1: U1 (proposte pubblicabili da CLI e MCP), U2 (blocchi di contenuto per destinazione su ogni add/supersede, controllo dei consumatori senza fallback né ausiliari esterni, preflight dei pacchetti prima del digest), U5a (installazione da copia root-owned con manifest), U6, U9 (esportazione per ChatGPT).
- Script di verifica `p1.py` e `p2.py` scritti in pianificazione e validati in due direzioni: rossi sul codice attuale, verdi su un'implementazione di riferimento usa e getta tenuta fuori dal repository. Bocciati due volte dalla revisione GPT: start `--senza-revisione` deciso da Rakki, con 4 limiti dichiarati.
- Run: U1 passata al 2° tentativo, U2 al 1°, nessuna escalation, ~4,6 USD di esecutori. Revisione CSO G3: GO con condizioni, corrette dopo la run e riverificate:
  - consumatore senza `config.yaml` → ora blocca (prima lasciava passare);
  - caratteri invisibili tolti prima dei blocchi;
  - gitleaks solo da percorsi root-owned.
- Pacchetto di installazione pronto: artefatti con shebang riscritti, `MANIFEST.sha256`, gitleaks 8.21.2 verificato con i checksum ufficiali.

### 7. SpesaBot
- **Lidl**: ricerca dei link fallita per un timeout della homepage. Aggiunti 3 tentativi con attesa dei link veri e una memoria dei link della settimana. Scoperte: Lidl numera le settimane una indietro rispetto all'ISO, e la homepage elenca due settimane consecutive. Validità quindi basata sulla data di salvataggio e su al massimo due etichette `kw` consecutive. Rilancio: 22/22 pagine, 311 prodotti.
- **Offerte doppie**: ~19.500 righe attive in più. Causa: le date di ogni negozio vengono dalla «prima promo» dell'elenco, il cui ordine varia, quindi lo stesso volantino finisce in campagne diverse, mentre la pulizia del giro vale solo per la stessa campagna.
**Result**: con lo specialista backend, transazione unica sotto il lucchetto della pipeline, con controlli prima e dopo (rollback automatico se qualcosa non torna): 25.643 righe tolte e salvate in una tabella di backup, 5 campagne superate ritirate, 0 doppioni rimasti. Aggiunto un allarme al monitor (ogni 15 minuti). Correzione strutturale rimandata a quando ci sarà un database di test.

## Configuration Changes
- Hermes: chiavi Gemini e Z.AI ruotate (valori solo in 1Password e nei `secrets.env` renderizzati); 5 profili su glm-5.3; drop-in `hermes-gateway.service.d/firecrawl.conf`; Home Assistant e plugin `kai-luci` con la taverna 1.4.
- Terze parti: firecrawl-cli 1.29.0 con auto-update spento; registro aggiornato.
- Memoria: codice nuovo nel sorgente (non ancora installato); `memoria-index.timer` fermo fino all'installazione, perché eseguirebbe il sorgente modificato.
- SpesaBot: ricerca dei link Lidl con riprova e memoria; monitor con allarme dei doppioni; pulizia del DB con backup.

## Key Discoveries
- Latenze identiche su apparecchi diversi indicano un collegamento in comune: utile per riconoscere un Deco passato da cavo a radio.
- Z.AI: le chiavi del Coding Plan si creano in una pagina diversa da «API Keys». Prova prima del render: `coding/paas/v4/chat/completions` deve dare 200.
- Un agente con HOME del profilo può «aggiustare» uno script copiando segreti nella propria HOME. Va cercato periodicamente.
- Un CLI con auto-update aggira registro e regola dei 3 giorni: va spento in più punti.
- Un test di verifica va provato in entrambe le direzioni: rosso sul codice vecchio, verde su un riferimento corretto. Ha trovato tre errori nei miei test prima della run.
- La revisione GPT degli script di verifica non converge in 2 giri su test d'integrazione ampi: correggere i punti seri e far decidere a Rakki con i limiti dichiarati.
- Uno script di verifica storico che toglie le variabili `MEMORIA_*` può pubblicare sui `SOUL.md` veri: ogni test deve puntare `MEMORIA_PROFILI` a una sandbox.

## Errors & Solutions
| Error | Cause | Solution |
|-------|-------|----------|
| Internet a 1–5 s, router a 170 ms via cavo | Deco del garage passato al collegamento Wi-Fi | Tutti i Deco di nuovo in Ethernet |
| Z.AI 429 «Insufficient balance» con la chiave nuova | Chiave dell'API normale, non del Coding Plan | Chiave creata nella pagina del Coding Plan |
| Gateway: cron `hermes-docs` «fire ownership lost» | Due rilanci sovrapposti (il primo ucciso dal timeout della CLI) | Lavoro comunque completato e riconciliato; non rilanciare `hermes cron run` con un timeout breve |
| `rivedi-verifiche` NON adeguato ×2 | Test ampi, nuovi casi limite a ogni giro | Correzioni serie + `start --senza-revisione` deciso da Rakki |
| Memoria dei link Lidl scartata | Due settimane `kw` nella homepage, numerazione diversa dall'ISO | Validità su data di salvataggio + due etichette consecutive |
| `passwd`: authentication token manipulation error | Password attuale non accettata da `pam_unix` (il secondo prompt è di `pam_sss`) | `sudo passwd <utente>` |

## Final State
- Rete sana; chiavi ruotate e vecchie revocate; profili su glm-5.3; firecrawl aggiornato in sicurezza.
- Fetta 1 della memoria pronta all'installazione con istruzioni, manifest e gitleaks verificato.
- SpesaBot senza doppioni, con allarme attivo; Lidl tornato.
- Nessun commit nel repository di SpesaBot: contiene modifiche non committate di un'altra sessione.

## Open Questions
- Installazione U5a della memoria e pubblicazione delle 5 schede esportabili.
- Database di test per la correzione strutturale dei doppioni di SpesaBot (serve un comando da amministratore).
- Hermes 0.23.1 (regola dei 3 giorni) e OpenClaw CLI 11.2 in agenda.
- Controllo settimanale che segnali la comparsa di `~/.firecrawl/versions`.
- Una password incollata per errore in chat: cambiata subito; la riga va tolta dalla trascrizione da una sessione nuova.
