# OOLONG benchmark fixtures

Private development fixtures from `oolongbench/oolong-synth`, validation split. `context_len` is the dataset's tokenizer/window construction length, not UTF-8 bytes.

- `row-645.json` / `context-131072.txt`: subset-by-month exact ham count, gold `Answer: 132`; cheap diagnostic.
- `row-650.json` / `context-1048576.txt`: least-common label, gold `Label: ham`; saturated/guessable smoke only.
- `row-651.json` / `context-1048576.txt`: full exact ham count, gold `Answer: 8638`; primary hard task.

Every row binds its context filename, SHA-256, byte, character, and line counts. `run.py` fails closed on mismatches, API-key-like environment variables, ambiguous OAuth routing, wrong output format, stale skill config, or a missing explicit inference acknowledgement.

The controller executes arms serially in a deterministic shuffled order with fresh homes/sessions and GPT-5.4 at medium reasoning over ChatGPT subscription OAuth. Every arm is instructed to use only the supplied context, with no network, external dataset, or precomputed-label lookup. Native jcode and Prime receive their ordinary file-analysis tools. The azdaja treatment explicitly activates the installed skill; task payload, fixture, question, model, reasoning, scorer, and timeout remain identical. Results must disclose this treatment difference. Raw trajectories in a persistent `--work-dir` are sensitive and private.

Example (performs subscription inference):

```bash
python3 bench/oolong/run.py \
  --row bench/oolong/row-651.json \
  --output bench/results/oolong-1m.jsonl \
  --repetitions 3 --timeout 1800 --yes-run-inference
```

No benchmark result is a release claim until repeated unseen items establish accuracy noninferiority and paired token/latency advantages.
