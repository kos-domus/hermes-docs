---
title: "Samba Shares Denied by apparmor-profiles Package (Ubuntu)"
slug: "samba-apparmor-denials"
category: "troubleshooting"
tags:
  - samba
  - apparmor
  - ubuntu
  - smb
  - file-sharing
  - troubleshooting
  - kernel-log
sources:
  - "sessions/2026-11-25-separazione-compartimenti-samba-apparmor.md"
last_updated: "2026-11-26"
version: 1
hermes_version_min: "0.23.0"
---

# Samba Shares Denied by apparmor-profiles Package (Ubuntu)

Installing the `apparmor-profiles` package on Ubuntu 24.04 for one specific profile (for example
`bwrap-userns-restrict` for a sandbox) silently breaks Samba file sharing: the package also ships
**experimental Samba profiles in enforce mode** written for Debian paths, while Ubuntu places the
Samba binaries elsewhere. Samba goes from `unconfined` to partially blocked with no Samba
configuration change of your own.

## Symptoms

- iOS/macOS clients show a generic SMB failure ("unexpected error" when opening a share).
- `smbclient` from a shell **logs in successfully** but fails the share step:

  ```text
  tree connect failed: NT_STATUS_ACCESS_DENIED
  ```

- The failure appears days or weeks after a Samba setup that used to work — the trigger is the
  `apparmor-profiles` install date, not any Samba edit.
- Time Machine backups over SMB may have been silently failing since the same date.

## Diagnosis

Check the kernel log for AppArmor denials from the Samba daemons:

```bash
journalctl -k | grep -i apparmor
```

Observed denial classes:

- `smbd` denied **exec of the `root preexec` shell** of a share.
- `rpcd` denied socket and exec operations for RPC.

The path mismatch that makes the profiles fail on Ubuntu: they reference Debian's
`/usr/lib/samba`, while Ubuntu uses `/usr/libexec/samba`.

### Why some clients fail and others do not

iOS (and some macOS flows) **enumerate shares via RPC** before connecting. A plain
`smbclient //host/share` connects directly and skips the RPC step, so a manual test can pass the
login stage while iPhone access fails — the denial hits the enumeration path, not the mount.

## Fix

Disable the Samba profiles that came with `apparmor-profiles`. Samba returns to `unconfined` (the
state before the package arrived); the package itself can stay installed for the profile you
actually wanted.

1. Symlink each Samba profile into AppArmor's `disable` directory (as root).
2. Unload the running profiles with `apparmor_parser -R` for each.
3. Restart the daemon: `systemctl restart smbd`.

Verify from an affected client: share enumeration and connect both succeed again.

## Related client gotchas

- **macOS/iOS keep one SMB session per server name.** Different credentials on the same host do
  not coexist reliably; expose each identity under a different name (for example the raw IP for
  one share, a MagicDNS hostname for another) so clients treat them as different servers.
- Before writing a custom AppArmor profile for `smbd` on Ubuntu, consider a systemd sandbox
  instead — it does not depend on distro-specific binary paths.

## Related docs

- [Client Compartment Isolation for a Single-User Agent Fleet](../guides/client-compartment-isolation.md)
- [Cron Script Errors](cron-script-errors.md)
