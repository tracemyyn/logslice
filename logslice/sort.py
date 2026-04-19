"""Sort log records by one or more fields."""

from typing import Any, Dict, Iterable, List, Optional

Record = Dict[str, Any]


def _coerce(value: Any) -> Any:
    """Try to coerce a value to float for numeric sorting."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value) if value is not None else ""


def sort_records(
    records: Iterable[Record],
    fields: List[str],
    reverse: bool = False,
    numeric: bool = False,
) -> List[Record]:
    """Sort records by the given fields in order.

    Args:
        records: Iterable of log records.
        fields: Field names to sort by (left = primary key).
        reverse: If True, sort descending.
        numeric: If True, coerce values to float before comparing.

    Returns:
        Sorted list of records.
    """
    records = list(records)
    if not fields:
        return records

    def key_fn(rec: Record):
        values = [rec.get(f) for f in fields]
        if numeric:
            return [_coerce(v) for v in values]
        return [str(v) if v is not None else "" for v in values]

    return sorted(records, key=key_fn, reverse=reverse)


def stable_sort_records(
    records: Iterable[Record],
    field: str,
    reverse: bool = False,
) -> List[Record]:
    """Stable sort by a single field; records missing the field sort last."""
    present = [r for r in records if field in r]
    missing = [r for r in records if field not in r]  # type: ignore[operator]
    # re-iterate — collect once
    all_records = list(records) if not (present or missing) else present + missing
    present = [r for r in all_records if field in r]
    missing = [r for r in all_records if field not in r]
    sorted_present = sorted(present, key=lambda r: _coerce(r[field]), reverse=reverse)
    return sorted_present + missing
