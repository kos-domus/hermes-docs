---
title: "Fleet Learner Architecture"
slug: "fleet-learner-architecture"
category: "concepts"
tags: ["self-improvement", "multi-agent", "memory", "skills", "concepts"]
sources:
  - "sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md"
last_updated: "2026-06-05"
version: 1
hermes_version_min: "0.14.0"
---

# Fleet Learner Architecture

A **Fleet Learner** is a dedicated Hermes profile that learns from *other agents'* sessions instead of (or in addition to) its own. It is the role-based answer to the question "who watches the fleet?" — and it is the only safe way to let an LLM propose edits to procedural memory (`SOUL.md`, `procedures/`, `skills/`).

This concept doc captures the architecture used to repoint a self-improvement profile from idle to active Learner. The pattern is inspired by Quarq Agent's continual-learning design, but is implementation-agnostic: you do not need the Quarq runtime. The principles are what you steal.

## Why a dedicated Learner profile

Generation agents (`mc`, `kos`, specialist profiles) are busy producing work. Asking them to also self-edit their own operating prompt creates two failure modes:

1. **Conflict of interest**: the same prompt that runs the agent also judges whether a patch is safe.
2. **Context starvation**: a generation profile reads its own sessions, which are full of its own assumptions. There is no outside-in signal.

A Learner profile solves both:

- It runs on its own cron, with its own scope, its own immutable sections, and its own tool surface.
- It reads a **corpus** that is *not its own* — typically the public sessions of one or more generation profiles.
- It produces **targeted edits** against the procedural layer of those profiles, gated by deterministic safety controls.

## Anatomy: three memory layers

Map the Quarq three-layer model onto a Hermes profile:

| Layer | Quarq name | Hermes location | Role in the Learner loop |
|---|---|---|---|
| 1 | Semantic | `sessions/` + `memory/` | **Input only.** The Learner reads these on the target profile; it must not edit them as part of the patch loop. |
| 2 | Procedural | `SOUL.md`, `procedures/`, `skills/` | **Target of the edit.** The Learner proposes or applies patches here. |
| 3 | Episodic | Runtime tool-call transcripts, in-process state | Not durable. Useful for KPI verification but not for learning directly. |

The crucial invariant: **semantic feeds procedural, never the reverse**. A patch to `SOUL.md` does not get to retroactively edit the session log it came from.

## Edit operations: targeted-edit, not append-only

A Learner does not append facts indefinitely. It applies one of four targeted operations against each candidate change:

| Operation | When to use |
|---|---|
| `add` | New rule, new procedure, new skill section not present anywhere in the corpus |
| `update-outdated` | Existing rule is contradicted by a newer session with stronger signal |
| `dedup` | Same rule already exists in another section, file, or layer |
| `delete-contradiction` | Two rules in the same scope disagree and the newer one is canonical |

`dedup` is where most candidates die. The cross-layer check (does this rule already live in `skills/`, or in a related procedure?) eliminates roughly 80% of proposals in a mature corpus.

## Temporal-Truth: four rules

A fact's storage date is not the same as the event date. The Learner applies four rules:

1. **Storage ≠ event.** A session dated 2026-04-12 may describe a workaround that was fixed in Hermes 0.13. The fact "X fails" was true *then*. It may not be true now.
2. **Newer evidence outranks older storage.** A 2026-06-01 session overrides a 2026-04-12 memory entry, even if the memory entry was written later.
3. **Versioned facts carry their version.** A rule that depends on a specific Hermes release must record `hermes_version_min`. A rule without a version floor is treated as current.
4. **Deprecation is not deletion.** When an era ends (e.g., a migration from one agent runtime to another), the rules of that era are *deprioritized*, not erased. They may still apply to legacy artifacts.

In practice, on a mature corpus, Temporal-Truth filters out roughly 60% of candidate patches because the lessons belong to a deprecating era.

## ADD-only vs targeted-edit by layer

A common mistake is to apply the same edit policy to every layer. They are not the same.

| Layer | Edit policy | Why |
|---|---|---|
| `memory/` (facts) | ADD-only, with explicit timestamps | Facts accumulate; let temporal-truth sort them at retrieval time. Editing old facts erases evidence. |
| `SOUL.md` / `procedures/` / `skills/` (rules) | Targeted-edit (add / update-outdated / dedup / delete-contradiction) | Rules must stay coherent; an ADD-only `SOUL.md` grows past its char limit and internally contradicts itself. |
| Session logs | Read-only | History is immutable; the Learner never edits a session. |

The temptation is to make `SOUL.md` ADD-only because it feels safer. It is not — a SOUL that has accumulated every rule it ever learned is no longer a working prompt.

## Cross-layer dedup

Before proposing an `add`, the Learner must check:

1. Is the rule already in `SOUL.md` (possibly phrased differently)?
2. Is it in a `procedures/*.md` referenced by `SOUL.md`?
3. Is it in a `skills/<name>/SKILL.md` that the profile loads?
4. Is it in `memory/` as a fact?

Only if the answer to all four is "no" does the candidate become an `add`. This is the single highest-leverage filter in the loop.

## Yield is forward-looking

A repointed Learner running against an old, well-covered corpus will produce approximately zero patches on its first few runs. **This is the correct outcome.** It means:

- Temporal-Truth is doing its job (deprecating era-bound lessons).
- Cross-layer dedup is doing its job (catching rules already migrated).
- The corpus has been digested.

The value of a Learner is realized on **new sessions**, where a rule the operator had not yet articulated can be extracted, deduplicated, and proposed as a clean patch. Do not assess a Learner by its yield on the backlog. Assess it by its yield on the next two weeks of fresh sessions.

## Recommended cadence

For a single-profile Tier-1 deployment:

```cron
0 20 * * 0   hermes-learner-<profile>
```

Weekly is sufficient. Daily Learner runs against a corpus that changes slowly produce noise, not signal.

## Safety scaffolding

A Fleet Learner without scaffolding is just an LLM editing prompts. The scaffolding is non-optional:

- **Advisory mode** for a shadow period before writes are enabled.
- **Immutable sections** with SHA256 baseline checks. See [Self-Improvement Agent Safety](self-improvement-agent-safety.md).
- **Capability-matrix allowlist** (`state/capability-matrix.yaml`, deploy-only 0444) defining which paths the Learner may read. See [Capability Matrix Allowlist](../guides/capability-matrix-allowlist.md).
- **MCP sandbox narrowing** so the `filesystem` MCP server cannot reach outside the allowlist.
- **gitleaks** before any patch is committed.
- **Patch ledger** with revert commands and an auto-revert window (default 7 days for non-confirmed patches).

## What this architecture is not

- **Not RAG.** The Learner is not a retrieval-augmented chatbot. It is a patch proposer with deterministic gates.
- **Not a memory tool.** The Learner does not own the semantic layer; it only reads it.
- **Not a generation agent.** The Learner does not answer user messages. It runs on cron and produces patches (or silence).

## Related docs

- [Self-Improvement Agent Safety](self-improvement-agent-safety.md)
- [Capability Matrix Allowlist](../guides/capability-matrix-allowlist.md)
- [Skill Consolidation Pattern](skill-consolidation-pattern.md)
