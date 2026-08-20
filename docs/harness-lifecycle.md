# Harness lifecycle and custody

Azdaja manages one skill directory per supported harness:

| Harness | Managed target |
|---|---|
| Jcode | `${JCODE_HOME:-~/.jcode}/skills/azdaja` |
| Claude | `~/.claude/skills/azdaja` |
| Codex | `~/.agents/skills/azdaja` |
| Gemini | `~/.gemini/skills/azdaja` |
| OpenCode | `${XDG_CONFIG_HOME:-~/.config}/opencode/skills/azdaja` |

When `JCODE_HOME` is set, its value is authoritative for Jcode detection and every install, doctor, uninstall, snapshot, and rollback path. Explicit `JCODE_HOME`, `AZDAJA_HOME`, and `AZDAJA_CONFIG` overrides must be nonempty absolute paths. An invalid Jcode override fails before harness lifecycle mutation; invalid Azdaja state/config overrides fail before provider entry. Unset, empty, or relative `XDG_CONFIG_HOME` and `XDG_STATE_HOME` values are ignored as required by the XDG specification, falling back to the absolute `HOME` locations `~/.config` and `~/.local/state`. This prevents a working directory from becoming an implicit configuration, OpenCode, or state root. Paths containing spaces, Unicode, or apostrophes are supported; the managed install next step shell-quotes its exact binary path.

## Install and session discovery

The curl one-liner supports Apple Silicon macOS and Linux x86-64 and requires a detected Jcode, Claude, Codex, Gemini, or OpenCode harness. With none detected it exits before downloading or writing. Its `Written:` line is also the command-name boundary: use `az` only when it reports the `az -> azdaja` alias; when it reports `short alias skipped`, use `azdaja`. A foreign `az`, including Azure CLI, remains untouched.

```bash
az install --harness jcode
az install --harness all
```

The commands above assume the curl installer reported its alias. Otherwise use `azdaja install ...`. Managed install output is exactly three lines. The third line contains the shell-quoted absolute managed-binary `doctor` command and the selected harness's reload/restart step. Run that exact doctor command rather than the Cargo/PATH binary: the managed copy is adjacent to the selected route configuration. Installation writes files only; it does not contact a provider, invoke a harness, kill a session, or claim that an open session has discovered the skill.

A Cargo install creates only `azdaja`. Complete its setup with `azdaja install` for automatic detection or `azdaja install --harness NAME` for a supported named harness, then run the exact managed doctor command it prints. Remove Cargo-managed skills before removing the executable:

```bash
azdaja install
azdaja install --harness jcode
# Run the exact managed-binary doctor command printed above.
azdaja uninstall --harness all
cargo uninstall azdaja
```

Harnesses can cache their skill registry. In particular, a Jcode session opened before installation will not see the new skill until you run `skill_manage reload_all`, choose `/skills` -> `Reload all`, or start a fresh Jcode session. Restart Claude, Codex, Gemini, or OpenCode after installing when its open session does not discover the skill. For `--harness all`, reload or restart all five.

The standalone curl installer also emits exactly three lines. If its binary directory is off `PATH`, the final line starts with a shell-quoted absolute `azdaja doctor` command that is directly executable even when the path contains spaces, Unicode, or apostrophes; reload/restart and `PATH` guidance follows on that same line.

## Provider-free custody doctor

```bash
az doctor --harness jcode
az doctor --harness all
```

This route makes no provider call. For every selected target it verifies:

- the target is a real directory rather than a symlink/reparse point;
- the managed marker names exactly `SKILL.md`, `config.toml`, and the managed
  binary, with no unknown directory entries or changed hashes;
- `SKILL.md` has the `azdaja` frontmatter name and discovery description, the
  managed-skill awareness text, the current version, and the absolute embedded
  managed-binary path;
- the binary is a nonempty regular executable; and
- the configuration is a valid regular file.

A pass says **installed on disk**. The following `INFO` line preserves the
session boundary: it never claims that an already-open harness has loaded the
skill. The unqualified `az doctor` retains its existing evaluator and configured
provider canary semantics.

## Safe uninstall

```bash
az uninstall --harness claude   # one managed skill
az uninstall --harness all      # all five managed skills
az uninstall --standalone       # curl only: owned PATH surface
az uninstall --all              # curl only: all skills plus standalone
az uninstall --help
```

Harness removal is idempotent when a target is missing. Every multi-target
operation has a validation phase before its deletion phase, so a changed skill,
unknown file, or symlink in any selected target refuses the whole operation
before mutation. A customized harness `config.toml` is allowed during uninstall;
changed managed binaries and skills are not.

Standalone removal is relative to the currently executing canonical `azdaja`
binary. The exact adjacent `azdaja-config.toml.managed` contents must prove curl
installer ownership. Only these owned paths are eligible:

- `azdaja` (the currently executing binary),
- an exact relative `az -> azdaja` symlink, when present,
- `azdaja-config.toml`, and
- `azdaja-config.toml.managed`.

A foreign `az` alias and unrelated neighboring files are never deleted.
Incomplete, foreign, or unsafe configuration ownership state causes refusal
before any selected harness is removed. Unix permits a running process to
unlink its executable. Platforms with locked running executables fail closed
with manual-path guidance.

Successful uninstall output is exactly three concise lines. `--harness` says it removed skill copies only and kept standalone; `--standalone` says it kept harness skills; `--all` names both surfaces. The standalone modes are curl-only: without the curl ownership marker, the executable is left untouched and line 3 tells the user to return to the original installer or run `cargo uninstall azdaja` for a Cargo installation. When skills were removed, the same line also asks the user to reload/restart affected harnesses so cached registries forget them.
