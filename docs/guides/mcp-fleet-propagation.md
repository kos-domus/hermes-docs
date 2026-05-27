---
title: "Propagate MCP Servers Across a Hermes Profile Fleet"
slug: "mcp-fleet-propagation"
category: "guides"
tags: ["mcp", "mcp-servers", "fleet", "configuration", "oauth", "profiles"]
sources:
  - "sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md"
last_updated: "2026-05-27"
version: 1
hermes_version_min: "0.14.0"
---

# Propagate MCP Servers Across a Hermes Profile Fleet

This guide describes how to propagate MCP (Model Context Protocol) servers across multiple Hermes profiles in a multi-agent fleet. Each Hermes profile can have its own set of MCP servers, and this guide shows how to design, configure, and verify a cross-fleet MCP deployment.

## When to use this guide

- You have a Hermes fleet with multiple profiles (e.g., default + specialist profiles).
- You want each agent to access the MCP servers relevant to its domain.
- You need to set up OAuth-based MCP servers (like Sentry) that require per-profile authentication.

## Prerequisites

- Hermes Agent ≥ 0.14.0 with the `mcp_servers` config section available.
- At least one MCP server package installed (e.g., `@modelcontextprotocol/server-github`).
- A clear understanding of which domains each profile covers.

## Design the MCP mapping

Before editing configs, decide which MCP servers each profile needs. The source session used this mapping for a six-profile fleet:

| Profile | MCP servers | Rationale |
|---|---|---|
| **default** (Kos) | sentry, github, filesystem, codebase-memory | General-purpose: issue tracking, code access, knowledge graph |
| **mc** (Master Control) | sentry, github, filesystem, codebase-memory | Same as default: orchestrator needs full visibility |
| **backend** | postgres, github, filesystem, codebase-memory | Database access + code + knowledge graph |
| **cso** | semgrep, trivy, github, sentry, filesystem | Security scanning + code + issue tracking |
| **frontend** | chrome-devtools, playwright, sentry, filesystem | Browser testing + error tracking |
| **orcharch** | deep-research, github, codebase-memory, filesystem | Research + code + knowledge graph |

> **Note**: Obsidian MCP was intentionally excluded from Hermes on the mini-PC. The Obsidian REST API (`127.0.0.1:27124`) only runs on the Mac desktop, not on the Hermes host. Use filesystem MCP for vault file read/write access instead.

## Configure MCP servers in profile config.yaml

Edit each profile's `config.yaml` to add an `mcp_servers:` section. Place it before `toolsets:` in the file.

### Example: stdio MCP server (GitHub)

```yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}
```

### Example: stdio MCP server with arguments starting with `-`

The `hermes mcp add` CLI has a known bug where arguments starting with `-` (like `-y`) are misinterpreted by argparse as flags. **Workaround**: edit the YAML config file directly instead of using the CLI.

```bash
# This FAILS due to argparse:
hermes mcp add github --command npx --args -y @modelcontextprotocol/server-github
# error: unrecognized arguments: -y @...

# Instead, edit config.yaml directly (see example above)
```

### Example: HTTP MCP server with OAuth (Sentry)

```yaml
mcp_servers:
  sentry:
    url: https://mcp.sentry.dev/mcp
    auth: oauth
```

### Example: stdio MCP server with custom args (codebase-memory)

```yaml
mcp_servers:
  codebase-memory:
    command: codebase-memory-mcp
    args: ["--ui=true", "--port=9749"]
```

### Example: filesystem MCP server

```yaml
mcp_servers:
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/kos/job-desk"]
```

## Apply and verify

### For daemon profiles (default, mc)

After editing config, restart the gateway service:

```bash
systemctl --user restart hermes-gateway.service        # default profile
systemctl --user restart hermes-gateway-mc.service      # mc profile
```

### For passive profiles (backend, cso, frontend, orcharch)

Passive profiles read config on-demand when spawned as subprocesses. No restart is needed.

### Verify all profiles

```bash
hermes mcp list
hermes -p mc mcp list
hermes -p backend mcp list
hermes -p cso mcp list
hermes -p frontend mcp list
hermes -p orcharch mcp list
```

Each command should list the MCP servers for that profile with `✓ enabled` status.

## Set up OAuth-based MCP servers

Hermes maintains **separate OAuth sessions per profile** by design. This prevents refresh-token rotation conflicts where one profile's refresh invalidates another's session. See [OAuth credential separation](../concepts/oauth-credential-separation.md) for the full rationale.

### OAuth login per profile

For each profile that uses an OAuth MCP server (e.g., Sentry), run a separate login:

```bash
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p mc mcp login sentry
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p cso mcp login sentry
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p frontend mcp login sentry
```

The `HERMES_MCP_CONNECT_TIMEOUT=300` sets a 5-minute timeout instead of the default 30 seconds. This is necessary because the OAuth flow involves opening a browser, authenticating, and waiting for the callback. See [MCP errors troubleshooting](../troubleshooting/mcp-errors.md) for details on the timeout issue.

### OAuth flow on a machine with a browser

When the Hermes host has a physical display and browser:

1. Run `hermes -p <profile> mcp login sentry` — it prints an OAuth URL and starts a listener on `127.0.0.1:<random_port>`.
2. Open the URL in the browser on the same machine.
3. Authorize the application.
4. The browser redirects to `127.0.0.1:<port>/callback` — Hermes receives the authorization code and completes token exchange.
5. Verify token persistence:

```text
~/.hermes/profiles/<profile>/mcp-tokens/
├── sentry.client.json    (OAuth client metadata)
├── sentry.json           (access_token + refresh_token + expires_at, mode 600)
└── sentry.meta.json      (tool discovery cache)
```

### OAuth flow on a headless SSH machine

If the Hermes host is headless (no browser), use an SSH tunnel to forward the callback port:

1. **Terminal A** (SSH to Hermes host): Run `hermes -p <profile> mcp login sentry` — note the printed port number `<PORT>`.
2. **Terminal B** (your local machine): Forward the port:
   ```bash
   ssh -N -L <PORT>:127.0.0.1:<PORT> <hermes-host>
   ```
3. **Local browser**: Open the OAuth URL, authorize, and the redirect will be tunneled back to Hermes.

This is more complex and slower (~20–30 min for 3 profiles) compared to the direct browser approach (~10–15 min).

### Token auto-refresh

Hermes transparently refreshes OAuth access tokens using the stored refresh token. Access tokens typically expire in 1 hour; refresh tokens last weeks. No manual intervention is needed after the initial login, but monitor the first natural expiry to confirm the refresh flow works.

## Backup discipline

Before editing profile configs, create timestamped backups:

```bash
cp ~/.hermes/profiles/mc/config.yaml \
   ~/.hermes/profiles/mc/config.yaml.bak.pre-mcp.$(date +%s)
```

## Sentry project structure recommendation

For agentic systems with fewer than 10 agents, use a **single Sentry project** with tag-based segmentation:

```text
tags: agent={profile_name}, env={staging|production}, phase={development|review}
```

Do **not** create one Sentry project per agent — this causes alert fatigue and fragments the error quota.

## Related docs

- [MCP server setup reference](../reference/mcp-server-setup.md)
- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [MCP errors troubleshooting](../troubleshooting/mcp-errors.md)
- [Provider and gateway errors](../troubleshooting/provider-and-gateway-errors.md)
