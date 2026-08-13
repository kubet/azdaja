# OOLONG benchmark fixtures

Private development fixtures from `oolongbench/oolong-synth`, validation split. `context_len` is the dataset's tokenizer/window construction length, not UTF-8 bytes.

- `row-645.json` / `context-131072.txt`: subset-by-month exact ham count, gold `Answer: 132`; cheap diagnostic.
- `row-650.json` / `context-1048576.txt`: least-common label, gold `Label: ham`; saturated/guessable smoke only.
- `row-651.json` / `context-1048576.txt`: full exact ham count, gold `Answer: 8638`; primary hard task.

Every row binds its context filename, SHA-256, byte, character, and line counts. `run.py` fails closed on mismatches, API-key-like environment variables, ambiguous OAuth routing, wrong output format, stale skill config, or a missing explicit inference acknowledgement.

The controller executes arms serially in a deterministic frozen order with fresh homes/sessions and GPT-5.6 Luna at medium reasoning over subscription OAuth. Each arm receives a random read-only context filename and the same official question; wrapper instructions differ by product and are hashed. Native jcode and Prime retain their ordinary file-analysis tools. The azdaja arm invokes the staged `solo` product directly, eliminating an unrelated outer-agent loop while preserving the same model, reasoning level, fixture, scorer, and timeout.

Retained artifacts are owner-only, credential-redacted stdout/stderr and azdaja model/solo traces; copied OAuth homes, task copies, histories, and runtime state are deleted after each arm. The tool-event scan catches obvious network or external-dataset commands but is **post-hoc detection, not OS containment**. Until the native-tool processes run behind an enforceable filesystem/network sandbox or broker, these runs are diagnostic and cannot support a superiority claim.

Example (performs subscription inference):

```bash
python3 bench/oolong/run.py \
  --row bench/oolong/row-651.json \
  --output bench/results/oolong-1m.jsonl \
  --repetitions 3 --timeout 1800 --yes-run-inference
```

A frozen suite may instead use `--suite-manifest MANIFEST --resume`. The controller creates an immutable owner-only schedule before inference, binds every run to fixture/candidate/controller/executable hashes, rejects duplicate or out-of-order prefixes, and defers gold scoring until every scheduled run is terminal. Crash-orphaned claims fail closed rather than risking duplicate inference.

After a suite is terminal and its deferred scores exist, `report.py` independently verifies the frozen schedule and run IDs, raw JSONL hash, every claim/completion receipt, manifest fixture hashes, and every recomputed strict score before reporting. It reports fixed-denominator completion/exactness/failures, all-attempt latency and token coverage, route integrity, paired both-correct efficiency ratios, and deterministic context-cluster bootstrap intervals. It refuses partial or tampered artifacts:

```bash
python3 bench/oolong/report.py /private/tmp/suite.jsonl \
  --suite-manifest /private/tmp/sealed-suite/suite-manifest.json \
  --bootstrap-iterations 20000 --pretty
```

No benchmark result is a release claim until repeated unseen items establish accuracy noninferiority and paired token/latency advantages.
