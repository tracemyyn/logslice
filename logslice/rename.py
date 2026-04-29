"""Bulk field renaming with pattern support."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List


def rename_by_map(record: dict, mapping: Dict[str, str]) -> dict:
    """Return a new record with fields renamed according to *mapping*.

    Keys not present in *mapping* are left unchanged.
    If a source key does not exist in the record it is silently skipped.
    """
    out = {}
    for key, value in record.items():
        out[mapping.get(key, key)] = value
    return out


def rename_by_prefix(record: dict, old_prefix: str, new_prefix: str) -> dict:
    """Replace *old_prefix* with *new_prefix* on every matching key."""
    out = {}
    for key, value in record.items():
        if key.startswith(old_prefix):
            out[new_prefix + key[len(old_prefix):]] = value
        else:
            out[key] = value
    return out


def rename_by_regex(record: dict, pattern: str, replacement: str) -> dict:
    """Rename keys where *pattern* matches, substituting with *replacement*.

    Uses :func:`re.sub` so capture groups in *replacement* are supported.
    """
    rx = re.compile(pattern)
    out = {}
    for key, value in record.items():
        new_key = rx.sub(replacement, key)
        out[new_key] = value
    return out


def parse_rename_arg(arg: str) -> tuple[str, str]:
    """Parse a ``old=new`` rename specification.

    Returns ``(old, new)`` or raises :class:`ValueError`.
    """
    parts = arg.split("=", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid rename spec {arg!r}: expected 'old=new'")
    return parts[0], parts[1]


def parse_rename_args(args: List[str]) -> Dict[str, str]:
    """Parse a list of ``old=new`` specs into a mapping dict."""
    return dict(parse_rename_arg(a) for a in args)


def apply_rename(
    records: Iterable[dict],
    mapping: Dict[str, str] | None = None,
    prefix_old: str | None = None,
    prefix_new: str | None = None,
    regex: str | None = None,
    regex_replacement: str = "",
) -> Iterable[dict]:
    """Apply renaming operations to each record in *records*.

    Operations are applied in order: map → prefix → regex.
    """
    for record in records:
        if mapping:
            record = rename_by_map(record, mapping)
        if prefix_old is not None and prefix_new is not None:
            record = rename_by_prefix(record, prefix_old, prefix_new)
        if regex is not None:
            record = rename_by_regex(record, regex, regex_replacement)
        yield record
