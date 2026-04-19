"""Field type casting for log records."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


_CASTERS = {
    "int": int,
    "float": float,
    "str": str,
    "bool": lambda v: v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes"),
}


def cast_field(record: Dict[str, Any], field: str, typename: str) -> Dict[str, Any]:
    """Return a copy of *record* with *field* cast to *typename*."""
    if field not in record:
        return dict(record)
    caster = _CASTERS.get(typename)
    if caster is None:
        raise ValueError(f"Unknown type '{typename}'. Choose from: {', '.join(_CASTERS)}")
    result = dict(record)
    try:
        result[field] = caster(record[field])
    except (ValueError, TypeError):
        pass  # leave original value on failure
    return result


def apply_casts(record: Dict[str, Any], specs: List[str]) -> Dict[str, Any]:
    """Apply a list of 'field:type' cast specs to *record*.

    Each entry in *specs* must be of the form ``field:typename``.
    Unknown fields are silently skipped; invalid values are left unchanged.
    """
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Cast spec must be 'field:type', got: {spec!r}")
        field, typename = spec.split(":", 1)
        record = cast_field(record, field.strip(), typename.strip())
    return record


def parse_cast_args(raw: Optional[List[str]]) -> List[str]:
    """Normalise cast args from the CLI (may be None)."""
    return list(raw) if raw else []
