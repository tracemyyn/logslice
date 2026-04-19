"""Field validation for log records."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

Rule = Dict[str, Any]
Record = Dict[str, Any]


def _check_required(record: Record, fields: List[str]) -> List[str]:
    return [f"missing required field: {f}" for f in fields if f not in record]


def _check_type(record: Record, field: str, expected: str) -> Optional[str]:
    if field not in record:
        return None
    type_map = {"int": int, "float": (int, float), "str": str, "bool": bool}
    typ = type_map.get(expected)
    if typ is None:
        return f"unknown type '{expected}' for field '{field}'"
    if not isinstance(record[field], typ):
        return f"field '{field}' expected {expected}, got {type(record[field]).__name__}"
    return None


def _check_pattern(record: Record, field: str, pattern: str) -> Optional[str]:
    if field not in record:
        return None
    value = str(record[field])
    if not re.search(pattern, value):
        return f"field '{field}' value {value!r} does not match pattern {pattern!r}"
    return None


def validate_record(record: Record, rules: List[Rule]) -> List[str]:
    """Return list of validation error messages (empty means valid)."""
    errors: List[str] = []
    for rule in rules:
        if "required" in rule:
            errors.extend(_check_required(record, rule["required"]))
        if "type" in rule:
            err = _check_type(record, rule["field"], rule["type"])
            if err:
                errors.append(err)
        if "pattern" in rule:
            err = _check_pattern(record, rule["field"], rule["pattern"])
            if err:
                errors.append(err)
    return errors


def apply_validation(
    records: List[Record],
    rules: List[Rule],
    drop_invalid: bool = False,
    tag_field: Optional[str] = None,
) -> Tuple[List[Record], int]:
    """Filter/tag records by validation rules. Returns (records, invalid_count)."""
    out: List[Record] = []
    invalid = 0
    for rec in records:
        errors = validate_record(rec, rules)
        if errors:
            invalid += 1
            if drop_invalid:
                continue
            if tag_field:
                rec = {**rec, tag_field: errors}
        elif tag_field:
            rec = {**rec, tag_field: []}
        out.append(rec)
    return out, invalid


def parse_rule_arg(arg: str) -> Rule:
    """Parse 'field:type' or 'field~pattern' into a rule dict."""
    if ":" in arg:
        field, typ = arg.split(":", 1)
        return {"field": field.strip(), "type": typ.strip()}
    if "~" in arg:
        field, pattern = arg.split("~", 1)
        return {"field": field.strip(), "pattern": pattern.strip()}
    return {"required": [arg.strip()]}
