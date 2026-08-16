# Azdaja Product-First Week Progress

## Current state

- **The product path, not benchmark score, is the release gate.** A shippable v0.1 means a stranger can install Azdaja with one command, point it at a 50 MiB UTF-8 file, and receive a correct answer without a process death. Any defect on that path outranks benchmark work; benchmark results belong only in the README appendix.
- The first blocking offline acceptance now exists in `tests/product_50mb.rs`. It serially generates exact 50 MiB build-log, repository-dump, and operations-transcript inputs, invokes the real `azdaja solo` CLI through a scripted local harness, and requires exact full-`ctx` answers. Each case has a 90-second outer watchdog, exactly one root call, zero child calls, one snapshot save, no snapshot load, no retained session, a private succeeded runtime trace, and a root prompt below 64 KiB with no host path or exact 100-byte source span.
- The complete locked Rust suite passes: 93 tests passed and one release-only stress test was intentionally ignored. Strict clippy, formatting, and release build pass. A real one-command source installation (`cargo install --path . --locked`) into an empty temporary root produced `azdaja 0.1.0`, and `doctor --caps` passed without provider access.
- A customized managed `config.toml` can now be uninstalled normally. Binary/SKILL changes and unknown files remain protected. The regression also preserves the existing customized-config upgrade behavior.
- Managed installation is provider-free: it validates local evaluator capabilities but never executes the configured harness adapter. Live authentication remains an explicit `azdaja doctor` action. The literal `site/install` pipe rejects wrong hashes before HOME mutation and installs matching immutable bytes without a provider call.
- A clean locked release build produced the initial Apple Silicon macOS asset `azdaja-v0.1.0-darwin-arm64`: 6,434,288 bytes, SHA-256 `6b50716382ac35e4f2bc9fc3c1cc3db9ee059edde783b78dba21273bf626762a`, exact version/capability checks passing. The installer is now bound to that versioned GitHub release URL and digest; validation overrides require an explicit local test mode and cannot silently replace public bindings.
- The owner-authorized external RAH-199 continues independently and immutably. It does not gate v0.1 and is not rerun, retried, or used as product acceptance evidence.

## Strict next step

Close distribution, not another benchmark candidate: publish the prepared commit as immutable tag `v0.1.0`, upload the bound Darwin-arm64 asset plus `SHA256SUMS`, make the repository/artifacts reachable to a stranger, and pass the literal public one-command flow from a clean Apple Silicon macOS HOME. That receipt must cover version/capability checks, managed harness installation, the same three 50 MiB product cases, idempotent reinstall, customized-config uninstall, wrong-byte rejection, and cleanup after failure. Only then may the sealed website installer be opened.

After offline distribution passes, run a separately authorized live-harness smoke on fresh product fixtures to test model planning and authentication. The scripted acceptance proves CLI/load/evaluator/finalization behavior but does not claim live-model semantic reliability.

## Blocking

- GitHub is still private and the prepared tag/assets are not published yet; the remote command is not usable until that external publication completes.
- Initial binary support is Apple Silicon macOS only. Other platforms remain source-install only until separately built and validated immutable assets exist.
- Hosted release automation and broader OS/architecture coverage remain unproven.
- No benchmark optimization, frozen-candidate rerun, provider probe, or gold access may displace these product blockers.
