# Model-availability amendment, before semantic observations

Date: 2026-09-16, 18:45 UTC. Applies to a new named run, `pilot-alias-20260916`, not a rewrite of the first receipt.

## Observed setup failure

The original run at commit `71f2c22` requested `jev-1.12` and stopped after exactly one inference attempt with HTTP 400. No validated judgment or token usage was returned. Its immutable receipt is [pilot-20260916.json](../../bench/jev/results/pilot-20260916.json). This is a setup/service rejection, not a semantic error and not evidence of model efficacy. The root's assumption that this concrete identifier was available was not verified before the request.

A single subsequent **non-inference** `GET /v1/models` returned HTTP 200 and advertised only `jev-latest` and `jev-preview`. The endpoint was checked in the official `typesafe-sdk` 0.6.0 wheel's `_core/constants.py`, inspected as inert source without installation. Only sanitized model names and a body hash were preserved in [model-discovery-20260916.json](../../bench/jev/results/model-discovery-20260916.json). The unavailable pin is consistent with the 400, but its cause is not proven because the transport deliberately discarded the error body.

## Explicit decision

The original protocol already permits an explicitly selected alias if only an alias is available, provided alias drift remains unresolved. Use **`jev-latest`** for one new screening run. Do not use `jev-preview`, probe additional versions, or hide this change as a retry of the original run.

Unchanged:

- Fixture SHA-256: `3fe530372fefe2dd62e823bad9eeec8aad10a1783328a502805851ebd733929f`.
- Prompt, question schema, option ordering, policy digest, acceptance thresholds and stopping rules.
- Sequential smoke, challenge, prospective holdout, and invariance stage order.
- No automatic retries, fallback, private repository data, or model replacement after a failure.
- No semantic outcomes have been observed or used to choose this amendment.
- Existing core runtime and ordinary `llm` behavior remain unchanged.

Resource envelope: at most 79 inference attempts in the new run, at most 80 combined with the first rejected request, within the original 96-attempt ceiling. The existing per-request, byte, question, token, and elapsed-time limits remain enforced. Usage from the rejected request is unknown, not certified zero. The metadata GET is separately recorded and is not an inference request.

Record the requested alias and returned `model` field on every response. The strict response contract still requires that field to match the requested identifier. If the service exposes no immutable deployment revision, these results cannot be claimed reproducible against a permanently pinned Jev revision. Any further setup/transport/schema failure stops this run without more discovery-and-retry cycles. A semantic stop is final for this frozen policy, not a trigger to tune thresholds or wording.

This amendment does not relax the acceptance bar. It corrects account availability before any semantic evidence exists. The first failed run stays part of the research record.
