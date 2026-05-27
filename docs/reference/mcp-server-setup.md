---
title: "MCP Server Setup Reference"
slug: "mcp-server-setup"
category: "reference"
tags: ["mcp", "mcp-servers", "configuration", "oauth", "cli", "reference"]
sources:
  - "sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md"
last_updated: "2026-05-27"
version: 1
hermes_version_min: "0.14.0"
---

# MCP Server Setup Reference

This reference covers Hermes MCP server configuration syntax, CLI commands, OAuth patterns, and the per-profile token persistence layout.

## Config file location

MCP servers are configured in each profile's `config.yaml`:

```text
~/.hermes/config.yaml                        # default profile
~/.hermes/profiles/<name>/config.yaml         # named profile
```

Add an `mcp_servers:` top-level section. Place it before `toolsets:` for readability.

## Config syntax

### stdio transport (local process)

```yaml
mcp_servers:
  <server-name>:
    command: <executable>
    args: ["<arg1>", "<arg2>"]
    env:
      <ENV_VAR>: ${VARIABLE_REFERENCE}
```

The `env` block supports `${VAR}` syntax for referencing environment variables available to the Hermes process.

### HTTP transport (remote server)

```yaml
mcp_servers:
  <server-name>:
    url: https://example.com/mcp
    auth: oauth   # or omit for no-auth
```

### Multiple servers

```yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
  sentry:
    url: https://mcp.sentry.dev/mcp
    auth: oauth
```

## CLI commands

### List MCP servers for a profile

```bash
hermes mcp list
hermes -p <profile> mcp list
```

Output shows each server name and status (`✓ enabled`, `! Needs authentication`).

### Add an MCP server via CLI

```bash
hermes mcp add <name> --command <cmd> --args <arg1> <arg2>
hermes -p <profile> mcp add <name> --url <url> --auth oauth
```

> ⚠️ **Known bug**: `hermes mcp add` misinterprets arguments starting with `-` (e.g., `-y`) as argparse flags. When adding servers that need such arguments, edit `config.yaml` directly instead.

### Remove an MCP server

```bash
hermes mcp remove <name>
hermes -p <profile> mcp remove <name>
```

### Test MCP server connectivity

```bash
hermes mcp test <name>
hermes -p <profile> mcp test <name>
```

### Initiate OAuth login for an MCP server

```bash
hermes mcp login <name>
hermes -p <profile> mcp login <name>
```

The command prints an OAuth URL and starts a local HTTP listener on a random port. See [MCP fleet propagation guide](../guides/mcp-fleet-propagation.md) for the full OAuth flow walkthrough.

## OAuth token persistence

After a successful OAuth login, Hermes stores three files per server per profile:

```text
~/.hermes/profiles/<profile>/mcp-tokens/
├── <server>.client.json    # OAuth client metadata (~319 bytes)
├── <server>.json           # access_token + refresh_token + expires_at (~305 bytes, mode 600)
└── <server>.meta.json      # Tool discovery cache (~812 bytes)
```

For the default profile, the path is `~/.hermes/mcp-tokens/`.

Key points:

- **Per-profile separation**: each profile stores its own tokens. No cross-profile sharing. This prevents refresh-token rotation conflicts.
- **File permissions**: `<server>.json` is created with mode 600 (owner read/write only).
- **Auto-refresh**: Hermes transparently refreshes access tokens using the stored refresh token.
- **Typical TTL**: access tokens ~1 hour; refresh tokens ~weeks.

## Environment variable: HERMES_MCP_CONNECT_TIMEOUT

The default connect timeout for MCP server probing is 30 seconds. For OAuth flows that require interactive browser authentication (especially over SSH tunnels), this is too short.

Override with the environment variable:

```bash
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p <profile> mcp login <server>
```

This sets the timeout to 5 minutes. The override affects both `mcp test` and `mcp login` code paths.

> ⚠️ **Note**: This env var was introduced via a local patch to `hermes_cli/mcp_config.py`. It may not be available in upstream Hermes releases. Verify with your installed version.

## Server catalog: validated configurations

The following MCP server configurations have been validated in the source session:

| Server | Transport | Config | Notes |
|---|---|---|---|
| GitHub | stdio | `command: npx, args: ["-y", "@modelcontextprotocol/server-github"]` | Requires `GITHUB_PERSONAL_ACCESS_TOKEN` in env |
| Filesystem | stdio | `command: npx, args: ["-y", "@modelcontextprotocol/server-filesystem", "/path"]` | Mount point for file access |
| Codebase Memory | stdio | `command: codebase-memory-mcp, args: ["--ui=true", "--port=9749"]` | Knowledge graph server |
| Sentry | HTTP | `url: https://mcp.sentry.dev/mcp, auth: oauth` | OAuth login required per profile |
| Chrome DevTools | stdio | `command: npx, args: ["-y", "chrome-devtools-mcp@latest", "--isolated", "--headless"]` | For browser testing/debugging |
| Playwright | stdio | Requires `npx playwright install firefox` (~100 MB) first | Headless browser automation |
| Semgrep | stdio | Security scanning | Used by CSO profile |
| Trivy | stdio | Container/filesystem security scanning | Used by CSO profile |
| Deep Research | stdio | Research aggregation | Used by orchestrator-architect profile |
| Postgres | stdio | Database access via MCP | Used by backend profile |

## Source code patch note

The `HERMES_MCP_CONNECT_TIMEOUT` env var override was implemented in:

```text
~/.hermes/hermes-agent/hermes_cli/mcp_config.py:167-180
```

Function `_probe_single_server` reads the env var with a default fallback of 30 seconds.

> **Caveat**: This modification lives in the vendored Hermes source directory (`~/.hermes/hermes-agent/`). It will be lost on the next Hermes update via pip or installer. Prepare a re-applicable patch file or contribute the change upstream.

## Related docs

- [MCP fleet propagation guide](../guides/mcp-fleet-propagation.md)
- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [MCP errors troubleshooting](../troubleshooting/mcp-errors.md)
