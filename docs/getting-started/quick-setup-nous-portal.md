---
title: Quick Setup via Nous Portal
slug: quick-setup-nous-portal
category: getting-started
tags:
- setup
- nous-portal
- onboarding
- providers
- oauth
- models
sources:
- upstream:https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5
- upstream:https://pypi.org/project/hermes-agent/0.16.0/
last_updated: '2026-06-10'
version: 1
hermes_version_min: 0.16.0
---
# Quick Setup via Nous Portal

Hermes Agent 0.16.0 adds a shorter first-run path called **Quick Setup via Nous Portal**. Use it when the goal is to get from a fresh install to a working first message without walking through every advanced provider, tool, and gateway setting.

## When to use Quick Setup

Use Quick Setup when:

- the user is new to Hermes Agent;
- the machine should use the Nous Portal flow for model access;
- you want the setup wizard to present a model picker and then start chatting immediately;
- advanced self-hosted gateway, custom provider, or profile-fleet wiring can wait until later.

Use **Full Setup** instead when you need to preconfigure custom endpoints, multiple profiles, self-hosted gateway auth, MCP servers, or platform-specific messaging before first use.

## Start the Portal flow

Hermes 0.16.0 introduces a human-readable alias:

```bash
hermes portal
```

During first-run setup, choose **Quick Setup** when prompted. The wizard explains the difference between Quick Setup and Full Setup inline.

## What Quick Setup configures

The 0.16.0 release notes describe the flow as:

1. sign in with Nous Portal;
2. choose a model from the model picker;
3. start chatting.

The model picker is now fuzzy-searchable across the desktop app, web dashboard, TUI, and CLI. You can type partial model names rather than scrolling a long provider list.

## Choosing provider later

Hermes 0.16.0 also allows onboarding to continue with **Choose provider later**. This is useful when:

- you are validating installation only;
- credentials are not available yet;
- a custom or local endpoint will be added after setup.

For secret hygiene, add API keys through environment variables or Hermes credential flows. Do not hard-code keys in `config.yaml`.

## Related docs

- [Provider Authentication Reference](../reference/provider-authentication.md)
- [Build a Subscription-First Provider Chain](../guides/provider-chain-subscription-oauth.md)
