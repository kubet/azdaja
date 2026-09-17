# Offline validation record

Run on 2026-09-17 from the current working tree. No provider call, API key,
or credential store was used. The current `src/judge.rs` SHA-256 was
`0707a24c0a86426f51277e72e1d61e37482864c8d67b1b0ed10c5d5071c7bf39`.

## New diagnostic witness

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest bench.jev.second_reader.diagnostic.test_diagnostic -v
Ran 4 tests in 0.010s
OK
```

The witness reads retained files only. It distinguishes one rejected
25-question batch from zero individually observed failed responses, and
audits 11 retained successful typed observations.

## Existing actual Rust seams

```text
cargo +1.95.0 test --locked --offline --features typesafe --test judge_native
running 6 tests
test result: ok. 6 passed; 0 failed; 0 ignored

cargo +1.95.0 test --locked --offline --features typesafe --lib judge::tests
running 14 tests
test result: ok. 14 passed; 0 failed; 0 ignored
```

These are the existing public CLI and injected-transport Rust seams. They
exercise current validation behavior, but they cannot recover the discarded
historical response body. No source or test outside this directory was
modified by this diagnostic.
