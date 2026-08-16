# Azdaja Product-First Week Progress

## Current state

- **The product path, not benchmark score, is the release gate.** A shippable v0.1 means a stranger can install Azdaja with one command, point it at a 50 MiB UTF-8 file, and receive a correct answer without a process death. Any defect on that path outranks benchmark work; benchmark results belong only in the README appendix.
- The first blocking offline acceptance now exists in `tests/product_50mb.rs`. It serially generates exact 50 MiB build-log, repository-dump, and operations-transcript inputs, invokes the real `azdaja solo` CLI through a scripted local harness, and requires exact full-`ctx` answers. Each case has a 90-second outer watchdog, exactly one root call, zero child calls, one snapshot save, no snapshot load, no retained session, a private succeeded runtime trace, and a root prompt below 64 KiB with no host path or exact 100-byte source span.
- The complete locked Rust suite passes: 93 tests passed and one release-only stress test was intentionally ignored. Strict clippy, formatting, and release build pass. A real one-command source installation (`cargo install --path . --locked`) into an empty temporary root produced `azdaja 0.1.0`, and `doctor --caps` passed without provider access.
- A customized managed `config.toml` can now be uninstalled normally. Binary/SKILL changes and unknown files remain protected. The regression also preserves the existing customized-config upgrade behavior.
- Managed installation is now provider-free: it validates local evaluator capabilities but never executes the configured harness adapter. Live authentication remains an explicit `azdaja doctor` action. The literal `site/install` pipe is implemented in sealed mode and tested with local immutable-byte overrides: absent defaults and wrong hashes leave a fresh home untouched; a matching hash installs the managed binary without a provider call.
- The website no longer advertises a working curl command while `site/install` is deliberately sealed. The README labels the benchmark section as a non-gating appendix and states the current distribution boundary truthfully.
- The owner-authorized external RAH-199 continues independently and immutably. It does not gate v0.1 and is not rerun, retried, or used as product acceptance evidence.

## Strict next step

Close distribution, not another benchmark candidate: publish one immutable v0.1 source/tag or versioned binary set, make the repository/artifacts actually reachable to a stranger, replace the installer's deliberately empty public URL/hash defaults with those immutable bytes, and pass the literal public one-command flow from a clean supported machine. That receipt must cover version/capability checks, managed harness installation, the same three 50 MiB product cases, idempotent reinstall, customized-config uninstall, wrong-byte rejection, and cleanup after failure. Only then may the sealed website installer be opened.

After offline distribution passes, run a separately authorized live-harness smoke on fresh product fixtures to test model planning and authentication. The scripted acceptance proves CLI/load/evaluator/finalization behavior but does not claim live-model semantic reliability.

## Blocking

- GitHub is currently private and has no immutable v0.1 tag, release assets, or checksums; therefore no public remote one-command installation is claimed.
- `site/install` must remain fail-closed until real immutable release bytes and a clean-machine receipt exist.
- The current source install requires Rust 1.95 and a checkout; it is validated but is not the stranger-facing distribution goal.
- Hosted release automation and the supported OS/architecture matrix remain unproven.
- No benchmark optimization, frozen-candidate rerun, provider probe, or gold access may displace these product blockers.
