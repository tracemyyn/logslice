"""Field transformation utilities for logslice records."""

from typing import Any, Callable, Dict, List, Optional


def rename_fields(record: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """Return a new record with fields renamed according to mapping."""
    result = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        result[new_key] = value
    return result


def drop_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record with specified fields removed."""
    return {k: v for k, v in record.items() if k not in fields}


def keep_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record containing only specified fields."""
    return {k: v for k, v in record.items() if k in fields}


def add_field(record: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """Return a new record with an additional field set."""
    result = dict(record)
    result[key] = value
    return result


def apply_transforms(
    record: Dict[str, Any],
    rename: Optional[Dict[str, str]] = None,
    drop: Optional[List[str]] = None,
    keep: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Apply a sequence of transformations to a record.

    Order: rename -> drop -> keep.
    """
    if rename:
        record = rename_fields(record, rename)
    if drop:
        record = drop_fields(record, drop)
    if keep:
        record = keep_fields(record, keep)
    return record


def parse_rename_arg(arg: str) -> Dict[str, str]:
    """Parse a comma-separated list of old=new rename pairs.

    Example: 'msg=message,ts=timestamp'
    """
    mapping: Dict[str, str] = {}
    for pair in arg.split(","):
        pair = pair.strip()
        if "=" not in pair:
            raise ValueError(f"Invalid rename pair (expected old=new): {pair!r}")
        old, new = pair.split("=", 1)
        mapping[old.strip()] = new.strip()
    return mapping
