"""Numeric field filtering: range checks and comparisons."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple


def _coerce(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_numeric_arg(arg: str) -> Tuple[str, str, float]:
    """Parse 'field:op:value', e.g. 'latency:gt:200'.

    Supported ops: gt, gte, lt, lte, eq, ne
    """
    parts = arg.split(":")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid numeric filter {arg!r}. Expected field:op:value."
        )
    field, op, raw = parts
    valid_ops = {"gt", "gte", "lt", "lte", "eq", "ne"}
    if op not in valid_ops:
        raise ValueError(f"Unknown op {op!r}. Choose from {sorted(valid_ops)}.")
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"Cannot parse {raw!r} as a number in filter {arg!r}.")
    return field, op, value


def numeric_match(record: Dict[str, Any], field: str, op: str, threshold: float) -> bool:
    """Return True if record[field] satisfies op relative to threshold."""
    v = _coerce(record.get(field))
    if v is None:
        return False
    return {
        "gt":  v > threshold,
        "gte": v >= threshold,
        "lt":  v < threshold,
        "lte": v <= threshold,
        "eq":  v == threshold,
        "ne":  v != threshold,
    }[op]


def apply_numeric_filters(
    records: Iterable[Dict[str, Any]],
    filters: List[Tuple[str, str, float]],
) -> Iterator[Dict[str, Any]]:
    """Yield records that satisfy ALL numeric filters."""
    for record in records:
        if all(numeric_match(record, f, op, v) for f, op, v in filters):
            yield record


def parse_numeric_args(args: List[str]) -> List[Tuple[str, str, float]]:
    """Parse a list of raw filter strings into (field, op, value) triples."""
    return [parse_numeric_arg(a) for a in args]
