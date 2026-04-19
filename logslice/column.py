"""Column selection and reordering for structured log records."""
from typing import Dict, Any, List, Optional


def select_columns(record: Dict[str, Any], columns: List[str]) -> Dict[str, Any]:
    """Return a new record containing only the specified columns, in order."""
    return {col: record[col] for col in columns if col in record}


def reorder_columns(record: Dict[str, Any], first: List[str]) -> Dict[str, Any]:
    """Return record with `first` keys appearing before the rest."""
    ordered = {k: record[k] for k in first if k in record}
    ordered.update({k: v for k, v in record.items() if k not in ordered})
    return ordered


def exclude_columns(record: Dict[str, Any], exclude: List[str]) -> Dict[str, Any]:
    """Return record with specified columns removed."""
    return {k: v for k, v in record.items() if k not in exclude}


def column_names(records: List[Dict[str, Any]]) -> List[str]:
    """Collect all unique column names seen across records, preserving first-seen order."""
    seen: List[str] = []
    seen_set: set = set()
    for rec in records:
        for key in rec:
            if key not in seen_set:
                seen.append(key)
                seen_set.add(key)
    return seen


def apply_column_args(
    records: List[Dict[str, Any]],
    select: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    reorder: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Apply column transformations to a list of records."""
    result = []
    for rec in records:
        if select:
            rec = select_columns(rec, select)
        if exclude:
            rec = exclude_columns(rec, exclude)
        if reorder:
            rec = reorder_columns(rec, reorder)
        result.append(rec)
    return result
