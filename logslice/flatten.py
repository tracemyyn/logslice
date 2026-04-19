"""Flatten nested dicts in log records into dot-notation keys."""
from typing import Any, Dict, Iterator, List, Optional


def _flatten(obj: Any, prefix: str, sep: str) -> Iterator[tuple]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}{sep}{k}" if prefix else k
            yield from _flatten(v, full_key, sep)
    else:
        yield prefix, obj


def flatten_record(
    record: Dict[str, Any],
    sep: str = ".",
    max_depth: Optional[int] = None,
) -> Dict[str, Any]:
    """Return a new record with nested dicts flattened to dot-notation keys."""
    if max_depth == 0:
        return dict(record)

    result: Dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, dict) and (max_depth is None or max_depth > 0):
            sub = flatten_record(value, sep=sep, max_depth=None if max_depth is None else max_depth - 1)
            for sub_key, sub_val in sub.items():
                result[f"{key}{sep}{sub_key}"] = sub_val
        else:
            result[key] = value
    return result


def unflatten_record(record: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Reconstruct nested dicts from dot-notation keys."""
    result: Dict[str, Any] = {}
    for key, value in record.items():
        parts = key.split(sep)
        target = result
        for part in parts[:-1]:
            if part not in target or not isinstance(target[part], dict):
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
    return result


def apply_flatten(
    records: List[Dict[str, Any]],
    sep: str = ".",
    max_depth: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Apply flatten_record to a list of records."""
    return [flatten_record(r, sep=sep, max_depth=max_depth) for r in records]
