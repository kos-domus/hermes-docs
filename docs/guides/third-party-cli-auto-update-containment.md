---
title: "Containing Third-Party CLI Auto-Update Behavior"
slug: "third-party-cli-auto-update-containment"
category: "guides"
tags:
  - security
  - third-party
  - supply-chain
  - configuration
  - systemd
  - gateway
sources:
  - "sessions/2026-11-10-rotazione-chiavi-rete-e-memoria-fetta-1.md"
last_updated: "2026-11-11"
version: 1
hermes_version_min: "0.23.0"
---

# Containing Third-Party CLI Auto-Update Behavior

Some third-party CLIs used by Hermes agents ship an **auto-update feature** that downloads the next
minor version into a private directory (for example `~/.firecrawl/versions/`) and executes it in
place of the installed binary. If your fleet discipline relies on an install registry, a waiting
period before adopting new versions, or an admin-controlled rollout, a self-updating CLI silently
bypasses all three: the code that runs tomorrow is not the code you reviewed today.

This guide documents the containment pattern field-tested with `firecrawl-cli` 1.25.3 → 1.29.0,
where the new release introduced exactly such an auto-updater.

## Before upgrading: review what changed

Do not upgrade a third-party CLI on version number alone. Before installing:

1. **Check for new maintainer or packaging metadata** — a maintainer change is a supply-chain signal.
2. **Read the release notes / diff for auto-update or self-download behavior** — look for private
   version directories, background download tasks, or postinstall activity.
3. **Scan the package** (e.g. `trivy`, registry diff) and confirm there are **no install scripts**
   (`--ignore-scripts` must be a safe install mode).

If the review passes but the new version *has* an auto-updater, upgrade **only together with the
containment steps below** — an auto-updater left enabled makes the review meaningless.

## Disable the updater in every place it reads

Auto-update is typically controlled by more than one knob, and a single flag is often not enough.
Disable it redundantly:

1. **Config file** — write the tool's own disable switch, e.g.
   `~/.firecrawl/auto-update.json` containing `{"disabled": true}`.
2. **Environment variables in the interactive shell profile** — e.g.
   `FIRECRAWL_NO_UPDATE_CHECK=1` and `FIRECRAWL_NO_AUTO_UPDATE=1`, so ad-hoc agent shells do not
   trigger update checks either.
3. **Environment variables in every service that runs the tool** — a systemd **drop-in** on the
   gateway (`hermes-gateway.service.d/<tool>.conf`) with `Environment=` lines, since drop-ins
   survive gateway updates while unit-file edits do not.
4. **Install with `--ignore-scripts`** so no postinstall hook can stage an updater.
5. **Verify the version cache directory is absent** after install (e.g. `~/.firecrawl/versions`).
   If it exists, something already self-updated — investigate before proceeding.

## Expect the permission classifier to push back

Editing shell profiles and service drop-ins from inside an agent session can be blocked by the
permission classifier as **"unauthorized persistence"** — that is the classifier doing its job.
The correct path is explicit human authorization for those specific startup-file edits, not a
workaround. Treat any agent proposing to edit its own startup files without authorization as a
signal to review, not to bypass.

## Keep watching after containment

- Add a **periodic check** (e.g. weekly) that the version cache directory has not reappeared —
  a reconfiguration from the vendor app or a new flag rename can silently re-enable updates.
- Record the upgrade in your third-party install **registry** with the conditions applied
  (auto-update disabled, install mode, verification steps) so the next reviewer knows the
  containment is deliberate.

## Why this matters for agent fleets

Agents execute whatever binary is on the path. A CLI that can replace itself between runs converts
every reviewed dependency into an unreviewed one, and does it outside the audit trail your
scheduler and registry provide. Disabling self-update keeps the dependency graph static between
deliberate, reviewed upgrades.

## Related docs

- [Safe Gateway Update Procedure](gateway-update-procedure.md) — drop-ins survive updates; unit
  files do not.
- [Secrets Vault Integration](secrets-vault-integration.md) — rendering secrets into service
  environments via drop-ins.
- [Cron Script Errors](../troubleshooting/cron-script-errors.md)
