---
title: "Compartimenti per cliente: share Samba B-bis, guasto AppArmor, agenti senza percorsi clienti, skill e memorie ripulite"
date: "2026-11-25"
author: "kos-domus"
status: "ready"
tags: ["security", "permissions", "mcp", "cron", "memory", "multi-agent", "troubleshooting", "tailscale", "configuration"]
session_type: "hermes"
client: ""
openclaw_version: ""
environment:
  os: "Ubuntu 24.04 (mini PC)"
  ide: "VS Code + Claude Code 2.1.330"
  model: "claude-opus-5-5"
---

## Objective

Completare la separazione «un utente unix per cliente» (decisa il 21/11): scambio file comodo da Mac e iPhone verso il compartimento di ogni cliente, nessun dato di cliente leggibile dall'utente degli agenti (`kos`) né dagli agenti Hermes, migrazione dei clienti attivi e archivio cifrato degli altri. In più: riparare l'accesso SMB dall'iPhone e una serie di lavori di manutenzione della flotta (memoria del CSO, skill di MC, comandi senza LLM per Kai).

## Context

- Tutti gli agenti Hermes (Kos, MC, specialisti, Kai, Posta…) girano come lo stesso utente unix `kos`; le cartelle dei clienti stavano sotto `kos` ed erano nei server MCP filesystem degli agenti.
- Un primo compartimento cliente esisteva già dal 21/11; passare file richiedeva `sudo find/install/scp` da un utente amministrativo.
- Processo decisionale: specialisti (CSO, orchestration architect, backend, privacy) in parallelo → piano → red team GPT (abbonamento, effort high) → revisione del co-CEO → decisione di Rakki.

## Steps Taken

### 1. Guasto SMB dall'iPhone («unexpected error»)
- `smbclient` locale: login riuscito ma `tree connect failed: NT_STATUS_ACCESS_DENIED`.
- `journalctl -k`: denials AppArmor di smbd (exec della shell del preexec) e di rpcd (socket RPC, exec del demone).
- Causa: il pacchetto `apparmor-profiles` (installato il 18/11 per il profilo `bwrap-userns-restrict` della sandbox di Codex) contiene profili **sperimentali** per Samba, in enforce, scritti per i percorsi Debian (`/usr/lib/samba`) mentre Ubuntu usa `/usr/libexec/samba`. Bloccavano il `root preexec` della share e l'enumerazione delle share via RPC (quella che fa iOS, non `smbclient` diretto).
**Result**: disattivati i 6 profili Samba (link nella cartella `disable` di AppArmor, `apparmor_parser -R`, restart di smbd) (Samba torna unconfined come prima del 18/11; il pacchetto resta per bwrap). iPhone ok. Probabile effetto collaterale anche su Time Machine dal 18/11.

### 2. Piano di separazione e revisioni
- Co-CEO: clienti prima, agenti dopo; una share per lo scambio; trascrittore per cliente; «vetrina» a spinta per MC.
- CSO: variante **B-bis** (una sola identità Samba, una share per cliente con `force user = cl-<slug>`, niente gruppi/ACL), `EXCEPT` dell'IP del mini PC negli `hosts allow` (prima un processo locale poteva collegarsi), veto sulla bozza di uno script root `cl-nuovo` (scriveva nella home di un utente esistente seguendo link simbolici) e sulla chiave degli archivi letta da un file dell'utente degli agenti.
- GPT round 1: REVISE, 23 red flag (tra cui: `rsync -a` che riporta i permessi 0775 della sorgente sulla home di destinazione; storia git che conserva i dati spostati; sorgenti preparate in una cartella scrivibile dagli agenti prima dell'installazione; `tar | age` senza pipefail).
- Co-CEO: «procedere con modifiche»; **oggi niente distruzioni**: originali congelati in una cartella di root, shred/`restic rewrite`/cancellazione repo remoti in un unico giorno con tutte le prove.
**Result**: piano v3 con staging di root e confronto sha256, congelamento con `mv` sullo stesso filesystem, manifest sha256 al posto di `diff -r`.

### 3. Esecuzione (parte fatta)
- `kos`: file in `/tmp`, `/var/tmp`, `/dev/shm` resi privati (3.484 → 0 leggibili da altri); push del vecchio repo dei log clienti bloccato (`git remote set-url --push origin no-push`); progetti dei clienti tolti dall'indice codebase-memory.
- Hermes: percorsi dei clienti (e altre cartelle non necessarie) tolti da `mcp_servers.filesystem.args` di 7 profili; 3 cron di MC che leggevano codice clienti in pausa; Daily/Digest/Wrap senza `git pull` dei log clienti; skill e SOUL aggiornati; proposta di scheda di memoria che sostituisce la regola sull'instradamento dei log (va pubblicata, altrimenti il pacchetto della memoria rimette la riga vecchia nel SOUL).
- Root (Rakki): backup esteso alle home dei compartimenti e alle cartelle di scambio (memo audio esclusi); volume loop dedicato da 10 GB per lo scambio; identità di sistema dedicata, solo Samba e senza login; share `[cl-<slug>]` in un file incluso; globali senza ospiti (`map to guest = Never`, `restrict anonymous = 2`, usershare spenti).
**Result**: compartimento del cliente A raggiungibile da Finder e File su iPhone via il nome MagicDNS di Tailscale, sessione cifrata AES-128-GCM / firmata GMAC; `kos` e la LAN negati; nessun file di proprietà dell'identità Samba; prova nei due sensi (in/out) riuscita.

### 4. Altri lavori della sessione
- Memoria del profilo CSO: era il clone della memoria di MC incollato due volte (29k su 2.2k); ridotta a 7 voci, fatti spostati in skill/scheda, `write_approval: true`, richiamo 6/6; avviso giornaliero deterministico per le scritture in attesa di approvazione.
- Skill `mc-daily-ops` di MC: da 99k a 22k caratteri (oltre i 100k l'agente ne vedeva solo un'anteprima), riferimenti per workflow; prompt dei cron corretti (niente `python3 -c` in cron, procedura Drive della skill).
- Kai: plugin senza LLM per documenti d'identità (`/ci`, `/tes`, `/pp`, `/pat`): invio fronte/retro e stampa su A4 a grandezza reale; `/ts` è riservato da Hermes (alias di `/timestamps`).
- Claude Code di `kos` rotto dal 22/11: l'aggiornamento aveva lasciato lo stub di 500 byte senza binario nativo; riparato con `node install.cjs`.

## Configuration Changes
- AppArmor: disattivati i profili Samba del pacchetto `apparmor-profiles`.
- Samba: globali più restrittivi, share per cliente in un file incluso, esclusione dell'IP del server stesso negli `hosts allow`.
- Volume loop dedicato con tetto di spazio per lo scambio (`nodev,nosuid,noexec`).
- Backup notturno esteso ai compartimenti.
- Config Hermes di 7 profili: percorsi clienti tolti (con copie di backup).
- Esclusioni del backup: cache del browser di uno scraper (causa di un exit 3 notturno).

## Key Discoveries
- `apparmor-profiles` su Ubuntu non è innocuo: porta in enforce profili per servizi che prima giravano unconfined, con percorsi sbagliati. Sintomo: `NT_STATUS_ACCESS_DENIED` solo per alcuni client (iOS enumera le share via RPC).
- macOS/iOS tengono una sessione SMB per nome di server: per credenziali diverse sullo stesso host conviene un nome diverso (IP per una share, MagicDNS per un'altra).
- `useradd --comment` rifiuta i due punti (sono il separatore di `/etc/passwd`).
- `sudo cmd /root/*` da un utente senza accesso a `/root`: l'asterisco lo espande la shell dell'utente → «No such file»; usare `sudo sh -c '…/*'`.
- Un auto-mode classifier blocca giustamente l'approvazione programmatica delle scritture di memoria in attesa: l'approvazione resta umana.
- Profilo dentro un blocco generato (pacchetto della memoria): le modifiche a mano vengono sovrascritte; si cambia la scheda sorgente.

## Errors & Solutions
| Error | Cause | Solution |
|-------|-------|----------|
| iOS «unexpected error» / `NT_STATUS_ACCESS_DENIED` | profili AppArmor sperimentali di Samba in enforce | disattivare i profili Samba di `apparmor-profiles` |
| `useradd: invalid comment` | `:` nel GECOS | commento senza due punti; marcatore `cliente-<slug>` |
| `claude: native binary not installed` | postinstall saltato all'aggiornamento | `node install.cjs` nel pacchetto |
| test di richiamo falliti | gateway riavviato durante le domande | ripetere dopo il riavvio |

## Final State
Compartimento del cliente A operativo con scambio file da Mac e iPhone; agenti senza percorsi clienti; backup esteso. Prossimo: migrazione del cliente B (repo intero nel suo compartimento, originali congelati), archivi cifrati per classe di conservazione, giorno unico della distruzione il 2/12 dopo decifratura dal Mac, backup buono e prova di ripristino.

## Open Questions
- Script `cl-nuovo` da riscrivere secondo i requisiti del CSO (solo `runuser` nella home, `--prova`, `testparm` prima del reload).
- Vetrina per MC con UID pubblicatore distinto e stato strutturato approvato.
- Egress del Claude del compartimento (nftables per uid + allowlist).
- Sandbox systemd di smbd prima di un eventuale profilo AppArmor adatto a Ubuntu.
- La skill `save-session` va aggiornata: i log dei clienti ora nascono nel compartimento del cliente, il vecchio repo dei log è ritirato.
