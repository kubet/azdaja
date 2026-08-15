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


## Isolated V58 low-reasoning campaign

The prospective V58 campaign does **not** retarget the historical medium-reasoning controller above. It uses versioned files `v58_run.py`, `v58_validate.py`, `v58_score.py`, `v58_report.py`, and `v58_rehearsal.py`. The inference process can read only the goldless public manifest at `/private/tmp/azdaja-v58-oolong-public-v1/manifest.json` (SHA-256 `bbf624cec245d971879ad3c1058148a1d188eadeb546f2cc6f860f8c74584eb4`). Expected answers remain in the detached encrypted custody image and are accepted only by the one-shot scorer after independent terminal validation.

The V58 runner admits only the evaluated three-component candidate, the pinned Jcode v0.75.3 executable, Luna/low, seed `20260813`, timeout 600, and the fixed production root `/private/tmp/azdaja-v58-oolong-frozen-v1`. Its 78-job order is candidate 1–10, both controls for those fixtures 11–30, candidate 31–46, then remaining controls 47–78. After candidate row/claim/done 10 it durably seals pass or abort. Abort exits 3 and permanently refuses resume before OAuth or further inference. The inference runner never opens gold and never scores.

Before any authorized production launch, run the OAuth-free synthetic rehearsal at a fresh root. It proves exact 78-row/claim/done/artifact validation, independent no-gold validation, the 25/24 report boundary, a sealed abort at 10, and pre-OAuth resume refusal. The resulting receipt binds the runner, historical adapter, validator, scorer, reporter, rehearsal, public suite, candidate components, Jcode, Prime, Node, kernel Python, platform, schedule, Luna/low profile, and fixed production root.

Production remains blocked unless the separately audited receipt is supplied and explicit launch authorization is given. The required post-inference sequence is: independent goldless `v58_validate.py`; one attachment of the committed gold image; one `v58_score.py` invocation; immediate gold detachment; then one `v58_report.py` invocation. A valid report passes continuation only at candidate execution ≥25/26, strict exact ≥24/26, and all integrity/route/leak/cleanup gates. Even PASS does not authorize RAH, publication, release, or a superiority claim.
