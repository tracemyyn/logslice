"""coalesce.py – return the first non-null/non-empty value across a list of fields."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def coalesce_value(record: Dict[str, Any], fields: List[str], default: Any = None) -> Any:
    """Return the value of the first field in *fields* that is present and non-None.

    An empty string is treated as absent so that logfmt records with empty
    values are skipped in favour of the next candidate.
    """
    for field in fields:
        value = record.get(field)
        if value is not None and value != "":
            return value
    return default


def coalesce_field(
    record: Dict[str, Any],
    fields: List[str],
    target: str,
    default: Any = None,
    drop_sources: bool = False,
) -> Dict[str, Any]:
    """Write the coalesced value to *target* and optionally remove source fields."""
    result = dict(record)
    result[target] = coalesce_value(record, fields, default=default)
    if drop_sources:
        for field in fields:
            if field != target:
                result.pop(field, None)
    return result


def apply_coalesce(
    records: Iterable[Dict[str, Any]],
    fields: List[str],
    target: str,
    default: Any = None,
    drop_sources: bool = False,
) -> Iterable[Dict[str, Any]]:
    """Apply :func:`coalesce_field` to every record in *records*."""
    for record in records:
        yield coalesce_field(
            record,
            fields,
            target,
            default=default,
            drop_sources=drop_sources,
        )


def parse_coalesce_arg(arg: str) -> tuple[List[str], str]:
    """Parse a coalesce argument of the form ``field1,field2,...->target``.

    Returns a tuple of (source_fields, target_field).

    Raises ``ValueError`` if the format is invalid.
    """
    if "->" not in arg:
        raise ValueError(
            f"Invalid coalesce argument {arg!r}: expected 'src1,src2->target' format."
        )
    sources_part, _, target = arg.partition("->")
    target = target.strip()
    sources = [s.strip() for s in sources_part.split(",") if s.strip()]
    if not sources:
        raise ValueError(f"No source fields specified in coalesce argument {arg!r}.")
    if not target:
        raise ValueError(f"No target field specified in coalesce argument {arg!r}.")
    return sources, target
