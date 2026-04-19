"""Diff consecutive log records by field changes."""
from typing import Iterator, Dict, Any, Optional, List


def diff_records(
    records: Iterator[Dict[str, Any]],
    fields: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield records annotated with fields that changed from the previous record.

    Each output record gains a ``_changed`` key listing field names whose
    values differ from the previous record.  The first record always has an
    empty ``_changed`` list.

    Args:
        records: Iterable of parsed log records.
        fields: If given, only track changes in these fields.
    """
    prev: Optional[Dict[str, Any]] = None
    for rec in records:
        out = dict(rec)
        if prev is None:
            out["_changed"] = []
        else:
            watch = fields if fields else list(rec.keys())
            changed = [
                k for k in watch
                if rec.get(k) != prev.get(k)
            ]
            out["_changed"] = changed
        yield out
        prev = rec


def only_changed(
    records: Iterator[Dict[str, Any]],
    fields: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield only records where at least one tracked field changed.

    The first record is always suppressed because there is nothing to compare
    it against.

    Args:
        records: Iterable of parsed log records.
        fields: If given, only consider changes in these fields.
    """
    for rec in diff_records(records, fields=fields):
        if rec.get("_changed"):
            yield rec


def summarise_changes(
    records: Iterator[Dict[str, Any]],
    fields: Optional[List[str]] = None,
) -> Dict[str, int]:
    """Return a count of how many times each field changed across all records.

    Args:
        records: Iterable of parsed log records.
        fields: If given, only count changes in these fields.

    Returns:
        A dict mapping field name to the number of records in which it changed.
    """
    counts: Dict[str, int] = {}
    for rec in diff_records(records, fields=fields):
        for field in rec.get("_changed", []):
            counts[field] = counts.get(field, 0) + 1
    return counts
