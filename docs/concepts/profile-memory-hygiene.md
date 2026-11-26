---
title: "Profile Memory Hygiene and Approval Boundaries"
slug: "profile-memory-hygiene"
category: "concepts"
tags:
  - memory
  - profiles
  - security
  - approval
  - maintenance
  - concepts
sources:
  - "sessions/2026-11-25-separazione-compartimenti-samba-apparmor.md"
last_updated: "2026-11-26"
version: 1
hermes_version_min: "0.23.0"
---

# Profile Memory Hygiene and Approval Boundaries

A profile's memory is injected into every session of that profile. That makes it both
high-leverage and fragile: a bloated, duplicated, or silently regenerated memory degrades every
future run. Three failure modes and the disciplines that fix them.

## 1. Memory files have a hard budget — and can be double-pasted

The reference failure: a specialist profile's memory turned out to be another profile's memory
**pasted twice** (~29k characters against a ~2.2k budget), silently degrading every prompt of that
agent. Memory files must contain structured facts only:

- who and what the profile is (identity, scope),
- stable environment facts,
- standing conventions.

Procedures and how-to knowledge do **not** belong in memory — move them into skills, which load
only when relevant. A memory repaired this way went from 29k characters to 7 entries and passed a
recall spot-check (6/6 questions answered from the trimmed memory).

## 2. Approval-gated memory writes stay human-approved

When a profile's memory is configured with `write_approval`, changes land in a pending state until
a human approves them. Two supporting disciplines:

- A **deterministic daily reminder** (cron, no LLM in the loop) lists pending memory writes so
  they cannot rot invisibly.
- The runtime's auto-mode classifier **correctly blocks programmatic approval** of pending memory
  writes. This is a feature, not an obstacle: an agent approving its own memory changes would make
  the approval boundary decorative. Keep the approval human.

## 3. Generated blocks are regenerated — edit the source card

Some profile files contain sections **generated from a memory package** (source cards). Hand
edits inside a generated block are overwritten at the next regeneration, and the old rule comes
back. The fix is upstream of the generated file:

1. Change the **source card** that feeds the generator.
2. **Publish the updated package** so the regeneration actually picks it up.

Editing only the generated file changes nothing — it schedules the reversion.

## Related docs

- [Skill Consolidation Pattern](skill-consolidation-pattern.md)
- [Self-Improvement Agent Safety](self-improvement-agent-safety.md)
