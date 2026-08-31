---
title: "Secrets Vault Integration (1Password, Bitwarden, Command Helper)"
slug: "secrets-vault-integration"
category: "guides"
tags: ["secrets", "1password", "bitwarden", "vault", "security", "configuration", "profiles"]
sources:
  - "upstream:https://hermes-agent.nousresearch.com/docs/user-guide/secrets/"
  - "upstream:https://hermes-agent.nousresearch.com/docs/user-guide/secrets/onepassword"
  - "upstream:https://hermes-agent.nousresearch.com/docs/user-guide/secrets/bitwarden"
  - "upstream:https://github.com/NousResearch/hermes-agent/issues/36949"
last_updated: "2026-08-31"
version: 1
hermes_version_min: "0.19.0"
---

# Secrets Vault Integration (1Password, Bitwarden, Command Helper)

How to pull API keys into Hermes from an external secret manager at process startup, instead of keeping them in plaintext inside `~/.hermes/.env`. The bootstrap token for the secret manager lives in `.env`; every other provider key (OpenAI, Anthropic, OpenRouter, etc.) stays in the manager and rotates centrally.

The `SecretSource` interface landed in Hermes Agent **0.19.0**. The command-helper source, `preserve_existing`, and profile aliasing landed in **0.20.0**. OS-keychain encryption for stored secrets is opt-in from **0.20.6**.

## When to use a vault source

**Good fit:**

- Multi-machine fleets, shared dev boxes, gateway VPSes — anywhere you want centralized rotation and revocation across multiple Hermes installations.
- Profile fleets sharing one vault with per-profile overrides (see [Profiles and shared vaults](#profiles-and-shared-vaults)).

**Poor fit:**

- Single-machine personal setups where `~/.hermes/.env` is fine — you trade one credential for another and add a network dependency at startup.
- Air-gapped environments that cannot reach the vault's API.
- CI/CD where a secrets-injection mechanism (GitHub Actions secrets, platform Vault) is already set up — pick one path, not two.

## 1Password

Auth is whatever your `op` CLI already uses: a **service-account token** (`OP_SERVICE_ACCOUNT_TOKEN`, headless; also auto-loaded from a gitignored `~/.hermes/.op.env` so cron/launchd/Docker work) or a desktop/interactive session.

### Setup

```bash
hermes secrets onepassword setup    # verify op, set account/token env var, enable
```

### CLI surface

| Command | What it does |
|---|---|
| `hermes secrets onepassword setup` | Verify `op`, set account / token env var, enable |
| `hermes secrets onepassword status` | Show config, binary, auth, and configured references |
| `hermes secrets onepassword token` | Rotate the service-account token: validate with `op whoami`, then store it in `.env` |
| `hermes secrets onepassword set ENV_VAR "op://…"` | Map an env var to a reference (stored stripped + validated) |
| `hermes secrets onepassword remove ENV_VAR` | Drop a mapping |
| `hermes secrets onepassword sync` | Dry-run: resolve references now and show what would apply |
| `hermes secrets onepassword sync --apply` | Resolve and export into the current shell's environment |
| `hermes secrets onepassword disable` | Flip `enabled: false`; leaves mappings in place |

### Configuration

```yaml
secrets:
  onepassword:
    enabled: false
    env:
      OPENAI_API_KEY: "op://Private/OpenAI/api key"
      ANTHROPIC_API_KEY: "op://Private/Anthropic/credential"
    account: ""
    service_account_token_env: OP_SERVICE_ACCOUNT_TOKEN
    binary_path: ""
    cache_ttl_seconds: 300
    override_existing: true
```

### Security notes

- A 1Password service-account token can read **every secret the account has access to**. Store it in `~/.hermes/.env` (not `config.yaml`), and revoke + regenerate from 1Password if it leaks.
- Explicit `op://` bindings win contested vars over bulk project dumps; conflicts are warned, and every credential is labelled with its source (setup flows and `hermes model` show `(from 1Password)`).

## Bitwarden Secrets Manager

Uses a **machine account** with read access to a project. The access token (starts with `0.`) is the only secret stored in `.env` as `BWS_ACCESS_TOKEN`. At startup Hermes calls `bws secret list <project_id>` and sets the returned keys into `os.environ`. The secret **Name** becomes the environment variable name — use `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, etc.

The `bws` binary is auto-downloaded into `~/.hermes/bin/` on first use — no `apt`, no `brew`, no `sudo`. Secrets Manager is included on the Bitwarden free tier with limits.

### Setup

```bash
hermes secrets bitwarden setup
```

The wizard downloads and verifies `bws v2.0.0`, prompts for the access token (hidden input), asks for the region (US Cloud / EU Cloud / self-hosted URL → `secrets.bitwarden.server_url`), lists visible projects, test-fetches, and flips `secrets.bitwarden.enabled: true`.

Non-interactive:

```bash
hermes secrets bitwarden setup \
  --access-token "$BWS_ACCESS_TOKEN" \
  --server-url https://vault.bitwarden.eu \
  --project-id <project-uuid>
```

### CLI surface

| Command | What it does |
|---|---|
| `hermes secrets bitwarden setup` | Interactive wizard |
| `hermes secrets bitwarden status` | Config + binary version + token presence/validation |
| `hermes secrets bitwarden token` | Rotate the access token |
| `hermes secrets bitwarden sync` | Dry-run pull |
| `hermes secrets bitwarden sync --apply` | Pull and export into the current shell |
| `hermes secrets bitwarden install` | Just download the pinned `bws` binary |
| `hermes secrets bitwarden disable` | Flip `enabled: false`; leaves token + project id |

By default Bitwarden **overrides** values already in the environment (`override_existing: true`) so the vault is the source of truth — rotate once in the web app and every Hermes process picks it up on next start. Flip to `false` if you want `.env` to win.

Machine accounts cannot be 2FA-gated (no human in the loop); treat the token as a high-value bearer token.

## Command helper (any CLI vault)

For vaults without a native source — `keepassxc-cli`, `secret-tool`, `pass`, custom scripts — the command-helper source runs a user-configured helper that prints `KEY=VALUE` lines. It composes with all other vault sources. See the [official command-helper docs](https://hermes-agent.nousresearch.com/docs/user-guide/secrets/command).

## Multiple sources at once

You can enable more than one source — e.g. a team Bitwarden project alongside a personal 1Password vault. Sources compose per env var with a deterministic precedence ladder:

1. **Your `.env` / shell wins by default.** A source only replaces a pre-existing value when its own `override_existing: true` is set (Bitwarden defaults to true).
2. **Mapped sources beat bulk sources.** A source with an explicit `env:` map (1Password) outranks one injecting a whole project implicitly (Bitwarden), regardless of ordering.
3. **First source wins.** Within the same shape, the order of the optional `secrets.sources` list (or registration order) decides. Later claims on an already-claimed var are skipped with a startup warning — never silently.

`override_existing` never lets one source overwrite a var another source already claimed, and **no source can ever overwrite another source's bootstrap token** (e.g. `BWS_ACCESS_TOKEN`).

```yaml
secrets:
  sources: [bitwarden, onepassword]   # optional explicit ordering
  bitwarden:
    enabled: true
    project_id: "..."
  onepassword:
    enabled: true
    env:
      OPENAI_API_KEY: "op://Private/OpenAI/api key"
```

## Profiles and shared vaults

Two orchestrator-level knobs make one shared vault safe across profiles:

- **`secrets.preserve_existing`** — env var names whose existing `.env` / shell value always wins, even against `override_existing: true`. Use for per-profile platform secrets that intentionally differ while everything else rotates centrally:

  ```yaml
  secrets:
    preserve_existing: [FEISHU_APP_SECRET, TELEGRAM_BOT_TOKEN]
  ```

- **Profile aliasing** (on by default; `secrets.profile_alias: false` to disable) — when Hermes runs under a named profile, a vault secret named `FOO_<PROFILE>` (credential-shaped suffixes only: `*_API_KEY`, `*_TOKEN`, `*_SECRET`, `*_KEY`, `*_PASSWORD`) also hydrates the canonical `FOO`. Store `TELEGRAM_BOT_TOKEN_MILLA` in the shared project and the `milla` profile's adapters — which read the fixed name `TELEGRAM_BOT_TOKEN` — get the right value automatically. A var supplied directly under its canonical name always beats an alias.

Both knobs live in the orchestrator, so they apply to every source — bundled and plugin.

## Writing your own backend

Third-party secret managers ship as **standalone plugins**, not core PRs. A backend subclasses `agent.secret_sources.base.SecretSource` (one required method: `fetch(cfg, home_path) -> FetchResult`) and registers via `ctx.register_secret_source(MySource())` in the plugin's `register(ctx)`. The orchestrator owns precedence, conflict handling, timeouts, and provenance — the source only fetches. The bundled set is deliberately closed (same policy as memory providers): Bitwarden, 1Password, and the command helper ship in-tree; everything else (Infisical, Proton Pass, HashiCorp Vault, AWS Secrets Manager, OS keystores) belongs in plugin repos.

See [Building a Secret Source Plugin](https://hermes-agent.nousresearch.com/docs/developer-guide/secret-source-plugin).

## Gotchas

- **Inline SecretRef limits**: `${file:...}`, `${vault:...}`, `${bitwarden:...}` are **not** resolved inline in `config.yaml` — external secret backends inject values into the environment at startup via the `secrets:` block, so reference them as `${env:NAME}` (or plain `${NAME}`) instead. `${env:VAR}` and `${VAR}` are equivalent (Cursor-style parity).
- **Bootstrap token protection**: the vault's own access token is protected — no source may overwrite it. If you rotate it, use `hermes secrets <source> token`.
- **Resolution timing**: secrets resolve at process startup, after `~/.hermes/.env` loads. A cron job or gateway restart picks up rotations; a long-running process does not until restart.
- **Secret-source env vars reach stdio MCP servers** (0.20.0+) — vault-injected keys are available to MCP server processes, scoped per profile home.

## Related docs

- [Hermes Agent 0.19–0.20 Release Wave Reference](../reference/hermes-019-020-release-wave.md)
- [Provider Authentication Reference](../reference/provider-authentication.md)
- [OAuth Credential Separation in Hermes](../concepts/oauth-credential-separation.md)
