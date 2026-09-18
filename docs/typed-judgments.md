# Optional typed judgments inside Azdaja

Development source capability, not a promise that an existing installed release includes it.

**Available in this source tree, not guaranteed in an existing installed release.** The formerly stale
notice gate has been repaired with a source-backed inventory for both default
and optional `typesafe` dependencies. The actual
`python3 release/verify-third-party-notices.py` command passes, while the old
notice and published installer/assets remain unchanged. This is an engineering
check, not a legal-completeness determination or publication authorization.
The frozen published installer intentionally rejects this unpublished notice.
See the [final source follow-through](research/jev-final-followthrough-20260917.md)
for exact build identities, installed acceptance and remaining limits.

For an explicit long-source work list, use [checkpointed semantic batches](jev-batch.md): native execution, per-request durable output and resume without repeating completed requests. This does not rely on a model choosing a typed call or generating finalization code.

## The useful boundary

```text
retain complete source + stable occurrence IDs
  → deterministic parsing / search / joins / aggregation
  → explicit selected state + independent typed questions
  → judge_many: raw distributions + actual model string + accounting
  → RLM examines alternatives, contradictions and missing evidence
  → llm explanations / further inspection when useful
  → final source-backed work, with unresolved uncertainty visible
```

This is an optional execution leaf beside `llm`, not a mandatory workflow or a replacement for generative reasoning. The model chooses which semantic questions are worth asking. The runtime enforces representation and resource limits, not a confidence threshold or a preferred interpretation. Existing generative providers work unchanged without the feature or a TypeSafe account.

**Preserve uncertainty:** retain the complete returned distribution, evidence and alternatives. A `choice` winner is not ground truth. Do not multiply correlated probabilities as if independent, treat cache hits as independent confirmation, or let entropy alone choose what matters. A confidently wrong high-impact judgment can be more dangerous than an uncertain low-impact one. Numeric entropy describes the model's distribution, not missing evidence, truth, or task completeness.

## Enable explicitly

First use `azdaja doctor --caps` for provider-free discovery. Its
`typed_judgments` object names `judge_many` and `judge_stats`, reports whether
the `typesafe` transport was compiled, and identifies the per-cell cache/budget
scope. This is **build capability, not runtime readiness**: the command does
not read configuration or credentials, create state, or call a provider.
Use the exact `doctor --caps` form: bare `doctor` is a different diagnostic
that can make a model canary call.
`typesafe_compiled: true` does not mean that the host enabled inference or
supplied a valid key. A default-feature build still exposes the API names but
reports `typesafe_compiled: false`. The existing opt-in and ordinary-execution
recovery behavior below is unchanged.
The [discovery acceptance report](research/jev-native-discovery-20260917.md)
records the before-fix failure, both build modes and the actual installed output.

Build this source tree with Rust 1.95:

```sh
cargo build --locked --features typesafe --bin azdaja
```

In a host-selected `AZDAJA_CONFIG` TOML file:

```toml
[judge]
enabled = true
model = "jev-latest"
key_env = "TYPESAFE_API_KEY"
# Optional only if you actually know the provider's returned identifier:
# expected_model = "known-provider-identifier"
max_requests_per_cell = 4
max_questions_per_cell = 64
max_input_tokens_per_cell = 100000
```

Supply the secret in the named **host environment variable**, using your normal secret management, or attach it once with `az jev attach --stdin` through a private stdin pipe. `az jev status` and `az doctor jev` report local source and syntax status without provider calls. `az jev detach` removes the named attachment. A present environment variable takes precedence, including an invalid value: there is no silent fallback. For a custom `key_env`, pass the same `--key-env NAME` to attachment commands.

Attachment is an owner-only plaintext file under the private host state root, not an encrypted vault or a cross-user secret service. It is supported on macOS/Linux/Android and fails closed elsewhere. It does not enable `[judge]`, change an installed binary, or write to repository memory/configuration. Hard termination can leave a private staging file until the next attachment/replacement or detach recovers it. See [CLI credential boundaries](cli.md) for exact semantics.

Never put the key in argv, TOML, an RLM prompt, `state`, a question, a note, a committed script, or shell history. The key is not forwarded to custom generative subprocesses. The HTTP destination is fixed, uses TLS, does not follow redirects, use inherited proxies, or automatically retry. Only the explicitly supplied state/questions are sent. TypeSafe-shaped trace redaction is defense in depth, not automatic detection of arbitrary secrets in source data. Selecting evidence for an external service remains the caller's responsibility.

The feature is excluded from default Cargo features. `[judge].enabled` defaults to false even in a feature-enabled build. No fallback from a failed typed request to `llm` happens silently.

## Ordinary persistent evaluator example

Start a normal session, load a public document into `source`, then run this cell:

```python
questions = {"support": {
    "type": "choice",
    "instructions": "Does this document establish that all stored records were searched? Judge only this document, not unstated runtime behavior.",
    "criteria": {
        "supports": "Explicitly establishes complete coverage of all stored records.",
        "contradicts": "Explicitly establishes that some records were not searched.",
        "insufficient": "Does not establish either complete coverage or a known omission."
    }
}}
observation = judge_many(state=source, questions=questions)
FINAL({"raw": observation, "accounting": judge_stats()})
```

`observation` remains an ordinary typed dictionary in the session. Another `exec` can inspect `observation["answers"]["support"]["probabilities"]`, join it with source IDs, or pass it to `llm` as fallible evidence. Store the source digest beside observations if you retain them. Their existence does not prove all task-relevant evidence was sent.

Question types follow the [TypeSafe API](https://docs.typesafe.ai/api.md):

- `noul`: a probability for an explicit proposition. Optional criteria are `true` and `false` strings.
- `choice`: a complete distribution over at least two named alternatives. Criteria are label→description/null.
- `score`: a distribution over an ordered rubric of at least two descriptions, plus its weighted score.

Question IDs are plumbing, not semantic instructions. Put the complete question and its evidence references in `instructions`. The runtime checks exact ID coverage, types, finite probabilities, probability domains/sums and score consistency. It does not validate semantic accuracy, calibration or independence.

Exact serialized requests are cached **within one cell**. `_azdaja.cache_hit` and `new_request_usage` distinguish reuse from new inference. `judge_stats()` counters are separate from generative call counts. Automatic cache and limits reset on each `exec`; they are not session-wide spending limits, a resumable database, or a global scheduler. Saved variables do persist. After transport/schema/resource failure, that cell's engine is terminal. Keep errors visible and explicitly decide whether a later cell is warranted.

The remaining cell wall deadline caps an HTTP call. Known usage crossing the host cap rejects the answer while retaining known usage in `judge_stats()`. If provider usage is absent or invalid, it is unknown, not free. A reported-token cap cannot undo a request already billed. Dollar cost needs separate provider billing evidence. Model strings describe provider-reported identity, not immutable weights; moving aliases may change across requests.

## Optional `solo` workflow

With both the `typesafe` build feature and `[judge].enabled = true`, `solo`
advertises `judge_many`, `judge_stats`, `llm` and `llm_batch` to its root model.
Only successful host-accounted semantic requests satisfy its semantic gate.
Stats inspection, cache hits and failed preflight are not semantic evidence.
Typed accounting remains separate in the host-owned `judge_cells` trace.
Default-disabled and feature-off root prompts and execution retain their prior
behavior. This does not override an external host skill's mandatory policy.

The native `sha256(text)` helper accepts text and returns hexadecimal text.
For the opted-in `solo` path, a syntax-aware preflight rejects known mistakes
such as `sha256(ctx.encode()).hexdigest()` **before the generated cell runs**.
The existing bounded root-repair mechanism can request corrected code without
having performed the cell's child reads or typed requests. No code is silently
rewritten and no already-paid cell is automatically replayed.

This is a narrow lint, not a general typechecker. It checks direct result
`.digest`/`.hexdigest` access, byte literals, and direct encoding of literal
text or the unshadowed original `ctx`. Strings and comments are not code.
Known misuse in unreachable code is still rejected. Any syntactic `sha256`
binding makes the lint abstain for that program, including nested bindings.
Aliases, dynamic namespaces and unknown argument types are not inferred.
The existing program size limits apply, with a 256-level lint traversal bound.

These engineering safeguards do not establish autonomous long-task accuracy
or a Jev speedup. The [failed live CUAD runs and offline recovery](../bench/jev/long_task_salvage/RESULTS.md)
remain separate, unchanged evidence. Use the checkpointed batch workflow above
when you need an explicit durable work list rather than model-authored control.

## Angles worth testing

| Application | Why the RLM might help | What would falsify the value |
|---|---|---|
| Retrieval/reranking | Use semantic scores to inspect candidate alternatives and expand evidence, without confusing top-k with full coverage. | Strong lexical/full-context baseline matches final answers with less cost, or rare evidence is lost. |
| Evidence and counterexample analysis | Materialize claim×source judgments with provenance, keep conflicting hypotheses, choose further inspection adaptively. | Extra judgments merely restate the draft or cause confident wrong conclusions. |
| High-impact verification | Trace which judgments affect many downstream decisions and inspect consequential assumptions, including confident ones. | Verification misses high-fan-out errors or costs more than directly checking the important source. |
| Reusable structured views / entity joins | Ask for typed features, use exact code for supported joins and duplicate expansion, retain ambiguous residual pairs. | The supplied feature representation cannot express the relation, or semantic error amplification overwhelms savings. |
| Extraction and parser repair | Generate deterministic extraction for regular cases and inspect uncertain/drifted regions semantically. | Unseen formats silently disappear or a static parser plus ordinary LLM is just as good. |
| Cross-context memory assistance | Suggest associations, conflicting evidence and stale-source checks without turning suggestions into authoritative memory. | Retrieval/review usefulness does not improve or uncertainty/provenance is lost in a stored summary. |
| Orchestration | Choose exact code, typed questions, generative calls or stopping based on observed workload and consequences. | A competent Python loop with the same models, cache and budget matches it. |

The operators themselves are not novel. LOTUS, Palimpzest, DocETL and other systems already address semantic operations and adaptive execution. The research hypothesis is useful adaptive control over persistent evidence with interchangeable kinds of work. Native availability is necessary for trying it, not evidence of superior quality. See the primary-source research in `docs/research/jev-engine-design-20260916.md`.

## Current practical evaluation

The [seven-task development panel](../bench/jev/usefulness/README.md) and [frozen live plan](../bench/jev/usefulness/LIVE_PLAN.md) compare full-context self-review with full-distribution-informed review through the actual native CLI. They use source-backed developer decisions, not synthetic gold labels alone. The plan also includes one small retrieval diagnostic. This panel cannot establish automatic planning, large-corpus performance or superiority to matched Python. The [actual native run](../bench/jev/usefulness/RESULTS.md) improved required-source coverage from 2/4 to 4/4 in one top-4 retrieval diagnostic, but did not improve final-answer quality over full-context self-review. Both answer arms missed the same pre-transfer privacy safeguard. That negative result is why generic judging is not made mandatory.

A separate [exact-source selection study](../bench/jev/span_selection/RESULTS.md)
completed 18 tasks through the actual installed native evaluator with identical
candidates and questions in both arms. Jev scored 17/18 versus 18/18 for the
generative selector. Its median observed block latency was 1.162s versus 2.529s,
but it confused ambiguity with absence, so both the predeclared quality and
benefit bars failed. No threshold or extra repair call was chosen after that
failure. The [consolidated angle and application portfolio](research/jev-angle-of-attack-20260917.md)
separates these observations from untested orchestration, memory and ETL ideas.
