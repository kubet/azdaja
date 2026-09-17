# Historical notice remediation diagnostic (superseded)

**Date:** 2026-09-17
**Historical status at the initial diagnostic:** blocked, not a publication or legal approval
**Base:** `44b1e1b6cc78d6c0f67cfe49188e1cf94b7be7f5`

## Current disposition

The diagnostic below records the pre-repair state and is retained as historical evidence only. The current root notice and public verifier have since been repaired from actual cached archives. See [generation and verification](../../release/THIRD-PARTY-NOTICE-GENERATION.md) for the authoritative workflow, 191/default and 242/typesafe scope, 402 named occurrences, historical preservation, and remaining publication boundary. No legal-sufficiency or full-release approval is asserted.

## Historical decision

No notice or release asset was regenerated in this candidate. Updating only the candidate version or `Cargo.lock` digest would be a hash-only substitution and would overclaim completeness. The current source facts require a reviewed regeneration that includes the optional `typesafe` closure, exact package/path attribution, exact legal bytes, and the four retained CRLF-to-LF fidelity corrections.

The evidence record reports 191 default-union records and 242 records when `typesafe` is enabled. The feature adds 51 package records and 88 named legal-file occurrences. Of those occurrences, 63 have no byte-identical body among retained notice texts, and none has an existing exact package/version/path/digest attribution occurrence. The current input manifest remains explicitly source-input evidence only and is not legal completeness evidence.

## Reproduced gates

From the isolated clone:

```text
cargo test --locked --offline --test notice_distribution \
  current_notice_front_matter_tracks_canonical_version_targets_and_table_membership \
  -- --exact --nocapture
```

Failed at `tests/notice_distribution.rs:95`: notice says `Azdaja v0.1.14`, while `Cargo.toml` says `0.1.17`.

```text
python3 -B release/verify-third-party-notices.py
```

Failed closed because the notice binds `4e2419eaf2f1cf4818dca37950af56a7aedf6a079567357f4b7b72f8dd72066d`, while the current `Cargo.lock` is `2667713c7c9f40cb305d7846431d36cb4b9451b0b3472958bc8c38b45b01976f`.

The existing source-input check also failed because its checked-in manifest is not current for this revision. That is expected evidence of the same reconciliation gap, not a reason to weaken the check.

## Mutation evidence

The verifier's stale-binding mutation fails with exit 1. Its duplicate-binding mutation also fails closed because exactly one lock binding is required. A future regenerated notice must add equivalent fail-closed mutations for removing one current feature record, changing one exact legal body, and changing one package/path attribution. Until those mutations pass against regenerated content, changing the current notice pins would not be evidence-backed.

## Promotion boundary

This candidate deliberately leaves `THIRD-PARTY-NOTICES.md`, release assets, historical receipts, proof claims, package version, and verification gates unchanged. A follow-up can be promoted only after a locally reproducible regeneration produces the 242-record current feature/target inventory, exact supplied legal/attribution text, corrected byte-fidelity declarations, and a reviewed current-lock binding together. No legal approval is asserted here.
