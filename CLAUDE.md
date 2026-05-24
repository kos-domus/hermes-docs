# Hermes Docs — Kos Elaboration Engine

This project is a **living documentation system** for Hermes Agent (Nous Research).
Kos reads raw work sessions and produces structured, analytical documentation.

Sister project of [openclaw-docs](https://github.com/kos-domus/openclaw-docs) (Claude Code).

## Your Role

You are the **documentation elaboration engine**. Your job:

1. **Read** new or updated session files in `sessions/`
2. **Analyze** the content: extract features, configs, patterns, gotchas, solutions
3. **Generate or update** structured docs in `docs/`
4. **Update** the machine-readable index at `docs/index.yaml`
5. **Log** what you did in `changelog/CHANGELOG.md`

## Elaboration Rules

### Reading Sessions
- Sessions are markdown files in `sessions/` with YAML frontmatter
- Check the `status` field: only process sessions with `status: ready`
- After processing, update the session's status to `status: processed`
- Each session has tags — use them to route content to the right doc section

### Writing Docs
- Follow the **Diátaxis** framework:
  - `docs/getting-started/` — First-time setup, installation, basic usage (pip install, hermes setup, first chat)
  - `docs/guides/` — Task-oriented how-to guides (multi-profile fleet, gateway install, cron setup, 1Password integration, MCP install)
  - `docs/reference/` — Exhaustive reference (CLI commands, profile commands, environment variables, tools, skills catalog)
  - `docs/concepts/` — Architecture, mental models, design decisions (profile system vs OpenClaw workspaces, FTS5 sessions, Honcho user modeling)
  - `docs/troubleshooting/` — Known issues, error messages, solutions
- Every doc file MUST have YAML frontmatter:
  ```yaml
  ---
  title: "Human-readable title"
  slug: "unique-kebab-case-id"
  category: "getting-started|guides|reference|concepts|troubleshooting"
  tags: ["profiles", "cron", "gateway", "mcp"]
  sources: ["sessions/2026-05-24-step1-kos-migration.md"]
  last_updated: "2026-05-24"
  version: 1
  hermes_version_min: "0.14.0"
  ---
  ```
- Use clear H2/H3 hierarchy for scannability
- Include practical code examples whenever possible
- Cross-reference related docs using relative links
- Keep each doc focused on ONE topic — split if it grows beyond ~500 lines

### Updating Docs
- When new session data overlaps with existing docs, **merge** — don't duplicate
- Increment the `version` field when updating
- Add the new session to the `sources` array
- Preserve information from previous versions unless explicitly contradicted
- Update `hermes_version_min` if the doc now applies only from a newer release

### Index Management
- After every elaboration run, regenerate `docs/index.yaml`
- The index must list every doc with: slug, title, category, tags, path, last_updated, hermes_version_min
- This index is the **primary entry point for programmatic fetching**

### Changelog
- Append to `changelog/CHANGELOG.md` with format:
  ```
  ## YYYY-MM-DD
  - **Added**: new-doc-slug — Brief description
  - **Updated**: existing-doc-slug — What changed
  - **Sources**: list of session files processed
  ```

### Language
- ALL generated docs MUST be written in **US English**, regardless of the source session language
- Sessions may be in any language (Italian, English, etc.) — extract the knowledge and write docs in English
- Use American spelling

### Quality Standards
- Be analytical, not just descriptive — explain WHY things work, not just HOW
- Flag contradictions between sessions
- When uncertain, mark with `> ⚠️ **Unverified**: ...` blockquote
- Prefer concrete examples over abstract explanations
- **Accuracy over speed**: double-check commands, flags, and config paths against the actual session logs
- **Detail matters**: include full commands with all flags
- **Real error messages**: when documenting troubleshooting, include exact error text
- **Version-aware**: Hermes evolves fast — always note `hermes_version_min` (current as of 2026-05-24: `0.14.0`)
- **Cross-link aggressively**

### Reference Section Priority

Active reference docs to create or expand for Hermes:

1. **Profile commands reference** — every `hermes profile <subcommand>` flag, behavior, edge cases. Distribution system (`install`, `update`, `info`).
2. **CLI commands reference** — top-level commands inventory with options.
3. **Gateway architecture** — single-profile vs multi-profile setups, systemd vs launchd vs Termux, network mode.
4. **Cron and scheduling** — `hermes cron` syntax, payload conventions, output dir, delivery routing.
5. **1Password integration** — `op inject` template pattern, render scripts, systemd drop-in for `EnvironmentFile=` + `ExecStartPre=`.
6. **MCP servers** — `mcp.json` syntax per profile, installation patterns, troubleshooting.
7. **Skills catalog** — bundled skills, distributions, custom skill authoring.
8. **Telegram forum topics** — `message_thread_id` patterns, `hermes send -t platform:chat:thread`.
9. **`hermes send` cookbook** — LLM-free messaging from scripts/cron, cross-platform targets.
10. **Multi-profile fleet design** — Master Control + passive specialist profiles + `hermes -p <name> chat -q` invocation pattern.

When processing a session, ask yourself: "Is there a command, config pattern, or technical detail here that someone would look up in isolation?" If yes, it belongs in a reference doc, not buried in a guide.

## Upstream Sync Protocol

### Official Sources to Monitor

Before each elaboration run, check for updates from:

1. **Hermes Agent GitHub**: `https://github.com/NousResearch/hermes-agent`
   - Check releases for version updates
   - Read RELEASE_v*.md for breaking changes
   - Monitor `/website/docs/reference/` for official doc updates

2. **Hermes PyPI**: `https://pypi.org/project/hermes-agent/`
   - Latest version

3. **agentskills.io**: skills catalog and standard updates

4. **Nous Research blog**: feature announcements

Mirror upstream config / API changes here, with attribution.

## What we DON'T document

- Specific user secrets, tokens, account IDs (anonymize or omit)
- Proprietary upstream code (link, don't copy)
- Speculative roadmap (only what's released)

## Naming conventions

- Hermes Agent (proper noun, capital A)
- hermes-agent (package name, lowercase hyphenated)
- "Hermes" alone OK in casual context
- `hermes` (lowercase) when referring to the CLI binary
