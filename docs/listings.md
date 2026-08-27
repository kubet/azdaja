# Visibility listings checklist

Verified preparation, public-install evidence, and submission receipts. This file does not authorize future third-party PRs, directory forms, email, invite requests, or community posts beyond the actions explicitly recorded below.

## Gemini CLI extension gallery

Repository preparation:

- `gemini-extension.json` exists at the repository root.
- Manifest name and version are `azdaja` and `0.1.14`.
- `skills/azdaja/SKILL.md` is the discoverable agent skill.
- The GitHub topic `gemini-cli-extension` is live.

Official discovery is automatic and crawls public tagged repositories daily. Tag `v0.1.14` is the first release intended to contain the root manifest. Gallery appearance must still be checked after the crawler processes that tag; do not claim listing before the public gallery resolves it.

Provider-free load acceptance used the official Gemini CLI 0.57.0 through `npx` in an isolated `HOME`:

```bash
tmp="$(mktemp -d)"
HOME="$tmp" npx -y @google/gemini-cli extensions link "$PWD" --consent
HOME="$tmp" npx -y @google/gemini-cli extensions list
```

The real CLI linked and enabled `azdaja (0.1.14)`, exposed the `azdaja` agent skill, and listed the repository path as a linked extension. No authentication or model inference was performed.

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

Public marketplace install acceptance also passed from an isolated `HOME`:

```text
claude plugin marketplace add kubet/azdaja
claude plugin install azdaja@azdaja
```

Claude cloned the public repository, validated the marketplace, and installed `azdaja@azdaja` at user scope.

External directory action still gated:

- Submit the official Claude plugin-directory form only after explicit authorization.
- Record the submitted URL and scan result.
- Do not claim `claude.com/plugins` listing until the public page resolves.

The official `https://clau.de/plugin-directory` shortlink currently resolves to an authenticated Claude surface and returns HTTP 403 without a browser session. No directory submission receipt exists.

## skills.sh

Expected command:

```bash
npx skills add kubet/azdaja
```

The public directory page at <https://www.skills.sh/kubet/azdaja> returns HTTP 200. A clean public install completed and rendered the Azdaja skill for its supported targets with no unresolved `{{BIN}}` or `{{VERSION}}` tokens; the Claude target symlink resolved to the installed skill.

Acceptance:

- The installed skill name is `azdaja`.
- No unresolved `{{BIN}}` or `{{VERSION}}` template token remains.
- Azure CLI `az` is rejected.
- An identity-proven Azdaja `az` fallback is accepted.
- No install hook, automatic download, telemetry, or publication action exists.

The public skills.sh listing and install path are verified. Directory ranking or future crawler state is not treated as a product claim.

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

Opening any additional third-party PR requires a fresh rules check.

Submitted listing PRs:

- [awesome-opencode/awesome-opencode#650](https://github.com/awesome-opencode/awesome-opencode/pull/650) adds `data/projects/azdaja.yaml`; all 230 repository YAML files passed `npm run validate` before submission.
- [ccplugins/awesome-claude-code-plugins#404](https://github.com/ccplugins/awesome-claude-code-plugins/pull/404) adds Azdaja to the English and Chinese marketplace sections.

The primary `hesreallyhim/awesome-claude-code` list explicitly forbids PR submissions and requires a human-created web UI issue form. Azdaja satisfies its 14-day active-development threshold, but no automated recommendation was filed.

## Console.dev beta note

Draft subject:

```text
Beta submission: Azdaja v0.1.14 — bounded LLM analysis over 50 MiB inputs
```

Draft body:

```text
Azdaja is an MIT-licensed Rust CLI that keeps complete large UTF-8 inputs in a local Monty/Python evaluator while exposing a bounded model-facing surface.

The v0.1.14 release includes a reproducible provider-free acceptance test over three exact 52,428,800-byte inputs, one root turn each, zero child calls, and a root prompt below 65,536 bytes. Public receipts, limitations, and reproduction commands are collected at:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

Release:
https://github.com/kubet/azdaja/releases/tag/v0.1.14
```

The current Console.dev criteria accept pre-1.0 developer-tool betas, so v0.1.14 is eligible for consideration. Sending remains blocked until an authorized mail account is connected; no email receipt exists.

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
| Gemini CLI | yes; official CLI link passed | topic added | no gallery claim |
| Claude plugin | yes; public marketplace install passed | directory form auth-gated | no directory claim |
| skills.sh | yes; public install passed | automatic discovery | yes |
| Awesome lists | two validated PRs open | [OpenCode #650](https://github.com/awesome-opencode/awesome-opencode/pull/650), [Claude plugins #404](https://github.com/ccplugins/awesome-claude-code-plugins/pull/404) | pending review |
| Console.dev | eligible copy ready | sender connection required | no |
| Lobsters | checklist ready | no invite requested | no |
