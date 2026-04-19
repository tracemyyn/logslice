"""unique.py – yield only records where a field's value is seen for the first time."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional


def unique_by(records: Iterable[dict], fields: List[str]) -> Iterator[dict]:
    """Yield records whose combination of *fields* values has not been seen before."""
    seen: set = set()
    for rec in records:
        key = tuple(rec.get(f) for f in fields)
        if key not in seen:
            seen.add(key)
            yield rec


def unique_by_value(records: Iterable[dict], field: str) -> Iterator[dict]:
    """Yield records where *field* value is unique (first occurrence wins)."""
    return unique_by(records, [field])


def count_unique(records: Iterable[dict], fields: List[str]) -> int:
    """Return the number of distinct field-value combinations across *records*."""
    seen: set = set()
    for rec in records:
        seen.add(tuple(rec.get(f) for f in fields))
    return len(seen)


def apply_unique(
    records: Iterable[dict],
    fields: Optional[List[str]],
) -> Iterable[dict]:
    """Apply uniqueness filtering; passthrough when *fields* is empty/None."""
    if not fields:
        return records
    return unique_by(records, fields)
