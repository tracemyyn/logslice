"""Pivot log records: transpose field values into columns for comparison."""
from typing import List, Dict, Any, Optional


def pivot_records(
    records: List[Dict[str, Any]],
    index_field: str,
    column_field: str,
    value_field: str,
) -> List[Dict[str, Any]]:
    """Pivot records so unique values of column_field become keys.

    Each output row is keyed by index_field; columns are the distinct
    values found in column_field, with the corresponding value_field value.
    """
    rows: Dict[Any, Dict[str, Any]] = {}
    for rec in records:
        idx = rec.get(index_field)
        col = rec.get(column_field)
        val = rec.get(value_field)
        if idx is None or col is None:
            continue
        if idx not in rows:
            rows[idx] = {index_field: idx}
        rows[idx][str(col)] = val
    return list(rows.values())


def column_names(
    records: List[Dict[str, Any]],
    index_field: str,
) -> List[str]:
    """Return sorted column names excluding the index field."""
    cols = set()
    for rec in records:
        cols.update(k for k in rec if k != index_field)
    return sorted(cols)


def fill_missing(
    pivoted: List[Dict[str, Any]],
    columns: List[str],
    fill_value: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Ensure every row has every column, filling absent ones with fill_value."""
    result = []
    for row in pivoted:
        filled = dict(row)
        for col in columns:
            if col not in filled:
                filled[col] = fill_value
        result.append(filled)
    return result
