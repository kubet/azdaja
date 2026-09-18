#!/usr/bin/env python3
"""Export a prepared plan and native batch job as a standalone read-only HTML queue.

Usage: python /path/to/examples/jev_review_queue.py --plan DIR --job DIR --output NEW.html
Only Python's standard library is needed. No provider or application code is loaded.
Source bytes are the prepared snapshot, not a reread of the original local files.
NUL-containing text is rejected because HTML cannot preserve it exactly.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


# This constant is the only stylesheet. No source, question, or result enters CSS.
STYLE = """body { max-width: 76rem; margin: 0 auto; padding: 1rem; font: 1rem/1.5 system-ui, sans-serif; color: #222; background: #fff; overflow-wrap: anywhere; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font: 0.95rem/1.45 ui-monospace, monospace; }
details { margin: 0.75rem 0; padding: 0.75rem; border: 1px solid #bbb; border-radius: 0.3rem; }
summary { cursor: pointer; font-weight: 600; }
dt { font-weight: 600; }
dd { margin-left: 1rem; }
nav { margin: 1rem 0; }
"""
STYLE_HASH = base64.b64encode(hashlib.sha256(STYLE.encode("utf-8")).digest()).decode("ascii")


# Load the frozen sibling explicitly, including when invoked from outside the repo.
_spec = importlib.util.spec_from_file_location(
    "_jev_queue_batch_review", Path(__file__).resolve().with_name("jev_batch_review.py")
)
_review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_review)


def _escape(value):
    # Preserve CR and CRLF in the DOM too, rather than HTML newline normalization.
    return html.escape(str(value), quote=True).replace("\r", "&#13;")


def _json_text(value):
    return _escape(json.dumps(value, ensure_ascii=False, allow_nan=False))


def _criteria(plan):
    # report() validates source/request bindings first. This additional gate prevents
    # a global ranking of incomparable meanings in otherwise well-bound jobs.
    _, rows = _review._plan_rows(plan)
    question = rows[0]["questions"]
    if (set(question) != {"match"} or not isinstance(question["match"], dict)
            or set(question["match"]) != {"type", "instructions"}
            or question["match"]["type"] != "noul"
            or not isinstance(question["match"]["instructions"], str)
            or not question["match"]["instructions"].strip()
            or any(row["questions"] != question for row in rows)):
        raise ValueError("all windows must have one identical noul match question")
    return question["match"]["instructions"]


def _reject_nul(value):
    # HTML replaces NUL with U+FFFD. Refuse rather than silently alter source text.
    if isinstance(value, str):
        if "\0" in value:
            raise ValueError("NUL is not supported by the exact UTF-8 HTML text view")
    elif isinstance(value, dict):
        for key, item in value.items():
            _reject_nul(key)
            _reject_nul(item)
    elif isinstance(value, list):
        for item in value:
            _reject_nul(item)


def _render(rows, criteria):
    """Render only rows produced by report(), after all source validation succeeds."""
    completed = sorted((r for r in rows if r["status"] == "completed"),
                       key=lambda r: (-r["p"], r["id"]))
    unknown = sorted((r for r in rows if r["status"] in ("unknown", "unknown_inflight")),
                     key=lambda r: r["id"])
    pending = sorted((r for r in rows if r["status"] == "pending"), key=lambda r: r["id"])
    sources = {}
    for row in rows:
        # Source occurrence, not filename or hash: identical files remain distinct.
        sources.setdefault(row["id"].split("-", 1)[0], []).append(row)
    total_bytes = sum(len(r["text"].encode("utf-8")) for r in rows)
    parts = [
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">',
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
        f'script-src \'none\'; style-src \'sha256-{STYLE_HASH}\'; style-src-attr \'none\'; '
        'base-uri \'none\'; form-action \'none\'">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<style>{STYLE}</style>',
        '<title>Source review queue</title></head><body><main>',
        '<h1>Source review queue</h1>',
        '<section id="criteria"><h2>Question / criteria for every raw noul value</h2>',
        f'<pre><code>{_escape(criteria)}</code></pre></section>',
        '<p><strong>Probability is not truth.</strong> Raw noul values are model outputs, '
        'not verified facts or calibrated confidence. Ordering is for manual review only. '
        'There is no threshold, automatic approval, or recommendation to accept an answer.</p>',
        '<p>Read-only snapshot. All prepared source windows were validated before rendering. '
        'Source, request and response bindings were checked by jev_batch_review.report(). '
        'Coverage refers to the complete prepared sources, not the current original files. '
        'Unknown or in-flight work may have run without a retained result. '
        'Pending means no local intent or result was recorded at export time.</p>',
        f'<p id="counts">Full-source coverage: {len(sources)} source occurrences, '
        f'{len(rows)} of {len(rows)} windows, {total_bytes} UTF-8 bytes. '
        f'Completed: {len(completed)}. Unknown: {len(unknown)}. Pending: {len(pending)}.</p>',
        '<nav aria-label="Queue sections"><a href="#coverage">Coverage</a> | '
        '<a href="#completed">Completed</a> | <a href="#unknown">Unknown</a> | '
        '<a href="#pending">Pending</a></nav>',
        '<section id="coverage"><details id="coverage-sources">',
        f'<summary>Full-source coverage ({len(sources)} source occurrences)</summary>',
        '<p>Every window is included below, without truncation. Open a window to read its '
        'full source. Byte ranges are half-open [start, end) in the original UTF-8 source. '
        'Repeated names or hashes do not merge source occurrences.</p>',
        '<ul>',
    ]
    for index, windows in sources.items():
        first = windows[0]
        byte_count = sum(len(r["text"].encode("utf-8")) for r in windows)
        parts.append(
            f'<li>Source occurrence {_escape(index)}: {_escape(first["source_name"])}; '
            f'{len(windows)} windows; {byte_count} / {byte_count} UTF-8 bytes; '
            f'SHA-256 <code>{_escape(first["source_sha256"])}</code></li>'
        )
    parts.append('</ul></details></section>')
    for section, label, group in (
        ("completed", "Completed: descending raw p, then stable ID", completed),
        ("unknown", "Unknown: failed or ambiguous / in-flight", unknown),
        ("pending", "Pending: not locally attempted", pending),
    ):
        parts.append(f'<section id="{section}"><h2>{label} ({len(group)})</h2>')
        if not group:
            parts.append('<p>No windows in this section.</p>')
        for row in group:
            ident = _escape(row["id"])
            parts.extend([
                f'<details id="window-{ident}"><summary>ID {ident} | '
                f'{_escape(row["source_name"])} | {_escape(row["status"])} | '
                f'raw noul: {_json_text(row["p"])}</summary>',
                '<dl>',
                f'<dt>Stable ID</dt><dd>{ident}</dd>',
                f'<dt>Source name</dt><dd>{_escape(row["source_name"])}</dd>',
                f'<dt>Source SHA-256</dt><dd><code>{_escape(row["source_sha256"])}</code></dd>',
                f'<dt>Original UTF-8 byte offsets [start, end)</dt><dd>'
                f'[{row["start_byte"]}, {row["end_byte"]})</dd>',
                f'<dt>Status</dt><dd>{_escape(row["status"])}</dd>',
                f'<dt>Raw noul value (null means unavailable)</dt><dd><code>{_json_text(row["p"])}</code></dd>',
                f'<dt>Raw answer</dt><dd><pre><code>{_json_text(row["raw_answer"])}</code></pre></dd>',
                '</dl><h3>Full source window</h3>',
                f'<pre class="source"><code>{_escape(row["text"])}</code></pre></details>',
            ])
        parts.append('</section>')
    parts.append('</main></body></html>\n')
    return '\n'.join(parts).encode('utf-8')


def export(plan, job, output):
    """Validate in private scratch space, then exclusively create an owner-only HTML file."""
    plan, job, output = Path(plan), Path(job), Path(output)
    if output.suffix.lower() != ".html":
        raise ValueError("output must be a new .html file")
    if os.path.lexists(output):
        raise ValueError("output already exists")
    parent = os.environ.get("JCODE_SCRATCH_DIR") or str(output.absolute().parent)
    with tempfile.TemporaryDirectory(prefix="jev-review-queue-", dir=parent) as temporary:
        snapshot = Path(temporary) / "plan"
        snapshot.mkdir(mode=0o700)
        for name in ("plan.jsonl", "sources.json"):
            _review._create_private(snapshot / name, _review._bytes(plan / name))
        report_path = Path(temporary) / "validated.jsonl"
        _review.report(snapshot, job, report_path)
        criteria = _criteria(snapshot)
        # The private report can exceed MAX_PLAN_BYTES because it adds audit fields.
        # It is generated locally from the bounded plan, not an untrusted input file.
        with report_path.open("rb") as handle:
            rows = [_review._loads(line) for line in handle]
        _reject_nul(rows)
        _reject_nul(criteria)
        document = _render(rows, criteria)
    # Same exclusive/no-follow/0600 helper as the frozen exporter. No replacement.
    _review._create_private(output, document)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        export(args.plan, args.job, args.output)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, RecursionError):
        print("error: invalid, changed, unsafe or occupied input/output; no provider was contacted",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
