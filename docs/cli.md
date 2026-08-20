# CLI reference

Use `azdaja` in every command below when the short `az` alias is unavailable.

## Commands

| Command | Signature | Purpose |
|---|---|---|
| `help` | `az help [command]` | Show the five-line overview or help for one command. |
| `start` | `az start` | Create an evaluator session and print its ID. |
| `load` | `az load <session-id> <path> <variable>` | Load one UTF-8 file into a session variable. |
| `exec` | `az exec <session-id>` | Read evaluator code from standard input and execute it. |
| `final` | `az final <session-id>` | Print the session's final value. |
| `list` | `az list` | List sessions. |
| `kill` | `az kill <session-id>` | Remove a session. |
| `solo` | `az solo <question> -f <path> [--model <model>] [--sub-model <model>]` | Run one file question. |
| `doctor` | `az doctor [jcode|claude|codex|gemini|opencode|all|--caps]` | Check the configured route, or name a tool to check installed files only. |
| `install` | `az install [jcode|claude|codex|gemini|opencode|all]` | Detect supported tools and install their managed integrations. |
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
