# CLI reference

Use `azdaja` in every command below when the short `az` alias is unavailable.

A bare interactive `azdaja` prints one static provider-free snapshot. It reads validated configuration, owner-only live-session state, and local numeric source summaries, then exits. A piped or otherwise non-terminal invocation keeps the stable five-line help output. Run `az map` for the optional full-screen view.

## Reading the snapshot

The snapshot uses plain operational labels:

- `new work` is this invocation's configured default model, runner, and thinking level. It describes how newly started work would be configured. It is not an observed route shared by existing sessions.
- `live` counts current evaluator sessions. Each session row shows the default model persisted when that session was created.
- `memory` counts local numeric source summaries and their measured source bytes. These summaries are separate from live sessions.
- `pattern` places summaries on a plain `repeated ← … → varied` axis and reports `avg variety`. The axis uses local aggregate numbers only. It is distributional, not semantic, and not a quality score.
- `recent` describes the newest local source summary as loaded or finished, with size, line count, and age.

Simultaneous live sessions may show different persisted default models because configuration can change between session starts or a session can be started with an explicit model. Individual model calls may also override a session's default. The console therefore does not claim one observed universal provider or model route.

Source-summary privacy applies to the numeric summary records. They exclude source text, paths, hashes, prompts, and responses. Live-session rows remain session state and may show a shortened session ID, status, age, state size, load count, and persisted default model.

Exact byte entropy is details-on-demand. The overview deliberately says `variety` rather than displaying entropy notation. In `az map`, select a live session or source summary and press Enter or `d` to see exact local entropy alongside the plain variety and repetition interpretations. Entropy describes byte distribution only. It does not measure meaning, answer quality, model exposure, or coverage.

`az map` refreshes local state at a low fixed rate. Its constellation uses source-size bands vertically and the same repeated-to-varied source-variety axis horizontally. `●` marks the selected or newest summary, `○` marks an earlier summary, and a digit marks overlapping points. Every point is one local numeric source summary.

Keys in `az map`: arrows or `j/k` select, Enter inspects, `d` toggles measured details, `i` opens validated local integration state, `r` refreshes, and `q`, Esc, or Ctrl-C exits. Raw mode, cursor visibility, and the prior screen are restored on normal exit and panic. Narrow or incapable terminals print the static line-oriented snapshot instead.

## Commands

| Command | Signature | Purpose |
|---|---|---|
| `help` | `az help [command]` | Show the five-line overview or help for one command. |
| `start` | `az start` | Create an evaluator session and print its ID. |
| `load` | `az load <session-id> <path> <variable>` | Load one UTF-8 file into a session variable. |
| `exec` | `az exec <session-id>` | Read evaluator code from standard input and execute it. |
| `final` | `az final <session-id>` | Print the session's final value. |
| `list` | `az list` | Show the live-session and source-summary table in a terminal while emitting stable raw session IDs when piped. |
| `map` | `az map` | Open the optional full-screen local source-summary constellation, with a static fallback when not interactive. |
| `kill` | `az kill <session-id>` | Remove a session. |
| `solo` | `az solo <question> (-f <path> \| --repo <directory>) [--model <model>] [--sub-model <model>]` | Run one question over one UTF-8 file or a deterministic bounded repository bundle. |
| `doctor` | `az doctor [jcode|claude|codex|gemini|opencode|all|--caps]` | Check configured execution or inspect named integration files. |
| `install` | `az install [TARGET[,TARGET...]|all]` | Detect supported tools or atomically install a named comma-separated subset. |
| `uninstall` | `az uninstall [jcode|claude|codex|gemini|opencode|standalone|all]` | Remove detected integrations, one named scope, or everything. |

Use `az help` for the short overview and `az help <command>` for command-specific help. `--help` remains available. Invalid options or arity print the same canonical usage line on standard error and return status 2.

## Process and signal custody

On Unix, `SIGINT`, `SIGTERM`, and `SIGHUP` stop the active provider process group and wait for its direct child before returning `128 + signal`. Success, provider error, timeout, and unwind also terminate remaining descendants before pipe workers join, so inherited pipes cannot keep the adapter alive.

Windows retains direct-child timeout custody but does not claim the Unix process-group descendant guarantee.

## Sessions and temporary files

A provider adapter removes a bound `{prompt_file}` temporary without following a replaced path. An interrupted `exec` does not replace the previous snapshot, so the session remains usable.

`solo` accepts exactly one of `-f` and `--repo`. It rejects a blank question, blank model override, blank input path, or blank configured default before entering a provider. Repository input follows Git ignore boundaries when Git metadata is present, excludes build caches and credential-shaped files, skips non-UTF-8 content, and fails instead of silently truncating its file or byte limits.

## Configuration errors

Configuration failures report a sanitized path, terminal cause, and repair action. Invalid explicit `AZDAJA_HOME` or `AZDAJA_CONFIG` values fail before provider entry. Relative or empty XDG config and state roots cannot redirect state into the working directory.
