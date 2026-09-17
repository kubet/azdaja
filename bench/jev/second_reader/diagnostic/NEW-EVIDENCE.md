# New diagnostic evidence: flat-02, 2026-09-17

This is an independent offline check of the three completed attempts under
`bench/jev/second_reader/results/diagnostic-20260917`. It performs no semantic
grading, does not alter the old panel, and does not infer the discarded
historical body. No production file was changed.

## Identity and retention checks

The original request file was parsed with duplicate-key rejection and then
serialized with the repository's canonical JSON rules.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| Original request file | 31,717 | `d2e67d0385c8f49524b1bc55d3bc80bebb8838a5f6b78cdbd204dd6eaa7decf0` |
| Canonical parsed request wire | 31,716 | `b167b440de13e414a35e6c3b244d7cd8eb05465c1176c1a21ed24d276653d251` |

All three receipts carry the original request-file hash and the canonical wire
hash. Thus the wire hash matches the canonical serialization of the original
request. It does **not** equal the raw request-file hash because the file has
one additional byte, consistent with its trailing newline. This is a request
serialization distinction, not a request-content mismatch.

The three retained raw bodies and receipts independently hash as follows:

| Attempt | Receipt SHA-256 | Raw body SHA-256 | Raw bytes | Receipt/raw hash and size checks |
| ---: | --- | --- | ---: | --- |
| 1 | `928e82fa3bbfd8e1bcb8d4c674fc226c0298e25366efb4efb10f01ebc9bf14b2` | `3f718f9067c93fb08fd5cb70890956a3234c463f742b59ae126ca0688b085a4b` | 3,098 | pass |
| 2 | `2722a27e6cefcdec79ba57f6efccbd0119ac8c782ae04bd86873959df54b6bdc` | `3fbdae902ec9a3d8f0725841a9113168298f3184293993075d5ba0eb4575c1ae` | 3,085 | pass |
| 3 | `38b33347b6cec108876c619e42e26d81dbbdc8b4fe1dc0b8c94080039e0f37b5` | `b0f2aaf75823dcbb57528bc16bed946ab8f3d4a267861dc190e26d124cd6d8f3` | 3,093 | pass |

The raw sidecars and receipts are mode `0600` for all three attempts.

## Response and accounting checks

Every attempt independently passed strict duplicate-safe JSON parsing, had
model `jev-1.13.0`, exactly the 25 request IDs, and complete probability
domains. Each had 24 four-option Choice questions and one three-option Choice
question. Every receipt reported:

- `accepted: true`, `error: null`;
- one attempt and one provider request;
- 25 questions, 8,966 known input tokens, zero unknown input-usage requests;
- `poisoned: false`, `cache_hits: 0`, `cached_requests: 1`;
- response usage of 8,966 input tokens and 1,245 output tokens;
- no semantic grade and no repair of the original panel.

Per-attempt elapsed times were 1.065240459s, 0.908243709s, and 0.917208166s.
The campaign summary reports 3.149323249992449s and 26,898 known input tokens.
The three-call and 100,000-token campaign caps were not exceeded.

## Decimal and actual Rust-float sum checks

The exact-decimal audit and the Rust-order binary64 audit were kept separate.
The decimal audit found these largest absolute sum errors:

| Attempt | Largest Decimal error | Question ID |
| ---: | ---: | --- |
| 1 | `3E-17` | `f026` |
| 2 | `0` | none |
| 3 | `1E-16` | `f039` |

The overall exact-decimal maximum was `1E-16`.

Re-parsing the unchanged raw JSON as ordinary binary64 values and accumulating
in the same insertion order as `src/judge.rs` produced:

| Attempt | Largest actual f64 error | Question ID | ULPs at 1.0 | `<= 1e-6` |
| ---: | ---: | --- | ---: | --- |
| 1 | `0.0` | `f049` (tie for maximum) | 0 | yes |
| 2 | `0.0` | `f049` (tie for maximum) | 0 | yes |
| 3 | `2.220446049250313e-16` | `f034` | 1 | yes |

Therefore all 75 new Choice distributions are within the current Rust
validator tolerance. The largest observed binary64 residual is one ULP at
1.0, far below `1e-6`. This demonstrates that these three new bodies are
accepted by the current unchanged validation path. It does not reconstruct,
locate, or explain the old rejected body.

## Warranted claims

1. Three newly authorized, separately retained calls used the same parsed
   flat-02 request and canonical wire identity, remained within the stated
   diagnostic budgets, and were accepted by the unchanged instrumented Rust
   engine.
2. The three new raw bodies are retained and hash-bound. Their actual Decimal
   and binary64 sum behavior is known. No malformed distribution was observed
   in these three attempts.
3. The old evidence still supports one previously rejected 25-question batch,
   not 25 failed responses. Its actual body and exact failure cause remain
   unrecoverable.
4. The prior admission failure is appropriately described as a setup/orchestration
   failure: the output parent was absent before child/provider spawn, with zero
   provider calls. The separate setup-only recovery and retained original claim
   show a procedural correction, not a validator, TypeSafe, or provider defect
   fix.
5. No provider defect report is warranted from this evidence. A defect report
   would require a reproduced malformed response or transport defect, and none
   was reproduced here.

## Claims not warranted

These results do not establish that the old failure was caused by rounding,
serialization, TypeSafe, Jev, Azdaja, one question, or the provider. They do
not establish that a defect is absent, that the model is reliable in general,
that the new responses are semantically correct, or that the old 25 judgments
can be repaired. The differing raw hashes show only that the accepted calls
were distinct responses, not that their semantic decisions should be compared.
No quality, calibration, cost, or benchmark claim was computed.

The three-call diagnostic cap is now consumed. The correct stopping point is
to preserve these hash-bound raw artifacts privately and leave the old failure
incomplete. Further work would need a separately authorized reproduction and
must not be presented as reconstruction of the discarded body.
