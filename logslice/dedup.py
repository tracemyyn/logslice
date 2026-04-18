"""Deduplication utilities for log records."""
from __future__ import annotations

import hashlib
import json
from typing import Iterable, Iterator, Optional


def _record_key(record: dict, fields: Optional[list[str]] = None) -> str:
    """Return a stable hash key for a record.

    If *fields* is given only those fields contribute to the key,
    otherwise the entire record is hashed.
    """
    if fields:
        subset = {k: record[k] for k in fields if k in record}
    else:
        subset = record
    serialised = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.md5(serialised.encode()).hexdigest()


def dedup_records(
    records: Iterable[dict],
    fields: Optional[list[str]] = None,
    keep: str = "first",
) -> Iterator[dict]:
    """Yield deduplicated records.

    Parameters
    ----------
    records:
        Iterable of parsed log record dicts.
    fields:
        Optional list of field names to use as the dedup key.
        When *None* the whole record is compared.
    keep:
        ``'first'`` (default) keeps the first occurrence;
        ``'last'`` keeps the last occurrence.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    if keep == "first":
        seen: set[str] = set()
        for record in records:
            key = _record_key(record, fields)
            if key not in seen:
                seen.add(key)
                yield record
    else:  # last
        # Buffer everything — only feasible for reasonably sized streams.
        buf: dict[str, dict] = {}
        order: list[str] = []
        for record in records:
            key = _record_key(record, fields)
            if key not in buf:
                order.append(key)
            buf[key] = record
        for key in order:
            yield buf[key]


def count_duplicates(records: Iterable[dict], fields: Optional[list[str]] = None) -> int:
    """Return the number of records that are duplicates (would be removed by dedup)."""
    seen: set[str] = set()
    duplicates = 0
    for record in records:
        key = _record_key(record, fields)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates
