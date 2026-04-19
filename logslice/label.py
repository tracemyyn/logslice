"""Add computed label fields to records based on field value conditions."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

Record = Dict[str, Any]
Rule = Tuple[str, str, str, str]  # (dest_field, src_field, pattern, label)


def _match(value: str, pattern: str) -> bool:
    try:
        return bool(re.search(pattern, str(value)))
    except re.error:
        return str(value) == pattern


def apply_label(record: Record, rules: List[Rule], default: Optional[str] = None) -> Record:
    """Return a copy of *record* with label fields added according to *rules*.

    Each rule is (dest_field, src_field, pattern, label).  The first matching
    rule for a given dest_field wins.  If no rule matches and *default* is
    given the dest_field is set to *default*; otherwise it is omitted.
    """
    out = dict(record)
    dest_fields: Dict[str, bool] = {}
    for dest, src, pattern, label in rules:
        if dest in dest_fields:
            continue  # already resolved
        value = record.get(src)
        if value is not None and _match(str(value), pattern):
            out[dest] = label
            dest_fields[dest] = True
    if default is not None:
        for dest, _, __, ___ in rules:
            if dest not in dest_fields:
                out.setdefault(dest, default)
                dest_fields[dest] = True
    return out


def label_records(
    records: Iterable[Record],
    rules: List[Rule],
    default: Optional[str] = None,
) -> Iterable[Record]:
    for rec in records:
        yield apply_label(rec, rules, default=default)


def parse_label_arg(arg: str) -> Rule:
    """Parse 'dest:src:pattern:label' into a Rule tuple."""
    parts = arg.split(":", 3)
    if len(parts) != 4:
        raise ValueError(
            f"label rule must be 'dest:src:pattern:label', got: {arg!r}"
        )
    return (parts[0], parts[1], parts[2], parts[3])


def parse_label_args(args: List[str]) -> List[Rule]:
    return [parse_label_arg(a) for a in args]
