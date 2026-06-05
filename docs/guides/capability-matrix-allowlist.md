---
title: "Capability Matrix Allowlist (Data-Not-Prosa Derogations)"
slug: "capability-matrix-allowlist"
category: "guides"
tags: ["security", "profiles", "self-improvement", "configuration", "mcp"]
sources:
  - "sessions/2026-06-04-selfimprove-fleet-learner-tier1-fabric-spike.md"
last_updated: "2026-06-05"
version: 1
hermes_version_min: "0.14.0"
---

# Capability Matrix Allowlist

A **capability matrix** is a deploy-only YAML file that lists the exact paths an agent is allowed to read, and the exact path patterns it must never read. The point is that the agent itself cannot widen the list: the file is data, not prose, and it is hash-protected alongside the rest of the immutable prompt.

This guide shows how to wire a capability matrix for a profile that needs **scoped read derogations** — for example a Fleet Learner that must read another profile's procedural root, but should not be able to read client folders.

## Why data, not prose

You can write "you may read `/home/kos/.hermes/profiles/kos/SOUL.md`" in plain English inside `SOUL.md`. The problem is that the same prompt that contains this rule also tells the agent how to interpret it. A persuasive context (a clever session log, a tool output, a long conversation) can talk the agent into reading outside the line.

A YAML file at `state/capability-matrix.yaml` chmod `0444` deploy-only solves this in three ways:

1. **The agent cannot edit the file.** The shell permissions deny write to the runtime user. Editing requires a deploy step (root or sudo).
2. **The matrix is hashed as an immutable section.** Any tampering shows up at the next `immutable-check.sh --verify`.
3. **Tools that consume the matrix can be deterministic.** A wrapper around `read_file` can hard-check the path against `read_roots` and `read_deny` without asking the LLM.

This is what preserves the non-drift invariant: the derogation is **data the operator owns**, not prose the agent interprets.

## File layout

```yaml
# state/capability-matrix.yaml
# Permissions: chmod 0444, owned by root or a deploy user.
# Edits require a deploy step, not a runtime write.

profile: hermes-selfimprove

read_roots:
  # Tier-1 derogation: read the public procedural root of the kos profile
  - /home/kos/.hermes/profiles/kos/SOUL.md
  - /home/kos/.hermes/profiles/kos/procedures
  - /home/kos/.hermes/profiles/kos/skills

read_deny:
  # Glob patterns — deny wins over allow
  - "**/request_dump_*.json"
  - "**/.env"
  - "**/.env.*"
  - "**/secrets.env"

# Invariant: cross-profile writes are denied unconditionally.
# This is enforced by the SOUL immutable section, not by this matrix.
write_deny_cross_profile: true
```

### `read_roots`

A list of absolute paths the profile is allowed to read. Both files and directories are valid entries. A directory entry grants recursive read access to everything under it.

### `read_deny`

A list of glob patterns. Any path matching a deny pattern is rejected, **even if it sits under a `read_roots` entry**. Use this to carve sensitive files out of broader allow trees.

The pattern syntax is the same as `.gitignore`: `**/` matches any number of directories, `*` matches anything except `/`.

### `write_deny_cross_profile`

Set to `true`. Cross-profile writes are already denied by the SOUL immutable section; this flag exists so the matrix records the invariant explicitly. The matrix is the single source of truth a tool can read without parsing prose.

## Wiring it into the SOUL

The SOUL keeps a **pointer** to the matrix, not a duplicate of the rules:

```markdown
## Read permissions

This profile's read permissions are defined in
`state/capability-matrix.yaml`. The allowlist is data; this section
does not duplicate it. If a tool reports "outside allowlist", do not
attempt to widen the matrix from within the runtime — escalate.
```

This wording matters. A longer prose version invites the agent to negotiate. The pointer is short on purpose.

## Re-baseline after edit

When you (the operator) legitimately edit the matrix, you must re-baseline the immutable section that records its hash:

```bash
immutable-check.sh --profile hermes-selfimprove --init --force
immutable-check.sh --profile hermes-selfimprove --verify
```

`--init --force` rewrites the baseline. `--verify` reports green only if the new hash matches and every *other* immutable section is unchanged. This is what catches a "while you were editing the matrix, you also accidentally rewrote the security policy" mistake.

A correct re-baseline produces output like:

```text
Section capability-matrix   : CHANGED (operator-initiated)
Section security-policy     : UNCHANGED
Section patch-protocol      : UNCHANGED
Section permissions-model   : UNCHANGED
Section redaction-rules     : UNCHANGED
VERDICT: green
```

If two sections show as changed and you only intended one, abort and investigate.

## MCP filesystem sandbox: narrow it to match

The matrix governs tools that *respect* it. The `filesystem` MCP server has its own enforcement layer: its `allowedDirectories` setting is a **hard sandbox** the LLM cannot widen at all. Keep the two in sync:

```yaml
# config.yaml — MCP server entry for filesystem
mcp:
  filesystem:
    enabled: true
    config:
      allowedDirectories:
        # Match the capability matrix read_roots for this profile
        - /home/kos/.hermes/profiles/kos
        # Add profile-local paths the agent actually needs
        - /home/kos/job-desk/hermes
        - /home/kos/job-desk/openclaw-docs
        - /home/kos/job-desk/hermes-docs
        # ...explicit allow list, no client folders
```

If the MCP sandbox is *wider* than the matrix, the matrix is the weaker fence. If the MCP sandbox is *narrower* than the matrix, the matrix promises reads the agent cannot perform. Aim for parity.

A common mistake is to start with `allowedDirectories: ["~/job-desk"]` and forget that this includes every client folder under it. After onboarding a new client, the sandbox widens silently. Enumerate allowed directories explicitly; do not use a single broad root.

## Deny-glob for `request_dump_*.json`

When Hermes retries a failing request until `max_retries_exhausted`, it can dump the request body to disk. The dump can include the `Authorization` header verbatim — a **bearer token at rest**.

Always add to `read_deny`:

```yaml
read_deny:
  - "**/request_dump_*.json"
```

This is a defense-in-depth control. The right fix is to scrub and rotate the token; the deny-glob ensures the Learner does not read the dumps in the meantime.

## Audit gap: read enforcement is partial

In the current Hermes runtime (as of 0.14.x):

- The `filesystem` MCP server **hard-enforces** its `allowedDirectories`. Reads outside the sandbox are blocked at the tool layer.
- Native tools (`read_file`, `read_text_file`) are governed by SOUL instructions, which in turn point to the matrix.
- There is no `PreToolUse` hook that hard-checks the matrix against every native read.

This means the matrix is **instruction-enforced for native tools**, not **mechanically enforced**. A hard read-gate (hook + audit log) is a prerequisite for higher-tier deployments (Tier-2 private corpus, Tier-3 family), not for Tier-1.

To verify the matrix is being respected in Tier-1, you currently have to:

- inspect the Learner's tool-call transcript in `state.db` (note: this requires `sqlite3`, may be locked by the running gateway, and the schema is not stable across Hermes versions), or
- run a smoke-test session with a deliberately-out-of-allowlist target and confirm the Learner refuses.

## When to use this pattern

| Situation | Use a capability matrix? |
|---|---|
| A Fleet Learner reads another profile's procedural root | Yes — Tier-1 minimum |
| A generation agent reads only its own profile | Not needed — `read_roots` defaults to the profile dir |
| An agent reads client folders | Yes, with per-client entries and explicit deny-globs for secrets |
| An agent needs to write across profiles | **No.** Cross-profile writes are denied unconditionally; redesign the flow. |

## Related docs

- [Self-Improvement Agent Safety](../concepts/self-improvement-agent-safety.md)
- [Fleet Learner Architecture](../concepts/fleet-learner-architecture.md)
- [MCP Server Setup](../reference/mcp-server-setup.md)
- [MCP Errors](../troubleshooting/mcp-errors.md)
