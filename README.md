<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="260"></p>

# azdaja

**A minimal recursive-language-model layer for any agent harness that can run a command.** One binary, one skill, ordinary Python plus `llm()`.

Aždaja (roughly *azh-DAH-yah*) is the many-headed Serbian dragon: one persistent body, parallel model-call heads, and an appetite for contexts too large for one window.

> **Status: experimental v0.1.** The engine and jcode path are end-to-end tested. Monty 0.0.21 calls itself experimental, its snapshot format is version-bound, and the first benchmark pilot did **not** beat native jcode. The numbers are published below rather than hidden.

## Thesis

`load` puts a UTF-8 file in a persistent [Monty](https://github.com/pydantic/monty) session and returns only metadata. The harness model writes Python that inspects the variable and may call sub-models from inside the evaluator. There are no chunk, search, retrieval, or decomposition tools: those are strategies, and the model owns them.

The evaluated namespace is exactly ordinary Monty/Python plus:

```python
llm(prompt, model=None, ctx="")
llm_batch(prompts, model=None, workers=8)
FINAL(answer)
FINAL_VAR("variable_name")
```

`FINAL = answer` is also accepted because real RLM trajectories commonly use the paper-style assignment.

## Build and install

Requires Rust 1.95. Dependencies, including Monty `=0.0.21`, are locked exactly.

```bash
cargo build --release
./target/release/azdaja install --harness jcode
# alternatives: claude, codex, gemini, opencode, all
```

`install` performs a real Monty/snapshot canary and one tiny live model call **before** changing a skill directory, then writes an owned folder containing the binary, stamped `SKILL.md`, and editable `config.toml`. It therefore requires a working harness login and may consume subscription/API quota. Reinstall preserves an edited config; uninstall refuses to remove changed or unknown files.

```bash
azdaja doctor          # Monty + live adapter check
azdaja doctor --caps   # offline embedded capability manifest
azdaja uninstall --harness jcode
```

jcode 0.75.3 does not accept a prompt on stdin. Its installed adapter uses a mode-0600 temporary prompt file, keeping long prompts and shell metacharacters out of argv. Other adapters use stdin. Command templates are split into argv without a shell; `{model}` and `{prompt_file}` are substituted inside existing arguments.

## Manual use

```bash
sid=$(azdaja start)
azdaja load "$sid" ./huge.log ctx

cat <<'PY' | azdaja exec "$sid"
interesting = [line for line in ctx.splitlines() if "failure" in line.lower()]
judgments = llm_batch(["Explain this line:\n" + x for x in interesting])
FINAL({"count": len(interesting), "judgments": judgments})
PY

azdaja final "$sid"
azdaja kill "$sid"
```

`start`, `load`, `exec`, `final`, `list`, and `kill` are separate processes. State survives through versioned Monty snapshots; there is no daemon, tmux, Python, or Jupyter dependency. `exec` input comes from stdin. Every displayed cell result, traceback, and final answer is Unicode-scalar capped (8192 characters by default) with middle elision.

For a demo or benchmark where azdaja drives the root loop too:

```bash
azdaja solo "question about this input" -f ./large.txt \
  --model claude-haiku-4-5 --sub-model claude-haiku-4-5
```

Normal use keeps the existing harness as root; `solo` is not the product boundary.

## Configuration

The installed binary reads the `config.toml` beside itself. Development builds use `$AZDAJA_CONFIG`, then a config beside the executable, then `$XDG_CONFIG_HOME/azdaja/config.toml`, then embedded defaults.

```toml
sub_llm_cmd = "jcode run --no-update --quiet --model {model} Read_the_complete_UTF-8_prompt_at_{prompt_file}_and_return_only_its_answer"
default_model = "claude-haiku-4-5"
output_cap = 8192
max_depth = 1
sub_timeout = 300
max_sessions = 4
cell_timeout = 30
idle_timeout = 1800
clean_patterns = [] # regexes for adapter banners; shipped jcode config includes known patterns
```

Depth is enforced in the invoking process through `RLM_DEPTH` and repeated as an explicit instruction to sub-agents. A daemon-backed harness may not propagate the environment to its tool subprocesses, so depth is not a security boundary.

## Safety, precisely

- Monty code has no ambient host filesystem, environment, subprocess, or network access. azdaja rejects Monty OS callbacks.
- The **azdaja CLI itself** reads any path the user gives `load`, stores the raw text unencrypted in a mode-0600 snapshot, and runs `sub_llm_cmd` with user permissions. A full harness used as a sub-model can use its own tools.
- `load` never emits file contents automatically, but this is not information-flow control: code can `print(ctx)`, send slices through `llm`, or call `FINAL(ctx)`. One response is capped; disclosure accumulated across repeated calls is unbounded.
- Snapshot replacement is atomic against ordinary process crashes on Unix, but files are not `fsync`ed and are not promised to survive power loss. Windows replacement currently has a smaller remove/rename crash window. A process crash can leave a mode-0600 prompt file until the next age-based reap.
- Unix timeouts kill and join the local adapter process group; Windows kills only the direct child. A remote turn owned by a daemon-backed harness may continue after its local client dies.
- There is no Monty memory ceiling or total sub-call/cost budget. Batch concurrency is clamped to 32, but code can allocate memory or make repeated calls until the OS/provider limit. Large non-string bare-expression reprs may allocate before display capping.
- In-process Monty is a real language sandbox, not a process-containment boundary. Upstream recommends its worker pool for hostile code because interpreter/allocator defects can still abort the host.
- `install --harness all` stages and replaces each harness independently; it is not one cross-harness transaction and concurrent installers are unsupported.
- Monty implements a Python subset. The tested RLM idioms and regex probes are in `tests/monty_compat.rs`; notable gaps remain (for example external callbacks inside `map`, `re.VERBOSE`, third-party packages, and parts of the stdlib).

## Verification

```bash
cargo test -- --test-threads=1
python3 bench/perf.py --binary target/release/azdaja \
  --repeats 20 --output bench/results/macos-arm64.json
```

The test suite covers separate-process persistence, metadata-only loading, mode-0600 state/prompt files, Unicode cell/final cap semantics, partial-state preservation after exceptions, `FINAL`/`FINAL_VAR`, depth refusal, ordered batch calls, cell timeout, Unix process-tree timeout, exact >ARG_MAX prompt-file transport, argv injection, filesystem/environment/module denial, path/symlink validation, concurrent session limits, solo root/sub orchestration, failed-canary rollback, staged reinstall, safe-uninstall refusal, ten RLM idioms, and regex lookaround/backreference/finditer/flags.

### Snapshot benchmark

Release build, M2 MacBook Air, macOS 26.5.1, 20 serial repetitions. `snapshot exec` restores, evaluates `len(ctx)`, serializes, and atomically replaces the snapshot. The CPython arm is a separate process doing read + `len` + print; it is not an RLM competitor or a strict lower bound.

| Input | load median / p95 | snapshot exec median / p95 | direct Python read median / p95 | peak RSS |
|---:|---:|---:|---:|---:|
| 1 MB | 7.8 / 9.1 ms | 7.1 / 9.4 ms | 22.1 / 28.6 ms | 11.6 MB |
| 10 MB | 15.7 / 17.5 ms | 16.5 / 18.8 ms | 28.4 / 31.4 ms | 38.6 MB |
| 100 MB | 91.9 / 135.8 ms | 105.5 / 193.9 ms | 36.6 / 58.6 ms | 308.6 MB |

The planned p95 `<100 ms @100 MB` gate **failed**. Median load passed; full snapshot exec did not. Monty snapshots are uncompressed (~100,002,009 bytes for the 100 MB case) and peak RSS is roughly 3.1× payload. Raw JSON is committed in `bench/results/macos-arm64.json`.

### Harness pilot

One run on the generated 1.08 MB semantic-incident fixture. All arms answered 6/6 correctly. This is a smoke test, not a statistically controlled quality claim; Prime used a different model and all transports had warm subscription daemons.

| Arm | Model | Correct | Wall | max RSS |
|---|---|---:|---:|---:|
| jcode native | Claude Haiku 4.5 | yes | **5.75 s** | 283.9 MB |
| azdaja `solo` through jcode | Claude Haiku 4.5 root + sub | yes | 29.89 s | 286.0 MB |
| Prime Agent 0.7.0 | GPT-5.4 | yes | 19.70 s | **182.6 MB** |

Native jcode won this task decisively. azdaja was slower than Prime here too, though model/provider mismatch makes that comparison directional only. Prime reported 59,840 summed tokens and $0.0604 API-equivalent cost; the jcode text adapter does not expose structured total usage to azdaja. The exact serial runner, fixture generator, gold scorer, outputs, timings, versions, and manually collated summary are in `bench/`; rerun with `bench/e2e-pilot.sh`.

## Non-goals

No installer infrastructure, marketplace, GUI, provider framework, API-key management, memory system, document pipeline, chunking/search/index tools, MCP server, monetization, or feature requests that add a strategy to the contract. No new subcommand without removing one.

## License

MIT.
