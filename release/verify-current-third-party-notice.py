#!/usr/bin/env python3
"""Compatibility alias for the authoritative public release verifier."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("verify-third-party-notices.py")), run_name="__main__")
