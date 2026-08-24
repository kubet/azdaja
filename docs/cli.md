# CLI reference

Use `azdaja` in every command below when the short `az` alias is unavailable. A bare interactive `azdaja` prints a compact provider-free memory snapshot from validated configuration, owner-only session state, and aggregate-only observability records; piped/non-terminal invocation keeps the stable five-line help output. Run `az map` for the optional full-screen view.

The snapshot shows route, resident state, retained aggregate traces, a byte-entropy constellation strip, zero-order byte redundancy, nonempty-line density, and recent work. `az map` refreshes local state at a low fixed rate and expands the constellation into a fixed scatter plot: horizontal position is exact byte entropy, vertical position is an absolute source-size band, `●` is the newest trace, `○` is an older trace, and digits are collisions. It is not a semantic graph. Persisted observability excludes source text, paths, hashes, prompts, and responses.

Keys: arrows or `j/k` select, Enter inspects, `d` toggles measured details, `i` opens validated local integration state, `r` refreshes, and `q`, Esc, or Ctrl-C exits. Raw mode, cursor visibility, and the prior screen are restored on normal exit and panic. Narrow terminals use a static line-oriented fallback.

## Commands

| Command | Signature | Purpose |
|---|---|---|
| `help` | `az help [command]` | Show the five-line overview or help for one command. |
| `start` | `az start` | Create an evaluator session and print its ID. |
| `load` | `az load <session-id> <path> <variable>` | Load one UTF-8 file into a session variable. |
| `exec` | `az exec <session-id>` | Read evaluator code from standard input and execute it. |
| `final` | `az final <session-id>` | Print the session's final value. |
| `list` | `az list` | Show the memory-nest session table in a terminal while emitting stable raw IDs when piped. |
| `map` | `az map` | Open the optional full-screen exact-local memory constellation, with a static fallback when not interactive. |
| `kill` | `az kill <session-id>` | Remove a session. |
| `solo` | `az solo <question> -f <path> [--model <model>] [--sub-model <model>]` | Run one file question. |
| `doctor` | `az doctor [jcode|claude|codex|gemini|opencode|all|--caps]` | Check the configured route, or name a tool to check installed files only. |
| `install` | `az install [TARGET[,TARGET...]|all]` | Detect supported tools or atomically install a named comma-separated subset. |
| `uninstall` | `az uninstall [jcode|claude|codex|gemini|opencode|standalone|all]` | Remove detected integrations, one named scope, or everything. |

Use `az help` for the short overview and `az help <command>` for command-specific help. `--help` remains available. Invalid options or arity print the same canonical usage line on standard error and return status 2.

## Process and signal custody

On Unix, `SIGINT`, `SIGTERM`, and `SIGHUP` stop the active provider process group and wait for its direct child before returning `128 + signal`. Success, provider error, timeout, and unwind also terminate remaining descendants before pipe workers join, so inherited pipes cannot keep the adapter alive.

Windows retains direct-child timeout custody but does not claim the Unix process-group descendant guarantee.

## Sessions and temporary files

A provider adapter removes a bound `{prompt_file}` temporary without following a replaced path. An interrupted `exec` does not replace the previous snapshot, so the session remains usable.

`solo` rejects a blank question, blank model override, or blank configured default before loading the input or entering a provider.

## Configuration errors

Configuration failures report a sanitized path, terminal cause, and repair action. Invalid explicit `AZDAJA_HOME` or `AZDAJA_CONFIG` values fail before provider entry. Relative or empty XDG config and state roots cannot redirect state into the working directory.
