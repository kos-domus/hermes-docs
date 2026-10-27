---
title: Safe Gateway Update Procedure
slug: gateway-update-procedure
category: guides
tags:
- update
- gateway
- systemd
- whatsapp-bridge
- config-migration
- telegram
- multiplex
sources:
- sessions/2026-10-26-posta-agent-quick-commands-codex-entitlement.md
last_updated: '2026-10-27'
version: 1
hermes_version_min: 0.22.0
---
# Safe Gateway Update Procedure

A field-tested sequence for updating a long-running Hermes gateway that hosts multiple messaging bridges (Telegram bots, WhatsApp) and several profiles. Verified on the v0.21.6 → v0.22.5 update with 9 profiles under `gateway.multiplex_profiles: true`, including a config schema migration from v50 to v52.

The core idea: an in-place update that restarts the gateway itself can race the WhatsApp bridge port and rewrite your systemd unit. Do the update in controlled stages instead.

## Procedure

### 1. Stop the gateway before updating

```bash
systemctl --user stop hermes-gateway.service
```

Stopping first prevents the running process from holding the WhatsApp bridge port and state while files are replaced underneath it.

### 2. Run the updater without a gateway restart

```bash
hermes update --yes --backup --no-gateway-restart
```

- `--backup` keeps a rollback point of the previous installation.
- `--no-gateway-restart` stops the updater from starting the service itself, which would race the bridge shutdown.

### 3. Wait for the WhatsApp bridge port to be released

After a gateway stop, the WhatsApp bridge can hold its port for a while. Wait for the port to be free before starting again — observed to take around 90 seconds. Starting too early produces a bridge bind failure.

### 4. Start and verify the bridges

```bash
systemctl --user start hermes-gateway.service
journalctl --user -u hermes-gateway.service --since '5 min ago' -f
```

Verify both of these lines appear:

```text
Connected to Telegram
Bridge started
```

If either is missing, stop and re-check step 3 — a port race usually shows up here.

## What the updater changes (and what survives)

- **Config schema migration runs automatically across profiles.** In the v0.21.6 → v0.22.5 update, config schema v50 was migrated to v52 across all 9 profiles on the host without manual edits.
- **The updater rewrites the `hermes-gateway.service` systemd unit.** Any local customizations made directly in the unit file are lost on update.
- **Drop-in overrides survive.** A drop-in directory such as `hermes-gateway.service.d/` (for example, one that renders secrets into the service environment) is not touched by the updater and keeps being applied.

This is the reason to put host-specific service customizations in a drop-in (`systemctl --user edit hermes-gateway.service`) rather than in the unit file itself: drop-ins survive updates, unit-file edits do not.

## Harmless post-update warnings

```text
unknown toolset 'messaging'
unknown toolset 'moa'
```

If these appear after an update, check whether the named toolsets were already removed in the release you were running before. When the removal happened in an earlier version, the warnings are harmless residue from stale config references, not a new problem introduced by the update.

## Rollback

If the new version misbehaves, the updater's `--backup` flag left a snapshot of the previous installation. Stop the gateway, restore the backup produced by the update run, and restart — then re-verify both bridge lines from step 4.

## Related docs

- [Quick Commands Reference](../reference/quick-commands.md)
- [Provider and Gateway Errors](../troubleshooting/provider-and-gateway-errors.md)
