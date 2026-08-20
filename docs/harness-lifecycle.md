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

```bash
az install --harness jcode
az install --harness all
```

Managed install output is exactly three lines. The third line contains the exact
managed-binary `doctor` command and the selected harness's reload/restart step.
Installation writes files only: it does not contact a provider, invoke a harness,
kill a session, or claim that an open session has discovered the skill.

Harnesses can cache their skill registry. In particular, a Jcode session opened
before installation will not see the new skill until you run
`skill_manage reload_all`, choose `/skills` -> `Reload all`, or start a fresh
Jcode session. Restart Claude, Codex, Gemini, or OpenCode after installing when
its open session does not discover the skill. For `--harness all`, reload or
restart all five.

The standalone curl installer also emits exactly three lines. Its final line is
collision-aware: it reports `az doctor` when it safely created `az`, otherwise
`azdaja doctor`; reload/restart the selected detected harnesses after that
command finishes.

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
az uninstall --standalone       # installer-owned adjacent PATH surface
az uninstall --all              # all five skills plus standalone
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

Successful uninstall output is exactly three concise lines. `--harness` says it removed skill copies only and kept standalone; `--standalone` says it kept harness skills; `--all` names both surfaces. The last line asks you to reload/restart the affected harnesses so cached registries forget the removed skill.
