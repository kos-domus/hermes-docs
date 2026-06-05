---
title: "Self-Improvement Agent Safety"
slug: "self-improvement-agent-safety"
category: "concepts"
tags: ["self-improvement", "security", "profiles", "cron", "prompting", "skills", "scripts", "mcp", "memory"]
sources:
  - "sessions/2026-05-27-skill-consolidation-codex-root-cause-master-prompt-review.md"
  - "sessions/2026-06-01-cron-script-containment-fix.md"
  - "sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md"
last_updated: "2026-06-05"
version: 3
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

## Fleet Learner mode

The profile does not have to learn only from its own sessions. A more powerful pattern is **Fleet Learner mode**, in which a self-improvement profile reads the public session corpus of *another* profile and proposes targeted edits to that profile's procedural memory (`SOUL.md`, `procedures/`, `skills/`).

This pattern separates the **learning role** from the **generation role**, which is the only way to get an outside-in signal on a working agent's prompt. See [Fleet Learner Architecture](fleet-learner-architecture.md) for the three-layer memory model and the targeted-edit operations.

### CSO tiered gating

Not all corpora are safe to learn from. A three-tier model works in practice:

| Tier | Corpus | Verdict | Prerequisites |
|---|---|---|---|
| Tier 1 | Public procedural root of another profile | **GO** with capability matrix + sandbox hygiene + advisory shadow | Allowlist + 0444 matrix + gitleaks + advisory mode |
| Tier 2 | Private/client folders | **HOLD** | Hard read-gate (PreToolUse hook + audit log), per-client allowlist, output segregation, denylist |
| Tier 3 | Family/personal corpus | **HOLD** | Same as Tier 2, plus explicit user sign-off on every patch |

Tier-1 is the only tier that can be enabled without a hard read-gate. The reason is blast radius: Tier-1 reads only procedural files the operator has already chosen to make public, and a misread produces a noisy patch that gets caught at review. Tier-2/3 read sensitive context where a misread is itself a leak.

### Capability matrix as data, not prose

The allowlist of paths the Learner may read should be a YAML file at `state/capability-matrix.yaml` chmod `0444`, hashed as an immutable section. The agent cannot widen it without a deploy step. The SOUL keeps a pointer to the matrix, not a duplicate of its rules.

See [Capability Matrix Allowlist](../guides/capability-matrix-allowlist.md) for the file format and re-baseline flow.

### MCP filesystem sandbox narrowing

The `filesystem` MCP server's `allowedDirectories` is a hard sandbox the LLM cannot widen. Keep it at parity with the capability matrix `read_roots`. A common drift is starting with `allowedDirectories: ["~/job-desk"]` and forgetting that this includes every client folder onboarded since.

Enumerate allowed directories explicitly. Do not use a single broad root.

### Bearer tokens at rest in `request_dump_*.json`

Hermes can dump failed request bodies to `request_dump_*.json` when `max_retries_exhausted` fires. These dumps can contain the `Authorization` header verbatim — a bearer token at rest. Always add to `read_deny`:

```yaml
read_deny:
  - "**/request_dump_*.json"
```

The deeper fix is to scrub and rotate the token; the deny-glob is defense-in-depth while that ticket is open.

### Re-baseline immutable sections after a legitimate edit

When the operator legitimately edits the capability matrix or another immutable section:

```bash
immutable-check.sh --profile hermes-selfimprove --init --force
immutable-check.sh --profile hermes-selfimprove --verify
```

`--init --force` rewrites the baseline; `--verify` reports green only if *other* sections are unchanged. Two sections changing when you intended one is the signal to abort.

### Partial read enforcement

As of 0.14.x, the capability matrix is **instruction-enforced** for native tools (`read_file`, `read_text_file`) and **mechanically enforced** for the `filesystem` MCP server. There is no `PreToolUse` hook that hard-checks the matrix against native reads yet. This makes the matrix sufficient for Tier-1 (low-blast-radius public corpus) and insufficient for Tier-2/3 (sensitive corpus), where the hard read-gate is a prerequisite.

## Anti-patterns

- A 30+ section monolithic prompt that tries to encode every behavior eagerly.
- A daily cron that patches memory or skills without human review.
- Allowing retrieved notes to override the core safety policy.
- Restructuring the root of an existing Obsidian vault instead of writing to a clearly owned subdirectory.
- Treating frontmatter volume as quality.

## Practical rule

A self-improvement agent should be boring by default: read broadly, propose narrowly, write only through deterministic gates, and keep its own blast radius smaller than the system it is improving.
