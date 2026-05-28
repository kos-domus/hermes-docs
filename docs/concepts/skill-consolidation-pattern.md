---
title: "Skill Consolidation Pattern"
slug: "skill-consolidation-pattern"
category: "concepts"
tags: ["skills", "prompting", "architecture", "agent-design", "maintenance"]
sources:
  - "sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md"
last_updated: "2026-05-28"
version: 1
hermes_version_min: "0.14.0"
---

# Skill Consolidation Pattern

Hermes skills work best when they are the single source of truth for a recurring workflow. A common anti-pattern is a workflow split across a profile `SOUL.md`, a procedure file, and a generic skill. The result is prompt bloat, duplicated rules, and fuzzy failure handling.

The skill consolidation pattern turns that into a small profile reference plus one focused lazy-loaded skill.

## When to consolidate

Consolidate when a workflow has any of these symptoms:

- The same rules appear in two or more files.
- The profile `SOUL.md` contains exact tool-call templates for a workflow.
- Operators must jump between `SOUL.md`, `procedures/`, and `skills/` to complete one task.
- Decision boundaries are described narratively instead of as a state machine.
- Failure modes are scattered or implicit.

## Target shape

```text
SOUL.md
  └── small trigger reference: "for capture, load skill: capture"
       └── skills/capture/SKILL.md
            ├── frontmatter
            ├── trigger conditions
            ├── state machine
            ├── tool-call templates
            ├── ACK templates
            ├── failure modes
            ├── anti-patterns
            └── lazy-load references
```

Old procedure files can remain as redirect shims for compatibility, but they should not contain active logic.

## Design principles

### 1. State machine over prose

Bad:

> If the user sends an audio note, save it, process it if needed, and acknowledge it.

Better:

```text
classify input → compute slug/job_id → archive raw/source → write index note → ACK success/failure
```

### 2. Sharp decision boundaries

Use explicit thresholds and branches:

```text
voice_transcript_words < 500  → inline note
voice_transcript_words >= 500 → audio pipeline job folder + index note
text input                    → direct markdown note
document input                → document archive branch
```

### 3. Tool templates, not tool prose

Put exact placeholder templates in the skill:

```yaml
path: "{vault}/Inbox/{yyyy-mm-dd}-{slug}.md"
content: |
  ---
  captured_at: "{now_iso}"
  source: "{source}"
  tags: ["capture"]
  ---

  {body}
```

### 4. Failure modes are part of the workflow

Every expected failure needs a concrete action and ACK shape:

| Failure | Action |
|---|---|
| Cannot write note | Report failure and include the intended path |
| Missing transcript | Save raw metadata and mark transcript pending |
| Ambiguous destination | Use default inbox; do not ask unless truly blocked |
| Tool timeout | Preserve input and return retry-safe status |

### 5. Keep generic skills generic

A generic Obsidian skill should remain a vault-writing reference. A specific capture workflow should live in its own `capture` skill and lazy-load the generic Obsidian skill only when needed.

## Why this matters

A source session reduced a capture flow from three active prompt locations to one skill, while shrinking the profile prompt and making ACK behavior deterministic. The important lesson is not the exact file count; it is the separation of concerns:

- `SOUL.md`: identity, routing, and trigger references.
- Workflow skill: operational truth.
- Generic skills: reusable primitives.
- Procedure files: optional human-facing docs or redirects.

## Review checklist

Before declaring a workflow consolidated:

- [ ] `SOUL.md` contains only the trigger and skill reference.
- [ ] The skill has frontmatter with version and supersedes lineage.
- [ ] The workflow has a state machine.
- [ ] Every branch has exact tool templates.
- [ ] Every failure mode has an action.
- [ ] ACK templates are deterministic.
- [ ] Generic skills are lazy-loaded, not duplicated.
- [ ] Deprecated files point to the new source of truth.
