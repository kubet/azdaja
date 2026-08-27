# Visibility listings checklist

Prepared state and submission copy. No third-party PR, directory form, email, invite request, or community post is authorized by this file.

## Gemini CLI extension gallery

Repository preparation:

- `gemini-extension.json` exists at the repository root.
- Manifest name and version are `azdaja` and `0.1.13`.
- `skills/azdaja/SKILL.md` is the discoverable agent skill.
- The GitHub topic `gemini-cli-extension` is live.

Official discovery is automatic and crawls public tagged repositories daily. The manifest landed after tag `v0.1.13`, so gallery appearance must be checked after the next tag containing the manifest. Do not claim listing before the gallery resolves it.

Install test to run when Gemini CLI is available:

```bash
HOME="$(mktemp -d)" gemini extensions link "$PWD"
```

Gemini CLI was not installed in the preparation environment, so real CLI loading remains an explicit acceptance check.

## Claude Code plugin

Repository preparation:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `skills/azdaja/SKILL.md`

`claude plugin validate .` passes. The static skill resolves `azdaja` first, accepts `az` only when `az --version` identifies Azdaja, rejects the Azure CLI collision, and prints installation guidance without downloading software automatically.

Local install acceptance:

```text
/plugin marketplace add ./
/plugin install azdaja@azdaja
```

External directory action still gated:

- Submit the official Claude plugin-directory form only after explicit authorization.
- Record the submitted URL and scan result.
- Do not claim `claude.com/plugins` listing until the public page resolves.

## skills.sh

Expected command:

```bash
npx skills add kubet/azdaja
```

Acceptance:

- The installed skill name is `azdaja`.
- No unresolved `{{BIN}}` or `{{VERSION}}` template token remains.
- Azure CLI `az` is rejected.
- An identity-proven Azdaja `az` fallback is accepted.
- No install hook, automatic download, telemetry, or publication action exists.

Do not claim skills.sh listing until the public directory resolves the repository.

## Awesome-list PRs

Prepare separate, maintainer-specific PRs. Never send one generic bulk submission.

Entry copy:

```text
[Azdaja](https://github.com/kubet/azdaja) — Rust virtual-memory layer for LLMs that keeps complete large inputs in a local evaluator and exposes bounded model-facing prompts; includes hash-bound receipts and a reproducible 50 MiB acceptance test.
```

Before opening each PR:

- Re-read the target repository's contribution rules.
- Place the entry in the narrowest matching category.
- Preserve its punctuation and alphabetical conventions.
- Link `BENCHMARKS.md` only when the list accepts secondary links.
- Do not mention stars, launch timing, or an unmeasured benchmark win.

Opening third-party PRs requires separate explicit authorization.

## Console.dev beta note

Draft subject:

```text
Beta submission: Azdaja v0.1.13 — bounded LLM analysis over 50 MiB inputs
```

Draft body:

```text
Azdaja is an MIT-licensed Rust CLI that keeps complete large UTF-8 inputs in a local Monty/Python evaluator while exposing a bounded model-facing surface.

The v0.1.13 release includes a reproducible provider-free acceptance test over three exact 52,428,800-byte inputs, one root turn each, zero child calls, and a root prompt below 65,536 bytes. Public receipts, limitations, and reproduction commands are collected at:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

Release:
https://github.com/kubet/azdaja/releases/tag/v0.1.13
```

Sending email requires separate explicit authorization.

## Lobsters

- Request an invite only through the site's current documented route.
- Read current self-promotion requirements before posting.
- Use the `show` tag and lead with engineering tradeoffs.
- An invite request and any post are external communication and require separate authorization.

## Homebrew

Do not submit to Homebrew core yet. The repository does not currently satisfy the self-submission popularity gate documented in the launch research. A dedicated tap can be prepared later after the release and crates.io paths stabilize.

## Completion ledger

| Surface | Repository-ready | External action | Public listing verified |
|---|---:|---:|---:|
| Gemini CLI | yes | topic added | no |
| Claude plugin | yes | not submitted | no |
| skills.sh | yes | not submitted | no |
| Awesome lists | copy ready | no PR opened | no |
| Console.dev | email ready | not sent | no |
| Lobsters | checklist ready | no invite requested | no |
