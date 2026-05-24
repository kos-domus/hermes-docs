# HermesFlow — Hermes Agent Docs

**Community-driven, AI-elaborated documentation for [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research).**

This is a living documentation project. Humans contribute raw work sessions. An AI agent (Kos) reads them daily, extracts knowledge, and produces structured, queryable documentation.

Sister project of [openclaw-docs](https://github.com/kos-domus/openclaw-docs) (which covers Claude Code / OpenClaw).

## How It Works

```
Contributors write session logs → sessions/
                ↓
    Kos reads & analyzes daily (cron)
                ↓
    Structured docs generated → docs/
                ↓
    Index updated → docs/index.yaml
                ↓
    Anyone can fetch & query the docs
```

## Quick Start

### Read the docs

Browse `docs/` by category:

| Category | Path | Description |
|----------|------|-------------|
| Getting Started | `docs/getting-started/` | Installation, first run, basic setup |
| Guides | `docs/guides/` | Step-by-step how-to for specific tasks (profiles, gateway, cron, integrations) |
| Reference | `docs/reference/` | Complete reference for CLI, profile commands, MCP, skills, tools |
| Concepts | `docs/concepts/` | Architecture, mental models, design decisions (multi-profile fleet, FTS5 sessions, Honcho user modeling) |
| Troubleshooting | `docs/troubleshooting/` | Known issues, errors, and solutions |

### Programmatic access

Fetch the index for machine-readable doc discovery:

```bash
# Full index
curl -s https://raw.githubusercontent.com/kos-domus/hermes-docs/main/docs/index.yaml

# Specific doc
curl -s https://raw.githubusercontent.com/kos-domus/hermes-docs/main/docs/guides/profile-multi-fleet.md
```

### Use in your agent context

Add to your agent's instructions / `SOUL.md`:

```markdown
# Hermes Reference
Fetch https://raw.githubusercontent.com/kos-domus/hermes-docs/main/docs/index.yaml
for the documentation index. Fetch individual docs by path as needed.
```

## Contributing

We welcome session contributions from anyone using Hermes Agent. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**TL;DR:**
1. Fork the repo
2. Copy `sessions/_template.md` to `sessions/YYYY-MM-DD-your-topic.md`
3. Fill in your session details
4. Set `status: ready`
5. Open a PR

Kos will process your session in the next daily run and integrate your knowledge into the docs.

## Project Structure

```
hermes-docs/
├── CLAUDE.md              # Instructions for Kos (elaboration engine)
├── sessions/              # Raw work session logs (input)
│   ├── _template.md       # Template for new sessions
│   └── schema.yaml        # Validation schema
├── docs/                  # Elaborated documentation (output)
│   ├── index.yaml         # Machine-readable index (fetch this first)
│   ├── getting-started/
│   ├── guides/
│   ├── reference/
│   ├── concepts/
│   └── troubleshooting/
├── strategy/              # Hermes strategy / architecture decisions
├── skill-draft/           # Skill drafts before promotion to Hermes catalog
└── changelog/
    └── CHANGELOG.md       # Log of all elaboration runs
```

## Why a separate repo from openclaw-docs?

OpenClaw (Claude Code) and Hermes (Nous Research) are different runtimes with different idioms:
- OpenClaw: workspace-based, custom YAML config, OpenClaw-specific tool registry
- Hermes: profile-based, FTS5 session search, Honcho user modeling, multi-platform messaging gateway built-in, agentskills.io standard

Keeping the docs separate avoids confusion and lets each repo follow its native conventions.

## License

MIT — use freely, contribute back.
