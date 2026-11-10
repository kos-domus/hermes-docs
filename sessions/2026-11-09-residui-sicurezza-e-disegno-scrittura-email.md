---
title: "Hermes: residui di sicurezza dopo la v0.23 e disegno di un agente email che scrive senza LLM"
date: "2026-11-09"
author: "kos-domus"
status: "processed"
tags: ["security", "permissions", "mcp", "multi-agent", "automation", "testing", "troubleshooting"]
session_type: "hermes"
client: ""
openclaw_version: ""
environment:
  os: "Ubuntu 24.04 (mini PC)"
  ide: "VS Code + Claude Code"
  model: "claude-opus-5-5"
---

## Objective

Chiudere i residui del controllo di sicurezza settimanale sul mini PC che ospita la flotta Hermes, spostare i job rimasti sul runtime v0.23 e progettare la fase di scrittura di un agente email (etichette e archivio automatici, cestino solo con conferma umana).

## Context

Gateway Hermes v0.23.0 multiplex con più profili. L'agente email leggeva già la casella in sola lettura, tramite un server MCP stdio dedicato. Il processo di decisione usato sui piani di sicurezza è: pareri di specialisti, revisione di un altro fornitore (red team + PM), disposizioni dell'host, co-CEO, decisione umana.

## Steps Taken

### 1. Pulizia dei residui

Aggiornati i pacchetti di sistema, rimosse le CLI npm globali non usate (spazio da 5,0 a 1,8 GB), attivato Ubuntu Pro, spento un servizio voce non più necessario e il relativo hostname del tunnel. Un riavvio ha chiuso il giro.

**Result**: rimane una vulnerabilità critica in una dipendenza annidata, da aggiornare a una data fissata. Il kernel precedente è stato tenuto come riserva, contro il suggerimento dello scanner.

### 2. Job selfimprove sul runtime v0.23

Un servizio cron usava ancora il vecchio venv pre-0.22, e caricava dipendenze vulnerabili. Spostato con un drop-in systemd sul lanciatore nuovo; il venv è stato rinominato, non cancellato, per poterlo ripristinare durante una settimana di osservazione.

### 3. Agente email: disegno della scrittura

Separati due percorsi:

- **Lettura**: agente LLM + MCP + scope `gmail.readonly`, invariati.
- **Scrittura**: motore deterministico, senza LLM, sotto un utente unix proprio e con credenziale OAuth propria.

Le regole leggono solo etichette e intestazioni ammesse. Guardie globali (protezioni, età minima da `internalDate`, mai `CATEGORY_UPDATES`) precedono ogni regola positiva; nel dubbio la mail resta in inbox.

**Result**: la prima tranche è tutta in sola lettura (censimento, regole, campione, modalità ombra). Il permesso di scrittura arriva solo dopo i gate.

### 4. Correzione del parser HTML del server di lettura

Una regex a costo cubico era applicata al corpo HTML, che è input ostile: 34 KB richiedevano 16,6 s. Sostituita con `html.parser` di stdlib, taglio dell'input prima di ogni trasformazione e timeout.

**Result**: 84 combinazioni avversarie fino a 25 MB, caso peggiore 2,04 s; lo stesso test sul codice vecchio fallisce, come controllo negativo.

### 5. Regole di smistamento provate con mutanti

Funzione pura `classifica(meta, cfg)` con esito a enum chiuso, verificata solo su metadati sintetici. Il test altera il sorgente in 17 punti (guardia tolta, soglia cambiata, confronto di dominio allentato) e pretende che ogni alterazione faccia fallire almeno un controllo.

**Result**: tutti i controlli superati, 17/17 mutanti rilevati.

## Configuration Changes

- Drop-in systemd per il job selfimprove verso il lanciatore v0.23.
- Registro dei componenti di terze parti esteso alle CLI aggiornate.
- Hostname del servizio voce tolto dal tunnel.

## Key Discoveries

- **Separare il potere di scrittura dal modello è più semplice che difenderlo.** Con un motore senza LLM, una mail ostile non può ordinare una scrittura: gran parte del protocollo di conferma del primo disegno (elicitation, card generate dal server) è caduta.
- **`gmail.modify` permette anche l'invio e la lettura.** Il confine utile è quale processo possiede il token, non lo scope.
- **La revisione di un altro fornitore ha trovato un errore nella garanzia, non nel codice.** Il sì su un bot Telegram era descritto come resistente alla compromissione del bot. Non lo è: il bot attesta da solo il consenso. Vanno dichiarate le garanzie vere e limitato il danno con i tetti.
- **Togliere una regola sudoers non revoca i processi già avviati.** Un cutover di isolamento deve fermare anche i server MCP vivi e rifare il grant OAuth quando il controllo esclusivo non è dimostrabile.
- **Un parametro di gate si fissa prima di raccogliere i campioni.** Zero errori su 150 dà un limite superiore unilaterale al 95% dell'1,98%, su 300 dello 0,99%. Vale solo se il campione non ha guidato modifiche alla versione provata.
- **Le restrizioni non devono costare come le estensioni.** Azzerare i gate per l'aggiunta di un dominio protetto scoraggerebbe la modifica più prudente.
- **Al riavvio, i servizi che leggono segreti da 1Password possono fallire perché il DNS non è ancora pronto.** Si riprendono da soli in pochi secondi, ma il sentinel manda un allarme per ciascuno. Le unità `systemd-run` lanciate per prova alimentano lo stesso canale.
- In un gruppo WhatsApp, Hermes autorizza per chat e non per persona: i comandi ammessi nel gruppo valgono per chiunque ne faccia parte.

## Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Falso positivo nella ricerca di file di firma | Lo schema `*signature*.py` prendeva librerie e `*firma*` anche «confirmation» | Schema ancorato ai separatori, provato su nomi veri e falsi |
| Piano B del parser inutile | Il taglio a 256 KB non copriva un input da 34 KB già patologico | Trasformazione lineare; lo ha segnalato il revisore |
| Verifica rossa senza alcuno sforamento | Il controllo aggregato trattava come fallimento una lista di esiti vuota | Contatore esplicito degli sforamenti |
| Revisore senza accesso ai file | Il sandbox di Codex non parte su quell'host | Piano passato inline; limite dichiarato nel log di revisione |

## Final State

Residui di sicurezza ridotti, runtime v0.23 esteso al job selfimprove, piano della fase di scrittura deciso con il proprietario della casella e prima tranche autorizzata. Parser e regole provati su dati sintetici.

## Open Questions

- Le soglie di copertura per scegliere fra motore e filtri nativi di Gmail sono state fissate senza dati: il censimento le rivedrà.
- Un modello locale per i casi dubbi è rinviato finché non esiste una coda misurabile.
