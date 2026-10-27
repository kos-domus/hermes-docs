---
title: Quick Commands Reference (exec, no LLM)
slug: quick-commands
category: reference
tags:
- quick-commands
- slash-commands
- configuration
- multiplex
- telegram
- whatsapp
- access-control
sources:
- sessions/2026-10-26-posta-agent-quick-commands-codex-entitlement.md
last_updated: '2026-10-27'
version: 1
hermes_version_min: 0.22.0
---
# Quick Commands Reference (exec, no LLM)

Quick commands are instant slash commands for chat users: they execute a local script directly, with no LLM call in the loop, and return the output to the chat. Verified on Hermes 0.22.5 with a multiplexed gateway (default profile plus secondary profiles on Telegram and WhatsApp).

Use them for shortcuts that must be fast, free, and deterministic — home automation toggles, status pings, presence updates.

## Configuration

A quick command is of type `exec`: it points at a script and runs it with a hard timeout (30 seconds observed). Keep the scripts in a stable location such as `~/.local/bin/`.

```yaml
quick_commands:
  - name: menu
    type: exec
    command: /home/<user>/.local/bin/menu.sh
    timeout: 30
```

Constraints:

- **No arguments.** Quick commands do not receive arguments from the chat message. If you need variants, define separate commands.
- **Names cannot contain `/`.** The internal `get_command` lookup discards names that contain a slash (it treats them as paths). `/hia/yt` is impossible; use `/hia_yt`.

## The multiplex gotcha: main profile only

With `gateway.multiplex_profiles: true`, the `quick_commands` block is read **only from the main profile config** (`~/.hermes/config.yaml`).

Defining quick commands in a secondary profile's config is silently ignored. The user-visible symptom:

```text
Unrecognized slash command /menu
```

even though the command is right there in the profile's config file.

Fix: move all `quick_commands` definitions into the main profile config.

### Access rules ARE per profile

The complementary half of the gotcha: who is allowed to run a command is controlled per profile, because permission follows the bot that receives the message. Configure access in the profile's root `whatsapp:` and `telegram:` blocks:

```yaml
telegram:
  allow_admin_from:
    - "<telegram-user-id>"
  user_allowed_commands:
    "<telegram-user-id>":
      - ha
      - menu
```

These fields are read by `gateway/slash_access.py` and bridged into the profile `extra` data at runtime.

### Testing rule

Simulating the access decision (for example by reproducing the `policy_from_extra` logic offline) is not sufficient: a simulation passes even when the gateway never loaded the command. Always verify end-to-end that the command exists in the running gateway — send the slash command from a real allowed account.

## YAML 1.1 boolean trap

Keys named `on` / `off` (and `yes` / `no` / `true` / `false`) are parsed as booleans by YAML 1.1. A quick command named `on`:

```yaml
quick_commands:
  - name: "on"   # quotes required
    type: exec
    command: /home/<user>/.local/bin/on.sh
```

must be quoted, or the name silently becomes a boolean and the command is unreachable.

## Related docs

- [Safe Gateway Update Procedure](../guides/gateway-update-procedure.md)
- [Build a Hardened Read-Only Agent](../guides/hardened-read-only-agent.md)
