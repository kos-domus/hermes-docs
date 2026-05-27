---
title: "MCP Server Errors"
slug: "mcp-errors"
category: "troubleshooting"
tags: ["mcp", "mcp-servers", "oauth", "troubleshooting", "timeout"]
sources:
  - "sessions/2026-05-26-mcp-fleet-propagation-sentry-oauth-3-profile-timeout-patch.md"
last_updated: "2026-05-27"
version: 1
hermes_version_min: "0.14.0"
---

# MCP Server Errors

This page covers errors specific to Hermes MCP server setup, OAuth login, and cross-profile propagation.

## `hermes mcp add` fails with `unrecognized arguments`

### Exact error

```text
error: unrecognized arguments: -y @modelcontextprotocol/server-github
```

### Cause

The `hermes mcp add` command uses argparse, and the `--args` parameter accepts `nargs=[ARGS ...]`. Arguments starting with `-` (like `-y`) are interpreted as argparse flags rather than positional values.

### Fix

Edit the profile's `config.yaml` directly instead of using the CLI:

```yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}
```

A future Hermes release may fix this with `--args=-y` equals syntax or proper `--` separator handling.

## MCP OAuth login times out at 30 seconds

### Exact error

```text
MCP call timed out after 40.0s (configured timeout: 40.0s)
```

### Cause

The `_probe_single_server` function in `hermes_cli/mcp_config.py` uses a fixed 30-second connect timeout (plus 10-second buffer = 40s total). MCP OAuth login requires:

1. Starting a local HTTP listener on a random port.
2. Printing an OAuth authorization URL.
3. Waiting for the user to open the URL, authenticate, and authorize.
4. Receiving the callback with the authorization code.
5. Completing the token exchange.

This interactive flow often takes more than 40 seconds, especially when using SSH tunnels or when the user is not immediately at the browser.

### Symptom

The OAuth token file (`<server>.json`) is **not written to disk** after login, even though the authorization may have succeeded in the browser. Only the `<server>.client.json` (client metadata) file exists.

### Fix

Set the `HERMES_MCP_CONNECT_TIMEOUT` environment variable to allow more time:

```bash
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p <profile> mcp login <server>
```

This gives 5 minutes for the OAuth flow. Adjust the value based on your setup:

- **Direct browser on same machine**: 120–180 seconds is usually sufficient.
- **SSH tunnel from remote**: 300 seconds (5 minutes) provides comfortable margin.

> ⚠️ **Note**: This env var requires a local patch to `hermes_cli/mcp_config.py`. It may not be available in upstream Hermes releases. See [MCP server setup reference](../reference/mcp-server-setup.md) for details.

## OAuth token file missing after apparent successful login

### Symptom

The login command appeared to complete, but `~/.hermes/profiles/<profile>/mcp-tokens/<server>.json` does not exist. Only `<server>.client.json` is present.

### Cause

The OAuth callback arrived at the Hermes listener after the timeout had already expired. The authorization code was lost because the listener had shut down.

### Fix

Re-run the login command with an extended timeout:

```bash
HERMES_MCP_CONNECT_TIMEOUT=300 hermes -p <profile> mcp login <server>
```

## OAuth callback fails to reach Hermes via SSH tunnel

### Symptom

The browser shows a successful authorization redirect to `127.0.0.1:<PORT>/callback`, but the page displays an error (connection refused). The Hermes terminal shows no activity.

### Cause

The SSH tunnel was not set up, was set up to the wrong port, or has already been closed.

### Fix

1. Start the login command on the Hermes host and note the printed port number `<PORT>`.
2. On your local machine, set up the tunnel **before** opening the OAuth URL:
   ```bash
   ssh -N -L <PORT>:127.0.0.1:<PORT> <hermes-host-alias>
   ```
3. Keep the tunnel open during the entire OAuth flow.
4. Open the OAuth URL and complete authorization.

If possible, use a machine with a direct browser instead of SSH tunneling. See [MCP fleet propagation guide](../guides/mcp-fleet-propagation.md) for both approaches.

## MCP server shows `! Needs authentication` after login

### Symptom

`hermes mcp list` shows the server with `! Needs authentication` even after a successful OAuth login on a different profile.

### Cause

Hermes maintains OAuth sessions **per profile**. Logging in on the default profile does not authenticate the same MCP server for a named profile.

### Fix

Run the OAuth login for each profile that uses the server:

```bash
hermes mcp login <server>                     # default profile
hermes -p mc mcp login <server>               # mc profile
hermes -p frontend mcp login <server>         # frontend profile
```

See [OAuth credential separation](../concepts/oauth-credential-separation.md) for the design rationale.

## MCP server not listed after config edit

### Symptom

`hermes mcp list` does not show a newly added server even though the `config.yaml` was updated.

### Cause

The profile's gateway service has not reloaded the config, or the config file has a YAML syntax error.

### Fix

1. Validate the YAML syntax:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('path/to/config.yaml'))"
   ```
2. For daemon profiles (default, mc), restart the service:
   ```bash
   systemctl --user restart hermes-gateway.service
   ```
3. For passive profiles, no restart is needed — config is read on subprocess spawn.

## Related docs

- [MCP server setup reference](../reference/mcp-server-setup.md)
- [MCP fleet propagation guide](../guides/mcp-fleet-propagation.md)
- [OAuth credential separation](../concepts/oauth-credential-separation.md)
- [Provider and gateway errors](provider-and-gateway-errors.md)
