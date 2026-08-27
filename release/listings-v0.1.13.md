# Visibility submissions for Azdaja v0.1.13

Status: passive surfaces are live. Drafts below are prepared only. Do not submit a form, open a pull request, send email, or request an invite without explicit owner approval.

## Live passive surfaces

- [x] Public release: https://github.com/kubet/azdaja/releases/tag/v0.1.13
- [x] README leads with the 52,428,800-byte acceptance proof and public demo GIF.
- [x] Claude marketplace and plugin manifests are on `main`.
- [x] `npx skills add kubet/azdaja --yes` installs exactly one static `azdaja` skill at version 0.1.13.
- [x] `gemini-extension.json` is at the repository root.
- [x] GitHub topic `gemini-cli-extension` is present for Gemini gallery crawling.
- [x] Repository topic `agent-skills` remains present.

## Claude plugin directory

Official submission documentation: https://claude.com/docs/plugins/submit

Submission forms:

- Claude.ai: https://claude.ai/admin-settings/directory/submissions/plugins/new
- Console: https://platform.claude.com/plugins/submit

Prepared fields:

- Plugin name: `azdaja`
- Repository: `https://github.com/kubet/azdaja`
- Version: `0.1.13`
- Description: `Virtual memory for language models with a bounded model-facing surface`
- License: `MIT`
- Validation evidence: `claude plugin validate .` and direct manifest validation both pass.
- Installation evidence: an isolated Claude Code 2.1.247 home added the local marketplace and installed `azdaja@azdaja` version 0.1.13 as enabled.
- Security note: the plugin contains a skill, no MCP server, no hook, no monitor, no automatic installer, and no network action. The skill identity-checks `azdaja` or `az` before use and rejects the Azure CLI collision.

Pre-submit checks:

- [ ] Owner accepts Anthropic's directory terms and policy.
- [ ] Owner selects the Claude.ai or Console organization used for submission.
- [ ] Owner explicitly approves submission.

## Awesome-list pull request draft

Before opening a PR, re-check that the target list is active, accepts self-submissions, and has a matching category. Follow its exact alphabetical and formatting rules.

Title:

`Add Azdaja for bounded large-input analysis`

Body:

> Adds [Azdaja](https://github.com/kubet/azdaja), an MIT-licensed Rust tool that gives language models a bounded local Python evaluator over the retained complete input. The reproducible product test processes three exact 52,428,800-byte scenarios in one root turn each, with zero child calls and a root prompt below 65,536 bytes. Release assets, checksums, test, and receipt are public. This is a self-submission.

Checklist:

- [ ] Select at least two currently active Claude Code or agent-tool lists.
- [ ] Select one currently active OpenCode list if its scope fits.
- [ ] Reformat the entry separately for each list.
- [ ] Link the immutable v0.1.13 release or tag where the list prefers versioned evidence.
- [ ] Owner explicitly approves each PR.

## Console.dev Betas email draft

To: `hello@console.dev`

Subject: `Beta submission: Azdaja`

Body:

> Hi Console team,
>
> I would like to submit Azdaja for consideration in Betas: https://github.com/kubet/azdaja
>
> Azdaja is an MIT-licensed Rust tool that gives language models a bounded local Python evaluator over complete inputs that do not fit in one ordinary context window. v0.1.13 includes checksummed standalone binaries and a reproducible three-scenario 52,428,800-byte acceptance test. The launch claim, test, receipt, and release assets are public.
>
> Release: https://github.com/kubet/azdaja/releases/tag/v0.1.13
>
> Thanks for reviewing it.

- [ ] Re-check Console.dev's current Betas criteria.
- [ ] Owner explicitly approves sending.

## Lobsters invite request draft

> I am preparing a technical launch for Azdaja, an MIT-licensed Rust tool for bounded large-input analysis by language models. I would like to participate in Lobsters beyond posting my own project, especially around evaluation integrity, agent tooling, Rust, and constrained execution. Repository and reproducible release evidence: https://github.com/kubet/azdaja

- [ ] Re-check current invite and self-promotion norms.
- [ ] Owner explicitly approves the request.

## Publication boundary

None of the drafts above grants permission to submit. Record the destination, final text, owner approval, and resulting URL before marking any external channel complete.
