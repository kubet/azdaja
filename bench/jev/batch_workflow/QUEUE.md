# Read-only source review queue

The optional `examples/jev_review_queue.py` turns an existing batch job into a
standalone HTML review file. It makes no model request. It does not enable Jev,
change configuration or turn a probability into an approval.

```sh
python3 examples/jev_review_queue.py \
  --plan ./review-plan --job ./review-job --output ./review.html
```

## Acceptance observed on 2026-09-18

| Requirement | Check and observed result |
|---|---|
| Useful ranked review without throwing evidence away | All 138 retained windows from 102 contracts appear. Completed results rank by raw Noul then stable ID. Full source, question, hashes and byte offsets remain visible. |
| Unknown work cannot disappear or masquerade as success | Actual partial-job export contains 137 completed windows plus one explicitly unknown/in-flight window. Synthetic tests also cover failed and never-attempted windows. |
| Comparable judgments only | Rehashed mixed-question plans are refused before rendering. Only the example's identical single Noul `match` question is admitted. |
| Exact source in the real browser | System WebKit rendered full and partial 4,779,822-byte queues. Every one of the 138 DOM source hashes matched its original window in each case. CRLF, Unicode and hostile markup also preserved their exact text. |
| Safe, readable local UI | No script/active injected element or external page resource was observed. Only fixed, SHA-authorized CSS is permitted. Expanded text wraps without horizontal overflow at the tested 1100-pixel viewport. Source coverage starts collapsed. |
| No overwrite, leakage or silent source mutation | Occupied/dangling outputs, source/response changes, mixed meanings and NUL text are refused. Private temporary snapshots are cleaned on success/failure. Output is owner-only. |
| Work with or without the optional transport compiled in | Both actual installed modes passed 23 composed commands/checks, including attach-without-enable, ordinary session, no-key full/partial/failure resume, all-three-primitive replay, full/partial HTML export and uninstall. HTML bytes match across modes. |
| Portable preparation and regression coverage | 46 scoped Python tests pass. The 19 queue and 15 composition/primitive checks also pass on Python 3.9. The unchanged first-party proof verifier passes. |

`queue-20260918/RETENTION.json` binds the 14 retained receipts, test outputs and
WebKit driver to the tested source. Full HTML is regenerated instead of storing a
second corpus copy. The completed HTML hash is
`62159e2bdefadd6f09138da04aa3caadaebee061a1038d61a9745f2f8c30c208`.
The partial HTML hash is
`3dc8a4b6e2e868b5b896852f34398b67d38a76d8a8f4a3497b40851c123d83b5`.

Browser acceptance used an isolated nonpersistent **WebKit** process. Firefox,
Chromium and mobile browsers were not tested. No user browser profile or settings
were read or modified. The original exporter, 138-window job and historical
failed planner studies are unchanged. Corpus attribution remains in
`../long_task/ATTRIBUTION.md` and accompanies the hosted full-text artifact.

This is an opt-in, local manual-review utility, not a multi-tenant service,
calibrated ranking guarantee, autonomous legal review, or a new Jev efficacy
result. The API compatibility check is separately reported in
`PRIMITIVE-RESULTS.md`, including its Noul semantic disagreement.
