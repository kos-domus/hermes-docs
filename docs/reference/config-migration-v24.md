---
title: "Config Migration v23 to v24"
slug: "config-migration-v24"
category: "reference"
tags: ["configuration", "migration", "profiles", "gateway", "dashboard", "mcp"]
sources:
  - "sessions/2026-05-27-hermes-pull-105-commits-codex-fix-tts-cornelia.md"
  - "sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md"
last_updated: "2026-05-28"
version: 1
hermes_version_min: "0.14.0"
---

# Config Migration v23 to v24

Hermes `config migrate` can update profile configuration files from schema version 23 to schema version 24. The observed migration was mostly structural and additive, but it can look alarming in a raw diff because some blocks move.

## Run migration per profile

Default profile:

```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.pre-v24-migrate.bak
hermes config migrate
```

Named profile:

```bash
PROFILE=mc
cp ~/.hermes/profiles/$PROFILE/config.yaml ~/.hermes/profiles/$PROFILE/config.yaml.pre-v24-migrate.bak
hermes -p $PROFILE config migrate
```

Fleet loop:

```bash
for p in mc backend frontend cso orcharch family-staging openclaw-observer; do
  cp ~/.hermes/profiles/$p/config.yaml ~/.hermes/profiles/$p/config.yaml.pre-v24-migrate.bak
  hermes -p $p config migrate
done
```

## Observed v24 changes

| Change | Meaning | Operational risk |
|---|---|---|
| `providers: {}` added | Empty scaffold for provider definitions | Low |
| `mcp_servers:` moved lower in the file | Section order changed; content preserved | Low, but easy to misread in partial diffs |
| `gateway:` block expanded | Adds media delivery and recent-file trust defaults | Low if defaults remain unchanged |
| `dashboard.oauth:` block added | Scaffolds dashboard OAuth settings | Low unless dashboard is enabled |
| `resume_*` keys added | Resume behavior defaults | Low |
| `paste_collapse_threshold*` keys added | Paste-collapsing defaults | Low |
| `fallback_model:` commented docs added | Documentation scaffold | None |
| Emoji prompts encoded as Unicode escapes | Cosmetic representation change | None |
| Legacy `vercel_runtime:` retained | Vercel runtime key remained even after upstream Vercel removal | Low; ignored by current code in the observed session |

## Gotcha: `mcp_servers:` may look deleted

A short diff can show `mcp_servers:` removed near the top of the file without showing that it was reinserted near the bottom.

Verify semantically instead of trusting a partial diff:

```bash
hermes mcp list
hermes -p <profile> mcp list
```

If the server list is intact, the migration preserved the MCP config.

## Restart daemons after migration

Long-running gateway services read config at startup. Restart active daemons after migrating their profile config:

```bash
systemctl --user restart hermes-gateway.service hermes-gateway-mc.service hermes-gateway-family-staging.service
```

Then check for errors:

```bash
journalctl --user -u 'hermes-gateway*.service' --since '2 minutes ago' | grep -iE 'error|exception|traceback'
```

No output from the grep is the expected clean result.

## Verify schema version

```bash
hermes doctor
hermes -p mc doctor
```

Expected:

```text
✓ Config version up to date (v24)
```

## Rollback

If migration creates a real issue, restore the backup and restart affected daemons:

```bash
mv ~/.hermes/profiles/<profile>/config.yaml.pre-v24-migrate.bak ~/.hermes/profiles/<profile>/config.yaml
systemctl --user restart hermes-gateway-<profile>.service
```

Use the exact service name used by your installation.
