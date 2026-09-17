# Exact-source pre-FINAL claim screening

`python3 -B -m bench.jev.angle_lab.verifier.prepare` reads literal Git spans from ad5a9ef and emits one native12-question pack. Each claim has an explicit allowed-evidence set. `gold.json` is detached and grader.py grades actual external labels by exact IDs, not positional zip.

Matched arms are direct generative, typed Choice, no-review (retain every claim), and deterministic abstention (accept no claim). Measure contradicted/unsupported claims retained and supported claims rejected separately. To pass screening every label must match the reviewed source contract. No provider tokens or latency are fabricated in the grader; those come exclusively from the native receipt.

This measures atomic claim screening, not prose rewriting, a completed code repair, general verifier reliability, or permission for a mandatory FINAL gate. The generic review negative result remains unchanged.
