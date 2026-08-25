# Claude Code Haiku 4.5 Azdaja delta

This is a five-pair diagnostic of Azdaja's metadata-projection behavior in the real Claude Code CLI. It is not a general benchmark, a statistical significance claim, or evidence that Azdaja improves every task.

## Task

The benchmark reuses the deterministic public fixture from [`../delta/fixture.py`](../delta/fixture.py):

- 1,306,163 bytes
- 306 records
- 64 May records requiring spam-versus-ham classification
- 4 KiB of irrelevant synthetic `User` metadata per record
- complete decision evidence in each `Instance` field
- exact frozen answer: `Answer: 42`

Both arms used Claude Code 2.1.245 with `--model haiku --effort low`. The candidate inner calls resolved to `claude-haiku-4-5-20251001`.

## Arms

### Native Claude Code

Claude received the shared task prompt and could use `Bash`, `Read`, and `Grep` against `context.txt`. It had to discover the May-record projection and classification strategy itself. No Azdaja state, trace, command, or skill was provided to the native work directory.

### Claude Code with Azdaja

The outer Claude turn could execute only `Bash(./azdaja-evaluate)`. The shim performed exactly one private `start` / `load` / `exec` / `final` / `kill` lifecycle. Its cell deterministically selected and deduplicated the 64 complete `Instance` values before exactly one inner Claude Code Haiku semantic call. There was no retry.

The candidate total includes measured outer and inner usage. Cache reads are excluded from the uncached total; fresh input, cache creation, output, and measured inner usage are included.

## Five-pair result

| Metric | Native | Azdaja | Observed delta |
|---|---:|---:|---:|
| Exact answers | 4/5 | **5/5** | Native returned `44` once |
| Median uncached tokens | 11,904 | **10,027** | **15.8% lower** |
| Median wall time | 46.754s | **24.151s** | **48.3% lower** |
| Mean uncached tokens | 25,687.2 | **10,464.6** | **59.3% lower** |
| Mean wall time | 67.745s | **27.638s** | **59.2% lower** |
| Mean Claude turns | 11.2 | **2.0** | **82.1% lower** |

Azdaja was faster in all five pairs and used fewer uncached tokens in four of five. The remaining pair used 229 more candidate tokens while still finishing 18.018 seconds faster.

The means are strongly affected by one valid native run that took 35 turns, 73,327 uncached tokens, and 160.835 seconds. The medians are therefore the safer estimate of typical behavior. The outlier still matters as reliability evidence because it completed normally under the same 300-second bound.

Every candidate arm returned the exact answer, made exactly one successful inner call, recorded complete usage, and had zero inner failures.

## Validation

Provider-free validation performs no Claude, model, network, installer, or Azdaja execution:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 bench/claude-haiku-delta/validate.py
```

The validator checks:

- runner, result, fixture, and prompt hashes
- deterministic fixture hash, byte count, row count, and gold answer
- all ten arm records and five pair identities
- exact answers and summary recomputation
- one successful inner call per candidate
- resolved inner model and provider
- complete usage and positive wall time
- absence of private paths, credentials, challenges, and raw authentication material
- the narrow claim boundary

## Live reproduction

Live execution uses the installed Claude subscription and costs provider usage. It creates private temporary arm directories under `JCODE_SCRATCH_DIR`, alternates arm order, applies a 300-second timeout per arm, and never retries:

```bash
PYTHONDONTWRITEBYTECODE=1 \
AZDAJA_DELTA_REPETITIONS=5 \
python3 bench/claude-haiku-delta/run.py
```

If an arm exceeds the bound, the runner records a sanitized `TimeoutExpired` row with return code `124`, continues the remaining scheduled arms, writes the result artifact, and exits nonzero. A timeout is never converted into a zero-token success or silently omitted from the paired result.

Optional environment overrides:

- `CLAUDE_BIN`: exact Claude Code executable
- `AZDAJA_CLAUDE_BINARY`: exact managed Azdaja binary
- `AZDAJA_DELTA_RESULT`: output JSON path
- `AZDAJA_DELTA_REPETITIONS`: pair count
- `AZDAJA_DELTA_TIMEOUT`: per-arm timeout in seconds, default `300`
- `AZDAJA_DELTA_ARMS`: `native,candidate`, or one arm for diagnostics

The frozen plan is [`plan.json`](plan.json). The sanitized result is [`results/v1-result.json`](results/v1-result.json).
