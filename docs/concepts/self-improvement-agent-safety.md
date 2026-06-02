---
title: "Self-Improvement Agent Safety"
slug: "self-improvement-agent-safety"
category: "concepts"
tags: ["self-improvement", "security", "profiles", "cron", "prompting", "skills", "scripts"]
sources:
  - "sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md"
  - "sessions/2026-06-01-cron-script-containment-fix.md"
last_updated: "2026-06-02"
version: 2
hermes_version_min: "0.14.0"
---

# Self-Improvement Agent Safety

A self-improvement profile is an agent that reviews logs, notes, prompts, and skills, then proposes or applies changes to its own operating system. This can be powerful, but it is also one of the easiest ways to create prompt drift, memory poisoning, and unsafe automation.

This concept doc captures safety constraints from a multi-specialist review of a large Hermes master prompt.

## Main risks

| Risk | Why it matters |
|---|---|
| Self-classification loophole | The agent may decide a risky patch is safe because the same prompt tells it how to judge safety |
| Retrieval prompt injection | Notes, docs, or web snippets can contain instructions that target the agent's patching behavior |
| LLM-only redaction | A model deciding whether a secret is safe to write is not a deterministic security gate |
| Cron auto-patch drift | Daily automated edits can compound small mistakes into a broken operating prompt |
| Environment propagation | Broad `env_passthrough` can expose credentials to tools or child processes unnecessarily |
| Vault ownership confusion | A self-improvement agent can accidentally restructure user-owned knowledge bases |

## Safer architecture

Use a dedicated profile instead of adding self-improvement duties to a production assistant profile.

```text
hermes-selfimprove profile
  ├── env_passthrough: []
  ├── advisory mode by default
  ├── immutable prompt sections with SHA256 checks
  ├── gitleaks pre-write/pre-commit gate
  ├── patch log with auto-revert window
  └── skills/
      ├── memory-governance
      ├── obsidian-curation
      ├── self-improvement
      └── output-contracts
```

## Recommended controls

### 1. Advisory mode first

Run the profile in advisory mode for at least a shadow period before allowing controlled writes. During shadow mode it can propose patches, but another actor reviews and applies them.

### 2. Immutable sections

Mark safety-critical sections as immutable and verify their hash before each run.

Examples:

- security policy
- patch protocol
- permissions model
- redaction rules
- cron behavior

If a hash changes unexpectedly, the run should stop and report drift.

### 3. Deterministic secret scanning

Run `gitleaks` before any patch is committed or shipped:

```bash
gitleaks dir <workspace> --no-banner
```

Do not rely on the LLM to decide whether a value is a secret.

### 4. Empty environment passthrough

For the self-improvement profile, start with:

```yaml
env_passthrough: []
```

Only add specific variables after a concrete need is proven.

### 5. Patch ledger and auto-revert

Persist proposed changes as patch records:

```text
~/job-desk/hermes/patches/YYYY-MM-DD-NN-<slug>.md
```

Include:

- before/after summary
- touched files
- risk class
- validation commands
- revert command
- expiry or review date

For experimental prompt changes, default to a seven-day auto-revert unless confirmed useful.

### 6. Conditional operating loop

Do not run heavy self-critique on trivial messages. Gate second-pass review to:

- output longer than a threshold, such as 500 tokens
- file writes
- security-sensitive changes
- user-visible scheduled reports

### 7. Metrics-triggered review

Daily review without input creates noise. Prefer metric-triggered or weekly review based on observable signals:

- failed cron runs
- gateway errors
- repeated user corrections
- stale skills
- broken links
- failed validation commands

### 8. Cron script containment

Script-based maintenance jobs should keep their declared Hermes entrypoint inside the profile's local `scripts/` directory. If a self-improvement profile needs to run a canonical script maintained elsewhere, use a short real wrapper file inside containment that `exec`s the canonical script.

This avoids two unsafe extremes:

- symlink escapes that Hermes can block with `Blocked: script path resolves outside the scripts directory`;
- copied script bodies that drift silently across profiles.

See [Cron Script Wrapper Pattern](../guides/cron-script-wrapper-pattern.md) and [Cron Script Execution Reference](../reference/cron-script-execution.md).

## Anti-patterns

- A 30+ section monolithic prompt that tries to encode every behavior eagerly.
- A daily cron that patches memory or skills without human review.
- Allowing retrieved notes to override the core safety policy.
- Restructuring the root of an existing Obsidian vault instead of writing to a clearly owned subdirectory.
- Treating frontmatter volume as quality.

## Practical rule

A self-improvement agent should be boring by default: read broadly, propose narrowly, write only through deterministic gates, and keep its own blast radius smaller than the system it is improving.
