#!/usr/bin/env python3
"""Offline verifier for Azdaja's narrow first-party proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "azdaja.first_party_proof_bundle.v1"
INDEX_SCHEMA = "azdaja.first_party_receipt_index.v1"
FIXTURE_SCHEMA = "azdaja.first_party_fixture_spec.v1"
EXPECTED_SCHEMA = "azdaja.first_party_expected_invariants.v1"
MANIFEST_KEYS = {
    "schema",
    "bundle",
    "source_commit",
    "hash_algorithm",
    "artifacts",
    "fixture_spec",
    "expected",
    "indexes",
    "claim_boundary",
}
ARTIFACT_KEYS = {"path", "role", "bytes", "sha256"}
HEX = set("0123456789abcdef")


def exact_dict(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} keys mismatch")
    return value


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected an object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX


def safe_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} path is missing")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ValueError(f"{label} path is unsafe: {value!r}")
    return value


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load verifier module: {path}")
    module = importlib.util.module_from_spec(spec)
    sibling_path = str(path.parent)
    sys.path.insert(0, sibling_path)
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path[0] == sibling_path:
            sys.path.pop(0)
    return module


def validate_artifacts(
    records: object, root: Path = ROOT
) -> dict[str, dict[str, object]]:
    if not isinstance(records, list) or not records:
        raise ValueError("artifacts must be a non-empty list")
    result: dict[str, dict[str, object]] = {}
    previous = ""
    for index, raw in enumerate(records):
        record = exact_dict(raw, ARTIFACT_KEYS, f"artifact {index}")
        relative = safe_relative_path(record["path"], f"artifact {index}")
        if relative <= previous:
            raise ValueError("artifact paths must be unique and sorted")
        previous = relative
        if not isinstance(record["role"], str) or not record["role"]:
            raise ValueError(f"artifact {relative} has no role")
        if not isinstance(record["bytes"], int) or record["bytes"] < 1:
            raise ValueError(f"artifact {relative} has invalid size")
        if not is_sha256(record["sha256"]):
            raise ValueError(f"artifact {relative} has invalid SHA-256")
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"artifact is missing or non-regular: {relative}")
        if path.stat().st_size != record["bytes"]:
            raise ValueError(f"artifact size mismatch: {relative}")
        if sha256(path) != record["sha256"]:
            raise ValueError(f"artifact hash mismatch: {relative}")
        result[relative] = record
    return result


def validate_git_binding(
    commit: object, paths: list[str], root: Path = ROOT
) -> bool:
    if not isinstance(commit, str) or len(commit) != 40 or not set(commit) <= HEX:
        raise ValueError("invalid bundle source commit")
    if not (root / ".git").exists():
        raise ValueError("bundle verification requires a Git checkout")
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if exists.returncode:
        raise ValueError("bundle source commit is unavailable")
    changed = subprocess.run(
        ["git", "diff", "--quiet", commit, "--", *paths], cwd=root, check=False
    )
    if changed.returncode:
        raise ValueError("bundle artifacts differ from the recorded source commit")
    return True


def validate_artifact_reference(
    value: object,
    label: str,
    artifacts: dict[str, dict[str, object]],
) -> dict[str, object]:
    record = exact_dict(value, {"path", "bytes", "sha256"}, label)
    path = safe_relative_path(record["path"], label)
    if path not in artifacts:
        raise ValueError(f"{label} is not in the artifact manifest")
    artifact = artifacts[path]
    if record["bytes"] != artifact["bytes"] or record["sha256"] != artifact["sha256"]:
        raise ValueError(f"{label} disagrees with the artifact manifest")
    return record


def validate_index(
    path: Path,
    expected_kind: str,
    artifacts: dict[str, dict[str, object]],
) -> dict[str, object]:
    data = load_json(path)
    keys = {"schema", "kind", "receipt", "summary", "observation_boundary"}
    if expected_kind == "provider_free":
        keys.add("log")
    exact_dict(data, keys, f"{expected_kind} index")
    if data["schema"] != INDEX_SCHEMA or data["kind"] != expected_kind:
        raise ValueError(f"{expected_kind} index identity mismatch")
    validate_artifact_reference(data["receipt"], f"{expected_kind} receipt", artifacts)
    validate_artifact_reference(data["summary"], f"{expected_kind} summary", artifacts)
    if expected_kind == "provider_free":
        validate_artifact_reference(data["log"], "provider-free log", artifacts)
    if not isinstance(data["observation_boundary"], str) or not data["observation_boundary"]:
        raise ValueError(f"{expected_kind} observation boundary is missing")
    return data


def compare_fields(actual: dict[str, object], expected: dict[str, object], label: str) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            raise ValueError(f"{label} mismatch: {key}")


def validate_live(
    expected: dict[str, object], fixtures: dict[str, object], root: Path
) -> dict[str, int]:
    receipt_path = root / safe_relative_path(expected["receipt"], "live receipt")
    receipt = load_json(receipt_path)
    verifier = import_module("bundle_live_verifier", root / "bench/live_fable_suite/verify.py")
    checks = verifier.validate_receipt(receipt, root=root)
    if checks != {"source": True, "binary": False}:
        raise ValueError("live verifier returned unexpected checks")
    if receipt["schema"] != expected["receipt_schema"]:
        raise ValueError("live receipt schema mismatch")
    compare_fields(receipt["totals"], expected["totals"], "live totals")

    wanted = expected["scenarios"]
    actual = receipt["scenarios"]
    if not isinstance(wanted, list) or not isinstance(actual, list) or len(wanted) != len(actual):
        raise ValueError("live scenario count mismatch")
    for observed, target in zip(actual, wanted):
        name = target["name"]
        if observed["name"] != name:
            raise ValueError(f"live scenario order mismatch: {name}")
        compare_fields(
            {
                "expected": observed["result"]["expected"],
                "actual": observed["result"]["actual"],
                "input_bytes": observed["fixture"]["bytes"],
                "input_sha256": observed["fixture"]["sha256"],
                "root_prompt_bytes": observed["prompt"]["bytes"],
            },
            {
                "expected": target["expected"],
                "actual": target["expected"],
                "input_bytes": target["input_bytes"],
                "input_sha256": target["input_sha256"],
                "root_prompt_bytes": target["root_prompt_bytes"],
            },
            f"live scenario {name}",
        )

    live_spec = fixtures["live_fable"]
    if live_spec["generator"] != "bench/live_fable_suite/run.py":
        raise ValueError("live fixture generator mismatch")
    for spec, target in zip(live_spec["inputs"], wanted):
        compare_fields(
            spec,
            {
                "name": target["name"],
                "bytes": target["input_bytes"],
                "record_bytes": 4096,
                "sha256": target["input_sha256"],
            },
            f"live fixture {target['name']}",
        )
    return {
        "scenarios": receipt["totals"]["scenarios"],
        "exact_results": receipt["totals"]["exact_results"],
        "provider_calls": receipt["totals"]["provider_calls"],
    }


def validate_provider_free(
    expected: dict[str, object], fixtures: dict[str, object], root: Path
) -> dict[str, int]:
    receipt_path = root / safe_relative_path(expected["receipt"], "provider-free receipt")
    log_path = root / safe_relative_path(expected["log"], "provider-free log")
    receipt = load_json(receipt_path)
    verifier = import_module("bundle_product_verifier", root / "bench/product_50mb/verify.py")
    checks = verifier.validate_receipt(
        receipt, root=root, log_path=log_path, require_log=True
    )
    if checks != {"source": True, "binary": False, "log": True}:
        raise ValueError("provider-free verifier returned unexpected checks")
    if receipt["schema"] != expected["receipt_schema"]:
        raise ValueError("provider-free receipt schema mismatch")
    compare_fields(receipt["summary"], expected["summary"], "provider-free summary")

    wanted = expected["scenarios"]
    actual = receipt["scenarios"]
    if not isinstance(wanted, list) or not isinstance(actual, list) or len(wanted) != len(actual):
        raise ValueError("provider-free scenario count mismatch")
    for observed, target in zip(actual, wanted):
        compare_fields(
            {
                "name": observed["scenario"],
                "answer": observed["answer"],
                "input_bytes": observed["input_bytes"],
                "root_prompt_bytes": observed["root_prompt_bytes"],
                "root_calls": observed["root_calls"],
                "exec_invocation_count": observed["exec_invocation_count"],
                "sub_call_count": observed["sub_call_count"],
            },
            target,
            f"provider-free scenario {target['name']}",
        )
        if observed["exact_answer"] is not True:
            raise ValueError(f"provider-free scenario is not exact: {target['name']}")

    provider_spec = fixtures["provider_free"]
    if provider_spec["generator"] != "tests/product_50mb.rs":
        raise ValueError("provider-free fixture generator mismatch")
    if not isinstance(provider_spec["digest_status"], str) or not provider_spec["digest_status"]:
        raise ValueError("provider-free digest limitation is missing")
    for spec, target in zip(provider_spec["inputs"], wanted):
        if spec != {"name": target["name"], "bytes": target["input_bytes"], "sha256": None}:
            raise ValueError(f"provider-free fixture specification mismatch: {target['name']}")
    return {
        "scenarios": receipt["summary"]["scenarios"],
        "surviving_sessions": receipt["summary"]["surviving_sessions"],
    }


def validate_public_surfaces(root: Path, live_receipt: dict[str, object]) -> None:
    readme = (root / "README.md").read_text()
    benchmarks = (root / "BENCHMARKS.md").read_text()
    site = (root / "site/index.html").read_text()
    proof = (root / "site/proof.html").read_text()
    guide = (root / "proof/reproduction/README.md").read_text()
    notice_audit = (root / "docs/release/notice-audit-2026-09-04.md").read_text()
    for path in (
        "proof/reproduction/manifest.json",
        "proof/reproduction/run.sh",
        "proof/reproduction/verify.py",
    ):
        if path not in readme + benchmarks + proof:
            raise ValueError(f"public proof surfaces do not link {path}")
    source_commit = live_receipt["source"]["commit"]
    if source_commit not in benchmarks or source_commit not in proof:
        raise ValueError("public live source binding mismatch")
    required_scope = (
        "Three exact first-party harness assertions",
        "This command does not reproduce that model call.",
        "not benchmark accuracy or independent replication",
    )
    for claim in required_scope:
        if claim not in proof:
            raise ValueError(f"public proof scope is missing: {claim}")
    required_home_scope = (
        "These first-party harness assertions returned <strong>3/3 exact</strong>",
        "This is not benchmark accuracy or independent replication.",
    )
    for claim in required_home_scope:
        if claim not in site:
            raise ValueError(f"public home scope is missing: {claim}")
    required_guide = (
        "git clone https://github.com/kubet/azdaja.git",
        "git fetch --unshallow",
        "A nonzero exit means the evidence was not verified.",
    )
    for instruction in required_guide:
        if instruction not in guide:
            raise ValueError(f"reproduction guide is missing: {instruction}")
    if "exact remaining semantic metadata blocker" not in notice_audit:
        raise ValueError("third-party notice limitation is missing")
    for digest in (
        "966b92bd3153c519bd3e4e9d62152a590ab848b77a2c84729d0c38cbaa86b508",
        "ebcc0632ef458a90b90eb0b95ed3343df85e66d9ed22633173e2ce3fdb1ec08b",
        "3111c880bcf2cbf738282bf826bd5649e175fa5a0efc0b3ace5b077425f0921a",
    ):
        if digest not in proof or digest not in guide:
            raise ValueError(f"public provenance digest is missing: {digest}")
    for scenario in live_receipt["scenarios"]:
        displayed = f"{scenario['transport']['elapsed_seconds']:.3f} s"
        if displayed not in benchmarks or displayed not in proof:
            raise ValueError(f"public timing mismatch: {displayed}")


def verify(manifest_path: Path, root: Path = ROOT) -> dict[str, object]:
    manifest = exact_dict(load_json(manifest_path), MANIFEST_KEYS, "manifest")
    if manifest["schema"] != SCHEMA or manifest["bundle"] != "azdaja-first-party-proof":
        raise ValueError("manifest identity mismatch")
    if manifest["hash_algorithm"] != "sha256":
        raise ValueError("unsupported hash algorithm")
    artifacts = validate_artifacts(manifest["artifacts"], root)
    validate_git_binding(manifest["source_commit"], list(artifacts), root)

    fixture_path = safe_relative_path(manifest["fixture_spec"], "fixture spec")
    expected_path = safe_relative_path(manifest["expected"], "expected invariants")
    indexes = exact_dict(manifest["indexes"], {"live_fable", "provider_free"}, "indexes")
    for referenced in (fixture_path, expected_path, *indexes.values()):
        if referenced not in artifacts:
            raise ValueError(f"manifest reference is not an artifact: {referenced}")

    fixtures = exact_dict(
        load_json(root / fixture_path), {"schema", "live_fable", "provider_free"}, "fixtures"
    )
    if fixtures["schema"] != FIXTURE_SCHEMA:
        raise ValueError("fixture schema mismatch")
    expected = exact_dict(
        load_json(root / expected_path),
        {"schema", "live_fable", "provider_free", "not_demonstrated"},
        "expected invariants",
    )
    if expected["schema"] != EXPECTED_SCHEMA:
        raise ValueError("expected invariant schema mismatch")
    claim_boundary = exact_dict(
        manifest["claim_boundary"],
        {"classification", "does_not_demonstrate"},
        "claim boundary",
    )
    if expected["not_demonstrated"] != claim_boundary["does_not_demonstrate"]:
        raise ValueError("claim boundary mismatch")
    if claim_boundary["classification"] != "narrow first-party reproducible evidence":
        raise ValueError("proof classification mismatch")

    live_index_path = safe_relative_path(indexes["live_fable"], "live index")
    provider_index_path = safe_relative_path(indexes["provider_free"], "provider-free index")
    validate_index(root / live_index_path, "live_fable", artifacts)
    validate_index(root / provider_index_path, "provider_free", artifacts)
    live = validate_live(expected["live_fable"], fixtures, root)
    provider_free = validate_provider_free(expected["provider_free"], fixtures, root)
    live_receipt = load_json(root / expected["live_fable"]["receipt"])
    validate_public_surfaces(root, live_receipt)
    return {
        "schema": "azdaja.first_party_proof_verification.v1",
        "bundle_source_commit": manifest["source_commit"],
        "artifacts_verified": len(artifacts),
        "git_binding": True,
        "live_fable": live,
        "provider_free": provider_free,
        "classification": claim_boundary["classification"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "proof/reproduction/manifest.json",
    )
    args = parser.parse_args()
    try:
        result = verify(args.manifest)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as error:
        print(f"proof verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
