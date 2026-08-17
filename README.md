<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="240"></p>

# azdaja

**A fast recursive-language-model layer for long contexts.**

Azdaja keeps the full input inside a persistent, sandboxed Monty/Python evaluator. A root model writes compact analysis code; semantic work is delegated through `llm` and `llm_batch`; deterministic reduction happens locally.

> v0.1.0 prerelease. The CLI and initial Apple Silicon macOS install path are end-to-end tested. Benchmark results below are diagnostics, not a product gate or superiority claim.

## Why

Long-context agents repeatedly reread, copy, and reason over the same input. Azdaja separates the work:

1. `load` places the complete UTF-8 input in a persistent evaluator.
2. Python performs exact parsing, filtering, grouping, and reduction.
3. Model calls handle only semantic predicates.
4. Strict manifests enforce complete ID coverage before `FINAL` is accepted.

The model-facing surface is deliberately small:

```python
llm(prompt, model=None, ctx="")
llm_batch(prompts, model=None, workers=2)
FINAL(answer)
FINAL_VAR("variable_name")
```

`solo` additionally preloads `semantic_manifest(items, task, labels)`: two blind independent full manifests, strict validation, and one blind complete adjudication of every disagreement within a preflighted call envelope.
`solo` treats a blank string passed to `FINAL` as an incomplete terminal answer and spends only its remaining bounded same-session correction budget; tasks whose intended answer is blank are therefore unsupported by `solo`.

## Install

The v0.1.0 prerelease provides one-command installation for Apple Silicon macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/v0.1.0/site/install | sh
```

The versioned installer downloads only the immutable `azdaja-v0.1.0-darwin-arm64` release asset, requires SHA-256 `6b50716382ac35e4f2bc9fc3c1cc3db9ee059edde783b78dba21273bf626762a`, validates version and local evaluator capabilities, and installs the managed Jcode skill without calling a model. The manual read-only `Public release integrity` workflow checks the peeled tag, GitHub release ID/state, exact asset names/sizes/GitHub digests, and exact versioned installer bytes/bindings without downloading or executing the binary asset. Hosted run `31997061278` passed with zero artifacts and left release download counters unchanged. Receipt: `release/v0.1.0/public-release-integrity-receipt.json` (`8cb2cefe2d4d0f925e9a869820ae5bbd6b5c65dc867525025a38170cb1216c9e`).

Then run the explicit live login check:

```bash
AZ="$HOME/.jcode/skills/azdaja/azdaja"
"$AZ" doctor
```

Choose another managed target with `sh -s -- --harness claude` (also `codex`, `gemini`, `opencode`, or `all`). A supported harness login is required for `doctor` and product use, not installation. A customized managed `config.toml` is preserved on upgrade and may be removed by normal uninstall; changed binaries, changed skills, and unknown files still fail closed.

Other platforms remain source-only and require Rust 1.95:

```bash
cargo install --git https://github.com/kubet/azdaja --tag v0.1.0 --locked
```

The manual read-only `Public source install` workflow replays the documented public git/tag/locked install on Ubuntu and Apple Silicon macOS with an isolation-only `--root`, verifies both the fetched checkout and pre/post remote annotated-tag target, exact version and evaluator capabilities, and fails if `doctor --caps` enters a configured provider or mutates a fresh HOME. It uploads no binary and does not expand supported public platforms. Hosted run `31993870431` passed both jobs and retained zero artifacts. Receipt: `release/v0.1.0/public-source-install-receipt.json` (`7394e15602cff76ca7b3cabe19d3adb2aeda154861d10943a7001569a82db816`). The strengthened gate also routes that exact installed source binary through the tag's build-log, repository-dump, and transcript 50 MiB acceptance cases before cleanup; hosted run `31995419472` passed both jobs with zero artifacts. Receipt: `release/v0.1.0/public-source-installed-50mb-receipt.json` (`00b442e7f7a38357477ebe17ec0e9d4f310b1640b753c50f41ca6f885f9bb1b3`).

The Jcode adapter uses its stable Harness API over an owner-only Unix socket and pins `openai-oauth:<model>`. It does not fall back to a metered API key.

## Use

### Direct product loop

```bash
azdaja solo "question about this input" -f ./large.txt \
  --model gpt-5.6-luna --sub-model gpt-5.6-luna
```

### Persistent evaluator

```bash
sid=$(azdaja start)
azdaja load "$sid" ./large.txt ctx

cat <<'PY' | azdaja exec "$sid"
rows = ctx.splitlines()
selected = [row for row in rows if "failure" in row.lower()]
judgments = llm_batch(["Classify:\n" + row for row in selected])
FINAL({"count": len(selected), "judgments": judgments})
PY

azdaja final "$sid"
azdaja kill "$sid"
```

Core commands:

```text
start  load  exec  final  list  kill  solo  doctor  install  uninstall
```

### Blocking 50 MiB product path

`tests/product_50mb.rs` serially exercises the real `solo` CLI on three exact 50 MiB UTF-8 inputs: a build log, repository dump, and operational transcript. A local scripted harness supplies only a short `ctx`-dependent program—never the expected answer—and every case must produce its exact answer before a 90-second outer watchdog, use one root turn and zero child calls, retain no session, and keep the root prompt below 64 KiB. The captured provider prompt must contain neither the host input path nor any exact 100-byte source span; the documented bounded escaped structural sample is still intentionally visible. This is an offline CLI/runtime acceptance test, not evidence of installed-artifact packaging or live-model planning quality.

```bash
cargo test --test product_50mb -- --test-threads=1
```

On Linux and macOS, the test also records `getrusage(RUSAGE_CHILDREN).ru_maxrss` as a byte-normalized, process-lifetime reaped-child high-water diagnostic; add `--nocapture` to display it. This is cumulative rather than independent per-case attribution, excludes un-reaped or non-child process-tree memory, and is neither a memory ceiling nor a claim about the published release binary unless that exact binary is selected with `AZDAJA_PRODUCT_BINARY`.

A separate public-release smoke used the hash-bound installed binary with Jcode subscription OAuth on one fresh, non-benchmark 50 MiB build log. `doctor` passed, then Luna/low returned the exact generated count `Answer: 37` in 8.980 seconds with one root turn, zero child calls, no repair, no retained session, no host path, and no exact 100-byte raw-source overlap in the provider trace. Receipt: `release/v0.1.0/live-harness-smoke.json` (`c3c0dbb15c612d35a6d3f053896a81a867bd0f346ae70ef6d0e6471955fadd4b`). This single smoke validates authentication and natural-language planning for that case; it is not a general accuracy estimate.

## First-use feedback

The initial published binary supports Apple Silicon macOS only. Report a [first-use result](https://github.com/kubet/azdaja/issues/new?template=first-use-feedback.yml) or a [product defect](https://github.com/kubet/azdaja/issues/new?template=product-defect.yml); installation failures, deaths, timeouts, wrong answers, config loss, and uninstall failures outrank benchmark work. The guarded forms automatically route reports to `first-use` or `product-defect`, and the repository regression fails if that top-level routing is removed or swapped. Receipt: `release/v0.1.0/feedback-routing-receipt.json` (`63739e2005253c2f6cd0f8cb003426962cc2c3191c8168aa83fd474c406e79a0`). Use synthetic or sanitized reproductions only—never post raw build logs, repository content, transcripts, traces, config files, host paths, OAuth material, tokens, or secrets. Security vulnerabilities belong in a [private advisory](https://github.com/kubet/azdaja/security/advisories/new), not a public issue.

The first public checkpoint found no submitted issues; release download counters were 2 for the binary and 1 for `SHA256SUMS`. Those mutable, non-unique counters may include maintainer validation and are not evidence of independent adoption or defect-free use. Receipt: `release/v0.1.0/first-use-feedback-checkpoint.json` (`313f5126ee99b9a7d213ac2800d689ec0f7348ea673381f2f3ddde461305c4fc`).
`tests/feedback_channel.rs` locks the collection boundary: blank issues and legacy Markdown templates are forbidden, every public issue form must retain the exact required privacy confirmation and synthetic/sanitized reproduction request, and the private advisory route must remain present.
The v0.1.0 prerelease page now exposes the same privacy-safe feedback and private-security routes. This notes-only update left the annotated tag, prerelease state, asset IDs, sizes, and digests unchanged. Receipt: `release/v0.1.0/feedback-discovery-receipt.json` (`e3c76f85c5444f54b25f8e93ffee998bf30787ab1eabc74de4353015427f1170`).

## Appendix: benchmark diagnostics (not a product gate)

The three-arm headline tables below retain one immutable comparative candidate,
private commit `6588c06` with binary SHA-256
`6be5b9ff567eca6d1a5c2315dfb0c12fb5bd847b58daef0b3b8191151e45b509`,
against both controls. Historical candidate versions are never mixed within a
table. The newer single-arm RAH-199 candidate is reported separately because its
schedule did not run paired controls; it cannot be combined with or used to
replace those comparative tables. These are single-run private diagnostics, not
official leaderboard results or superiority claims.

> **Latest campaign status:** the separately owner-authorized immutable RAH-199
> completed 199/199 rows and its authorized scorer ran exactly once. Candidate
> commit `99f8ee7`, binary SHA-256 `4ecb1e2178143b45e1bba8c30669b68adce68f30e8cf905d0bd500b28cb64225`,
> scored **61.4527%** on the fixed denominator with 161/199 execution successes.
> It is a validation-derived slice, not official full OOLONG, and has no paired
> control or superiority claim. Receipt SHA-256: `2847722dbe3d4ca9cc527b103c481036cabc65dfac868e55bc13fdefd72c70e1`.
>
> Candidate labels are experiment serials, not releases or monotonic upgrades.
> A newer experiment never retrofits results from a different candidate or
> schedule into an existing comparison.

### Latest RAH-199 validation-derived slice, 199 fixed fixtures

| Arm | Execution | Valid prediction | Fixed-199 official-semantics score | 95% bootstrap CI |
|---|---:|---:|---:|---:|
| **Azdaja `99f8ee7`** | **161/199 (80.90%)** | **161/199 (80.90%)** | **61.4527%** | **[54.8815%, 67.8713%]** |
| Native jcode | not run | not run | N/A | N/A |
| Prime Agent | not run | not run | N/A | N/A |

All 38 execution failures remained fixed-denominator zeroes. Root-context leak
and cleanup checks passed 199/199. The equal-weight 13-length-bucket macro was
61.4577%. The post-run no-gold validator was invoked once, returned its
pre-inference guard `already entered inference`, and was not retried. With 199
rows plus `completion.json` and no scoring sentinels, the separately authorized
scorer then ran once, created `gold.consumed` before opening gold, and exited 0.
No other gold access occurred. Exact public-safe artifacts are
`bench/results/rah199-99f-score.json`, `rah199-99f-completion.json`,
`rah199-99f-gold-consumed.json`, and `rah199-99f-terminal-receipt.json`.

The standing agent-transport paired scout was N/A rather than zero accuracy:
0/10 pairs executed because the frozen binary lacked the required per-model,
file-backed-`ctx` treatment interface. No substitute arm was fabricated.

### Derived RULER, 90 fixtures

| Arm | Execution | Completed strict exact | Fixed-90 strict exact | Mean root tokens | Median time / item |
|---|---:|---:|---:|---:|---:|
| **Azdaja** | **90/90 (100%)** | 85/90 (94.44%) | 85/90 (94.44%) | **2,835** | 22.5s |
| Native jcode | **90/90 (100%)** | **86/90 (95.56%)** | **86/90 (95.56%)** | 16,373 | **8.1s** |
| Prime Agent | 87/90 (96.67%) | 81/87 (93.10%) | 81/90 (90.00%) | 6,925 | 10.9s |

Azdaja cleared its 90/90 reliability gate and the separate candidate-only
90-item run completed at global width 4 in 562.3 seconds. The official
three-arm run completed 270 rows in 1,101.5 seconds. Azdaja's strict point
estimate was one item below native; the paired native-minus-Azdaja difference
was +1.11 percentage points with a 95% bootstrap interval of [-5.56, +7.78].
This supports neither superiority nor equivalence. Azdaja remained slower:
its median attempt was 2.77x native, so the <=1.5x speed gate did not pass.

### Derived LongBench-v2 hard/long subset, 63 fixtures

The unchanged exact-v43 candidate completed a new version-stamped 189-row
freeze after its required synthetic rehearsal passed. The terminal no-gold
validator passed before gold was opened. The pinned scorer then exited 0 and
produced the current authoritative private diagnostic below.

| Arm | Execution | Completed official accuracy | Fixed-63 official accuracy | Mean root tokens | Median time / item |
|---|---:|---:|---:|---:|---:|
| **Azdaja** | 45/63 (71.43%) | 17/45 (37.78%) | 17/63 (26.98%) | **7,587** | 53.7s |
| Native jcode | **63/63 (100%)** | **36/63 (57.14%)** | **36/63 (57.14%)** | 69,717 | **20.8s** |
| Prime Agent | 57/63 (90.48%) | 11/57 (19.30%) | 11/63 (17.46%) | 8,783 | 36.4s |

The separately preregistered syntax-only envelope metric counts pinned official
extraction first and then only an exact bare uppercase A-D plus one LF. Azdaja
scored **24/63 (38.10%)**, passing its frozen **>=16/63** gate. Its fixed-63
taxonomy is 24 correct, 20 recognized-but-wrong, one unrecognized, and 18
execution failures. The upstream official extractor remains authoritative at
17/63; strict full-string accuracy remains 0/63.

Passing the derived gate authorized the same-binary OOLONG run, which was
launched immediately. It does not erase the reliability and speed gaps: Azdaja
executed fewer rows and its median was 2.58x native. The run output SHA-256 is
`96ae71df5299d8c8a394d12531baa208f546d8b8f70e5b2d295e6424128eaa0e`;
the schedule SHA-256 is
`422ad89b6b59bae00068a40733e62eceef5a2bfc79a6bc8f7163f8b709a34359`;
and the scored report SHA-256 is
`5997a69808ab4acd8a688245d53d9b468d8bc92ff4f6c86015d63f0905eee13a`.

The earlier refresh rejected by its preregistered validator remains permanently
terminal-invalid and unscored. It was not retried, resumed, relabeled, or used
as score input. Neither run is an official leaderboard result, and the current
comparison supports no superiority claim.


### Derived OOLONG-Synth validation slice, 26 fixtures

LongBench's derived gate authorized the same exact-v43 binary for the frozen
26-fixture, three-arm OOLONG campaign. All 78 rows reached terminal validation;
Azdaja had four retained execution failures.

| Arm | Execution | Completed exact | Fixed-26 exact | Mean root tokens | Median time / item |
|---|---:|---:|---:|---:|---:|
| **Azdaja** | 22/26 (84.62%) | **19/22 (86.36%)** | 19/26 (73.08%) | 6,166 | 31.3s |
| Native jcode | **26/26 (100%)** | 22/26 (84.62%) | **22/26 (84.62%)** | 30,382 | **9.7s** |
| Prime Agent | **26/26 (100%)** | 20/26 (76.92%) | 20/26 (76.92%) | **2,278** | 12.0s |

The frozen continuation gates were 25/26 execution and 24/26 fixed-denominator
exact. Azdaja missed both at 22/26 and 19/26, with four `monty_subset_tax`
execution failures and three incorrect completed answers. Its median was 3.23x
native. The root-context leak hard gate passed 26/26 with zero leaks.

Therefore this historical exact-v43 candidate did **not** authorize an RAH
continuation under its frozen gates and was never resumed or relabeled. The
newer RAH result above belongs to a separately owner-authorized candidate,
schedule, locked runtime, custody chain, and one-shot scorer; the two candidates
are not combined. The historical OOLONG output SHA-256 is
`6f6a9c524b69ef16ef9eb8b85b375b2caeddae6c1226d53dda9675dffcbf5bfd` and its validated
report SHA-256 is `80bad59b241064b6430f4c56c1f9f114c4c82fdf564483b74906c4e43c8acfec`.

## Guarantees

- Failed cells cannot publish tentative `FINAL` or `FINAL_VAR` values.
- Semantic manifests reject missing, duplicate, unknown, malformed, or invalid-label records.
- Source occurrences and integer multiplicity are preserved.
- Provider/model routing fails closed.
- Session files, prompts, sockets, and retained benchmark artifacts are owner-only.
- OAuth inference uses explicit subscription routing.
- Batch successes survive sibling failures; retries never repeat valid items.
- Root and child session cleanup is bounded.

## Boundaries

Monty code has no ambient filesystem, environment, subprocess, or network access. The CLI itself can read paths explicitly supplied to `load`, and model calls can receive data selected by evaluator code. This is not information-flow control.

Native harnesses still run with the user’s host permissions. Benchmark staging and tool-event scans detect obvious violations but are not an OS sandbox. Strong containment requires a separate trusted inference broker.

Monty 0.0.21 is experimental and snapshot-format-bound. Snapshots are unencrypted owner-only files; there is no evaluator memory ceiling.

## Configuration

```toml
sub_llm_cmd = "jcode-api"
default_model = "gpt-5.6-luna"
jcode_provider = "openai"
jcode_reasoning = "medium"
output_cap = 8192
max_depth = 1
sub_timeout = 300
max_sessions = 4
cell_timeout = 30
idle_timeout = 1800
max_calls_per_cell = 64
clean_patterns = []
```

## Validate

```bash
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release --locked
python3 -m unittest discover -s bench/oolong -p 'test_*.py' -v
```

The suite covers the three-file 50 MiB product path, the literal sealed/hash-bound site installer, provider-free managed installation, lifecycle persistence, snapshot ownership, Unicode caps, transactional finalization, call budgets, batch ordering and partial recovery, Harness API framing, OAuth model pinning, streamed usage, bounded cleanup, manifest coverage, installer rollback and customized-config removal, Monty compatibility, and blind benchmark controls.

GitHub Actions push run `31988065758` passes on macOS and Ubuntu for commit `4b38d5e`. Before the same-commit manual run packaged either candidate, each exact release binary passed hash-bound local installation, byte comparison, the installed-binary three-file 50 MiB gate, customized-config reinstall, and uninstall cleanup. Downloaded archives then matched every recorded digest and mode. They remain `UNVALIDATED_NOT_FOR_PUBLICATION`: neither hash has a public installer or live OAuth receipt, and the macOS candidate must not replace published v0.1.0 bytes. Receipt: `release/candidates/4b38d5e/hosted-packaged-receipt.json` (`0707c072001a6e67664a0feac582e615acb806de8d2ec9b3680ce5059f8bde9b`).

## License

MIT.
