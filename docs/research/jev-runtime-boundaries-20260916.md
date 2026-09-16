# TypeSafe Jev runtime boundaries

_Date: 2026-09-16_

## Executive recommendation

Use a separate, opt-in experiment CLI first. Do not replace `llm` or `llm_batch`, and do not make Jev a provider selected by `sub_llm_cmd`. The smallest clean core integration, if the experiment proves useful, is a new host-owned external function exposed only in a dedicated capability profile, implemented beside the existing external dispatch in `src/lib.rs`, with a typed Rust request/response adapter and an explicit configuration section. The semantic call site should be a high-value RLM leaf that already has bounded records and a closed-world label/question set, not the root evaluator and not a general replacement for model calls.

The Jev endpoint is an HTTP POST `/v1/systemone`. It consumes structured `state`, `model`, and `questions` containing typed `Noul`, `Choice`, and `Score` values, and returns typed probabilities. It is therefore a classifier/scorer boundary, not a text-generation provider boundary.

## Observed architecture and exact extension points

A provider-neutral host name such as `judge` should select this optional adapter through a capability profile, rather than bake a Jev-only API into ordinary evaluator code. Provider-specific names below are sketches, not implemented public interfaces.

### Host configuration

`src/lib.rs:658-771` defines `Config`, loaded from TOML with `deny_unknown_fields`, defaulted, then validated before runtime use. Existing relevant controls are:

- `sub_llm_cmd` and model/provider fields, which are generation-provider concerns.
- `sub_timeout`, `cell_timeout`, `idle_timeout`.
- `max_calls_per_cell` and `max_depth`.

Adding Jev as another value of `sub_llm_cmd` would create lock-in and incorrectly model a typed HTTP scorer as a text provider. Prefer a nested, default-disabled semantic-operator configuration with a replaceable provider selection and a non-serializing secret source. The Jev implementation should have a fixed or explicitly allowlisted HTTPS origin, not a generic arbitrary-URL capability. If the host must accept an API key, read it from an explicitly named environment variable or OS secret mechanism, never from ordinary serialized `Config` or prompts. Configuration validation must reject malformed enabled settings before any request can be attempted.

### External-function dispatch

`src/lib.rs:5680-5940`, especially `:5804-5936`, is the current Monty host boundary. It dispatches `llm`, `llm_batch`, `llm_batch_fresh`, and the private semantic batch function, parses arguments, increments call accounting, enforces semantic phase budgets, calls `call_many_items`, and converts provider results into strings or batch error objects.

A Jev hook should not enter this existing match arm. Add a separate name, for example a private capability-gated `_az_jev_systemone` or a public-but-explicit `jev_systemone`, with:

1. exact positional/keyword arity;
2. conversion from Monty values to a bounded typed Rust request;
3. typed response decoding and schema validation;
4. a separate Jev call counter and deadline budget;
5. fail-closed error propagation, never a synthetic probability or generated-text fallback.

Keep the existing `llm` and `llm_batch` path byte-for-byte contract-compatible. In particular, do not route Jev through `parse_call`, `call_many_items`, or `batch_item_value`: those APIs intentionally return text and have partial batch-success semantics that are unsuitable for a probability vector.

### RLM semantic leaf location

`src/lib.rs:7080-7373` contains `call_many_items`, including `RLM_DEPTH` checking, prompt count limits, worker bounds, provider setup, retry behavior, and ordered result storage. This is a provider/text batch mechanism, not the right abstraction for Jev.

The useful Jev insertion point is one semantic leaf above this machinery, where an RLM operation has already produced a bounded set of records and an explicit question/model vocabulary. Existing semantic work is visible in `main.rs` and e2e tests around the semantic manifest/classification/adjudication path. The best first leaf is the narrow classification/adjudication decision that already has exact item accounting and closed-world label codes. Convert that leaf's structured records into `state/model/questions`, invoke Jev once for the shard or leaf, then map returned typed probabilities back by stable item/question IDs. Do not replace the root `solo`/RLM turn: the root still owns orchestration, projection, finalization, and ordinary model behavior.

A Jev leaf must receive an explicit host capability and should be unavailable in ordinary cells unless the host deliberately enables it. `RLM_DEPTH` and the existing projected-manifest rules remain relevant. Jev must not become an indirect recursive escape hatch.

### Subprocess/environment boundary

`src/lib.rs:10205-10251` defines a provider environment allowlist and `configure_provider_environment`. This protects subprocess provider calls, but it is not a suitable place to smuggle a Jev key. An HTTP client in the host should receive a key through a narrowly scoped credential lookup, redact it from errors/traces, and never expose it through Monty values or the provider environment allowlist. If the experiment CLI is used, pass only an ephemeral credential reference or inherited dedicated environment variable and keep it outside prompts and captured model traces.

### Existing deadline and accounting behavior

`Config.cell_timeout` is enforced by Monty resource limits in `run_cell` and related cell-loading paths. Provider calls also have `sub_timeout`. Existing semantic calls reserve total and phase-specific budgets before provider entry (`external` around `:5853-5887`), and tests verify that an over-budget semantic batch does not enter the provider (`tests/e2e.rs:3715-3761`). Jev should follow the same preflight-before-network rule, but with independent counters so enabling Jev cannot consume or alter `llm`/`llm_batch` allowances.

## Proposed typed Jev boundary

Define an internal Rust-only adapter, conceptually:

```text
JevSystemOneRequest {
  state: bounded string, object, or array,
  model: concrete version string, e.g. "jev-1.12",
  questions: ordered map<question_id, tagged Noul/Choice/Score declaration>,
}
JevSystemOneResponse {
  model: concrete version string,
  answers: map<question_id, tagged validated answer>,
  usage: { input_tokens: integer | null, output_tokens: integer | null },
}
```

The adapter should enforce:

- maximum serialized input bytes and maximum numbers of records, questions, and choices;
- finite numeric values only, with explicit probability range and normalization policy;
- stable IDs and exact cardinality, including duplicate IDs rejected rather than silently deduplicated;
- `Noul`, `Choice`, and `Score` represented as tagged types, not arbitrary JSON strings;
- response question IDs and occurrence indices matching the request exactly;
- no unknown response fields if the Jev contract is closed-world, or an explicitly documented ignored-field policy;
- no partial response accepted;
- no fallback to `llm`, local heuristics, or generated text on decode, transport, timeout, or schema failure.

The HTTP client should have a connect/request deadline bounded by the host Jev deadline, a response byte cap, one request per logical leaf/shard unless explicitly budgeted otherwise, and no automatic retry unless retries are counted in the Jev call budget and duplicate accounting is preserved. Keep the HTTPS origin fixed or explicitly allowlisted and activation default-disabled. The API key should be sent only in the intended authorization header and never logged.

## Exact duplicate and occurrence accounting

Do not use a `HashMap` keyed only by semantic content. Preserve an ordered occurrence ledger:

```text
Occurrence { occurrence: usize, stable_id: String, question_id: String, payload_hash: ... }
```

Before the request, assign occurrence numbers in input order. Validate duplicate stable IDs and duplicate question IDs according to the contract. If duplicates are allowed semantically, retain each occurrence and require one response for each occurrence. After decoding, compare the response multiset and ordered occurrence ledger, then project results back by occurrence. Counts must be checked at four boundaries: input records, encoded request entries, decoded response entries, and final projected outputs. This prevents a scorer from silently collapsing duplicate questions or records.

## Options

### Option A: separate experiment CLI, recommended first

Add a small CLI or research binary that reads a versioned JSON fixture/stdin request, validates it with the same typed adapter, performs the optional POST, validates the typed response, and writes a deterministic JSON result. It should have explicit `--enable-jev`, endpoint/key-source flags, byte/call/deadline limits, and a dry-run validator mode. It can exercise real semantic leaf fixtures without changing the production evaluator or Monty external namespace.

Advantages: zero network when the core runtime is unchanged, easy golden fixtures and malformed-response tests, no `llm` contract regression, easy comparison against current semantic output, and clear evidence before granting a runtime capability. Hazard: fixture drift unless the request schema is shared with the future core adapter.

### Option B: private capability-gated host function

After the experiment, expose `_az_jev_systemone` only to the semantic leaf capability profile. Keep the adapter and accounting in a separate module; the `external` match arm should only validate Monty input, check capability/config/budget, call the adapter, and return a typed structured Monty object or a fail-closed error. This is the smallest production integration.

Advantages: no provider abstraction pollution and no changes to `llm`/`llm_batch`. Hazards: Monty conversion complexity, capability leakage to arbitrary cells, and pressure to expose a generic JSON escape hatch. Mitigate with a narrow schema and private name.

### Option C: Jev as a `sub_llm_cmd`/provider

Reject for now. It conflates typed probabilities with generated text, would force lossy serialization, risks changing retries and failure semantics, and makes endpoint/key selection look like ordinary model-provider selection. It also invites accidental Jev calls whenever existing `llm` code runs.

### Option D: root evaluator replacement

Reject. The root has orchestration and finalization responsibilities and is the highest-risk location for changed behavior, network activation, and accounting regressions. Jev belongs at a bounded semantic leaf.

## Test plan

1. **Disabled/no-network:** default config and `enabled = false` must not create a socket, resolve DNS, read the key, or invoke the Jev adapter. Add a test with an unreachable endpoint and a network-attempt marker.
2. **Explicit enablement:** no request occurs unless both host enablement and the required credential/endpoint policy pass. Invalid enabled configuration fails before evaluation.
3. **Typed request fixtures:** golden fixtures for `Noul`, `Choice`, `Score`, empty/large values, Unicode, non-finite numbers, maximum sizes, and deterministic serialization.
4. **Typed response validation:** reject malformed JSON, wrong tags, out-of-range/non-finite probabilities, missing/extra questions, wrong occurrence counts, duplicate response IDs, and reordered responses when ordering is contractually significant.
5. **Exact occurrence accounting:** repeated identical records/questions must either be rejected by policy or return one result per occurrence with stable projection. Test duplicate IDs, duplicate payloads with distinct IDs, and duplicate IDs at different positions.
6. **Budgets before network:** input byte, record/question, Jev-call, and deadline limits are checked before HTTP. Assert the server marker is absent on every preflight failure.
7. **Timeout/fail closed:** connect timeout, response timeout, oversized response, HTTP errors, invalid authorization response, and truncated body all fail without fallback or partial output.
8. **Isolation:** existing `llm`, `llm_batch`, and `llm_batch_fresh` tests remain unchanged and pass. Jev counters must not affect `max_calls_per_cell`, semantic classification/adjudication reserves, or existing ordered batch error behavior.
9. **RLM safety:** Jev is denied at excessive `RLM_DEPTH`; ordinary cells cannot access the private function; projected-manifest and authoritative-record coverage rules remain enforced.
10. **Leaf integration:** a representative semantic leaf fixture proves request construction, response projection, duplicate accounting, and final output while the root orchestration remains unchanged.
11. **Secret hygiene:** API key absent from errors, traces, subprocess environment captures, serialized config, and generated prompts.

Existing evidence to preserve includes `tests/e2e.rs:2508-2556` for ordered batch/fail-closed behavior, `:2610-2670` for callback depth and timeout behavior, and `:3715-3761` for semantic budget enforcement before provider entry.

## Hazards and non-goals

- Do not infer typed probabilities from generated text.
- Do not silently normalize malformed probabilities unless the Jev contract explicitly requires it and the normalization is deterministic and tested.
- Do not let HTTP retries create unaccounted occurrences or exceed call/deadline budgets.
- Do not put the API key in `Config`'s serialized fields, Monty state, prompts, traces, or error strings.
- Do not make endpoint reachability part of startup when Jev is disabled.
- Do not reuse `batch_item_value` because its string error envelope is intentionally different from typed fail-closed semantics.
- Do not add a generic arbitrary-HTTP external function.
- Do not edit the unrelated dirty files `src/jcode_gate.rs` and `tests/jcode_release_commands.rs` as part of this work.

## Decision

Build Option A first, sharing the typed request/response module and validators with a future Option B. Promote to Option B only after the experiment demonstrates stable schema, exact occurrence accounting, representative semantic-leaf value, and acceptable timeout behavior. Keep Jev opt-in, host-owned, independently budgeted, and leaf-scoped. Leave `llm`, `llm_batch`, and `llm_batch_fresh` untouched.
