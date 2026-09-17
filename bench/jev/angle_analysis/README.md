# Retained six-angle results: offline replay

The live campaign is closed. Do not rerun it to seek better scores. Both frozen
admission markers are retained. The public replay never calls a provider:

```sh
python3 -B -m bench.jev.angle_analysis.report
python3 -B -m unittest bench.jev.angle_analysis.test_report -v
```

For a new JSON report, pass `--output /new/path.json`. Existing files and dangling
symlinks are refused. Requests, raw observations, both accounting ledgers, detached
gold and original method hashes are checked. Derived outcome files are rebuilt
from actual retained answers, not trusted as authoritative scores. Rehashed false
wins, altered baseline evidence, malformed probabilities and erased usage are
covered by negative tests.

This verifies recorded evidence, not provider authenticity, a live replay, or
immutable backend weights. Timing fields are preserved observations and cannot
be reproduced by offline grading. No live credentials or private runtime state
are included. The default attached key remains host-private.

Results and interpretation: [six-angle report](../../../docs/research/jev-six-angle-results-20260917.md).
Implementation and trust design: [agent wisdom](../../../docs/research/jev-wisdom-design-20260917.md).

Observed global totals: 10 typed HTTP requests, 279 questions, 56,094 input and
6,701 output tokens. Nine entered generative turns, 44,254 input and 4,199 output
tokens, plus one failed local setup admission. Typed documented-rate estimate
$0.002355948. Generative price and total billing remain unknown. All full semantic
promotion bars failed, despite a partial memory-handoff gain and faster bulk work.
