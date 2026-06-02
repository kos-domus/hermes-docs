---
title: "Cron Script Errors"
slug: "cron-script-errors"
category: "troubleshooting"
tags: ["cron", "scripts", "troubleshooting", "profiles", "scheduling", "security"]
sources:
  - "sessions/2026-06-01-cron-script-containment-fix.md"
last_updated: "2026-06-02"
version: 1
hermes_version_min: "0.14.0"
---

# Cron Script Errors

This troubleshooting page covers script-based Hermes cron jobs that fail before the script body runs.

## `Script not found: .../scripts/<profile>/<script>.sh`

### Symptom

A script-based cron job fails every scheduled run with an error like:

```text
Script not found: .../scripts/<profile>/<script>.sh
```

Prompt-based cron jobs in the same profile may continue to work.

### Cause

The job's `script` value is resolved relative to the profile-local `scripts/` directory:

```text
~/.hermes/profiles/<profile>/scripts/
```

If the `script` value includes an extra profile or directory prefix, Hermes preserves that prefix and looks for a nested path that may not exist.

For example:

```json
{
  "script": "<profile>/<script>.sh"
}
```

resolves to:

```text
~/.hermes/profiles/<profile>/scripts/<profile>/<script>.sh
```

This is not relative to `~/.hermes/scripts/` or the job `workdir`.

### Fix

Create a real wrapper file at the exact path Hermes expects:

```bash
mkdir -p ~/.hermes/profiles/<profile>/scripts/<profile>
cat > ~/.hermes/profiles/<profile>/scripts/<profile>/<script>.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

exec /home/<user>/job-desk/hermes/scripts/<script>.sh "$@"
SH
chmod +x ~/.hermes/profiles/<profile>/scripts/<profile>/<script>.sh
```

Then run:

```bash
hermes -p <profile> cron run <job-id>
hermes -p <profile> cron tick
```

Confirm that the new run ends with `last_status: ok`.

## `Blocked: script path resolves outside the scripts directory`

### Symptom

After adding a symlink under `~/.hermes/profiles/<profile>/scripts/`, the cron job fails with:

```text
Blocked: script path resolves outside the scripts directory
```

### Cause

Hermes enforces a containment check for cron scripts. The final resolved script path must stay inside the profile's `scripts/` directory.

A symlink can appear to be inside `scripts/` while resolving to a file outside it. Hermes blocks that path as an escape attempt.

### Fix

Replace the symlink with a real wrapper file inside `scripts/`:

```bash
rm ~/.hermes/profiles/<profile>/scripts/<path-to-wrapper>
cat > ~/.hermes/profiles/<profile>/scripts/<path-to-wrapper> <<'SH'
#!/usr/bin/env bash
set -euo pipefail

exec /home/<user>/job-desk/hermes/scripts/<script>.sh "$@"
SH
chmod +x ~/.hermes/profiles/<profile>/scripts/<path-to-wrapper>
```

Do not point the cron `script` field directly at the external canonical script. Keep the declared Hermes entrypoint profile-local.

## Diagnostic checklist

1. Is the job script-based?

   ```bash
   hermes -p <profile> cron list
   ```

   Check for `no_agent: true` and a `script` field.

2. What path will Hermes resolve?

   Combine the profile-local scripts root with the `script` value:

   ```text
   ~/.hermes/profiles/<profile>/scripts/<script-value>
   ```

3. Is the entrypoint a real file?

   ```bash
   file ~/.hermes/profiles/<profile>/scripts/<script-value>
   ```

4. Is it executable?

   ```bash
   test -x ~/.hermes/profiles/<profile>/scripts/<script-value>
   ```

5. Does a manual run pass?

   ```bash
   hermes -p <profile> cron run <job-id>
   hermes -p <profile> cron tick
   ```

## Related docs

- [Cron Script Execution Reference](../reference/cron-script-execution.md)
- [Cron Script Wrapper Pattern](../guides/cron-script-wrapper-pattern.md)
- [Provider and Gateway Errors](provider-and-gateway-errors.md)
