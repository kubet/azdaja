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

The curl one-liner supports Apple Silicon macOS 11+ and x86-64 Linux with glibc 2.35 or newer and requires a detected Jcode, Claude, Codex, Gemini, or OpenCode harness. With none detected it exits before downloading or writing. On Linux it verifies the runtime with `getconf GNU_LIBC_VERSION` and a numeric version comparison before creating staging files or changing anything under `HOME`; musl, glibc below 2.35, a missing `getconf`, and an invalid or unverifiable result fail with an actionable newer-system or Rust 1.95 source-build alternative. Local-validation Linux selectors must bind `AZDAJA_INSTALL_GLIBC_VERSION` explicitly, so selector tests never inherit the host libc. Its `Written:` line is also the command-name boundary: use `az` only when it reports the `az -> azdaja` alias; when it reports `short alias skipped`, use `azdaja`. A foreign `az`, including Azure CLI, remains untouched.

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

Before any install surface changes, the standalone installer downloads and checks the selected raw binary plus `LICENSE` and `THIRD-PARTY-NOTICES.md` against the four-payload `SHA256SUMS`. The document digests are additionally bound to the reviewed root bytes. It installs the two documents and an exact `.azdaja-managed` v2 ownership marker into `${XDG_DATA_HOME:-$HOME/.local/share}/azdaja`. The fixed v2 marker schema names the current expected LICENSE SHA-256 (`45dd135e…`) and notices SHA-256 (`ee908558…`); it is compared as one exact byte string and its fields are never parsed or trusted as caller-selected hashes. A set `XDG_DATA_HOME` must be nonempty and absolute; the `AZDAJA_INSTALL_DOC_DIR` override is accepted only with `AZDAJA_INSTALL_TEST_MODE=local`.

Reinstall accepts only an exact v2 marker with both exact current documents. The sole migration exception is the exact v1 marker with the exact current LICENSE and the previously supported notices digest `dde4b0d1…`. That set is quarantined, revalidated, replaced transactionally with current documents plus v2, and restored byte-for-byte if a later install step fails. Missing, mutated, linked, foreign, or marker-declared document identities are refused before HOME mutation. Shell install and Rust standalone removal share a private lifecycle exclusion directory; concurrent attempts fail closed or serialize without exposing a partial document set. The current binary may also remove the exact supported v1 set, but no other legacy or foreign bytes. Raw platform binaries satisfy this distribution contract only while the exact license and notices stay co-located release assets and the installer fetches them.

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
az uninstall --standalone       # curl only: owned PATH and document surfaces
az uninstall --all              # curl only: all skills, standalone, and documents
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
- `azdaja-config.toml`,
- `azdaja-config.toml.managed`, and
- the exact owned document directory containing only `LICENSE`, `THIRD-PARTY-NOTICES.md`, and the fixed v2 `.azdaja-managed` marker (or the one exact supported v1 set during safe removal).

A foreign `az` alias and unrelated neighboring files are never deleted. Incomplete, foreign, changed, symlinked, or hardlinked document/configuration ownership state causes refusal before any selected harness is removed. Selected paths first move to same-filesystem quarantines; a late pre-commit failure restores them, and deletion begins only after the complete standalone/document/harness set is quarantined. Unix permits a running process to unlink its executable. Platforms with locked running executables fail closed with manual-path guidance.

Successful uninstall output is exactly three concise lines. `--harness` says it removed skill copies only and kept standalone plus documents; `--standalone` says it kept harness skills; `--all` names all three surfaces. The standalone modes are curl-only: without the curl ownership marker, the executable and any documents are left untouched and line 3 links the repository notice and directs a Cargo installation through managed-skill removal and `cargo uninstall azdaja`. When skills were removed, the same line also asks the user to reload/restart affected harnesses so cached registries forget them.
