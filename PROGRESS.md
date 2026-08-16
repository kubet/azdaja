# Azdaja Product-First Week Progress

## Current state

- **The product path, not benchmark score, is the release gate.** A shippable v0.1 means a stranger can install Azdaja with one command, point it at a 50 MiB UTF-8 file, and receive a correct answer without a process death. Any defect on that path outranks benchmark work; benchmark results belong only in the README appendix.
- The first blocking offline acceptance now exists in `tests/product_50mb.rs`. It serially generates exact 50 MiB build-log, repository-dump, and operations-transcript inputs, invokes the real `azdaja solo` CLI through a scripted local harness, and requires exact full-`ctx` answers. Each case has a 90-second outer watchdog, exactly one root call, zero child calls, one snapshot save, no snapshot load, no retained session, a private succeeded runtime trace, and a root prompt below 64 KiB with no host path or exact 100-byte source span.
- The complete locked Rust suite passes: 93 tests passed and one release-only stress test was intentionally ignored. Strict clippy, formatting, and release build pass. A real one-command source installation (`cargo install --path . --locked`) into an empty temporary root produced `azdaja 0.1.0`, and `doctor --caps` passed without provider access.
- A customized managed `config.toml` can now be uninstalled normally. Binary/SKILL changes and unknown files remain protected. The regression also preserves the existing customized-config upgrade behavior.
- Managed installation is provider-free: it validates local evaluator capabilities but never executes the configured harness adapter. Live authentication remains an explicit `azdaja doctor` action. The literal `site/install` pipe rejects wrong hashes before HOME mutation and installs matching immutable bytes without a provider call.
- A clean locked release build produced the initial Apple Silicon macOS asset `azdaja-v0.1.0-darwin-arm64`: 6,434,288 bytes, SHA-256 `6b50716382ac35e4f2bc9fc3c1cc3db9ee059edde783b78dba21273bf626762a`, exact version/capability checks passing. The installer is now bound to that versioned GitHub release URL and digest; validation overrides require an explicit local test mode and cannot silently replace public bindings.
- The owner-authorized external RAH-199 continues independently and immutably. It does not gate v0.1 and is not rerun, retried, or used as product acceptance evidence.

- Repository, tag, prerelease, asset, and installer are public. Tag `v0.1.0` binds commit `021b79e76e5951dd6142b4c76e564ae41adb9504`; the public literal curl completed in a fresh HOME and installed the exact bound digest. The installed release binary then passed all three 50 MiB product cases in 31.19 seconds total, followed by idempotent reinstall, customized-config uninstall, and clean reinstall. Receipt `release/v0.1.0/public-receipt.json` SHA-256 `99989d2019db132c63e1d23c294c6b3d20af16762f97d0dc7394e90dccbc346b`.

## Strict next step

Run one separately authorized live-harness smoke on fresh non-benchmark product fixtures to test authentication and natural-language planning through the public installed binary. It must not reuse any frozen benchmark row or open benchmark gold. After that, expand immutable binary coverage beyond Apple Silicon macOS only when each platform passes the same public install receipt.

## Blocking

- The public scripted acceptance proves distribution, CLI, evaluator, exact computation, and cleanup; it does not prove live-model planning or harness authentication.
- Initial binary support is Apple Silicon macOS only. Other platforms use the locked Rust source install until separate immutable assets pass.
- Peak RSS is reported as a limitation rather than gated, and hosted release automation remains unproven.
- No benchmark optimization, frozen-candidate rerun, provider probe, or gold access may displace these product follow-ups.
