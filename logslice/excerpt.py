"""excerpt.py — extract a contiguous slice of records by index range."""
from __future__ import annotations

from typing import Iterable, Iterator


def excerpt_records(
    records: Iterable[dict],
    start: int = 0,
    end: int | None = None,
) -> Iterator[dict]:
    """Yield records whose 0-based index falls within [start, end).

    Args:
        records: Iterable of parsed log records.
        start:   First index to include (inclusive, default 0).
        end:     One past the last index to include (exclusive).
                 ``None`` means no upper bound.

    Yields:
        Records within the specified index range.
    """
    if start < 0:
        raise ValueError(f"start must be >= 0, got {start}")
    if end is not None and end < start:
        raise ValueError(f"end must be >= start, got end={end} start={start}")

    for idx, record in enumerate(records):
        if idx < start:
            continue
        if end is not None and idx >= end:
            break
        yield record


def excerpt_by_fraction(
    records: Iterable[dict],
    from_pct: float = 0.0,
    to_pct: float = 1.0,
) -> list[dict]:
    """Return records that fall within a fractional range of the total.

    Because the total count is unknown up front the input is fully
    materialised before slicing.

    Args:
        records:  Iterable of parsed log records.
        from_pct: Start fraction in [0.0, 1.0].
        to_pct:   End fraction in [0.0, 1.0].

    Returns:
        List of records in the requested fraction window.
    """
    if not (0.0 <= from_pct <= 1.0):
        raise ValueError(f"from_pct must be in [0, 1], got {from_pct}")
    if not (0.0 <= to_pct <= 1.0):
        raise ValueError(f"to_pct must be in [0, 1], got {to_pct}")
    if to_pct < from_pct:
        raise ValueError("to_pct must be >= from_pct")

    all_records = list(records)
    n = len(all_records)
    start = int(n * from_pct)
    end = int(n * to_pct)
    return all_records[start:end]


def parse_excerpt_arg(value: str) -> tuple[int, int | None]:
    """Parse a ``START:END`` or ``START:`` excerpt argument.

    Returns:
        Tuple of (start, end) where end may be None.
    """
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError(f"excerpt must be START:END or START:, got {value!r}")
    raw_start, raw_end = parts
    try:
        start = int(raw_start) if raw_start else 0
    except ValueError:
        raise ValueError(f"invalid start index: {raw_start!r}")
    if raw_end == "":
        return start, None
    try:
        end = int(raw_end)
    except ValueError:
        raise ValueError(f"invalid end index: {raw_end!r}")
    return start, end
