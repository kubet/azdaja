# Azdaja v0.1.1

Azdaja v0.1.1 adds one-command binary installation on Ubuntu x86_64 while
retaining Apple Silicon macOS support. Both assets come from the same reviewed
source commit and the versioned installer binds exact HTTPS URLs and SHA-256
digests.

Supported binary platforms:

- Apple Silicon macOS (`Darwin-arm64`)
- Ubuntu/glibc x86_64 (`Linux-x86_64`)

Other platforms fail before download and can use the locked Rust source install.
Installation remains provider-free; run `azdaja doctor` explicitly to validate
live Jcode OpenAI subscription OAuth. Benchmark diagnostics are not product
acceptance or superiority claims.

Report only sanitized product feedback. Never include raw inputs, traces,
configuration, host paths, OAuth material, tokens, or secrets in public issues.
Security vulnerabilities belong in a private GitHub advisory.
