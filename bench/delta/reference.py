#!/usr/bin/env python3
"""Reference mechanics for the one-call row-645 diagnostic.

This module performs no inference. It freezes deterministic selection, stable deduplication,
compact sharding, response validation, and multiplicity expansion for provider-free tests.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

MAX_ITEMS = 256
MAX_CHARS = 65536
WORKERS = 6


class ReferenceError(RuntimeError):
    pass


def selected_instances(text: str) -> list[str]:
    selected: list[str] = []
    for line in text.splitlines():
        if " || Instance: " not in line:
            continue
        date, instance = line.split(" || Instance: ", 1)
        if re.search(r"\bMay\b", date):
            selected.append(instance.strip())
    return selected


def stable_unique(values: Iterable[str]) -> tuple[list[str], list[int]]:
    order: list[str] = []
    positions: dict[str, int] = {}
    multiplicities: list[int] = []
    for value in values:
        if value in positions:
            multiplicities[positions[value]] += 1
        else:
            positions[value] = len(order)
            order.append(value)
            multiplicities.append(1)
    return order, multiplicities


def item_line(index: int, text: str) -> str:
    return f"{index:04d}\t{json.dumps(text, ensure_ascii=False, separators=(',', ':'))}\n"


def shard_prompt(items: list[str], start: int) -> str:
    lines = [item_line(start + offset, value) for offset, value in enumerate(items)]
    return (
        "Classify each SMS as ham (H) or spam (S). Return exactly one compact JSON "
        f"object {json.dumps({'labels': 'H' * len(items)}, separators=(',', ':'))} but replace "
        "each placeholder with the correct H or S. The labels string length and order must "
        "match the input rows. No prose.\n" + "".join(lines)
    )


def pack(items: list[str]) -> list[tuple[int, list[str], str]]:
    shards: list[tuple[int, list[str], str]] = []
    start = 0
    current: list[str] = []
    for value in items:
        proposed = current + [value]
        prompt = shard_prompt(proposed, start)
        if current and (len(proposed) > MAX_ITEMS or len(prompt) > MAX_CHARS):
            frozen = shard_prompt(current, start)
            shards.append((start, current, frozen))
            start += len(current)
            current = [value]
        else:
            current = proposed
    if current:
        shards.append((start, current, shard_prompt(current, start)))
    for _, shard, prompt in shards:
        if len(shard) > MAX_ITEMS or len(prompt) > MAX_CHARS:
            raise ReferenceError("single item exceeds shard contract")
    return shards


def parse_labels(raw: str, expected: int) -> str:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReferenceError("response is not JSON") from exc
    if not isinstance(value, dict) or set(value) != {"labels"}:
        raise ReferenceError("response object keys must be exact")
    labels = value["labels"]
    if not isinstance(labels, str) or len(labels) != expected or any(c not in "HS" for c in labels):
        raise ReferenceError("labels must be an exact H/S positional string")
    return labels


def weighted_ham(labels: str, multiplicities: list[int]) -> int:
    if len(labels) != len(multiplicities):
        raise ReferenceError("label/multiplicity length mismatch")
    return sum(weight for label, weight in zip(labels, multiplicities) if label == "H")


def build(context: Path) -> dict[str, object]:
    selected = selected_instances(context.read_text(encoding="utf-8"))
    unique, multiplicities = stable_unique(selected)
    shards = pack(unique)
    return {
        "selected_records": len(selected),
        "unique_items": len(unique),
        "multiplicities": multiplicities,
        "shards": shards,
        "workers": WORKERS,
    }
