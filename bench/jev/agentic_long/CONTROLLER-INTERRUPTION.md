# Controller interruption, not a model retry

The single pair in [PLAN.md](PLAN.md) was admitted before calls. The outer tool killed its Python controller after 600 seconds while the plain OpenCode process, in its own process group, survived. The tool timeout is retained as a measurement infrastructure failure.

At 835 seconds from the original launch, an independent guardian resumed monitoring **the same PID, process group, executable and working directory**. It did not invoke a model, change the task, extend the original 1,800-second deadline, or raise the $8 observed-cost stop. At that point the retained stream contained 77 completed steps, $1.9355296 known cost, no missing-usage records and no reader attempts. The gap remained inside the declared limits, but physical provider usage remains an observed lower bound.

The original parent's OS exit status cannot be recovered by the guardian. A completed artifact set must therefore be reported separately from process exit success. The original timeout and supervision gap are not erased by later artifact verification.

The Azdaja arm had not started. Its first already-admitted invocation may proceed only after the plain process group has stopped, its private credential copy is removed, original credential bytes remain unchanged, and every frozen input is rechecked. An exclusive continuation intent must prevent a second invocation. It receives the same task, model, configuration, reader implementation and budgets as originally sealed. No arm is restarted or extended.

This handling is an operational deviation from the initial controller. It prevents a clean causal speedup claim from this one sequential pair. The useful observations remain completed artifacts, verified byte evidence, observed time and usage, failures, and whether Azdaja was actually used. No new Jev arm or replacement campaign is admitted.

The measured instruction snapshot is the sealed `skill.md`, not subsequently edited repository guidance. The later explicit precedence sentence in the repository is not retroactively attributed to this measurement.
