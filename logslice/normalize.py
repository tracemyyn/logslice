"""normalize.py — field value normalization for log records.

Provides functions to normalize field values: lowercasing strings,
stripping whitespace, coercing booleans, and applying per-field
normalization rules to a stream of records.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]

# ---------------------------------------------------------------------------
# Low-level normalizers
# ---------------------------------------------------------------------------

def normalize_whitespace(value: Any) -> Any:
    """Strip leading/trailing whitespace from string values."""
    if isinstance(value, str):
        return value.strip()
    return value


def normalize_lowercase(value: Any) -> Any:
    """Lowercase string values."""
    if isinstance(value, str):
        return value.lower()
    return value


def normalize_uppercase(value: Any) -> Any:
    """Uppercase string values."""
    if isinstance(value, str):
        return value.upper()
    return value


def normalize_bool(value: Any) -> Any:
    """Coerce common truthy/falsy string representations to Python bools.

    Recognises: 'true', '1', 'yes', 'on' -> True
                'false', '0', 'no', 'off' -> False
    Non-matching strings are returned unchanged.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in ("true", "1", "yes", "on"):
            return True
        if lower in ("false", "0", "no", "off"):
            return False
    return value


def normalize_numeric(value: Any) -> Any:
    """Coerce string values that look like numbers to int or float."""
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        try:
            int_val = int(stripped)
            return int_val
        except ValueError:
            pass
        try:
            return float(stripped)
        except ValueError:
            pass
    return value


# Map of normalizer name -> callable
_NORMALIZERS = {
    "whitespace": normalize_whitespace,
    "lowercase": normalize_lowercase,
    "uppercase": normalize_uppercase,
    "bool": normalize_bool,
    "numeric": normalize_numeric,
}


# ---------------------------------------------------------------------------
# Per-record normalization
# ---------------------------------------------------------------------------

def normalize_field(record: Record, field: str, normalizer: str) -> Record:
    """Return a new record with *field* normalized using *normalizer* name.

    Unknown normalizer names raise ``ValueError``.
    Missing fields are silently ignored.
    """
    fn = _NORMALIZERS.get(normalizer)
    if fn is None:
        raise ValueError(
            f"Unknown normalizer '{normalizer}'. "
            f"Valid options: {sorted(_NORMALIZERS)}"
        )
    if field not in record:
        return record
    result = dict(record)
    result[field] = fn(record[field])
    return result


def apply_normalizations(
    records: Iterable[Record],
    rules: List[tuple],  # list of (field, normalizer_name)
) -> Iterator[Record]:
    """Apply a sequence of (field, normalizer) rules to every record.

    Rules are applied in order; each rule receives the output of the
    previous one.  Records that do not contain the target field are
    passed through unchanged.
    """
    for record in records:
        for field, normalizer in rules:
            record = normalize_field(record, field, normalizer)
        yield record


# ---------------------------------------------------------------------------
# CLI argument helpers
# ---------------------------------------------------------------------------

def parse_normalize_arg(arg: str) -> tuple:
    """Parse a ``field:normalizer`` argument string.

    Returns ``(field, normalizer)`` tuple.
    Raises ``ValueError`` for malformed input.
    """
    parts = arg.split(":", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f"Invalid normalize argument '{arg}'. Expected 'field:normalizer'."
        )
    field, normalizer = parts[0].strip(), parts[1].strip()
    if normalizer not in _NORMALIZERS:
        raise ValueError(
            f"Unknown normalizer '{normalizer}'. "
            f"Valid options: {sorted(_NORMALIZERS)}"
        )
    return field, normalizer


def parse_normalize_args(args: List[str]) -> List[tuple]:
    """Parse a list of 'field:normalizer' strings into rule tuples."""
    return [parse_normalize_arg(a) for a in args]
