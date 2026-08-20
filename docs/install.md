# Install edge cases and lifecycle details

## Compatibility preflight

The standalone installer accepts Apple Silicon macOS 11 or newer and x86-64 Linux with glibc 2.35 or newer. On Linux, it parses `getconf GNU_LIBC_VERSION` and refuses musl, an older glibc, a missing `getconf`, or an invalid result before download or mutation under `HOME`. Use a newer glibc host or build with Rust 1.95 when that preflight fails.

A set `XDG_CONFIG_HOME`, `XDG_STATE_HOME`, or `XDG_DATA_HOME` must be absolute. Empty or relative XDG config and state values fall back to the corresponding absolute `HOME` paths; an invalid data root fails closed.

## Harness discovery and reload

Supported harness names are `jcode`, `claude`, `codex`, `gemini`, `opencode`, and `all`. The curl route requires at least one detected harness and exits before download when none is present. Detection examines harness directories and `PATH`, not configuration contents.

`JCODE_HOME` is authoritative when set and must be an absolute path. After installation, run the exact shell-quoted managed-binary `doctor` command printed on output line three. Then reload an existing Jcode registry with `skill_manage reload_all` or `/skills` → `Reload all`, or start a fresh harness session.

`doctor --harness NAME` checks the managed files on disk without invoking a model. An unqualified `doctor` runs the configured route canary.

## Command names, paths, and configuration

The curl route creates the relative `az -> azdaja` alias only when no `az` command already resolves on `PATH`. It never replaces a foreign command such as Azure CLI. When install reports `short alias skipped`, use `azdaja`.

If the binary directory is off `PATH`, the printed next step uses its absolute shell-quoted path. Paths with spaces, Unicode, and apostrophes are supported.

Standalone configuration uses adjacent `azdaja-config.toml` and `azdaja-config.toml.managed` files. An unrelated `config.toml` is never changed. Explicit `AZDAJA_HOME` and `AZDAJA_CONFIG` values must be nonempty absolute paths.

## Cargo route

Cargo installs the canonical binary but no short alias or harness skill. Complete setup with `azdaja install` for detection or `azdaja install --harness NAME`, then run the managed doctor command that installation prints. Remove managed skills before `cargo uninstall azdaja`.

## Safe removal

`uninstall --harness` removes selected skills and keeps the standalone files. `uninstall --standalone` removes only curl-owned standalone surfaces and keeps skills. `uninstall --all` selects both.

Every multi-target removal validates all selected paths before deletion. Changed managed binaries or skills, unknown files, symlinks, hardlinks, incomplete ownership state, and foreign documents cause refusal before selected mutation. A user-edited harness `config.toml`, foreign `az`, and unrelated neighboring files remain untouched.

Selected files move to same-filesystem quarantine before commit. A late failure restores them; concurrent lifecycle operations serialize or fail closed. Standalone modes refuse an unmanaged Cargo executable and direct the user to the Cargo removal sequence.
