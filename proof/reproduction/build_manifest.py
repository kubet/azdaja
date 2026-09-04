#!/usr/bin/env python3
"""Build the hash manifest after the proof bundle implementation is committed."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROLES = {
    ".github/workflows/ci.yml": "ci_verifier",
    ".github/workflows/release.yml": "publication_gate",
    ".github/workflows/verify-proof.yml": "ci_verifier",
    "BENCHMARKS.md": "public_claim_surface",
    "README.md": "public_claim_surface",
    "bench/live_fable_suite/run.py": "live_fixture_generator",
    "bench/live_fable_suite/verify.py": "live_receipt_verifier",
    "bench/product_50mb/reproduce.py": "provider_free_reproducer",
    "bench/product_50mb/verify.py": "provider_free_receipt_verifier",
    "bench/results/live-fable-suite.json": "live_receipt",
    "bench/results/live-fable-suite.md": "live_summary",
    "bench/results/product-50mb-current-source.json": "provider_free_receipt",
    "bench/results/product-50mb-current-source.md": "provider_free_summary",
    "bench/results/product-50mb-current-source.txt": "provider_free_log",
    "docs/release/notice-audit-2026-09-04.md": "third_party_notice_limitation",
    "proof/reproduction/README.md": "bundle_documentation",
    "proof/reproduction/build_manifest.py": "manifest_builder",
    "proof/reproduction/expected/invariants.json": "expected_invariants",
    "proof/reproduction/fixtures/spec.json": "fixture_specification",
    "proof/reproduction/receipts/fable/index.json": "live_receipt_index",
    "proof/reproduction/receipts/provider-free/index.json": "provider_free_receipt_index",
    "proof/reproduction/run.sh": "one_command_verifier",
    "proof/reproduction/test_verify.py": "bundle_tests",
    "proof/reproduction/verify.py": "bundle_verifier",
    "release/test_verify_third_party_notices.py": "notice_verifier_tests",
    "release/verify-third-party-notices.py": "notice_provenance_gate",
    "site/index.html": "public_claim_surface",
    "site/proof.html": "public_claim_surface",
    "tests/product_50mb.rs": "provider_free_fixture_generator",
    "tests/public_surface.rs": "public_claim_tests",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def build_manifest() -> dict[str, object]:
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
    )
    if dirty:
        raise ValueError("refusing to bind a tracked-dirty worktree")
    commit = git("rev-parse", "HEAD")
    expected = json.loads(
        (ROOT / "proof/reproduction/expected/invariants.json").read_text()
    )
    artifacts = []
    for relative, role in sorted(ARTIFACT_ROLES.items()):
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing or non-regular artifact: {relative}")
        artifacts.append(
            {
                "path": relative,
                "role": role,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return {
        "schema": "azdaja.first_party_proof_bundle.v1",
        "bundle": "azdaja-first-party-proof",
        "source_commit": commit,
        "hash_algorithm": "sha256",
        "artifacts": artifacts,
        "fixture_spec": "proof/reproduction/fixtures/spec.json",
        "expected": "proof/reproduction/expected/invariants.json",
        "indexes": {
            "live_fable": "proof/reproduction/receipts/fable/index.json",
            "provider_free": "proof/reproduction/receipts/provider-free/index.json",
        },
        "claim_boundary": {
            "classification": "narrow first-party reproducible evidence",
            "does_not_demonstrate": expected["not_demonstrated"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "proof/reproduction/manifest.json",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {args.output}; pass --force")
    manifest = build_manifest()
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
