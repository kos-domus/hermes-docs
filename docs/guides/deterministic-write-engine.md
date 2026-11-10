---
title: "Deterministic Write Engine for Untrusted-Input Agents"
slug: "deterministic-write-engine"
category: "guides"
tags:
  - security
  - least-privilege
  - automation
  - gmail
  - oauth
  - testing
  - mutation-testing
  - shadow-mode
sources:
  - "sessions/2026-11-09-residui-sicurezza-e-disegno-scrittura-email.md"
last_updated: "2026-11-10"
version: 1
hermes_version_min: "0.23.0"
---

# Deterministic Write Engine for Untrusted-Input Agents

The companion pattern to [Build a Hardened Read-Only Agent](hardened-read-only-agent.md): when an agent that reads untrusted content (an inbox) needs to *modify* that content — label it, archive it, trash it — do not give the write power to the LLM. Run writes through a **deterministic engine with no model in the loop**, under its own Unix user and its own OAuth credential.

The core discovery from the reference build: **separating the write power from the model is simpler than defending it.** With no LLM on the write path, a hostile email cannot order a write — most of the confirmation machinery of the first design (elicitation flows, server-generated approval cards) became unnecessary and was dropped.

## Architecture: two paths, two credentials

| Path | Engine | Credential | Scope |
|---|---|---|---|
| Read | LLM agent + MCP stdio server | Agent-side OAuth | `gmail.readonly` |
| Write | Deterministic rules engine, no LLM | Own OAuth, owned by a dedicated Unix user | Grant exactly what the engine needs |

Rules read **only** an allowlist of labels and headers. Message bodies never reach the decision function.

## Scope reality: the boundary is the token owner, not the scope name

`gmail.modify` also permits sending and reading. Gmail scope names do not isolate actions, so *"give the write engine a modify-only scope"* is not a boundary. The boundary that actually holds is **which process owns the token**: the deterministic engine's credential lives under its dedicated Unix user and nothing else can use it. See [OAuth Credential Separation](../concepts/oauth-credential-separation.md).

## Guard-first rule evaluation

Global guards run **before** any positive rule:

- Protected labels are never touched.
- A minimum message age (from `internalDate`, not a client-parsable header) must pass.
- `CATEGORY_UPDATES` (transactional mail) is never eligible.

When a rule does not clearly match, **the mail stays in the inbox** — the tie always goes to no-action.

## Rollout: read-only first, write permission only after gates

The first tranche is entirely read-only, in this order:

1. **Census** — measure the mailbox (label distribution, ages, volumes).
2. **Rules** — draft the routing configuration.
3. **Sample** — run the engine over a sample in **shadow mode** (decide, don't act).
4. **Gates** — only after the pre-registered pass criteria hold does the engine receive write permission, one action type at a time (labels and archive; trash only with human confirmation).

### Fix gate thresholds before collecting samples

Decide the pass threshold **before** the sample exists, or the sample silently drives the criteria. With zero errors observed, the one-sided 95% upper bound on the true error rate is ~1.98% at n=150 and ~0.99% at n=300 — and the bound is only valid if the sampled data did not drive changes to the version being tested.

### Restrictions must not cost as much as extensions

If adding a protected domain triggers the same heavy gates as removing one, you have made the *safest* modification the most annoying one. Make gate cost asymmetric: cheap for restrictive changes, expensive for permissive ones.

## Verification

### Mutation-test the rules engine

Make the classifier a **pure function** with a closed-enum outcome (`classify(meta, cfg) -> action`), verified only against **synthetic metadata**. Then test the test: alter the source in N places — a guard removed, a threshold changed, a domain comparison loosened — and require **every alteration to fail at least one check**. Reference result: 17 alterations, 17/17 detected. If a mutant survives, the test suite has a hole, not the code.

### Count violations explicitly

An aggregate verification that treats an *empty* outcome list as failure will report red on a perfectly clean run. The check must count violations explicitly: zero violations = pass.

### Adversarial corpus with a negative control

When the engine touches message content (e.g. HTML parsing before classification), test with an adversarial corpus up to extreme sizes and **run the same corpus against the old implementation as a negative control** — the old code must fail. See [MCP Server Errors](../troubleshooting/mcp-errors.md) for the parser case.

## Honest guarantees and damage caps

A cross-provider review (red team + PM from a different vendor than the implementer's) caught an error in the *guarantee*, not in the code: an approval collected via a Telegram bot was documented as resistant to bot compromise. It is not — **the bot attests its own consent**, so a compromised bot can approve anything. Two rules fall out:

- Declare guarantees for what they are; a channel that self-attests consent provides no resistance to its own compromise.
- Limit damage with **caps** (rate limits, bounded action sets) instead of relying on the approval channel's integrity.

When the reviewer's sandbox cannot access the files (e.g. the sandbox runtime does not start on that host), pass the plan inline and **declare the limitation in the review log** — a constrained review is still useful, an overstated one is not.

## Isolation cutover checklist

Moving an existing agent to a dedicated user/credential is not just config editing:

- **Removing a sudoers rule does not revoke already-running processes.** An isolation cutover must also *stop the live MCP servers* launched under the old rule.
- When exclusive control of the token cannot be demonstrated (old copies may exist), **redo the OAuth grant** rather than reusing the credential.

## Open items from the reference build

- Coverage thresholds for choosing between the deterministic engine and Gmail's native filters were fixed without data; the census is expected to revise them.
- A local model for genuinely ambiguous cases is deferred until a measurable queue of such cases exists.

## Related docs

- [Build a Hardened Read-Only Agent (Isolated MCP Pattern)](hardened-read-only-agent.md)
- [OAuth Credential Separation in Hermes](../concepts/oauth-credential-separation.md)
- [MCP Server Errors](../troubleshooting/mcp-errors.md)
