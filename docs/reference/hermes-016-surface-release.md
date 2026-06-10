---
title: Hermes Agent 0.16.0 Surface Release Reference
slug: hermes-016-surface-release
category: reference
tags:
- release-notes
- desktop
- dashboard
- skills
- setup
- security
- cli
- tui
sources:
- upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5
- upstream:https://pypi.org/project/hermes-agent/0.16.0/
last_updated: '2026-06-10'
version: 1
hermes_version_min: 0.16.0
---
# Hermes Agent 0.16.0 Surface Release Reference

Hermes Agent `0.16.0` was published as tag `v2026.6.5` and is available on PyPI as `hermes-agent==0.16.0`. The upstream release title is **Hermes Agent v0.16.0 (2026.6.5) — The Surface Release**.

This reference extracts the operator-facing changes from the upstream release notes. It is not a replacement for the full upstream changelog.

## Release metadata

| Field | Value |
|---|---|
| Package version | `0.16.0` |
| Git tag | `v2026.6.5` |
| Release name | The Surface Release |
| Release date | 2026-06-05 / published 2026-06-06 UTC |
| PyPI latest observed | `0.16.0` on 2026-06-10 |
| Upstream release | <https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5> |

## Major additions

### Native desktop app

Hermes now ships a native Electron desktop app for macOS, Linux, and Windows. Key capabilities called out upstream:

- chat window with streaming;
- session list with archive and search;
- drag-and-drop files into chat;
- clipboard image paste;
- Cmd+K command palette;
- inline model picker in the status bar;
- in-app self-update;
- Simplified Chinese UI translation;
- concurrent multi-profile sessions;
- remote Hermes gateway connections.

### Remote gateway desktop mode

The desktop app can connect to a remote Hermes gateway using OAuth or username/password. Practical implications:

- API keys and compute can remain on a server;
- local machine can run only the GUI;
- profiles can target different remote hosts;
- OAuth WebSocket tickets are refreshed on reconnect.

See [Connect Hermes Desktop to a Remote Gateway](../guides/desktop-remote-gateway.md).

### Web dashboard administration panel

The dashboard expanded from session viewing into a browser administration surface. Upstream highlights include:

- MCP catalog enable/disable toggles;
- messaging channel setup;
- credential management;
- webhook and hook creation;
- memory configuration;
- gateway controls;
- system page with check-before-update and Debug Share;
- pluggable OIDC and username/password login.

### Quick Setup via Nous Portal

First-run setup now offers a shorter path:

```bash
hermes portal
```

Use Quick Setup to sign in with Nous Portal, choose a model, and start chatting. Full Setup remains the better fit for custom providers, profile fleets, and self-hosted gateway work.

See [Quick Setup via Nous Portal](../getting-started/quick-setup-nous-portal.md).

## CLI, TUI, and agent loop changes

Operator-facing additions:

- fuzzy model picker across desktop, web dashboard, TUI, and CLI;
- `/undo [N]` to back up the last N user turns with prefill and soft-delete;
- configurable default interface: classic CLI vs Ink TUI;
- `--cli` override for `hermes chat` when TUI is the default;
- `hermes prompt-size` diagnostic;
- `hermes sessions optimize` for FTS5 maintenance;
- compact line-number gutter for `read_file` output;
- unbounded delegation `max_spawn_depth` with floor 1.

## Skills changes

The default skill set was trimmed in 0.16.0.

Removed from bundled defaults or superseded:

- `spotify` → superseded by the native Spotify plugin tools;
- `linear` → superseded by `hermes mcp install linear`;
- `kanban-codex-lane`;
- `debugging-hermes-tui-commands`;
- stale or empty category markers.

Moved from bundled to optional:

- Baoyu creative skills;
- `dspy`;
- `subagent-driven-development`;
- `minecraft-modpack-server`;
- `pokemon-player`;
- `hermes-s6-container-supervision`.

New or changed skill infrastructure:

- `NVIDIA/skills` is a built-in trusted Skills Hub tap;
- `environments:` frontmatter gates context-specific skills from irrelevant indexes;
- the curator can prune unused built-in skills;
- blank-slate installs can use `install --no-skills`.

## Security and reliability notes

The upstream release notes call out several security and reliability changes:

- Starlette pinned to a patched version for `CVE-2026-48710`;
- URL SSRF checks moved off the async event loop;
- Bedrock inference bearer tokens stripped from subprocess environments;
- `bws_cache.json` added to file-safety read guards;
- Docker dangerous-pattern coverage expanded;
- invisible Unicode sanitized in vetted skill content;
- MCP OAuth no longer reports false success when no token was obtained.

## Upgrade attention points

Before upgrading a production profile fleet:

1. review the default skill-set changes if jobs depend on skills that moved to optional;
2. verify desktop/dashboard auth if exposing a remote gateway;
3. test provider model selection because the picker and provider grouping changed;
4. validate MCP OAuth flows if automation previously trusted success messages;
5. run existing cron jobs once manually after upgrade, especially those that rely on skills or MCP servers.

## Related docs

- [Quick Setup via Nous Portal](../getting-started/quick-setup-nous-portal.md)
- [Connect Hermes Desktop to a Remote Gateway](../guides/desktop-remote-gateway.md)
- [Provider Authentication Reference](provider-authentication.md)
- [MCP Server Setup Reference](mcp-server-setup.md)
