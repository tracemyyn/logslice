"""annotate.py — attach computed annotations to log records.

Annotations are derived fields added under a configurable key (default
``_annotations``) without modifying the original fields.  Each rule is a
``field:pattern`` pair; when the pattern matches the field value the rule
name is appended to the annotation list.

Example
-------
>>> rec = {"level": "error", "msg": "disk full"}
>>> rules = parse_annotation_args(["severity:level:error", "storage:msg:disk"])
>>> annotate_record(rec, rules)
{'level': 'error', 'msg': 'disk full', '_annotations': ['severity', 'storage']}
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# (annotation_name, field_name, compiled_pattern)
AnnotationRule = Tuple[str, str, re.Pattern]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_annotation_arg(arg: str) -> AnnotationRule:
    """Parse a single annotation rule string ``name:field:pattern``.

    The *pattern* portion may itself contain colons, so we only split on the
    first two colons.

    Raises ``ValueError`` if the argument does not contain at least two colons.
    """
    parts = arg.split(":", 2)
    if len(parts) < 3:
        raise ValueError(
            f"Invalid annotation rule {arg!r}: expected 'name:field:pattern'"
        )
    name, field, pattern = parts
    if not name or not field or not pattern:
        raise ValueError(
            f"Invalid annotation rule {arg!r}: name, field and pattern must be non-empty"
        )
    return name, field, re.compile(pattern)


def parse_annotation_args(args: List[str]) -> List[AnnotationRule]:
    """Parse a list of annotation rule strings into compiled rules."""
    return [parse_annotation_arg(a) for a in args]


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def annotate_record(
    record: Dict,
    rules: List[AnnotationRule],
    key: str = "_annotations",
) -> Dict:
    """Return a new record with matched rule names appended to *key*.

    Existing values at *key* are preserved so that multiple passes accumulate
    annotations rather than overwriting them.
    """
    matched: List[str] = []
    for name, field, pattern in rules:
        value = record.get(field)
        if value is not None and pattern.search(str(value)):
            matched.append(name)

    if not matched:
        return record

    result = dict(record)
    existing = result.get(key)
    if isinstance(existing, list):
        result[key] = existing + matched
    else:
        result[key] = matched
    return result


def annotate_records(
    records: Iterable[Dict],
    rules: List[AnnotationRule],
    key: str = "_annotations",
) -> Iterable[Dict]:
    """Yield annotated copies of every record in *records*."""
    for record in records:
        yield annotate_record(record, rules, key=key)


def filter_annotated(
    records: Iterable[Dict],
    annotation: str,
    key: str = "_annotations",
) -> Iterable[Dict]:
    """Yield only records whose annotation list contains *annotation*."""
    for record in records:
        tags = record.get(key)
        if isinstance(tags, list) and annotation in tags:
            yield record
