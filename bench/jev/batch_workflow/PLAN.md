# Checkpointed long-source batch: product acceptance

This is a new product workflow, not a rerun or replacement of the closed model-authored CUAD comparison. The earlier live failures and offline grades remain unchanged.

## Deliverable

`az jev batch` executes an explicit JSONL work list using the existing optional native engine. It preflights the entire plan, binds the source and limits, persists each result, finalizes in native code and skips durable completed requests on resume. An ambiguous in-flight request is never automatically retried. The companion stdlib example prepares byte-exact windows and exports all outcomes for human review.

## Bounded real acceptance

Use the already-public 102 CUAD test contracts from `bench/jev/long_task/fixtures/corpus.json`, without reading gold, annotations or previous predictions. Export contract texts verbatim to explicit files, in retained source order. Prepare the files using `examples/jev_batch_review.py` and one fixed question:

> Does this source window contain an operative clause that restricts a party from assigning or transferring this agreement or its contractual rights or obligations without another party's consent? Mere mentions of successors, permitted assigns, ownership, or assignment of intellectual property alone do not satisfy the question.

This is a source-window review queue, not a legal determination, a new calibration claim or a matched quality comparison. A split can separate qualifications or cross-references. Every input window and unknown must remain in exported accounting.

One new live job only after native/injected and public CLI tests pass. Caps: at most 256 requests, 2,000,000 reported input tokens, 600 wall seconds from original job creation, at most 20 seconds per request. The observed prepared plan must fit these caps or stop before admission. No generative calls, automatic retry, hidden fallback, threshold tuning or replacement campaign after provider failure. Cost is reported as usage, not an invoice.

## Observable acceptance

1. Whole source is represented by byte-exact windows with source hashes and offsets. No silent truncation.
2. The native command actually invokes typed transport and produces a complete source-linked result list, not a generated finalization program.
3. Every response and all known/unknown usage is persisted before the next request.
4. Invoke completed resume with the credential unavailable. It must return the same completed results with zero new requests.
5. Actual CLI refuses changed input/config/limits, invalid plans, unsafe outputs and ambiguous intents before transport. Injected transport exercises success, failure, budget crossing, interruption and resume.
6. Produce a human-reviewable report retaining raw probabilities and exact source text. Inspect examples for relevance and report deficiencies, without treating concentration as truth or asserting general accuracy.

The test is successful as a product workflow only if the actual end-to-end command completes and result export/resume work. Historical recovered-output timings are not a baseline. No inference speedup, improved task accuracy or automatic RLM-planning claim follows from this acceptance.
