#!/usr/bin/env python3
"""Render the README's evidence-bounded prompt-envelope crossover figure."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "token-context-crossover.svg"

WIDTH, HEIGHT = 960, 560
LEFT, RIGHT, TOP, BOTTOM = 105, 920, 78, 450
X_MIN_MIB, X_MAX_MIB = 0.01, 50.0
Y_MIN_TOKENS, Y_MAX_TOKENS = 2_000.0, 20_000_000.0
BYTES_PER_TOKEN = 4.0  # explicit illustration assumption, not tokenizer evidence
ROOT_ENVELOPE_BYTES = 64 * 1024  # public acceptance-test upper bound
ROOT_ENVELOPE_TOKENS = ROOT_ENVELOPE_BYTES / BYTES_PER_TOKEN


def x_pos(value: float) -> float:
    span = math.log10(X_MAX_MIB) - math.log10(X_MIN_MIB)
    return LEFT + (math.log10(value) - math.log10(X_MIN_MIB)) / span * (RIGHT - LEFT)


def y_pos(value: float) -> float:
    span = math.log10(Y_MAX_TOKENS) - math.log10(Y_MIN_TOKENS)
    return BOTTOM - (math.log10(value) - math.log10(Y_MIN_TOKENS)) / span * (BOTTOM - TOP)


def direct_tokens(mib: float) -> float:
    return mib * 1024 * 1024 / BYTES_PER_TOKEN


def render() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="560" viewBox="0 0 960 560" role="img" aria-labelledby="title desc">',
        '  <title id="title">Illustrative whole-input and bounded-root prompt crossover</title>',
        '  <desc id="desc">Log-log plot. A hypothetical prompt containing the whole UTF-8 input crosses a constant 64 KiB root-prompt envelope at 0.0625 MiB under a four bytes per token assumption. Exact Azdaja acceptance evidence exists only for three synthetic 50 MiB cases. This is not a total token, price, or savings measurement.</desc>',
        '  <rect width="960" height="560" fill="#ffffff"/>',
        '  <text x="480" y="34" text-anchor="middle" font-family="system-ui, sans-serif" font-size="22" font-weight="700" fill="#17202a">Prompt-envelope crossover (illustrative)</text>',
        '  <text x="480" y="58" text-anchor="middle" font-family="system-ui, sans-serif" font-size="13" fill="#52606d">Log scales; 4 UTF-8 bytes/token assumed for both lines</text>',
    ]

    x_ticks = [(0.01, "0.01"), (0.0625, "0.0625"), (0.1, "0.1"), (1, "1"), (10, "10"), (50, "50")]
    y_ticks = [(10_000, "10k"), (100_000, "100k"), (1_000_000, "1M"), (10_000_000, "10M")]
    for value, label in y_ticks:
        y = y_pos(value)
        lines.extend([
            f'  <line x1="{LEFT}" y1="{y:.2f}" x2="{RIGHT}" y2="{y:.2f}" stroke="#dfe3e8" stroke-width="1"/>',
            f'  <text x="{LEFT - 12}" y="{y + 4:.2f}" text-anchor="end" font-family="system-ui, sans-serif" font-size="12" fill="#52606d">{label}</text>',
        ])
    for value, label in x_ticks:
        x = x_pos(value)
        lines.extend([
            f'  <line x1="{x:.2f}" y1="{TOP}" x2="{x:.2f}" y2="{BOTTOM}" stroke="#eef0f2" stroke-width="1"/>',
            f'  <text x="{x:.2f}" y="{BOTTOM + 22}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#52606d">{label}</text>',
        ])

    lines.extend([
        f'  <line x1="{LEFT}" y1="{BOTTOM}" x2="{RIGHT}" y2="{BOTTOM}" stroke="#17202a" stroke-width="1.5"/>',
        f'  <line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{BOTTOM}" stroke="#17202a" stroke-width="1.5"/>',
        f'  <text x="{(LEFT + RIGHT) / 2:.1f}" y="{BOTTOM + 52}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="14" fill="#17202a">UTF-8 input size (MiB)</text>',
        f'  <text x="28" y="{(TOP + BOTTOM) / 2:.1f}" text-anchor="middle" transform="rotate(-90 28 {(TOP + BOTTOM) / 2:.1f})" font-family="system-ui, sans-serif" font-size="14" fill="#17202a">Estimated prompt tokens</text>',
    ])

    direct_points = " ".join(
        f"{x_pos(mib):.2f},{y_pos(direct_tokens(mib)):.2f}"
        for mib in (X_MIN_MIB, 0.02, 0.04, 0.0625, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, X_MAX_MIB)
    )
    root_y = y_pos(ROOT_ENVELOPE_TOKENS)
    cross_x = x_pos(0.0625)
    fifty_x = x_pos(50)
    fifty_direct_y = y_pos(direct_tokens(50))
    lines.extend([
        f'  <polyline points="{direct_points}" fill="none" stroke="#b33a3a" stroke-width="4"/>',
        f'  <line x1="{LEFT}" y1="{root_y:.2f}" x2="{RIGHT}" y2="{root_y:.2f}" stroke="#1967a3" stroke-width="4" stroke-dasharray="9 6"/>',
        f'  <circle cx="{cross_x:.2f}" cy="{root_y:.2f}" r="6" fill="#ffffff" stroke="#17202a" stroke-width="2"/>',
        f'  <line x1="{cross_x:.2f}" y1="{root_y + 7:.2f}" x2="{cross_x:.2f}" y2="{BOTTOM}" stroke="#7b8794" stroke-width="1.5" stroke-dasharray="4 4"/>',
        f'  <text x="{cross_x + 10:.2f}" y="{root_y - 12:.2f}" font-family="system-ui, sans-serif" font-size="12" fill="#17202a">assumed crossover: 0.0625 MiB (64 KiB)</text>',
        f'  <circle cx="{fifty_x:.2f}" cy="{fifty_direct_y:.2f}" r="5" fill="#b33a3a"/>',
        f'  <circle cx="{fifty_x:.2f}" cy="{root_y:.2f}" r="5" fill="#1967a3"/>',
        f'  <text x="{fifty_x - 8:.2f}" y="{fifty_direct_y + 19:.2f}" text-anchor="end" font-family="system-ui, sans-serif" font-size="12" fill="#8f2e2e">50 MiB whole-input estimate: 13,107,200</text>',
        f'  <text x="{fifty_x - 8:.2f}" y="{root_y + 20:.2f}" text-anchor="end" font-family="system-ui, sans-serif" font-size="12" fill="#155680">64 KiB envelope estimate: 16,384</text>',
        '  <line x1="126" y1="96" x2="164" y2="96" stroke="#b33a3a" stroke-width="4"/>',
        '  <text x="174" y="101" font-family="system-ui, sans-serif" font-size="12" fill="#17202a">hypothetical whole input in one prompt</text>',
        '  <line x1="126" y1="119" x2="164" y2="119" stroke="#1967a3" stroke-width="4" stroke-dasharray="9 6"/>',
        '  <text x="174" y="124" font-family="system-ui, sans-serif" font-size="12" fill="#17202a">assumed constant 64 KiB Azdaja root envelope</text>',
        '  <text x="480" y="525" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#52606d">Exact evidence: three synthetic 50 MiB cases had root prompts below 64 KiB. No continuum was measured.</text>',
        '  <text x="480" y="545" text-anchor="middle" font-family="system-ui, sans-serif" font-size="12" fill="#52606d">Excludes child, repair, output, caching, tokenizer, and pricing effects; no total-token or savings claim.</text>',
        '</svg>',
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the committed SVG is stale")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale generated asset: run {Path(__file__).name}")
        print(f"ok: {OUTPUT.relative_to(ROOT)} is reproducible")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
