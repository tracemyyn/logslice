"""Field enrichment: derive new fields from existing record values."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

Record = Dict[str, Any]


def enrich_static(record: Record, field: str, value: str) -> Record:
    """Add a static constant value as *field* (does not overwrite existing)."""
    if field in record:
        return record
    out = dict(record)
    out[field] = value
    return out


def enrich_copy(record: Record, src: str, dst: str) -> Record:
    """Copy the value of *src* into *dst* (does not overwrite existing *dst*)."""
    if dst in record or src not in record:
        return record
    out = dict(record)
    out[dst] = record[src]
    return out


def enrich_extract(record: Record, src: str, dst: str, pattern: str) -> Record:
    """Extract the first capturing group of *pattern* from *src* into *dst*."""
    value = record.get(src)
    if value is None:
        return record
    m = re.search(pattern, str(value))
    if m is None:
        return record
    out = dict(record)
    out[dst] = m.group(1) if m.lastindex else m.group(0)
    return out


def enrich_concat(record: Record, dst: str, fields: List[str], sep: str = " ") -> Record:
    """Concatenate *fields* with *sep* and store in *dst*."""
    parts = [str(record[f]) for f in fields if f in record]
    if not parts:
        return record
    out = dict(record)
    out[dst] = sep.join(parts)
    return out


EnrichRule = Tuple[str, ...]  # (kind, *args)


def apply_enrichments(records: Iterable[Record], rules: List[EnrichRule]) -> Iterable[Record]:
    """Apply a list of enrichment rules to every record."""
    for record in records:
        for rule in rules:
            kind = rule[0]
            if kind == "static":
                record = enrich_static(record, rule[1], rule[2])
            elif kind == "copy":
                record = enrich_copy(record, rule[1], rule[2])
            elif kind == "extract":
                record = enrich_extract(record, rule[1], rule[2], rule[3])
            elif kind == "concat":
                fields = list(rule[2:])
                record = enrich_concat(record, rule[1], fields)
        yield record


def parse_enrich_arg(arg: str) -> EnrichRule:
    """Parse a CLI enrichment argument of the form 'kind:dst:src_or_value[:extra]'."""
    parts = arg.split(":", 3)
    if len(parts) < 3:
        raise ValueError(f"Invalid enrich argument: {arg!r}")
    return tuple(parts)  # type: ignore[return-value]
