"""Truncate long field values to a maximum length."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]

_SENTINEL = "..."


def truncate_value(value: Any, max_len: int, marker: str = _SENTINEL) -> Any:
    """Truncate a string value to *max_len* chars, appending *marker* if cut."""
    if not isinstance(value, str):
        return value
    if len(value) <= max_len:
        return value
    cut = max(0, max_len - len(marker))
    return value[:cut] + marker


def truncate_fields(
    record: Record,
    fields: Optional[List[str]],
    max_len: int,
    marker: str = _SENTINEL,
) -> Record:
    """Return a copy of *record* with specified (or all) fields truncated."""
    if max_len <= 0:
        raise ValueError("max_len must be a positive integer")
    out = dict(record)
    targets = fields if fields else list(out.keys())
    for key in targets:
        if key in out:
            out[key] = truncate_value(out[key], max_len, marker)
    return out


def apply_truncate(
    records: Iterable[Record],
    fields: Optional[List[str]],
    max_len: int,
    marker: str = _SENTINEL,
) -> Iterator[Record]:
    """Yield records with truncated field values."""
    for record in records:
        yield truncate_fields(record, fields, max_len, marker)


def parse_truncate_args(fields_arg: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated fields string into a list, or return None."""
    if not fields_arg:
        return None
    return [f.strip() for f in fields_arg.split(",") if f.strip()]
