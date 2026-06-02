---
title: "Cron Script Execution Reference"
slug: "cron-script-execution"
category: "reference"
tags: ["cron", "scripts", "profiles", "scheduling", "security", "configuration"]
sources:
  - "sessions/2026-06-01-cron-script-containment-fix.md"
last_updated: "2026-06-02"
version: 1
hermes_version_min: "0.14.0"
---

# Cron Script Execution Reference

Hermes cron jobs can run in two broad modes:

- prompt-based jobs, where Hermes sends a prompt to an agent profile;
- script-based jobs, where `no_agent: true` and `script: "..."` execute a shell script without an LLM turn.

This page documents the script-path behavior observed for script-based cron jobs.

## Path resolution

For a profile-scoped cron job, Hermes resolves a relative `script` value under the profile's local `scripts/` directory:

```text
~/.hermes/profiles/<profile>/scripts/<script>
```

It does **not** resolve relative cron scripts from:

- `~/.hermes/scripts/`;
- the job `workdir`;
- the current shell directory;
- a sibling global script registry.

Example:

```json
{
  "id": "example-maintenance",
  "no_agent": true,
  "script": "maintenance/run.sh"
}
```

Hermes expects the executable file at:

```text
~/.hermes/profiles/<profile>/scripts/maintenance/run.sh
```

## Containment rule

Hermes enforces script containment before executing the cron script. The resolved script path must remain inside the profile's `scripts/` directory.

A symlink from inside `scripts/` to a file outside that directory can be rejected with:

```text
Blocked: script path resolves outside the scripts directory
```

This is an anti-escape guard. It prevents a cron job from declaring a safe-looking profile-local script while actually resolving to an arbitrary path elsewhere on disk.

## External canonical scripts

If your operational source of truth lives outside the profile directory, keep the Hermes entrypoint as a real file inside containment and delegate from there.

Use a small wrapper script:

```bash
#!/usr/bin/env bash
set -euo pipefail

exec /home/<user>/job-desk/hermes/scripts/<script>.sh "$@"
```

Then reference the wrapper from the cron job:

```json
{
  "id": "example-maintenance",
  "no_agent": true,
  "script": "maintenance/run.sh"
}
```

The wrapper file itself is inside `~/.hermes/profiles/<profile>/scripts/`, so Hermes' containment check passes. The wrapper's `exec` preserves a single canonical script body instead of copying logic into every profile.

## Testing script-based cron jobs

To run a script job immediately:

```bash
hermes -p <profile> cron run <job-id>
hermes -p <profile> cron tick
```

`cron run` schedules or queues the job; `cron tick` processes due work immediately instead of waiting for the next systemd timer tick.

## Design notes

- Prefer short wrappers over duplicated script bodies.
- Keep wrapper names stable and profile-local.
- Make wrappers executable.
- Avoid symlink escapes; even if a symlink works in a shell, Hermes can still reject it during cron script resolution.
- For public documentation or shared configs, use placeholders such as `<profile>`, `<job-id>`, and `/home/<user>/...` instead of local account-specific paths.

## Related docs

- [Cron Script Wrapper Pattern](../guides/cron-script-wrapper-pattern.md)
- [Cron Script Errors](../troubleshooting/cron-script-errors.md)
- [Self-Improvement Agent Safety](../concepts/self-improvement-agent-safety.md)
