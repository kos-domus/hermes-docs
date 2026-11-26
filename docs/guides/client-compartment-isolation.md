---
title: "Client Compartment Isolation for a Single-User Agent Fleet"
slug: "client-compartment-isolation"
category: "guides"
tags:
  - security
  - isolation
  - samba
  - mcp
  - least-privilege
  - file-permissions
  - fleet
  - profiles
  - tailscale
sources:
  - "sessions/2026-11-25-separazione-compartimenti-samba-apparmor.md"
last_updated: "2026-11-26"
version: 1
hermes_version_min: "0.23.0"
---

# Client Compartment Isolation for a Single-User Agent Fleet

When every Hermes profile in a fleet (chief of staff, master control, specialists, family bots)
runs as the **same Unix user**, that user's readable paths are the effective security boundary for
all client data. This guide documents a field-tested compartment design where:

- each client gets a dedicated Unix user (`cl-<slug>`) that owns their files,
- the agent user and every Hermes profile lose all read access to those files,
- humans exchange files with each compartment over a hardened per-client Samba share,
- the agent fleet keeps working with the files it still legitimately needs.

Reference deployment: Ubuntu 24.04 mini PC, all agents on one user, clients reached from macOS
Finder and iOS Files through Tailscale MagicDNS.

## Compartment design

| Asset | Owner | Access |
|---|---|---|
| Client files | `cl-<slug>` (no interactive login) | Samba share only |
| Exchange folder | `cl-<slug>` | Samba in/out, size-capped loop volume |
| Agent workspaces, skills, memories | agent user | Unchanged |

One Unix user per client, **no groups and no ACLs** — a single simple invariant to audit instead
of a matrix of group memberships. The Samba side uses one dedicated system identity (Samba-only,
no shell login) that maps every share to its client user.

## Samba hardening (the "B-bis" pattern)

One share per client, defined in an included file so the main `smb.conf` stays generic:

```ini
[cl-<slug>]
   path = /srv/compartments/<slug>/exchange
   force user = cl-<slug>
   valid users = <exchange-identity>
   hosts allow = <client-network> EXCEPT <server-own-ip>
```

Global settings that close the default openings:

- `map to guest = Never` — no guest fallback on bad credentials.
- `restrict anonymous = 2` — no anonymous share enumeration.
- No usershares.
- **`hosts allow` with `EXCEPT <server's own IP>`**: without the exclusion, any local process
  could connect to the share from the machine itself. The `EXCEPT` keeps the compartment open to
  remote humans only — local processes (the agent user included) cannot reach it.

The exchange folder lives on a dedicated loop-mounted volume with a hard size cap mounted
`nodev,nosuid,noexec`, so a runaway upload cannot fill the root filesystem or smuggle executables.

## Transport

Remote access rides Tailscale: clients connect via the server's MagicDNS name, which provides an
encrypted, authenticated channel (WireGuard; observed session cipher AES-128-GCM with GMAC
integrity). The agent user and raw-LAN clients are additionally refused at the Samba layer, so
both network position and file ownership must align for access.

## Agent-side narrowing checklist

Removing client data from the agents is config surgery across profiles — work through every item
or the compartments leak:

1. **MCP filesystem scope** — remove client directories (and any other unneeded path) from
   `mcp_servers.filesystem.args` of every profile that lists them (7 profiles in the reference
   fleet). Keep a config backup before each edit.
2. **Cron jobs** — pause any scheduled job that still reads client code (3 in the reference fleet,
   including daily digest pulls).
3. **Git push access** — retire old client-log repos with
   `git remote set-url --push origin no-push` so an agent cannot resurrect the data flow by
   pushing.
4. **`git pull` in routines** — remove client-log pulls from daily/digest/wrap-up flows.
5. **World-readable scratch** — privatize files the agent user left in `/tmp`, `/var/tmp`,
   `/dev/shm` (reference: 3,484 files → 0 readable by others).
6. **Indexes** — drop client projects from the codebase-memory index so agents cannot search their
   way back in.
7. **Memory and skills** — update memory cards and skills that encode the old routing ("client
   logs live at …"), or the next regeneration re-adds the stale rule. See
   [Profile Memory Hygiene and Approval Boundaries](../concepts/profile-memory-hygiene.md).

## Migration discipline (no destruction day)

Moving a client's data into its compartment is the dangerous step. Rules that survived a red-team
review:

- **Freeze, do not delete.** Originals move into a root-owned frozen directory via `mv` on the
  same filesystem (a move, not a copy), with a **sha256 manifest** recorded at freeze time
  (`diff -r` is not a verification).
- **Destruction is a separate, scheduled event.** Shredding, history rewrites, and remote-repo
  wipes happen on one known day, only after the new compartment is verified, a good backup
  exists, and a restore has been tested.
- **`rsync -a` carries permissions** — it copies source modes (e.g. group-writable 0775) onto the
  destination home; fix modes afterwards or pass an explicit `--chmod`.
- **Git history outlives the move** — a repo moved into the compartment keeps its full history in
  `.git`; include it in the same destruction day.
- **Never stage privileged sources in agent-writable directories** — the agent user could swap
  them between review and use.
- **`tar | age` needs `pipefail`** — without it, a failed tar quietly produces a "valid" encrypted
  archive of nothing.

## Unix pitfalls observed during the migration

- `useradd --comment` rejects `:` (the `/etc/passwd` field separator). Use a marker such as
  `cliente-<slug>` in the GECOS comment.
- `sudo cmd /root/*` fails with "No such file" because **the invoking user's shell expands the
  glob** before sudo runs (and the user cannot read `/root`). Use `sudo sh -c 'cmd /root/*'`.

## Verification

Test the compartment from both sides before declaring it done:

- **Positive**: Finder (Mac) and Files (iPhone) reach the share by its MagicDNS name and
  round-trip a test file in both directions.
- **Negative**: the agent user cannot read the compartment; a LAN client without credentials is
  refused.
- **Ownership**: no file inside the compartment is owned by the agent user or by the Samba
  identity.

## Related docs

- [Samba Shares Denied by apparmor-profiles Package (Ubuntu)](../troubleshooting/samba-apparmor-denials.md)
- [Build a Hardened Read-Only Agent (Isolated MCP Pattern)](hardened-read-only-agent.md)
- [OAuth Credential Separation in Hermes](../concepts/oauth-credential-separation.md)
