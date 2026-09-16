"""Run guarded offline mechanisms, with an optional exclusive evidence receipt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

from . import tests


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    tests.OBSERVATIONS.clear()
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    here = Path(__file__).resolve().parent
    binary = Path(os.environ.get("AZDAJA_BINARY", "target/debug/azdaja")).resolve(strict=True)
    report = {"origin": "provider_free_synthetic_mechanism_controls",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": sys.platform,
        "tests": {"run": result.testsRun, "failures": len(result.failures),
                  "errors": len(result.errors), "skipped": len(result.skipped)},
        "passed": result.wasSuccessful() and not result.skipped,
        "live_provider_calls": 0, "semantic_efficacy_established": False,
        "automatic_planning_established": False, "native_judge_function_implemented": False,
        "observations": tests.OBSERVATIONS,
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(here.glob("*.py")) + [here / "fixtures.json",
                       here.parent / "adapter.py", here.parent / "bridge.py", binary,
                       here.parents[2] / "docs/research/jev-engine-mechanism-protocol-20260916.md"]}}
    text = json.dumps(report, indent=2) + "\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as handle:
            handle.write(text)
    print(text, end="")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
