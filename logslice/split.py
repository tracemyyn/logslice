"""Split records into multiple output buckets by field value."""
from __future__ import annotations

import os
from collections import defaultdict
from typing import Dict, Iterable, List, Optional


def split_by_field(
    records: Iterable[dict],
    field: str,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field*.

    Records that do not contain *field* are placed in the *missing_key* bucket.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        value = record.get(field)
        key = str(value) if value is not None else missing_key
        buckets[key].append(record)
    return dict(buckets)


def split_by_pattern(
    records: Iterable[dict],
    field: str,
    patterns: List[str],
    default_bucket: str = "other",
) -> Dict[str, List[dict]]:
    """Partition records into named buckets using substring patterns.

    *patterns* is a list of ``"label:pattern"`` strings.  The first matching
    label wins; non-matching records go to *default_bucket*.
    """
    import re

    rules: List[tuple] = []
    for spec in patterns:
        label, _, pat = spec.partition(":")
        if not pat:
            raise ValueError(f"Invalid split pattern spec (expected label:pattern): {spec!r}")
        rules.append((label.strip(), re.compile(pat)))

    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        value = str(record.get(field, ""))
        matched = False
        for label, regex in rules:
            if regex.search(value):
                buckets[label].append(record)
                matched = True
                break
        if not matched:
            buckets[default_bucket].append(record)
    return dict(buckets)


def bucket_sizes(buckets: Dict[str, List[dict]]) -> Dict[str, int]:
    """Return a mapping of bucket name -> record count."""
    return {k: len(v) for k, v in buckets.items()}


def apply_split(
    records: Iterable[dict],
    field: Optional[str],
    patterns: Optional[List[str]] = None,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """High-level helper: split by pattern if patterns given, else by field value."""
    if field is None:
        return {"all": list(records)}
    if patterns:
        return split_by_pattern(records, field, patterns)
    return split_by_field(records, field, missing_key=missing_key)
