#!/usr/bin/env python3
"""Zero-network checks for README/draft links, evidence language, and plot freshness."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "README.md",
    ROOT / "bench" / "arc3" / "README.md",
    ROOT / "docs" / "history" / "README-draft.md",
    ROOT / "docs" / "history" / "drafts" / "v0.1.1-launch.md",
    ROOT / "docs" / "launch-saga.md",
    ROOT / "docs" / "transport-flip-postmortem.md",
    ROOT / "docs" / "day7-public-launch.md",
    ROOT / "docs" / "harness-lifecycle.md",
]
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


def check_site_onboarding_contract() -> list[str]:
    errors: list[str] = []
    site = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "site" / "styles.css").read_text(encoding="utf-8")
    command = "$ curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh"
    required = [
        "Apple Silicon macOS or Linux x86-64",
        "requires a detected Jcode, Claude, Codex, Gemini, or OpenCode harness",
        "otherwise it exits before downloading or writing anything",
        "callable by any agent that can run a command",
        "Model subcalls still route through a supported",
        "Use <strong>az</strong> only when the installer reports its alias",
        "including Azure CLI, is untouched",
    ]
    if site.count(command) != 1:
        errors.append("site/index.html: expected one complete curl-pipe-sh CTA")
    for phrase in required:
        if phrase not in site:
            errors.append(f"site/index.html: missing onboarding boundary: {phrase}")
    match = re.search(r"\.install-command\{([^}]*)\}", css)
    if not match:
        errors.append("site/styles.css: missing install-command rule")
    else:
        rule = match.group(1)
        if "white-space:nowrap" not in rule or "overflow-x:auto" not in rule:
            errors.append("site/styles.css: install CTA must remain fully horizontally scrollable")
        if "overflow:hidden" in rule:
            errors.append("site/styles.css: install CTA must not hide overflow")
    if "text-overflow:ellipsis" in css:
        errors.append("site/styles.css: install CTA must not be truncated with an ellipsis")
    return errors


def check_claim_contract() -> list[str]:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    draft = (ROOT / "docs" / "history" / "drafts" / "v0.1.1-launch.md").read_text(encoding="utf-8")
    saga = (ROOT / "docs" / "launch-saga.md").read_text(encoding="utf-8")
    postmortem = (ROOT / "docs" / "transport-flip-postmortem.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "day7-public-launch.md").read_text(encoding="utf-8")
    required_readme = [
        "All 199 rows reached terminal accounting",
        "not an official leaderboard result",
        "185/199 (92.96%)",
        "5,403.36 provider-authoritative mean across 198 measured rows; one row is not imputed",
        "4.26164968987583 percentage points",
        "**+4.3 points**",
        "highest bare-RLM number shown in this non-exhaustive ladder",
        "| Paper | RLM | Model recursion without agent tools | **64.38%** |",
        "| This repository | Azdaja — single-arm diagnostic; not paper/leaderboard | Bare RLM layer | **68.64%** |",
        "| Paper | Codex, No Retriever | Coding agent | **71.75%** |",
        "| Paper | RAH, GPT-5 | Recursive Agent Harness | **81.36%** |",
        "52,428,800",
        "65,536",
        "not a token or cost-savings claim",
        "docs/token-context-crossover.svg",
        "curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh",
        "cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.2 --locked",
        "Apple Silicon macOS and Linux x86-64",
        "requires a detected Jcode, Claude, Codex, Gemini, or OpenCode harness",
        "exits before downloading or writing anything",
        "Use the prominent short command `az` only when",
        "including Azure CLI, is untouched",
        "`az install --harness all`",
        "`az doctor`",
        "shell-quoted absolute `azdaja` path",
        "indexed 16-row truecolor half-block banner",
        "non-TTY output, `NO_COLOR`, and `TERM=dumb`",
        "same exact five-line text through either name",
        "Cargo creates `azdaja`, never `az`",
        "`azdaja install --harness NAME`",
        "exact absolute managed-binary `doctor` command",
        "cargo uninstall azdaja",
        "only for the curl installer's ownership marker",
        "`short alias skipped`",
        "`azdaja-config.toml` plus `azdaja-config.toml.managed`",
        "an unrelated adjacent `config.toml` is never overwritten",
        "A passing unqualified `doctor` proves only",
        "0.0 Ember-minus-baseline **local shadow RHAE** difference",
        "**+8; +1.24% relative to the baseline raw count**",
        "not an efficiency or improvement claim",
        "A retrieval-only follow-up recovered no missing absolutes",
        "three zero diagnostic counters",
        "36 journal records",
        "`ACTION_BUDGET` for each arm",
        "bench/arc3/README.md#benchmark-card",
        "not-run full-five boundary",
        "not a public-safe source tree",
        "clean allowlisted export under a new repository identity",
        "moving files does not sanitize history",
        "bench/results/integration-acceptance-v0.1.2-local.json",
        "binds the exact older source hashes recorded at its base commit",
        "does not validate this onboarding delta",
        "short-alias delta receipt",
        "bench/results/install-alias-delta-v0.1.2-public.json",
        "not a native cross-platform or provider validation",
        "release-only and ignored by the ordinary debug suite",
        "readiness supersession receipt",
        "bench/results/v0.1.2-candidate-readiness-superseded-public.json",
        "marks the retained v0.1.2 binaries and their earlier matrix stale",
        "new native assets and a fresh release matrix are required",
        "evidence for their old bytes only, not the current source",
        "bench/results/install-matrix-v0.1.2-final-public.json",
        "bench/results/install-real-adapters-v0.1.2-final-public.json",
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
    if not 100 <= readme_lines <= 155:
        errors.append(f"README.md: expected 100-155 lines, found {readme_lines}")
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
            errors.append(f"docs/history/drafts/v0.1.1-launch.md: missing required boundary phrase: {needle}")

    required_saga = [
        "**+4.3 percentage points**",
        "not proof of a global best-published result",
        "5,403.36 mean total root tokens",
        "Codex at 71.75",
        "local-shadow-RHAE Δ was 0.0 in each game",
        "+8, +1.24% of the baseline raw count",
        "one fixed-order pair per game, baseline then Ember",
        "seed 0, a fresh game/runtime per arm",
        "same pinned direct-Claude Sonnet common configuration",
        "no randomization or replication",
        "| ls20 | 0.0 | 92 | 103 |",
        "| ft09 | 0.0 | 186 | 208 |",
        "| vc33 | 0.0 | 0 | 0 |",
        "| ar25 | 0.0 | 137 | 110 |",
        "| wa30 | 0.0 | 231 | 233 |",
        "not an action-normalized rate, efficiency result, or improvement claim",
        "absent from retained v9 artifacts",
        "`0 / 0 / 0` in the separate unchanged-feedback / revisited-state / repeated-known-control counters",
        "memory-efficiency hypothesis remains open",
        "No new ARC or provider run supports this documentation",
        "arc3-vc33-smoke-v2-public.json",
        "arc3-scorecard-interrogation-public-v1.json",
        "v0.1.2 release candidate",
        "immutable historical evidence for the old bytes",
        "New Darwin arm64 and Linux x86-64 assets",
        "same exact five-line help",
        "v0.1.2-candidate-readiness-superseded-public.json",
        "install-alias-delta-v0.1.2-public.json",
        "not a native cross-platform or provider validation",
        "post-launch v0.2 roadmap material only",
    ]
    required_postmortem = [
        "pre-inference setup failure, non-diagnostic for discoverability or selection—not genuine disuse",
        "successful provider turns were **0**",
        "agent-class calls were **0**",
        "0.00 vs 0.00",
        "no live root turn was reached",
        "v0.2 roadmap",
        "does **not** authorize an extra",
    ]
    required_runbook = [
        "private staging only",
        "former calendar gate is superseded and is not an active launch gate",
        "AZDAJA_OWNER_APPROVAL=GO",
        "complete saga, complete README, and complete private author email",
        "16/16 install matrix is green",
        "refusing launch: AZDAJA_OWNER_APPROVAL must equal GO",
        "transport-flip-postmortem.md",
        "gpt-rah199-mortality-v3-terminal-public.json",
        "arc3-ember-five-public-v9-result.json",
        "arc3-scorecard-interrogation-public-v1.json",
        "arc3-vc33-smoke-v2-public.json",
        "install-matrix-v0.1.2-final-public.json",
        "install-real-adapters-v0.1.2-final-public.json",
        "independently builds v0.1.2 validation binaries from final `main` with Rust 1.95",
        "exact final-matrix-tested candidate bytes retained in owner-only custody",
        "AZDAJA_RELEASE_ASSET_DIR",
        "clean Mach-O links are not hash-reproducible",
        "rust:1.95.0-bookworm",
        "v0.1.1 tag and release are immutable and untouched",
        "brand-new immutable annotated tag and release",
        "Query the release object only",
        "Release asset `GET` and `HEAD` requests are forbidden",
        "Only now perform the visibility flip",
        "Anonymous public verification",
        "public runbook intentionally omits local staging locations and recipient addresses",
        "email script uses the same approval environment",
        "first post-launch update",
        "must not run before the public flip",
        "owner-only package",
        "Do not open a PR",
        "fast-forward the reviewed local head to private `main`",
        "delete every non-`main` remote head",
        "fresh-clones only `main`",
        "Stop there. Do not set the approval variable",
    ]
    for name, text, required in (
        ("docs/launch-saga.md", saga, required_saga),
        ("docs/transport-flip-postmortem.md", postmortem, required_postmortem),
        ("docs/day7-public-launch.md", runbook, required_runbook),
    ):
        flat_text = " ".join(text.split())
        for phrase in required:
            if phrase not in flat_text:
                errors.append(f"{name}: missing second-act boundary phrase: {phrase}")

    if saga.count("68.64164968987583%") != 1:
        errors.append("docs/launch-saga.md: expected exact launch percentage once")
    if "best published bare-configuration RLM" in readme or "best published bare-configuration RLM" in saga:
        errors.append("launch docs: unsupported absolute best-published claim")

    marker = "ENDGAME-FIXED199-SUBSTITUTION-POINT"
    if marker in readme:
        errors.append(f"README.md: frozen launch still contains {marker}")
    expected_result_rows = [
        "| RAH-protocol Oolong, fixed 199 rows | **68.64%** |",
        "| Execution / valid predictions | 185/199 (92.96%) |",
        "| Mean root tokens per item | ~5.4K |",
        "| Captured root-prompt source-span leaks in the scripted 50 MiB gate | 0 |",
    ]
    for row_start in expected_result_rows:
        if readme.count(row_start) != 1:
            errors.append(f"README.md: expected one current result row beginning {row_start}")
    comparison_rows = [
        "| Paper | RLM | Model recursion without agent tools | **64.38%** |",
        "| This repository | Azdaja — single-arm diagnostic; not paper/leaderboard | Bare RLM layer | **68.64%** |",
        "| Paper | Codex, No Retriever | Coding agent | **71.75%** |",
        "| Paper | RAH, GPT-5 | Recursive Agent Harness | **81.36%** |",
    ]
    if readme.count("| Source | Label | System class | Oolong score |") != 1:
        errors.append("README.md: expected exactly one shared paper/Azdaja comparison table")
    positions = [readme.find(row) for row in comparison_rows]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append("README.md: shared comparison rows are missing or not score-ordered")
    if "| Paper label | System class |" in readme:
        errors.append("README.md: separate paper-only comparison table remains")
    unsupported_readme_claims = [
        "Cheapest configuration in its table",
        "convergence is the claim",
        "~90%",
        "global best",
        "all runs, all time",
        "O(1) root",
        "cost of asking does not grow",
        "Model-agnostic, proven",
    ]
    for claim in unsupported_readme_claims:
        if claim.casefold() in readme.casefold():
            errors.append(f"README.md: unsupported owner-draft claim remains: {claim}")
    install_section = readme.split("## Install", 1)[1].split("## Use", 1)[0]
    install_blocks = re.findall(r"```bash\n(.*?)\n```", install_section, flags=re.DOTALL)
    expected_install_blocks = [
        "curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh",
        "cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.2 --locked",
        """azdaja install                              # Cargo: auto-detect installed harnesses
azdaja install --harness jcode              # Cargo: choose one; all is also accepted
# Run the exact managed-binary doctor command printed by install, then reload/restart.
azdaja uninstall --harness all              # Cargo: remove managed skills first
cargo uninstall azdaja
az doctor --harness jcode                   # curl: provider-free custody check
az uninstall --standalone                   # curl only: keep managed skills
az uninstall --all                          # curl only: remove skills and standalone""",
    ]
    if install_blocks != expected_install_blocks:
        errors.append(
            "README.md: Install must contain exactly the curl, Cargo, and combined lifecycle/uninstall bash blocks"
        )
    if "v0.1.1" in install_section:
        errors.append("README.md: Install section still references immutable v0.1.1 assets")
    if "git@github.com" in readme or "ssh://git@" in readme:
        errors.append("README.md: public examples must use HTTPS, not SSH")

    for doc in DOCS:
        doc_text = doc.read_text(encoding="utf-8")
        name = str(doc.relative_to(ROOT))
        if re.search(r"(?:~|≈)\s*72(?:\.0+)?%?", doc_text):
            errors.append(f"{name}: forbidden approximate-72 result claim")
        for private_prefix in ("/Users/", "/private/tmp/", "C:\\Users\\"):
            if private_prefix in doc_text:
                errors.append(f"{name}: private host path leaked: {private_prefix}")
    return errors



def check_root_layout() -> list[str]:
    """Keep the repository root limited to intentional public entry points."""
    errors: list[str] = []
    expected_files = {
        ".gitignore",
        "Cargo.lock",
        "Cargo.toml",
        "FAILS.md",
        "LICENSE",
        "README.md",
        "SCOREBOARD.md",
        "WINS.md",
        "azdaja-logo.png",
        "install.sh",
    }
    expected_directories = {
        ".github",
        "assets",
        "bench",
        "docs",
        "release",
        "site",
        "src",
        "tests",
        "tools",
    }
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if tracked.returncode:
        return [f"root cleanup: git ls-files failed: {tracked.stderr.strip()}"]
    tracked_paths = [Path(line) for line in tracked.stdout.splitlines() if line]
    actual_files = {path.name for path in tracked_paths if len(path.parts) == 1}
    actual_directories = {path.parts[0] for path in tracked_paths if len(path.parts) > 1}
    if actual_files != expected_files:
        errors.append(
            f"repository root files differ: expected {sorted(expected_files)}, found {sorted(actual_files)}"
        )
    if actual_directories != expected_directories:
        errors.append(
            f"repository root directories differ: expected {sorted(expected_directories)}, found {sorted(actual_directories)}"
        )
    required_moves = [
        ROOT / "docs" / "evidence" / "PERF.md",
        ROOT / "docs" / "history" / "PLAN.md",
        ROOT / "docs" / "history" / "PROGRESS.md",
        ROOT / "docs" / "history" / "JCODE_SESSION_FORK_API_REQUEST.md",
        ROOT / "docs" / "history" / "README-draft.md",
        ROOT / "docs" / "history" / "drafts" / "v0.1.1-launch.md",
    ]
    for path in required_moves:
        if not path.is_file():
            errors.append(f"root cleanup: missing moved history/evidence file {path.relative_to(ROOT)}")
    if (ROOT / "docs" / "history" / "drafts" / "README.md").exists():
        errors.append("root cleanup: redundant drafts boilerplate README remains")

    manifest = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))
    package = manifest.get("package", {})
    expected_include = [
        "/Cargo.toml", "/Cargo.lock", "/LICENSE", "/README.md", "/src/**",
        "/assets/SKILL.md", "/assets/config.toml",
    ]
    if package.get("publish") is not False or package.get("include") != expected_include:
        errors.append("Cargo.toml: publish=false or strict package include allowlist changed")
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    required_ignores = {
        ".env", ".env.*", "*.key", "*.pem", "*.p12", "*.log", "*.time",
        "*.timing", "*.trace", "*.raw", "**/raw/", "**/runs/", "**/outputs/",
    }
    missing_ignores = sorted(required_ignores - set(ignore))
    if missing_ignores:
        errors.append(f".gitignore: missing credential/raw-output patterns {missing_ignores}")
    return errors


def check_arc_public_surface() -> list[str]:
    """Keep the tracked ARC source reviewable while execution remains gated."""
    errors: list[str] = []
    arc = ROOT / "bench" / "arc3"
    readme_path = arc / "README.md"
    readme = readme_path.read_text(encoding="utf-8")

    if (arc / "POST_PUBLIC_FIVE.md").exists():
        errors.append("bench/arc3: private post-public runbook must not be tracked")
    for forbidden in ("/Users/", "/private/tmp/", "C:\\Users\\", ".private-upstream"):
        if forbidden in readme:
            errors.append(f"bench/arc3/README.md: private host material leaked: {forbidden}")
    code_blocks = re.findall(r"```(?:bash|sh)?\n(.*?)\n```", readme, flags=re.DOTALL)
    for block in code_blocks:
        if any(name in block for name in (
            "arc_v2_post_public.py", "bind_arc_v2_post_public.py", "driver.py live"
        )):
            errors.append("bench/arc3/README.md: executable post-public recipe is forbidden")

    required_card = [
        "## Benchmark card",
        "local shadow diagnostics, not official ARC scores",
        "one fixed-order pair per listed game (baseline, then Ember)",
        "seed 0 and a fresh game/runtime per arm",
        "same pinned direct-Claude Sonnet configuration",
        "per-level action caps of 5× the published human baselines",
        "one invocation after two completed turns",
        "| `ls20` | 0.0 | 92 | 103 |",
        "| `ft09` | 0.0 | 186 | 208 |",
        "| `vc33` | 0.0 | 0 | 0 |",
        "| `ar25` | 0.0 | 137 | 110 |",
        "| `wa30` | 0.0 | 231 | 233 |",
        "| **Total (counts only)** | — | **646** | **654** |",
        "**+8 (+1.24% of the baseline raw count)**",
        "not an action-normalized rate or an efficiency/improvement claim",
        "no randomization or replication",
        "All ten closed scorecard detail requests returned HTTP 404",
        "absent from the retained v9 artifacts",
        "| Baseline | 0.0 | 0 | 35 (`[35, 0, 0, 0, 0, 0, 0]`) | `0 / 0 / 0` | 36 records | `ACTION_BUDGET` |",
        "| Ember | 0.0 | 0 | 35 (`[35, 0, 0, 0, 0, 0, 0]`) | `0 / 0 / 0` | 36 records | `ACTION_BUDGET` |",
        "separate diagnostics, not a partition",
        "schema-v9 stub execution is disabled",
        "## Gated full-five source (not run)",
        "It remains **HOLD / not run**",
        "fresh receipt proving `kubet/azdaja` is public",
        "No new ARC or provider run was performed for this card",
        "../results/arc3-ember-five-public-v9-result.json",
        "../results/arc3-scorecard-interrogation-public-v1.json",
        "../results/arc3-vc33-smoke-v2-public.json",
        "arc-v2-five-postlaunch-manifest.json",
    ]
    for phrase in required_card:
        if phrase not in readme:
            errors.append(f"bench/arc3/README.md: missing benchmark-card boundary: {phrase}")
    active_arc_docs = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "bench/arc3/README.md": readme,
        "docs/launch-saga.md": (ROOT / "docs" / "launch-saga.md").read_text(encoding="utf-8"),
    }
    forbidden_framing = (
        "paired null",
        "true played zero-level null",
        "revisited-state/repeated-control split",
        "-1.24% fewer",
        "ar25 improved",
        "server no longer yields",
    )
    for name, active_text in active_arc_docs.items():
        for phrase in forbidden_framing:
            if phrase.casefold() in active_text.casefold():
                errors.append(f"{name}: unsupported ARC framing remains: {phrase}")

    new_tests = (
        arc / "test_arc_v2_local_custody.py",
        arc / "test_arc_v2_post_public.py",
        arc / "test_claude_lane.py",
        arc / "test_driver.py",
    )
    for test in new_tests:
        text = test.read_text(encoding="utf-8")
        for forbidden in ("/Users/", "/private/tmp/", "/owner/", "/private/"):
            if forbidden in text:
                errors.append(f"{test.relative_to(ROOT)}: hard-coded host path remains: {forbidden}")

    five_path = arc / "arc-v2-five-postlaunch-manifest.json"
    five = json.loads(five_path.read_text(encoding="utf-8"))
    gate = five.get("launch_gate", {})
    if (
        five.get("status") != "PREPARED_OWNER_AUTHORIZED_POST_PUBLIC_FLIP_GATE_NOT_YET_SATISFIED"
        or gate.get("explicit_owner_go_post_flip_bound") is not False
        or gate.get("post_public_visibility_receipt_bound") is not False
        or gate.get("repository_must_be_public_at_execution") is not True
    ):
        errors.append("ARC-v2 five-game manifest: post-public/GO gate is not fail-closed")

    required = {
        "driver.py", "claude_lane.py", "arc_v2_post_public.py",
        "bind_arc_v2_post_public.py", "arc-v2-local-custody-manifest.json",
        "arc-v2-five-postlaunch-manifest.json", "toolkit-lock.json",
        "mini-pilot-manifest.json",
    }
    missing = sorted(name for name in required if not (arc / name).is_file())
    if missing:
        errors.append(f"bench/arc3: referenced source or lock missing: {missing}")
    driver_tests = (arc / "test_driver.py").read_text(encoding="utf-8")
    for generation in range(2, 10):
        name = f"mini-pilot-live-manifest-v{generation}.json"
        if name not in driver_tests or not (arc / name).is_file():
            errors.append(f"bench/arc3: referenced historical manifest missing: {name}")

    for sidecar in sorted(arc.glob("*.sha256")):
        fields = sidecar.read_text(encoding="ascii").strip().split()
        if len(fields) != 2:
            errors.append(f"{sidecar.relative_to(ROOT)}: malformed hash sidecar")
            continue
        target = sidecar.parent / fields[1]
        if not target.is_file() or fields[0] != hashlib.sha256(target.read_bytes()).hexdigest():
            errors.append(f"{sidecar.relative_to(ROOT)}: stale hash sidecar")
    return errors


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def check_alias_delta_receipt() -> list[str]:
    errors: list[str] = []
    path = ROOT / "bench" / "results" / "install-alias-delta-v0.1.2-public.json"
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"alias delta receipt read failed: {exc}"]
    expected_result = {
        "expected_no_harness_refusals": 2,
        "green_cells": 16,
        "positive_cells": 14,
        "status": "PASS",
        "total_cells": 16,
    }
    cells = receipt.get("cells", [])
    identities = {
        (cell.get("platform_selector"), cell.get("scenario")) for cell in cells
    }
    expected_identities = {
        (platform, scenario)
        for platform in ("Darwin/arm64", "Linux/x86_64")
        for scenario in (
            "detected-jcode", "detected-claude", "detected-codex",
            "detected-gemini", "detected-opencode", "all",
            "no-harness", "already-installed",
        )
    }
    hashes = receipt.get("hashes", {})
    if (
        receipt.get("schema_version") != 2
        or receipt.get("record_type") != "azdaja_install_alias_delta_local_fixture_public_receipt"
        or receipt.get("base_commit") != "4b12e1aa3fb2774c5aebcf1ce079de7ccdbcd4e9"
        or receipt.get("result") != expected_result
        or len(cells) != 16
        or identities != expected_identities
        or hashes != {
            ".gitignore": "78f3a3211035abc61620600167071b7767bb483253c60db3153dfafb251fdcb5",
            "Cargo.toml": "2925561c94a507aa2ebae852e3773981ae2cfc05ed66da495297731163fd9ac8",
            "install.sh": "ae50243f6fe9354e010c4e6c56eea81e291708890d5b5b947bdcf6ea71c9bb2d",
            "site/install": "ae50243f6fe9354e010c4e6c56eea81e291708890d5b5b947bdcf6ea71c9bb2d",
            "src/banner.rs": "dec4128eea89db1c339ebc6b19f68433f6b7c7986c5f0105f334542720137f79",
            "src/main.rs": "898abd67f90eee1a5a4902bf629e0c6010483ad1f691c0de268f9843735a1877",
            "tests/cli_ux.rs": "f38264104329f3a80ec72e124f0fd058624951bca09406442607fe04e22bff61",
            "tests/site_installer.rs": "9d8d6114fcc0ff3a30de3f874e77bd2796de048c27fefe8ca5fcbf374ae07390",
        }
        or _sha256(path) != "7bfdd02ae912b82d815dded52ce154669cc429f2b062cc263b0ee2cc9a651fc9"
    ):
        errors.append("historical alias delta receipt: immutable identity, matrix, or bound source hashes changed")
    if (ROOT / "install.sh").read_bytes() != (ROOT / "site" / "install").read_bytes():
        errors.append("alias delta: root and site installers are not byte-identical")
    if receipt.get("scope", {}).get("provider_calls_performed") is not False:
        errors.append("alias delta receipt: provider-free boundary changed")
    if receipt.get("scope", {}).get("native_cross_platform_claim") is not False:
        errors.append("alias delta receipt: local selector scope misrepresented as native validation")
    expected_help = [
        "AZDAJA v0.1.2 — virtual memory for language models",
        "Usage: az <command> [options]  (azdaja also works)",
        "Commands: start load exec final list kill solo install doctor uninstall",
        "Setup: az install --harness <jcode|claude|codex|gemini|opencode|all>",
        'Example: az solo "summarize this file" -f ./document.txt',
    ]
    if receipt.get("positive_contract", {}).get("bare_exact_five_line_help") != expected_help:
        errors.append("alias delta receipt: exact five-line help contract changed")
    collision = receipt.get("foreign_az_collision_contract", {})
    ownership = receipt.get("config_ownership_contract", {})
    rollback = receipt.get("rollback_contract", {})
    if (
        collision.get("earlier_path_command_resolution_preserved") is not True
        or collision.get("later_path_command_resolution_preserved") is not True
        or collision.get("preexisting_managed_alias_removed_to_avoid_shadowing") is not True
        or collision.get("installer_stdout_lines") != 3
        or collision.get("stdout_line_2_contains") != "short alias skipped"
        or collision.get("stdout_line_3_uses") != "azdaja doctor"
        or ownership.get("standalone_config") != "azdaja-config.toml"
        or ownership.get("owner_marker") != "azdaja-config.toml.managed"
        or ownership.get("generic_config_toml_written") is not False
        or ownership.get("owned_custom_config_preserved") is not True
        or rollback.get("late_harness_refusal_restores_prior_state") is not True
    ):
        errors.append("alias delta receipt: collision, ownership, or rollback contract changed")
    for private_prefix in ("/Users/", "/private/tmp/", "C:\\Users\\"):
        if private_prefix in path.read_text(encoding="utf-8"):
            errors.append(f"alias delta receipt: private host path leaked: {private_prefix}")
    return errors


def check_integration_acceptance_receipt() -> list[str]:
    errors: list[str] = []
    path = ROOT / "bench" / "results" / "integration-acceptance-v0.1.2-local.json"
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"historical source acceptance receipt read failed: {exc}"]
    # This receipt is immutable evidence for its recorded base commit. Do not
    # compare it to the moving working tree and accidentally describe old
    # validation as coverage for a newer onboarding delta.
    expected_hashes = {
        ".github/workflows/ci.yml": "c88095bc18e1b796fc6c6c290b8b391356a94b2c5c4602c7f375d5a44d4559bd",
        ".github/workflows/source-install-integrity.yml": "1a946fc01c0c1a5f6dc78ffb9179bae5373dbf3c57f6b3d16cb65090ab63ac3b",
        "README.md": "4d972009b928914c6c71c9de345c9ca5c9ad002d93041749fe329ab06d8de86e",
        "SCOREBOARD.md": "5085dbef81adde7785efbc199b82aeb8bff473a4cffef1b324050a2c5d63fac8",
        "install.sh": "661740d0aa985ac348ad56643f884f225771d36337694a5567b363fc7c24cdb6",
        "site/install": "661740d0aa985ac348ad56643f884f225771d36337694a5567b363fc7c24cdb6",
        "src/main.rs": "c5778ed0c5d4344f9a943ac4525eb05a4de64ec6f88f66ca486a5073b9fa125e",
        "tests/product_50mb.rs": "87a66d26b5c82766af03b648540cb45802c1396aa5dd808f875f1b2e1ac279a8",
        "tests/site_installer.rs": "f8a3e0dd43c15e3373d5a668d619a3db318476c3b93a2b62205e7d949cedb004",
        "tools/check_docs.py": "5dbd07133f94e86143c2ec667e3750360168657a4b2f163b58a8e892250f6a87",
    }
    expected_commands = {
        "check_docs": "python3 tools/check_docs.py",
        "clippy": "cargo clippy --all-targets --all-features --locked -- -D warnings",
        "fmt": "cargo fmt --all --check",
        "ordinary_debug": "cargo test --all --locked -- --test-threads=1",
        "release_50mib": (
            "AZDAJA_PRODUCT_BINARY=target/release/azdaja "
            "cargo test --release --locked --test product_50mb "
            "offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death "
            "-- --ignored --exact --test-threads=1"
        ),
        "release_build": "cargo build --release --locked",
        "rustdoc": "cargo doc --no-deps --locked",
    }
    expected_results = {
        "check_docs": "PASS",
        "clippy": "PASS",
        "fmt": "PASS",
        "install_custody_refusals": "PASS",
        "ordinary_debug": "PASS",
        "release_50mib": "PASS",
        "rustdoc": "PASS",
    }
    expected_install_contract = {
        "complete_selected_set_preflight_before_mutation": True,
        "hardlink_symlink_inode_link_mode_unknown_target_refusal_zero_mutation": True,
        "late_multi_target_refusal_zero_mutation": True,
        "shell_harness_snapshots_or_recursive_rollback": False,
        "standalone_committed_after_managed_rust_install": True,
    }
    expected_performance_contract = {
        "ordinary_debug_functional_coverage_retained": True,
        "ordinary_debug_runs_gate": False,
        "outer_deadline_seconds": 90,
        "release_only_ignored_gate_active_on_push_and_pull_request": True,
    }
    expected_scope = {
        "external_network_or_release_requests_performed": False,
        "fixture": "provider-free loopback HTTP release fixture using a locally built current-source binary",
        "loopback_http_requests_performed": True,
        "native_cross_platform_claim": False,
        "platform_selectors_are_native_platform_evidence": False,
        "provider_calls_performed": False,
        "publication_performed": False,
    }
    expected_supersession = {
        "current_source_claims_superseded": True,
        "historical_bytes_modified": False,
        "path": "bench/results/install-alias-delta-v0.1.2-public.json",
        "reason": (
            "The historical receipt binds pre-integration source hashes and a then-pending "
            "Config::load label; it remains immutable historical evidence."
        ),
        "sha256": "7bfdd02ae912b82d815dded52ce154669cc429f2b062cc263b0ee2cc9a651fc9",
    }
    if (
        receipt.get("schema_version") != 1
        or receipt.get("record_type") != "azdaja_current_source_integration_acceptance_local_receipt"
        or receipt.get("status") != "PASS_PROVIDER_FREE_EXACT_SOURCE"
        or receipt.get("base_commit") != "fe2eb9705266e39d75eef49e85b19e5270ad899d"
        or receipt.get("source_sha256") != expected_hashes
        or receipt.get("commands") != expected_commands
        or receipt.get("results") != expected_results
        or receipt.get("install_custody_contract") != expected_install_contract
        or receipt.get("performance_contract") != expected_performance_contract
        or receipt.get("scope") != expected_scope
        or receipt.get("supersession") != expected_supersession
        or _sha256(path) != "2d0c0dc550b053383a8b232f33644cb63d2842aa29a48f743bd3ca3f93858c36"
    ):
        errors.append("historical source acceptance receipt: immutable identity, hashes, results, or boundary changed")
    if (ROOT / "install.sh").read_bytes() != (ROOT / "site" / "install").read_bytes():
        errors.append("active installers are not byte-identical")
    return errors


def check_candidate_readiness_supersession() -> list[str]:
    errors: list[str] = []
    path = ROOT / "bench" / "results" / "v0.1.2-candidate-readiness-superseded-public.json"
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"candidate readiness supersession read failed: {exc}"]
    supersession = receipt.get("supersession", {})
    publication = receipt.get("publication", {})
    local_validation = receipt.get("completed_local_source_validation", {})
    trigger = receipt.get("trigger", {})
    if (
        receipt.get("schema_version") != 1
        or receipt.get("record_type") != "azdaja_v0_1_2_candidate_readiness_supersession_receipt"
        or receipt.get("base_commit") != "4b12e1aa3fb2774c5aebcf1ce079de7ccdbcd4e9"
        or receipt.get("status") != "REBUILD_AND_CROSS_PLATFORM_RETEST_REQUIRED"
        or supersession.get("retained_v0_1_2_candidate_is_final") is not False
        or supersession.get("previous_final_matrix_valid_for_current_source") is not False
        or supersession.get("previous_receipts_remain_historical_evidence") is not True
        or supersession.get("old_binary_hashes_are_final_bindings") is not False
        or not str(local_validation.get("provider_free_alias_fixture_matrix", "")).startswith("PASS_")
        or local_validation.get("path_wide_foreign_az_collision_checks") != "PASS_EARLIER_AND_LATER_WITH_COMMAND_RESOLUTION"
        or local_validation.get("standalone_config_ownership_checks") != "PASS_COLLISIONS_REFUSE_OWNED_CUSTOM_PRESERVED_GENERIC_UNTOUCHED"
        or local_validation.get("late_installer_rollback_check") != "PASS_BINARY_HARNESS_ALIAS_RESTORED"
        or local_validation.get("exact_five_line_non_tty_help_and_alias_parity") != "PASS"
        or local_validation.get("interactive_banner_unit_contract", "").startswith("PASS_") is not True
        or local_validation.get("full_locked_rust_suite", {}).get("failed") != 0
        or local_validation.get("clippy_all_targets_all_features") != "PASS_DENY_WARNINGS"
        or local_validation.get("arc_offline_unit_tests", {}).get("passed") != 55
        or local_validation.get("provider_calls_performed") is not False
        or local_validation.get("arc_calls_performed") is not False
        or trigger.get("standalone_config_filename") != "azdaja-config.toml"
        or trigger.get("standalone_config_owner_marker") != "azdaja-config.toml.managed"
        or trigger.get("generic_adjacent_config_write_removed") is not True
        or trigger.get("config_load_integration_pending") is not True
        or trigger.get("path_wide_foreign_az_collision_guard_added") is not True
        or any(publication.values())
    ):
        errors.append("candidate readiness supersession: stale/nonpublication boundary changed")
    text = path.read_text(encoding="utf-8")
    for forbidden in (
        "1a8b442599c25eda05ba4d5a979e018148484ec0396610b900e85e7d9cef1a24",
        "ed71f631e137400754fb089dcf29f7194956c559f614c281c628838a08ae032e",
        "/Users/", "/private/tmp/", "C:\\Users\\",
    ):
        if forbidden in text:
            errors.append(f"candidate readiness supersession: forbidden old hash or private path: {forbidden}")
    return errors


def check_launch_receipts() -> list[str]:
    errors: list[str] = []
    release_path = ROOT / "release" / "day7-public-launch.json"
    public_path = ROOT / "bench" / "results" / "gpt-rah199-mortality-v3-terminal-public.json"
    transport_path = ROOT / "bench" / "results" / "endgame-agent-transport-v2-disease10-terminal.json"
    arc_path = ROOT / "bench" / "results" / "arc3-ember-five-public-v9-result.json"
    interrogation_path = ROOT / "bench" / "results" / "arc3-scorecard-interrogation-public-v1.json"
    vc33_smoke_path = ROOT / "bench" / "results" / "arc3-vc33-smoke-v2-public.json"
    install_matrix_path = ROOT / "bench" / "results" / "install-matrix-v0.1.2-final-public.json"
    historical_install_matrix_path = ROOT / "bench" / "results" / "install-matrix-v0.1.2-public.json"
    real_adapters_path = ROOT / "bench" / "results" / "install-real-adapters-v0.1.2-final-public.json"
    historical_real_adapters_path = ROOT / "bench" / "results" / "install-real-adapters-v0.1.2-public.json"
    postmortem_path = ROOT / "docs" / "transport-flip-postmortem.md"
    saga_path = ROOT / "docs" / "launch-saga.md"
    runbook_path = ROOT / "docs" / "day7-public-launch.md"
    try:
        release = json.loads(release_path.read_text(encoding="utf-8"))
        public = json.loads(public_path.read_text(encoding="utf-8"))
        transport = json.loads(transport_path.read_text(encoding="utf-8"))
        arc = json.loads(arc_path.read_text(encoding="utf-8"))
        interrogation = json.loads(interrogation_path.read_text(encoding="utf-8"))
        vc33_smoke = json.loads(vc33_smoke_path.read_text(encoding="utf-8"))
        install_matrix = json.loads(install_matrix_path.read_text(encoding="utf-8"))
        historical_install_matrix = json.loads(historical_install_matrix_path.read_text(encoding="utf-8"))
        real_adapters = json.loads(real_adapters_path.read_text(encoding="utf-8"))
        historical_real_adapters = json.loads(historical_real_adapters_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"launch receipt read failed: {exc}"]

    score = release.get("authorized_launch_score", {})
    public_score = public.get("score", {})
    root_usage = public.get("root_usage", {})
    evidence = release.get("evidence", {})

    if release.get("schema_version") != 3:
        errors.append("day7 receipt: expected private-main consolidation schema version 3")
    if release.get("record_type") != "day7_public_launch_private_main_consolidation_receipt":
        errors.append("day7 receipt: private-main consolidation record type changed")
    if release.get("status") != "PRIVATE_MAIN_CONSOLIDATION_READY_NO_PUBLICATION":
        errors.append("day7 receipt: private-main no-publication status changed")
    expected_assembly = {
        "active_remote_branch_dependency": False,
        "base_commit": "ece7520cd85e86f0bef2377973cd3b76610acb87",
        "readme_commit": "0ed643e31a93cc060cf7a4917108224f13553ee5",
        "saga_source_commit": "f9071c5fa08ec313814d8c977796c195069f3629",
        "source_consolidation_commit": "662b713f17a157cfd0241d87afcc3b9107232eed",
        "source_tree": "4e803f48a8784bd5322db2d3f47fe8cc578029b3",
        "status": "curated_private_main_consolidation_ready_for_owner_fast_forward",
        "target_branch": "main",
        "v0_1_2_implementation_commit": "662b713f17a157cfd0241d87afcc3b9107232eed",
    }
    if release.get("assembly") != expected_assembly:
        errors.append("day7 receipt: curated private-main assembly binding changed")
    obsolete_calendar_key = "_".join(("hard", "public", "launch", "not", "before"))
    if obsolete_calendar_key in release:
        errors.append("day7 receipt: superseded calendar field remains active")
    if release.get("superseded_calendar_gate") != {
        "active": False,
        "former_not_before": "2026-08-26T00:20:29.359377+00:00",
        "status": "superseded_by_explicit_owner_approval_and_green_install_matrix",
    }:
        errors.append("day7 receipt: superseded calendar-gate record changed")
    expected_gate = {
        "active_gate": "explicit_owner_go_after_complete_public_text_and_email_review_and_green_install_matrix",
        "environment_variable": "AZDAJA_OWNER_APPROVAL",
        "required_value": "GO",
        "satisfied_at_staging": False,
        "required_reviews": {
            "launch_saga_complete": True,
            "readme_complete": True,
            "private_author_email_complete": True,
        },
        "install_matrix_requirement": {
            "path": "bench/results/install-matrix-v0.1.2-final-public.json",
            "result": "PASS",
            "green_cells": 16,
            "total_cells": 16,
            "public_receipt_sha256": "6d6950dc55611130b3811b5988278f88ea00bffacc6fc9f29dfbd13e3d4044a9",
            "implementation_commit": "662b713f17a157cfd0241d87afcc3b9107232eed",
            "exact_matrix_tested_candidate_retained": True,
        },
    }
    if release.get("approval_gate") != expected_gate:
        errors.append("day7 receipt: explicit owner-GO review/matrix gate changed")

    expected_assets = {
        "SHA256SUMS": "33e8e6985ab500d874e4dd32cd4661c8475c4d91202f6cca7c8eba1c09d81ad1",
        "azdaja-v0.1.2-darwin-arm64": "1a8b442599c25eda05ba4d5a979e018148484ec0396610b900e85e7d9cef1a24",
        "azdaja-v0.1.2-linux-x86_64": "ed71f631e137400754fb089dcf29f7194956c559f614c281c628838a08ae032e",
    }
    expected_release_plan = {
        "version": "0.1.2",
        "tag": "v0.1.2",
        "implementation_commit": "662b713f17a157cfd0241d87afcc3b9107232eed",
        "candidate_source_commit": "662b713f17a157cfd0241d87afcc3b9107232eed",
        "source_tree": "4e803f48a8784bd5322db2d3f47fe8cc578029b3",
        "asset_source": "exact_final_matrix_tested_candidate_from_owner_only_custody",
        "independent_rebuilds_are_validation_only": True,
        "owner_asset_directory_disclosed": False,
        "candidate_custody_receipt": {
            "local_path_disclosed": False,
            "retained_owner_only": True,
            "sha256": "d65dcc21a791ec7d2ab2c3c02428ffc3c678d95b44c75b18e335d1172c91d33d",
        },
        "expected_asset_bytes": {
            "SHA256SUMS": 186,
            "azdaja-v0.1.2-darwin-arm64": 6434272,
            "azdaja-v0.1.2-linux-x86_64": 7941464,
        },
        "rust_version": "1.95.0",
        "v0_1_1_immutable": True,
        "release_assets_published_at_staging": False,
        "expected_assets": expected_assets,
    }
    if release.get("release_plan") != expected_release_plan:
        errors.append("day7 receipt: v0.1.2 implementation or expected release bytes changed")
    historical_assets = {
        "SHA256SUMS": "80fbdebeb6587552f6d04062427d3a699b67c1680b1857d35c30c86c588acb5b",
        "azdaja-v0.1.2-darwin-arm64": "4fdb907c0af87be49d82ec82849848ca340eae99aeb02d7e18691f19fa39b6b7",
        "azdaja-v0.1.2-linux-x86_64": "8ab01cc6c14c6d02e3a0cc2cbfbf12c28c4a7ab662bb9d892bffaf1b567c4e4b",
    }
    expected_historical_install_matrix = {
        "assets": historical_assets,
        "cells": {"expected_no_harness_failures": 2, "green": 16, "positive": 14, "total": 16},
        "implementation_commit": "a06a5acacf32c20dc19855bae54a013312b34597",
        "installer_sha256": "36abdc64885cb9f9ff93daca6e1941ffbc7639fd7d3a3bd1034a6494b5bbf636",
        "no_harness_contract": {
            "before_download": True,
            "doctor_and_solo": "not_run_impossible",
            "graceful_nonzero": True,
            "home_unchanged": True,
            "stack_trace": False,
        },
        "owner_aggregate_receipt_sha256": "d7413c826f3efc9124c757705c1fffa7b3099102497193f2a436b9e7a230290b",
        "platforms": ["Darwin/arm64", "Ubuntu-24.04-glibc/x86_64"],
        "positive_cell_contract": {
            "binary_checksum_match": True,
            "doctor_three_pass_lines": True,
            "exact_answer": "ORCHID-9472-A06A5AC",
            "genuine_provider_solo": True,
            "input_bytes": 52428800,
            "input_sha256": "a3c974d7669791eddea1332453302457d5e8de8622781568f760ea97c874171a",
            "installer_exact_three_lines": True,
            "passed": 14,
        },
        "provider_evidence": {
            "calls_succeeded": 28,
            "credentials_entered_linux_containers": False,
            "fake_provider_used": False,
            "route": "OpenAI gpt-5.4-mini through an owner-only local Jcode subscription relay",
        },
        "release_assets_published": False,
        "result": "PASS",
        "retention": {"host_paths": False, "prompts": False, "raw_input": False, "responses": False, "secrets": False, "traces": False},
        "scenarios": ["jcode", "claude", "codex", "gemini", "opencode", "all-five", "no-harness", "binary-already-installed"],
        "schema": "azdaja-install-matrix-public-v1",
        "version": "0.1.2",
    }
    if historical_install_matrix != expected_historical_install_matrix:
        errors.append("historical install matrix: exact public-safe schema or values changed")
    if _sha256(historical_install_matrix_path) != "9170d7527c52d2d7ec7972639c8c3f1df776dfb5c2722b71f5102f79b74ffbf7":
        errors.append("historical install matrix: canonical public byte hash changed")

    final_matrix_sha = "6d6950dc55611130b3811b5988278f88ea00bffacc6fc9f29dfbd13e3d4044a9"
    if _sha256(install_matrix_path) != final_matrix_sha:
        errors.append("final install matrix: canonical public byte hash changed")
    expected_matrix_result = {
        "expected_no_harness_failures_green": 2,
        "green_cells": 16,
        "positive_cells_passed": 14,
        "positive_exact_five_line_dragon_passed": 14,
        "total_cells": 16,
    }
    custody_assets = {
        asset.get("name"): asset.get("sha256")
        for asset in install_matrix.get("candidate_custody", {}).get("assets", [])
    }
    if (
        install_matrix.get("schema") != "azdaja-install-matrix-aggregate-v2"
        or install_matrix.get("implementation_commit") != "662b713f17a157cfd0241d87afcc3b9107232eed"
        or install_matrix.get("source_tree") != "4e803f48a8784bd5322db2d3f47fe8cc578029b3"
        or install_matrix.get("result") != expected_matrix_result
        or custody_assets != expected_assets
        or install_matrix.get("published_or_tagged") is not False
        or len(install_matrix.get("cells", [])) != 16
    ):
        errors.append("final install matrix: source, result, custody, or publication boundary changed")

    expected_historical_real_adapters = {'binary': {'name': 'azdaja-v0.1.2-darwin-arm64',
                'sha256': '4fdb907c0af87be49d82ec82849848ca340eae99aeb02d7e18691f19fa39b6b7',
                'version': '0.1.2'},
     'observed_nonpasses': [{'classification': 'local_credential_refresh_invalid',
                             'evaluator_check': 'PASS',
                             'fix_hint_printed': True,
                             'harness': 'codex',
                             'product_pass': False,
                             'provider_check': 'FAIL'},
                            {'classification': 'host_provider_route_failed',
                             'fix_hint_printed': True,
                             'harness': 'jcode',
                             'product_pass': False,
                             'provider_check': 'FAIL'}],
     'passing_routes': [{'doctor': {'checks': 3, 'failed': 0, 'passed': 3},
                         'harness': 'opencode',
                         'installer_stdout_lines': 3,
                         'solo': {'exact_answer': 'DRAGON-OPENCODE-5120',
                                  'input_bytes': 52428800,
                                  'input_sha256': 'e31f7338dcc8d5307fa91b6a22a421a76f094b8601e19450883eb3af08e50f31',
                                  'passed': True}},
                        {'doctor': {'checks': 3, 'failed': 0, 'passed': 3},
                         'harness': 'claude',
                         'installer_stdout_lines': 3,
                         'solo': {'exact_answer': 'DRAGON-CLAUDE-5120',
                                  'input_bytes': 52428800,
                                  'input_sha256': 'b5b6edc45bd8c926f8a27663de40f66ceda666742e5dddccef7cb15919925f1c',
                                  'passed': True}}],
     'platform': 'Darwin/arm64',
     'sanitization': {'authentication_material_retained': False,
                      'machine_locations_retained': False,
                      'model_io_retained': False,
                      'raw_diagnostics_retained': False,
                      'synthetic_inputs_deleted': True},
     'schema': 'azdaja-install-real-adapters-public-v1',
     'scope': {'installation_provider_free': True,
               'other_routes_validated': False,
               'passing_routes': ['opencode', 'claude'],
               'solo_e2e_genuine_installed_adapter': True},
     'version': '0.1.2'}
    if historical_real_adapters != expected_historical_real_adapters:
        errors.append("historical real-adapter receipt: exact public-safe schema or values changed")
    if _sha256(historical_real_adapters_path) != "d73dfefb3c277495d2a18cbce7ee7c304a8be8c73e75d375aa7dfa179557bada":
        errors.append("historical real-adapter receipt: canonical byte hash changed")

    if _sha256(real_adapters_path) != "b3c657da9be4cff611e9286d40be553232e7e51cfb8fe9f1eb734d8433ef48a8":
        errors.append("final real-adapter receipt: canonical byte hash changed")
    final_adapter_result = real_adapters.get("result", {})
    if (
        real_adapters.get("schema") != "azdaja-install-real-adapters-owner-v2"
        or real_adapters.get("implementation_commit") != "662b713f17a157cfd0241d87afcc3b9107232eed"
        or real_adapters.get("binary_sha256") != expected_assets["azdaja-v0.1.2-darwin-arm64"]
        or final_adapter_result != {
            "claude_full_50mib_pass": True,
            "codex_doctor_pass_solo_auth_failure": True,
            "genuine_provider_successes": 5,
            "jcode_honest_doctor_failure": True,
            "opencode_full_50mib_pass": True,
        }
    ):
        errors.append("final real-adapter receipt: source, binary, or outcome boundary changed")

    if score.get("percent") != 68.64164968987583 or public_score.get("fixed_199_score_percent") != 68.64164968987583:
        errors.append("launch receipts: frozen exact score mismatch")
    if public_score.get("execution_successes") != 185 or public_score.get("retained_failure_zeros") != 14:
        errors.append("sanitized terminal receipt: fixed-199 accounting mismatch")
    if abs(public_score.get("completed_row_mean_percent", 0) * 185 / 199 - 68.64164968987583) > 1e-12:
        errors.append("sanitized terminal receipt: completed-row mean does not decompose")
    if round(68.64164968987583 - 64.38, 1) != 4.3:
        errors.append("launch receipts: rounded class-reference delta changed")

    expected_root = {
        "scheduled_rows": 199,
        "measured_rows": 198,
        "missing_rows": 1,
        "measured_input_tokens": 891498,
        "measured_output_tokens": 178367,
        "measured_total_tokens": 1069865,
        "median_total_tokens_across_measured_rows": 4723,
        "successful_rows": 185,
        "successful_rows_total_tokens": 916133,
    }
    for key, value in expected_root.items():
        if root_usage.get(key) != value:
            errors.append(f"sanitized terminal receipt: root usage {key} changed")
    if root_usage.get("complete_fixed_199_aggregate") is not False or root_usage.get("estimated") is not False:
        errors.append("sanitized terminal receipt: missing-root boundary changed")
    if abs(root_usage.get("mean_total_tokens_across_measured_rows", 0) - 1069865 / 198) > 1e-12:
        errors.append("sanitized terminal receipt: measured root-token mean mismatch")
    if abs(root_usage.get("mean_total_tokens_across_successful_rows", 0) - 916133 / 185) > 1e-12:
        errors.append("sanitized terminal receipt: successful-row root-token mean mismatch")

    execution = transport.get("execution", {})
    transport_score = transport.get("score", {})
    if transport.get("terminal_status") != "FAIL" or execution.get("successful_provider_turns") != 0:
        errors.append("transport receipt: terminal pre-inference failure boundary changed")
    for key, value in (("agent_class_calls", 0), ("control_failures", 10), ("treatment_failures", 10), ("terminal_rows", 20)):
        if execution.get(key) != value:
            errors.append(f"transport receipt: {key} changed")
    if transport_score.get("control_official_points") != 0.0 or transport_score.get("treatment_official_points") != 0.0 or transport_score.get("delta_points") != 0.0:
        errors.append("transport receipt: fail-closed +0.00 accounting changed")
    if transport.get("forced_live_proof", {}).get("passed") is not False:
        errors.append("transport receipt: forced live proof boundary changed")

    expected_arc = {
        "arms": ["baseline", "ember"],
        "games": [
            {"baseline_wasted_actions": 92, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 103, "game_id": "ls20"},
            {"baseline_wasted_actions": 186, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 208, "game_id": "ft09"},
            {"baseline_wasted_actions": 0, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 0, "game_id": "vc33"},
            {"baseline_wasted_actions": 137, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 110, "game_id": "ar25"},
            {"baseline_wasted_actions": 231, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 233, "game_id": "wa30"},
        ],
        "identity": "Ember",
    }
    expected_arc_sha256 = "f6a518df0183f9d4791e99f58bdc0e91c198056ffa67b9013b8f97ff8fc27c21"
    if arc != expected_arc:
        errors.append("ARC receipt: exact public-safe schema or values changed")
    if _sha256(arc_path) != expected_arc_sha256:
        errors.append("ARC receipt: canonical v9 byte hash changed")
    else:
        baseline_wasted = sum(game["baseline_wasted_actions"] for game in arc["games"])
        ember_wasted = sum(game["ember_wasted_actions"] for game in arc["games"])
        if baseline_wasted != 646 or ember_wasted != 654:
            errors.append("ARC receipt: wasted-action totals changed")
        fewer_percent = (baseline_wasted - ember_wasted) / baseline_wasted * 100
        if abs(fewer_percent - (-1.238390092879257)) > 1e-15:
            errors.append("ARC receipt: wasted-action percentage changed")
        if any(game["ember_minus_baseline_rhae_delta"] != 0.0 for game in arc["games"]):
            errors.append("ARC receipt: paired RHAE delta changed")

    expected_interrogation = {
        "schema_version": 1,
        "record_type": "arc3_closed_scorecard_interrogation_sanitized_receipt",
        "scope": {
            "arms": ["baseline", "ember"],
            "closed_scorecards_queried": 10,
            "game_pairs": 5,
            "credential_continuity": "one unchanged owner credential",
            "new_experiment": False,
            "game_requests_performed": False,
            "provider_requests_performed": False,
        },
        "official_scorecard_retrieval": {
            "pinned_contract": "open or closed scorecard retrieval",
            "observed_http_status": 404,
            "observed_count": 10,
            "absolute_arm_rhae_recovered": False,
            "levels_completed_recovered": False,
            "total_actions_recovered": False,
        },
        "html_results_route": {
            "observation": "redirected to the generic ARC-AGI-3 page",
            "scorecard_detail_recovered": False,
        },
        "retention_boundary": {
            "driver_retained_close_responses": False,
            "public_v9_receipt_retains_paired_deltas": True,
            "public_v9_receipt_retains_aggregate_wasted_actions": True,
            "zero_level_vs_equal_nonzero_distinguishable": False,
            "memory_efficiency_hypothesis_status": "open",
        },
        "vc33": {
            "scorecard_lifecycles_created_reset_closed": 2,
            "lifecycle_source": "retained stdout metadata",
            "total_actions_established": False,
            "levels_completed_established": False,
            "degeneracy_status": "unresolved",
            "zero_wasted_actions_implies_zero_total_actions": False,
        },
        "redaction": {
            "scorecard_identifiers_included": False,
            "credentials_included": False,
            "host_paths_included": False,
            "raw_logs_included": False,
        },
    }
    if interrogation != expected_interrogation:
        errors.append("ARC interrogation receipt: exact sanitized schema or findings changed")
    if _sha256(interrogation_path) != "17de6893eee9cafafdd164965a91fe08b72aecc69d1f2e41044c0b7d4cbc210c":
        errors.append("ARC interrogation receipt: canonical byte hash changed")

    expected_vc33_smoke = {'schema_version': 1,
 'package': {'commit': '1d500edd8eaf651364cfdd8e29638ee540db6062',
             'manifest_sha256': 'ef56236950ba4e44f901dff79342145f944c79bb3c7236d64da06f6265e86ab1'},
 'game': 'vc33',
 'arms': {'baseline': {'shadow_rhae': 0.0,
                       'levels_completed': 0,
                       'total_actions': 35,
                       'per_level_action_counts': [35, 0, 0, 0, 0, 0, 0],
                       'wasted_actions': {'official_feedback_wasted_actions': 0,
                                          'revisited_states': 0,
                                          'repeated_known_controls': 0},
                       'termination': 'ACTION_BUDGET',
                       'journal': {'record_count': 36,
                                   'sha256': '18ddb74e409521a6666845ceab6283d8f227b5571c292d1a4d005828c0718e28'},
                       'terminal_receipt_sha256': '4ff55203bdbc6d61874a817b9059df850fe64e82f17b684b43d899d2ad11cac2'},
          'ember': {'shadow_rhae': 0.0,
                    'levels_completed': 0,
                    'total_actions': 35,
                    'per_level_action_counts': [35, 0, 0, 0, 0, 0, 0],
                    'wasted_actions': {'official_feedback_wasted_actions': 0,
                                       'revisited_states': 0,
                                       'repeated_known_controls': 0},
                    'termination': 'ACTION_BUDGET',
                    'journal': {'record_count': 36,
                                'sha256': '28ab0ade89e4d5d0996733b7d6fb26ee727e754fb6eac77315874da1f46eb55f'},
                    'terminal_receipt_sha256': 'bbc17cb9af387defc9ad3338353a44259ed63fba558c57e7cf6549bc88361a35'}},
 'paired': {'ember_minus_baseline_shadow_rhae_delta': 0.0,
            'receipt_sha256': 'a2f732483d707df9ce0de871243efef5e4e491fd7d34140e3af05765b51daed6'},
 'full_five_game_rerun': {'status': 'HOLD',
                          'release_condition': 'post-public flip and explicit owner authorization'}}
    if vc33_smoke != expected_vc33_smoke:
        errors.append("ARC-v2 vc33 smoke receipt: exact sanitized schema or values changed")
    if _sha256(vc33_smoke_path) != "002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551":
        errors.append("ARC-v2 vc33 smoke receipt: canonical byte hash changed")

    expected_second_act_arc = {'absolute_arm_rhae_retained': False,
     'all_paired_rhae_deltas': 0.0,
     'arms': ['baseline', 'ember'],
     'full_five_game_rerun': {'execution': 'owner_only_package',
                              'launch_order': 'first_post_launch_update',
                              'public_command': None,
                              'status': 'HOLD_UNTIL_AFTER_PUBLIC_FLIP'},
     'games': 5,
     'identity': 'Ember',
     'levels_completed_retained': False,
     'memory_efficiency_hypothesis': 'open',
     'method': {'fresh_sessions': True,
                'helper_anomaly_observed': False,
                'model_lane': 'Claude Sonnet',
                'obsolete_bridge_helper_bypassed': True,
                'transport': 'direct Claude CLI'},
     'paired_null_interpretation': 'zero_level_vs_equal_nonzero_not_distinguishable',
     'result_framing': 'same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)',
     'revisited_state_repeated_control_split_retained': False,
     'scorecard_interrogation': {'absolute_arm_rhae_recovered': False,
                                 'closed_scorecards_queried': 10,
                                 'game_or_provider_requests_performed': False,
                                 'html_result': 'redirected_to_generic_arc_agi_3_page',
                                 'observed_http_status': 404,
                                 'pinned_contract': 'open_or_closed_scorecard_retrieval'},
     'total_actions_retained': False,
     'vc33': {'baseline': {'journal_records': 36,
                           'levels_completed': 0,
                           'per_level_action_counts': [35, 0, 0, 0, 0, 0, 0],
                           'shadow_rhae': 0.0,
                           'termination': 'ACTION_BUDGET',
                           'total_actions': 35,
                           'wasted_actions': {'official_feedback_wasted_actions': 0,
                                              'repeated_known_controls': 0,
                                              'revisited_states': 0}},
              'custody': 'local_owner_only',
              'ember': {'journal_records': 36,
                        'levels_completed': 0,
                        'per_level_action_counts': [35, 0, 0, 0, 0, 0, 0],
                        'shadow_rhae': 0.0,
                        'termination': 'ACTION_BUDGET',
                        'total_actions': 35,
                        'wasted_actions': {'official_feedback_wasted_actions': 0,
                                           'repeated_known_controls': 0,
                                           'revisited_states': 0}},
              'game': 'vc33',
              'paired_shadow_rhae_delta': 0.0,
              'public_receipt_path': 'bench/results/arc3-vc33-smoke-v2-public.json',
              'public_receipt_sha256': '002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551'},
     'wasted_actions': {'baseline': 646,
                        'baseline_minus_ember_percent_of_baseline': -1.238390092879257,
                        'ember': 654}}
    if release.get("second_act", {}).get("arc") != expected_second_act_arc:
        errors.append("day7 receipt: ARC method or evidence boundary changed")

    expected_hashes = {
        "sanitized_terminal_receipt_sha256": _sha256(public_path),
        "transport_terminal_receipt_sha256": _sha256(transport_path),
        "transport_postmortem_sha256": _sha256(postmortem_path),
        "arc_terminal_receipt_sha256": _sha256(arc_path),
        "arc_interrogation_receipt_sha256": _sha256(interrogation_path),
        "arc_v2_public_receipt_sha256": _sha256(vc33_smoke_path),
        "install_matrix_public_receipt_sha256": _sha256(install_matrix_path),
        "install_matrix_owner_aggregate_receipt_sha256": "6d6950dc55611130b3811b5988278f88ea00bffacc6fc9f29dfbd13e3d4044a9",
        "install_real_adapters_public_receipt_sha256": _sha256(real_adapters_path),
    }
    for key, value in expected_hashes.items():
        if evidence.get(key) != value:
            errors.append(f"day7 receipt: stale {key}")
    if evidence.get("arc_terminal_receipt_path") != "bench/results/arc3-ember-five-public-v9-result.json":
        errors.append("day7 receipt: stale ARC public receipt path")
    if evidence.get("arc_interrogation_receipt_path") != "bench/results/arc3-scorecard-interrogation-public-v1.json":
        errors.append("day7 receipt: stale ARC interrogation receipt path")
    if evidence.get("arc_v2_public_receipt_path") != "bench/results/arc3-vc33-smoke-v2-public.json":
        errors.append("day7 receipt: stale ARC-v2 public receipt path")
    if evidence.get("install_matrix_public_receipt_path") != "bench/results/install-matrix-v0.1.2-final-public.json":
        errors.append("day7 receipt: stale install-matrix public receipt path")
    if evidence.get("install_real_adapters_public_receipt_path") != "bench/results/install-real-adapters-v0.1.2-final-public.json":
        errors.append("day7 receipt: stale final real-adapter public receipt path")
    expected_historical_install_evidence = {
        "status": "preserved_superseded_by_final_662b713_matrix",
        "a06a_matrix_public_receipt_path": "bench/results/install-matrix-v0.1.2-public.json",
        "a06a_matrix_public_receipt_sha256": _sha256(historical_install_matrix_path),
        "a06a_matrix_owner_aggregate_receipt_sha256": "d7413c826f3efc9124c757705c1fffa7b3099102497193f2a436b9e7a230290b",
        "a06a_real_adapters_public_receipt_path": "bench/results/install-real-adapters-v0.1.2-public.json",
        "a06a_real_adapters_public_receipt_sha256": _sha256(historical_real_adapters_path),
    }
    if evidence.get("historical_install_evidence") != expected_historical_install_evidence:
        errors.append("day7 receipt: historical a06a install evidence binding changed")
    if score.get("terminal_receipt_path") is not None or score.get("terminal_receipt_retained_private") is not True:
        errors.append("day7 receipt: missing private-terminal path boundary")
    if score.get("terminal_receipt_sha256") != "27bbb4da02bf75ff5c3c6b73697bf8518e33566a55f3b9fc8d7012ee5b648e74":
        errors.append("day7 receipt: retained private terminal identity changed")
    saga = release.get("saga", {})
    expected_historical_saga = {
        "authorized_score_occurrences": 1,
        "git_blob": "0592ed60ec98c57e5e7f37e170ba7ec036303f69",
        "path": "docs/launch-saga.md",
        "private_draft_markers_remaining": 0,
        "sha256": "5899a4047941d85dce67493366772e0e1c05df5ffd350c4841507c9506faa72d",
    }
    if saga != expected_historical_saga:
        errors.append("day7 receipt: historical launch saga identity changed")
    runbook = release.get("runbook", {})
    if runbook != {
        "path": "docs/day7-public-launch.md",
        "sha256": _sha256(runbook_path),
        "git_blob": _git_blob(runbook_path),
    }:
        errors.append("day7 receipt: stale launch runbook identity")
    if _sha256(release_path) != "3f5a32294fb3a678baf53223f65c1f6bca5d58387e75bc20ab33e62bd214334e":
        errors.append("day7 receipt: canonical private-main receipt byte hash changed")
    if saga.get("authorized_score_occurrences") != 1 or release.get("release_asset_requests_performed") is not False:
        errors.append("day7 receipt: publication or score-occurrence boundary changed")

    go_section = runbook_path.read_text(encoding="utf-8").split(
        "## Approval-gated private-main validation, build, tag, and release", 1
    )[1].split("## Anonymous public verification", 1)[0]
    for forbidden in ("ASSEMBLY=", "launch/day7-public-assembly", "git fetch ", "git switch ", "git merge "):
        if forbidden in go_section:
            errors.append(f"day7 runbook: GO block retains deleted-branch dependency: {forbidden}")

    for path in (
        release_path,
        public_path,
        transport_path,
        arc_path,
        interrogation_path,
        vc33_smoke_path,
        install_matrix_path,
        historical_install_matrix_path,
        real_adapters_path,
        historical_real_adapters_path,
        postmortem_path,
    ):
        text = path.read_text(encoding="utf-8")
        for private_prefix in ("/Users/", "/private/tmp/", "C:\\Users\\"):
            if private_prefix in text:
                errors.append(f"{path.relative_to(ROOT)}: private host path leaked: {private_prefix}")
    return errors

def main() -> int:
    errors = (
        check_root_layout()
        + check_relative_links()
        + check_site_onboarding_contract()
        + check_claim_contract()
        + check_arc_public_surface()
        + check_alias_delta_receipt()
        + check_integration_acceptance_receipt()
        + check_candidate_readiness_supersession()
        + check_launch_receipts()
    )
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
