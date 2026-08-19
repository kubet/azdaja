#!/usr/bin/env python3
"""Zero-network checks for README/draft links, evidence language, and plot freshness."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md", ROOT / "drafts" / "README.md", ROOT / "drafts" / "v0.1.1-launch.md"]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_RE = re.compile(r'''src=["\']([^"\']+)["\']''')


def check_relative_links() -> list[str]:
    errors: list[str] = []
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        targets = LINK_RE.findall(text) + HTML_SRC_RE.findall(text)
        for raw_target in targets:
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_text = unquote(target.split("#", 1)[0])
            if path_text and not (doc.parent / path_text).resolve().exists():
                errors.append(f"{doc.relative_to(ROOT)}: missing link or asset target {target}")
    return errors


def check_claim_contract() -> list[str]:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    draft = (ROOT / "drafts" / "v0.1.1-launch.md").read_text(encoding="utf-8")
    required_readme = [
        "All 199 scheduled rows reached terminal accounting",
        "not an official leaderboard result",
        "64.38%",
        "71.75%",
        "81.36%",
        "52,428,800",
        "65,536",
        "not a token or cost-savings claim",
        "docs/token-context-crossover.svg",
        "curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/v0.1.1/site/install | sh",
        "cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.1 --locked",
    ]
    required_draft = [
        "NONPUBLISHED DRAFT",
        "This draft makes no adoption claim",
        "not currently an anonymous install path",
        "Darwin-arm64",
        "Linux-x86_64",
        "provider-free",
        "52,428,800",
        "61.452662890467536%",
        "not a leaderboard result",
        "No cost or token",
    ]
    readme_lines = len(readme.splitlines())
    if not 100 <= readme_lines <= 140:
        errors.append(f"README.md: expected 100-140 lines, found {readme_lines}")
    stale_readme = [
        "## First-use feedback",
        "### Derived RULER",
        "### Derived LongBench",
        "### Derived OOLONG",
        "release candidate",
        "GitHub Actions push run",
        "prepublication plan",
        "The repository is private",
        "authenticated owner",
        "ssh://git@",
        "Do not publish or claim anonymous reachability",
    ]
    for needle in stale_readme:
        if needle in readme:
            errors.append(f"README.md: stale or nonpublic claim remains: {needle}")
    for needle in required_readme:
        if needle not in readme:
            errors.append(f"README.md: missing required evidence or install phrase: {needle}")
    for needle in required_draft:
        if needle not in draft:
            errors.append(f"drafts/v0.1.1-launch.md: missing required boundary phrase: {needle}")

    marker = "ENDGAME-FIXED199-SUBSTITUTION-POINT"
    if readme.count(marker) != 1:
        errors.append(f"README.md: expected exactly one {marker} marker")
    candidate_row = re.compile(
        r"^\| \*\*Azdaja — current terminal candidate\*\* "
        r"\| (\d+)/199 \((\d+\.\d+)%\) "
        r"\| (\d+\.\d+)% \| \*\*(\d+\.\d+)%\*\* "
        r"\| Not reported \| Not reported \|$",
        re.MULTILINE,
    )
    rows = candidate_row.findall(readme)
    if len(rows) != 1:
        errors.append("README.md: expected exactly one well-formed terminal Azdaja row")
    else:
        completed_text, execution_rate_text, completed_mean_text, fixed_score_text = rows[0]
        completed = int(completed_text)
        execution_rate = float(execution_rate_text)
        completed_mean = float(completed_mean_text)
        fixed_score = float(fixed_score_text)
        if completed > 199 or abs(execution_rate - 100 * completed / 199) > 0.005:
            errors.append("README.md: Azdaja execution count/rate is inconsistent")
        if abs(fixed_score - completed_mean * completed / 199) > 1e-12:
            errors.append("README.md: completed-row mean does not decompose to fixed-199 score")

    for doc, doc_text in (("README.md", readme), ("drafts/v0.1.1-launch.md", draft)):
        if re.search(r"(?:~|≈)\s*72(?:\.0+)?%?", doc_text):
            errors.append(f"{doc}: forbidden approximate-72 result claim")
        for private_prefix in ("/Users/", "/private/tmp/", "C:\\Users\\"):
            if private_prefix in doc_text:
                errors.append(f"{doc}: private host path leaked: {private_prefix}")
    return errors


def main() -> int:
    errors = check_relative_links() + check_claim_contract()
    plot_check = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "render_token_crossover.py"), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if plot_check.returncode:
        errors.append(plot_check.stdout.strip())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    readme_lines = len((ROOT / "README.md").read_text(encoding="utf-8").splitlines())
    print(f"ok: README.md is concise at {readme_lines} lines; {len(DOCS)} Markdown files have valid local links and evidence boundaries")
    print(plot_check.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
