#!/usr/bin/env python3
"""Weekly visibility sweep: surface live threads where Azdaja is a genuine answer.

Read-only. Queries public APIs (GitHub issue search, HN Algolia) and writes a
markdown queue for human review. It never posts, replies, emails, or runs model
inference. Posting any drafted reply is a separate, explicitly authorized human
action; see docs/visibility-ops.md OP-3 for the rules of engagement.

Usage:
  python3 tools/visibility_sweep.py [--out docs/outreach/queue-YYYY-MM-DD.md]
  python3 tools/visibility_sweep.py --force  # explicit same-path replacement

Unauthenticated GitHub search is rate-limited (~10 requests/min). With `gh`
installed and authenticated, set GITHUB_TOKEN to raise the limit.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

# Verified 2026-08-28: hit counts at last test are recorded in
# docs/visibility-ops.md OP-3. opencode lives at anomalyco/opencode (moved from
# sst/opencode).
GITHUB_QUERIES = [
    'repo:anthropics/claude-code is:issue is:open "context limit"',
    'repo:anthropics/claude-code is:issue is:open "large file" context',
    'repo:openai/codex is:issue is:open "context window"',
    'repo:anomalyco/opencode is:issue is:open "context window"',
    'repo:google-gemini/gemini-cli is:issue is:open "context window"',
]

HN_QUERIES = [
    '"context rot"',
    '"recursive language model"',
    '"context window" agent',
]

RECENT_DAYS = 8  # one-week cadence with overlap


def fetch_json(url: str) -> dict:
    headers = {"User-Agent": "azdaja-visibility-sweep"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def prior_queue_urls(out_path: str) -> set[str]:
    """Return links already surfaced in sibling queue files."""
    pattern = os.path.join(os.path.dirname(out_path) or ".", "queue-*.md")
    urls: set[str] = set()
    for path in glob.glob(pattern):
        if os.path.abspath(path) == os.path.abspath(out_path):
            continue
        try:
            with open(path, encoding="utf-8") as handle:
                urls.update(re.findall(r"\]\((https?://[^)]+)\)", handle.read()))
        except OSError:
            continue
    return urls


def github_rows(cutoff: str, seen: set[str]) -> list[str]:
    rows = []
    for query in GITHUB_QUERIES:
        scoped = f"{query} updated:>{cutoff}"
        url = (
            "https://api.github.com/search/issues?per_page=10&sort=updated&q="
            + urllib.parse.quote(scoped)
        )
        try:
            data = fetch_json(url)
        except Exception as error:  # rate limit or transient — record and move on
            rows.append(f"- QUERY FAILED `{scoped}`: {error}")
            continue
        rows.append(f"- `{scoped}` — {data.get('total_count', '?')} recently active")
        for item in data.get("items", []):
            if item["html_url"] in seen:
                continue
            rows.append(
                f"  - [ ] [{item['title'].strip()}]({item['html_url']})"
                f" ({item.get('comments', 0)} comments)"
            )
        time.sleep(7)  # stay under the unauthenticated search limit
    return rows


def hn_rows(cutoff_epoch: int, seen: set[str]) -> list[str]:
    rows = []
    for query in HN_QUERIES:
        url = (
            "https://hn.algolia.com/api/v1/search_by_date?tags=story"
            f"&numericFilters=created_at_i>{cutoff_epoch}&hitsPerPage=10&query="
            + urllib.parse.quote(query)
        )
        try:
            data = fetch_json(url)
        except Exception as error:
            rows.append(f"- QUERY FAILED `{query}`: {error}")
            continue
        rows.append(f"- HN `{query}` — {data.get('nbHits', '?')} stories this window")
        for hit in data.get("hits", []):
            item_url = f"https://news.ycombinator.com/item?id={hit['objectID']}"
            if item_url in seen:
                continue
            rows.append(
                f"  - [ ] [{(hit.get('title') or '(untitled)').strip()}]({item_url})"
                f" ({hit.get('points', 0)} pts)"
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    today = dt.date.today()
    parser.add_argument(
        "--out",
        default=f"docs/outreach/queue-{today.isoformat()}.md",
        help="markdown queue path",
    )
    parser.add_argument(
        "--include-seen",
        action="store_true",
        help="include URLs already present in earlier queue files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output file (never implicit)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="render the queue to stdout without writing a file",
    )
    args = parser.parse_args()

    seen = set() if args.include_seen else prior_queue_urls(args.out)

    cutoff_date = (today - dt.timedelta(days=RECENT_DAYS)).isoformat()
    cutoff_epoch = int(
        dt.datetime.combine(
            today - dt.timedelta(days=RECENT_DAYS), dt.time.min, dt.timezone.utc
        ).timestamp()
    )

    lines = [
        f"# Outreach queue — {today.isoformat()}",
        "",
        "Generated by `tools/visibility_sweep.py` (read-only). Review rules:",
        "docs/visibility-ops.md OP-3. Check a box only after a human decided the",
        "thread deserves a reply; drafting happens in this file, posting is manual.",
        "URLs from earlier queue files are omitted unless `--include-seen` is used.",
        "",
        "## GitHub issues (recently active)",
        *github_rows(cutoff_date, seen),
        "",
        "## Hacker News (new stories)",
        *hn_rows(cutoff_epoch, seen),
        "",
        "## Shortlist (human)",
        "",
        "Pick at most 5. For each, read the venue's current rules and draft one "
        "paragraph for operator review.",
        "",
        "## Reviewed but not shortlisted",
        "",
        "Record why plausible-looking threads were rejected. This is the anti-spam",
        "proof; a queue is incomplete until the rejection rationale is reviewed.",
        "",
    ]

    out_path = args.out
    rendered = "\n".join(lines)
    if args.dry_run:
        print(rendered, end="")
        return 0

    if os.path.exists(out_path) and not args.force:
        parser.error(f"refusing to overwrite existing queue: {out_path}; pass --force")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
