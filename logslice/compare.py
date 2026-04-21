"""Field-level value comparison utilities for logslice.

Allows comparing a specific field across two streams of records,
emitting records where the field value differs between the two inputs.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Record = Dict[str, Any]


def _get(record: Record, field: str) -> Optional[Any]:
    """Return the value of *field* from *record*, or None if absent."""
    return record.get(field)


def compare_field(
    left: Record,
    right: Record,
    field: str,
) -> Optional[Tuple[Any, Any]]:
    """Return (left_val, right_val) if they differ, else None."""
    lv = _get(left, field)
    rv = _get(right, field)
    if lv != rv:
        return (lv, rv)
    return None


def compare_records(
    left: Record,
    right: Record,
    fields: List[str],
) -> Dict[str, Tuple[Any, Any]]:
    """Return a mapping of field -> (left_val, right_val) for all differing fields."""
    diffs: Dict[str, Tuple[Any, Any]] = {}
    for field in fields:
        result = compare_field(left, right, field)
        if result is not None:
            diffs[field] = result
    return diffs


def align_by_key(
    left: Iterable[Record],
    right: Iterable[Record],
    key: str,
) -> Iterator[Tuple[Record, Record]]:
    """Yield (left_record, right_record) pairs sharing the same key value.

    Records with no match on either side are silently dropped (inner join).
    """
    index: Dict[Any, Record] = {}
    for rec in right:
        k = _get(rec, key)
        if k is not None:
            index[k] = rec
    for rec in left:
        k = _get(rec, key)
        if k is not None and k in index:
            yield rec, index[k]


def apply_compare(
    left: Iterable[Record],
    right: Iterable[Record],
    key: str,
    fields: List[str],
    tag: str = "_diff",
) -> Iterator[Record]:
    """Emit enriched left records where any of *fields* differ from the right side.

    Each emitted record gains a *tag* key containing the diff mapping.
    """
    for l_rec, r_rec in align_by_key(left, right, key):
        diffs = compare_records(l_rec, r_rec, fields)
        if diffs:
            out = dict(l_rec)
            out[tag] = {
                field: {"left": lv, "right": rv}
                for field, (lv, rv) in diffs.items()
            }
            yield out
