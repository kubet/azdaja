# Performance ledger

RULER inference rows now retain a fail-closed per-item ledger at
`arm_evidence.performance_ledger` for the `jcode-azdaja` arm. Controls use `null`.
The ledger is normalized from two already-retained authorities:

- `AZDAJA_MODEL_TRACE` v2: physical root/repair turns, inference milliseconds, and observed repair tokens.
- the unique absolute-EOF `solo_runtime` v1 row in `AZDAJA_SOLO_TRACE`: generated-program execs, in-memory checkpoint serialization/restoration, logical child prompts, and gross child-batch wall.

`exec_wall_ms` contains `sub_call_wall_ms`; do not add them. Snapshot fields describe
Monty in-memory `Dump` save/restore, not input-file I/O. Repair token fields are
`null` with `token_accounting_complete=false` if any repair usage is unobserved.
Missing, duplicated, malformed, unbound, partial, or internally inconsistent evidence
produces no normalized ledger and fails an otherwise-successful candidate item.

## Raw local smoke item

This is a non-subscription command-transport smoke, **not a latency benchmark**. It
exists to pin the emitted and normalized schemas without touching the frozen v38 run.
Every number below is bound to:

- candidate: `azdaja 0.1.0 (monty 0.0.21)` debug binary SHA-256 `928dd300bef91945c0f75db2a2896996a49458d58b0733086d8302abc4139a11`
- controller: `bench/ruler/run.py` SHA-256 `500aae5df22e84dbdd05d25dc1870e83ba0cd184ae165b9cb9a41487bc3f1d4a`
- scorer: `bench/ruler/score.py` SHA-256 `1cd3ebd65d38e3bfc8e1f8e4568ee53105d1ca903f6ea7138f68a86e1f69381c`
- item: `local-command-transport-ledger-smoke`, response `LEDGER_OK`, exit `0`

Raw absolute-EOF runtime row:

```json
{"schema_version":1,"event":"solo_runtime","request_id":"49475-1786664339960906000-1","outcome":"succeeded","exec_invocation_count":1,"exec_wall_ns":199333,"snapshot_save_count":1,"snapshot_save_wall_ns":633083,"snapshot_load_count":0,"snapshot_load_wall_ns":0,"sub_call_count":0,"sub_call_wall_ns":0}
```

Raw normalized per-item ledger:

```json
{"complete":true,"exec_invocation_count":1,"exec_wall_ms":0.199333,"repair_cost":{"cache_read_tokens":0,"inference_ms":0,"input_tokens":0,"output_tokens":0,"token_accounting_complete":true},"repair_count":0,"root_inference_ms":30,"root_turn_count":1,"schema_version":1,"snapshot_load_count":0,"snapshot_load_ms":0.0,"snapshot_save_count":1,"snapshot_save_ms":0.633083,"sub_call_count":0,"sub_call_turn_count":0,"sub_call_wall_ms":0.0}
```
