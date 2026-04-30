"""Compute field value frequency distributions over a stream of records."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Iterator


def count_values(records: Iterable[dict], field: str) -> Counter:
    """Return a Counter mapping each distinct value of *field* to its count."""
    c: Counter = Counter()
    for rec in records:
        if field in rec:
            c[str(rec[field])] += 1
    return c


def frequency_table(
    counter: Counter,
    top: int | None = None,
    ascending: bool = False,
) -> list[dict]:
    """Convert a Counter to a list of dicts with value/count/pct keys.

    Args:
        counter: raw counts produced by :func:`count_values`.
        top:     if given, return only the *top* most-frequent entries.
        ascending: sort least-frequent first when True.
    """
    total = sum(counter.values()) or 1
    pairs = counter.most_common()  # descending by default
    if ascending:
        pairs = list(reversed(pairs))
    if top is not None:
        pairs = pairs[:top]
    return [
        {"value": v, "count": c, "pct": round(c / total * 100, 2)}
        for v, c in pairs
    ]


def iter_frequency(
    records: Iterable[dict],
    field: str,
    top: int | None = None,
    ascending: bool = False,
) -> Iterator[dict]:
    """Convenience wrapper: consume *records* and yield frequency table rows."""
    counter = count_values(records, field)
    yield from frequency_table(counter, top=top, ascending=ascending)
