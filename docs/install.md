# Install edge cases and lifecycle details

## Compatibility preflight

The standalone installer accepts Apple Silicon macOS 11 or newer and x86-64 Linux with glibc 2.35 or newer. On Linux, it parses `getconf GNU_LIBC_VERSION` and refuses musl, an older glibc, a missing `getconf`, or an invalid result before download or mutation under `HOME`. Use a newer glibc host or build with Rust 1.95 when that preflight fails.

A set `XDG_CONFIG_HOME`, `XDG_STATE_HOME`, or `XDG_DATA_HOME` must be absolute. Empty or relative XDG config and state values fall back to the corresponding absolute `HOME` paths; an invalid data root fails closed.

## Tool discovery and reload

Supported tool names are `jcode`, `claude`, `codex`, `gemini`, `opencode`, and `all`. With no target, the curl route requires at least one detected tool and exits before download when none is present. Detection examines tool directories and `PATH`, not configuration contents. Use no target for automatic detection, as in `az install`; use a positional target only when needed, as in `az install jcode`.

The default `SKILL.md` remains the canonical execution and safety contract. Installation renders a profile for each selected tool with the same embedded managed-binary path and tool-specific routing and execution guidance. Claude also receives an always-loaded user rule at `~/.claude/rules/azdaja.md` and a managed hook plugin inside its skill directory. For complete-coverage work on a large input, the hook allows metadata checks and one structural sample of up to 10 lines and 64 KiB only through absolute trusted `/usr/bin/...` or `/bin/...` commands with literal, non-expanding paths, then blocks broader native `Read`, `Grep`, or `Bash` access until `Skill(azdaja)` succeeds. Small inputs and bounded excerpts stay unforced. The installer owns only the exact rule symlink and managed plugin files, refuses foreign entries, checks all surfaces in `doctor claude`, and removes only owned content. Restart Claude after install. Codex CLI 0.149 discovers Agent Skills from `$HOME/.agents/skills`, project/upward `.agents/skills`, project/upward `.codex/skills` from both trusted and untrusted project layers, system/admin roots, and `$CODEX_HOME/skills` when `CODEX_HOME` is set. `CODEX_HOME` must be absolute and isolates Codex config/auth, but it does not move the normal Azdaja compatibility profile away from `$HOME/.agents/skills/azdaja`. Codex skill activation is per turn: `$azdaja`, a plain skill-name request, or a task matching the narrow description can load the skill for that turn, while passive discovery, a repository name, and mere mentions are non-triggers. The managed Codex profile includes `agents/openai.yaml` with `interface.display_name`, `interface.short_description`, `interface.default_prompt`, and `policy.allow_implicit_invocation: true`, defaults to the standard conversational lane, and reserves the strict A/B benchmark/audit lane for explicit exact-schema requests. Restart Codex, or start a fresh `codex exec` invocation, after install or reinstall. `doctor codex` checks only files and effective user config, never providers; it rejects `[skills] include_instructions=false`, a managed skill disabled by `[[skills.config]]`, and any visible same-name duplicate unless that duplicate's exact absolute `SKILL.md` path is disabled by the user `$CODEX_HOME/config.toml`. OpenCode discovers Azdaja through its native `skill` tool. Its execution trigger routes only exhaustive semantic judgment over one large input and explicitly excludes repository audits, code navigation, structural searches, bounded excerpts, and small deterministic work; explicit requests to use Azdaja or confirm its availability remain awareness triggers. The standard lane uses deterministic reduction plus at most one semantic pass and returns to normal conversation; the A/B adjudication and fail-closed contract remain available only for explicit audit or benchmark work. OpenCode also searches global and project/upward Claude- and Agent Skills-compatible locations, so the managed Codex compatibility profile carries the same narrow standard/strict contract and `doctor opencode` rejects stale or foreign same-name profiles that could shadow the dedicated OpenCode copy. No OpenCode plugin blocks native tools. Reinstall every reported compatibility profile after upgrading. Reinstall a tool to reset its managed profile from the default contract.

`JCODE_HOME` is authoritative when set and must be an absolute path. After installation, run the exact shell-quoted managed-binary `doctor` command printed on output line three. Then reload an existing Jcode registry with `skill_manage reload_all` or `/skills` → `Reload all`, or start a fresh tool session.

`doctor NAME` checks that tool's managed files on disk without invoking a model. An unqualified `doctor` runs the configured route canary.

## Command names, paths, and configuration

The curl route creates the relative `az -> azdaja` alias only when no `az` command already resolves on `PATH`. It never replaces a foreign command such as Azure CLI. When install reports `short alias skipped`, use `azdaja`.

If the binary directory is off `PATH`, the printed next step uses its absolute shell-quoted path. Paths with spaces, Unicode, and apostrophes are supported.

Standalone configuration uses adjacent `azdaja-config.toml` and `azdaja-config.toml.managed` files. An unrelated `config.toml` is never changed. Explicit `AZDAJA_HOME` and `AZDAJA_CONFIG` values must be nonempty absolute paths.

## Cargo route

Cargo installs the canonical binary but no short alias or tool integration. Complete setup with `azdaja install` for detection or `azdaja install NAME` for one tool, then run the doctor command that installation prints. Remove managed integrations before `cargo uninstall azdaja`.

## Safe removal

`uninstall NAME` removes that tool integration and keeps standalone files. `uninstall standalone` removes only curl-owned standalone surfaces and keeps tool integrations. `uninstall all` removes both.

Every multi-target removal validates all selected paths before deletion. Changed managed binaries or skills, unknown files, symlinks, hardlinks, incomplete ownership state, and foreign documents cause refusal before selected mutation. A user-edited integration `config.toml`, foreign `az`, and unrelated neighboring files remain untouched.

Selected files move to same-filesystem quarantine before commit. A late failure restores them; concurrent lifecycle operations serialize or fail closed. Standalone modes refuse an unmanaged Cargo executable and direct the user to the Cargo removal sequence.
