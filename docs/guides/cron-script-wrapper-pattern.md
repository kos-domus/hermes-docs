---
title: "Cron Script Wrapper Pattern"
slug: "cron-script-wrapper-pattern"
category: "guides"
tags: ["cron", "scripts", "wrappers", "profiles", "scheduling", "security"]
sources:
  - "sessions/2026-06-01-cron-script-containment-fix.md"
last_updated: "2026-06-02"
version: 1
hermes_version_min: "0.14.0"
---

# Cron Script Wrapper Pattern

Use this pattern when a Hermes script-based cron job must run a canonical script that lives outside the profile's `scripts/` directory.

The goal is to keep one source of truth for the operational script while satisfying Hermes' profile-local script containment check.

## When to use this

Use a wrapper when all of these are true:

1. The cron job is script-based (`no_agent: true`).
2. The job has a `script` field, not a prompt.
3. The real script is maintained in another repository or workspace directory.
4. You do not want to copy the full script into each profile.
5. A symlink from the profile `scripts/` directory is rejected or would be too fragile.

Do **not** use this pattern to bypass security review. The wrapper keeps Hermes' declared entrypoint inside the profile boundary; the delegated target still needs normal shell-script review.

## Step 1: Confirm the cron job script value

Inspect the cron job definition for the profile:

```bash
hermes -p <profile> cron list
```

Look for a script-based job shaped like:

```json
{
  "id": "maintenance-job",
  "no_agent": true,
  "script": "maintenance/run.sh"
}
```

Hermes resolves that relative script to:

```text
~/.hermes/profiles/<profile>/scripts/maintenance/run.sh
```

If the `script` field already includes a redundant profile segment, Hermes will include it literally under `scripts/`. For example, `script: "<profile>/run.sh"` resolves to:

```text
~/.hermes/profiles/<profile>/scripts/<profile>/run.sh
```

## Step 2: Create a real wrapper file inside containment

Create the directory expected by the cron job:

```bash
mkdir -p ~/.hermes/profiles/<profile>/scripts/maintenance
```

Create the wrapper file:

```bash
cat > ~/.hermes/profiles/<profile>/scripts/maintenance/run.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

exec /home/<user>/job-desk/hermes/scripts/run.sh "$@"
SH
```

Make it executable:

```bash
chmod +x ~/.hermes/profiles/<profile>/scripts/maintenance/run.sh
```

The important part is that the wrapper is a **real file**, not a symlink that resolves outside `scripts/`.

## Step 3: Run the job immediately

Queue the cron job:

```bash
hermes -p <profile> cron run <job-id>
```

Force the scheduler to process due jobs now:

```bash
hermes -p <profile> cron tick
```

Then inspect status:

```bash
hermes -p <profile> cron list
```

The expected final state is a fresh successful run, such as `last_status: ok`.

## Why this works

Hermes checks the declared script path before launching it. The declared entrypoint is:

```text
~/.hermes/profiles/<profile>/scripts/maintenance/run.sh
```

That file is inside the allowed profile `scripts/` directory, so the containment check passes.

The shell then replaces itself with the canonical script via `exec`. This avoids drift because there is still only one real implementation to maintain.

## Rollback

Remove the wrapper file:

```bash
rm ~/.hermes/profiles/<profile>/scripts/maintenance/run.sh
```

If the cron job should instead point at a different profile-local wrapper, update the job's `script` value using the normal cron-edit workflow for your installation.

## Related docs

- [Cron Script Execution Reference](../reference/cron-script-execution.md)
- [Cron Script Errors](../troubleshooting/cron-script-errors.md)
