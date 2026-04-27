"""threshold.py – alert when a numeric field crosses a threshold."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

_OPS = {
    "gt": lambda v, t: v > t,
    "gte": lambda v, t: v >= t,
    "lt": lambda v, t: v < t,
    "lte": lambda v, t: v <= t,
    "eq": lambda v, t: v == t,
    "ne": lambda v, t: v != t,
}

_ARG_RE = re.compile(r"^([^:]+):([^:]+):(-?\d+(?:\.\d+)?)$")


def parse_threshold_arg(arg: str) -> Tuple[str, str, float]:
    """Parse 'field:op:threshold' into (field, op, threshold).

    Raises ValueError for malformed or unknown operator.
    """
    m = _ARG_RE.match(arg)
    if not m:
        raise ValueError(
            f"Invalid threshold spec {arg!r}. Expected field:op:number."
        )
    field, op, raw = m.group(1), m.group(2), m.group(3)
    if op not in _OPS:
        raise ValueError(
            f"Unknown operator {op!r}. Choose from: {', '.join(sorted(_OPS))}."
        )
    return field, op, float(raw)


def check_threshold(
    record: Dict[str, Any],
    field: str,
    op: str,
    threshold: float,
) -> Optional[bool]:
    """Return True/False if field is numeric, None if field absent or non-numeric."""
    raw = record.get(field)
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return _OPS[op](value, threshold)


def apply_thresholds(
    records: Iterable[Dict[str, Any]],
    rules: List[Tuple[str, str, float]],
    tag_field: str = "_threshold",
    only_triggered: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Annotate records with triggered threshold labels.

    Each triggered rule appends 'field:op:threshold' to *tag_field*.
    If *only_triggered* is True, records with no triggers are dropped.
    """
    for record in records:
        triggered: List[str] = []
        for field, op, threshold in rules:
            result = check_threshold(record, field, op, threshold)
            if result:
                triggered.append(f"{field}:{op}:{threshold:g}")
        if only_triggered and not triggered:
            continue
        out = dict(record)
        if triggered:
            out[tag_field] = ",".join(triggered)
        yield out
