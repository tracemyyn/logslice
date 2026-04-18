"""Field redaction utilities for logslice."""

import re
from typing import Any, Dict, Iterable, List, Optional

_MASK = "***"


def redact_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a copy of record with specified fields masked."""
    out = dict(record)
    for field in fields:
        if field in out:
            out[field] = _MASK
    return out


def redact_pattern(
    record: Dict[str, Any], pattern: str, replacement: str = _MASK
) -> Dict[str, Any]:
    """Return a copy of record with string values matching pattern replaced."""
    compiled = re.compile(pattern)
    out = {}
    for k, v in record.items():
        if isinstance(v, str) and compiled.search(v):
            out[k] = compiled.sub(replacement, v)
        else:
            out[k] = v
    return out


def apply_redactions(
    records: Iterable[Dict[str, Any]],
    fields: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    replacement: str = _MASK,
) -> Iterable[Dict[str, Any]]:
    """Apply field and/or pattern redactions to an iterable of records."""
    for record in records:
        if fields:
            record = redact_fields(record, fields)
        if pattern:
            record = redact_pattern(record, pattern, replacement)
        yield record
