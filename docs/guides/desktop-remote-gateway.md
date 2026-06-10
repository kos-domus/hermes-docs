---
title: Connect Hermes Desktop to a Remote Gateway
slug: desktop-remote-gateway
category: guides
tags:
- desktop
- gateway
- remote
- oauth
- profiles
- websocket
- authentication
sources:
- upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5
last_updated: '2026-06-10'
version: 1
hermes_version_min: 0.16.0
---
# Connect Hermes Desktop to a Remote Gateway

Hermes Agent 0.16.0 introduces a native Electron desktop app for macOS, Linux, and Windows. The desktop app can run as a thin client against a remote Hermes gateway, so the GUI can live on a laptop while the agent runtime, API keys, tools, and compute remain on a server.

## Use case

Use a remote desktop connection when:

- the Hermes gateway runs on a homelab, workstation, VPS, or team server;
- API keys should stay on the remote machine;
- the local machine should only provide the chat UI;
- different profiles target different remote hosts;
- you need concurrent sessions across multiple profiles from one window.

## Prerequisites

- Hermes Agent `0.16.0` or newer on the remote host.
- A reachable Hermes gateway endpoint.
- Remote gateway authentication configured with OAuth or username/password.
- Network access from the desktop app to the gateway WebSocket endpoint.

> ⚠️ **Unverified command surface**: the 0.16.0 release notes confirm remote desktop gateway support, OAuth-gated remote gateways, username/password login, per-profile remote hosts, and WebSocket ticket refresh. They do not provide a single canonical CLI command sequence for provisioning the gateway. Use the official Desktop App and dashboard docs for the exact UI flow on your build.

## Connection model

The remote-gateway flow has three moving parts:

1. **Desktop app** — the local GUI. It streams chat, manages sessions, accepts drag-and-drop files, and exposes a model picker in the status bar.
2. **Remote Hermes gateway** — the authenticated server-side runtime that owns providers, credentials, tools, MCP servers, and profile state.
3. **Authenticated WebSocket** — the desktop app connects to the gateway using OAuth or username/password. Hermes 0.16.0 re-mints OAuth WebSocket tickets on reconnect.

## Profile-aware remote hosts

Hermes 0.16.0 supports per-profile remote gateway hosts. This enables one desktop app to connect to multiple profile contexts, for example:

- `default` → local or personal remote gateway;
- `work` → work server gateway;
- `research` → GPU workstation gateway.

The release also adds concurrent multi-profile sessions and cross-profile `@session` links in the desktop app.

## Operational checks

Before treating the desktop connection as production-ready, verify:

1. the gateway is reachable from the desktop network;
2. OAuth or username/password login succeeds;
3. a new chat starts under the expected profile;
4. reconnect preserves the session;
5. profile-specific credentials and tools are not accidentally shared across profiles;
6. file drops and clipboard image paste route to the intended remote profile.

## Related docs

- [OAuth Credential Separation in Hermes](../concepts/oauth-credential-separation.md)
- [Provider Authentication Reference](../reference/provider-authentication.md)
- [Provider and Gateway Errors](../troubleshooting/provider-and-gateway-errors.md)
