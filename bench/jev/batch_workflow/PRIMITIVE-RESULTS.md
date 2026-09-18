# Three native primitives: compatibility, not accuracy

The separately declared one-request check in `PRIMITIVES.md` completed once through
`azdaja jev batch`. No retry or generative call occurred. It used the foundation
source `e0a828e` and binary `679adb6c...0cb19`, requesting `jev-latest` and receiving
provider-reported `jev-1.13.0`.

| Requirement | Actual observation |
|---|---|
| Noul, Choice and Score in one native request | One completed request, three answers with their expected types. |
| Choice domain and distribution | `workaround`, probability 1.0. All three options retained. |
| Score domain, legend and expectation | Score 1.0, full three-level legend, distribution `{0:0,1:1,2:0}`. |
| Preserve disagreement, not a success-only semantic story | Noul returned **0.47** for an explicitly described browser workaround. Choice and Score agreed with the illustrative interpretation. This is not an accuracy or calibration pass. |
| Account for the complete request | 468 reported input tokens, 77 output, one attempt/success, no unknown usage. Native evaluate wall 808,053,000 ns. Billing unknown. |
| No-key native restart | Completed replay made zero requests and preserved every job file. Re-exercised through both current TypeSafe and feature-off binaries. |
| Fail closed before replay | Seven provider-free tests cover altered/missing files, domains, legend, expectation, request/usage binding, links, duplicate keys, nonfinite JSON and the actual outside-repository default CLI. |

Replay retained evidence without any binary, key or network:

```sh
python3 -B bench/jev/batch_workflow/primitives.py
# Optional actual current-binary completed replay. Still no key or new requests:
python3 -B bench/jev/batch_workflow/primitives.py --binary /path/to/azdaja
```

The thirteen original artifacts and controller text are hashed in
`primitives-20260918/RETENTION.json`. The verifier checks source/request/result and
usage consistency. It does not independently authenticate the provider, verify
historical binary bytes on another machine, or turn confidence into permission to
act. No further inference is authorized by this receipt. Earlier closed panels
and the original 138-window long job are unchanged.
