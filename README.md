<p align="center"><img src="azdaja-logo.png" alt="Azdaja logo" width="120"></p>

# Azdaja

Azdaja keeps complete source material in a local evaluator and gives language models a bounded working surface for code and semantic calls. Load once, compute locally, and send selected work to a model.

[CLI](docs/cli.md) · [Live proof](https://azdaja.dev/proof.html) · [Releases](https://github.com/kubet/azdaja/releases)

## Install

macOS 11+ on Apple Silicon and Intel, or x86-64 Linux with glibc 2.35+:

```bash
curl -fsSL https://azdaja.dev/install | sh
```

Choose Jcode, Claude, Codex, Gemini or OpenCode when prompted. Installation makes no model calls. The installer adds `az` as an alias when available.

From source with Rust 1.95:

```bash
cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.18 --locked --features typesafe
```

Remove Azdaja-managed installations:

```bash
azdaja uninstall all
```

[Install options](docs/install.md) · [LICENSE](LICENSE) · [supported-target third-party notices](THIRD-PARTY-NOTICES.md)

## Use

```bash
azdaja solo "Summarize the unresolved issues" -f ./large.txt
azdaja solo "Find release blockers" --repo ./project
```

Use Azdaja only after explicit activation in your harness. It is not an OS security boundary. Selected source can be sent to the configured model provider. [Security](SECURITY.md).

**Optional [Jev](https://typesafe.ai):** set `TYPESAFE_API_KEY` or pipe it from a secret manager into `azdaja jev attach --stdin`, then check `azdaja jev status`. This enables typed judgments in `exec` and explicitly executed batches, with raw distributions available to your harness. No key or `enabled = false` means off. Automatic `solo` use stays off. [Guide](docs/typed-judgments.md).

## Docs and evidence

- [Evaluator and commands](docs/cli.md)
- [Leave evidence for the next session](docs/agent-memory-handoff-walkthrough.md)
- [Measurements and limitations](BENCHMARKS.md)
- Verify retained evidence with `./proof/reproduction/run.sh`. [Manifest](proof/reproduction/manifest.json) · [Offline verifier](proof/reproduction/verify.py). This makes no model calls and does not reproduce the original live runs.
