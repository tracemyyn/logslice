"""Score records by how well they match a set of weighted field patterns."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Record = Dict[str, Any]


def _compile(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


def parse_score_arg(arg: str) -> Tuple[str, str, float]:
    """Parse 'field:pattern:weight' into (field, pattern, weight).

    Weight is optional and defaults to 1.0.
    """
    parts = arg.split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid score rule {arg!r}: expected 'field:pattern[:weight]'")
    field = parts[0]
    pattern = parts[1]
    weight = float(parts[2]) if len(parts) == 3 else 1.0
    if weight <= 0:
        raise ValueError(f"Weight must be positive, got {weight}")
    return field, pattern, weight


def score_record(
    record: Record,
    rules: List[Tuple[str, re.Pattern, float]],
) -> float:
    """Return the total score for *record* across all rules.

    Each rule contributes its weight when the compiled pattern matches the
    string representation of the field value.
    """
    total = 0.0
    for field, compiled, weight in rules:
        value = record.get(field)
        if value is None:
            continue
        if compiled.search(str(value)):
            total += weight
    return total


def score_records(
    records: Iterable[Record],
    rules: List[Tuple[str, re.Pattern, float]],
    threshold: float = 0.0,
    score_field: str = "_score",
) -> Iterator[Record]:
    """Yield records annotated with their score, filtered by *threshold*."""
    for record in records:
        s = score_record(record, rules)
        if s >= threshold:
            yield {**record, score_field: s}


def build_rules(
    args: List[str],
) -> List[Tuple[str, re.Pattern, float]]:
    """Parse a list of raw score-arg strings into compiled rule tuples."""
    rules: List[Tuple[str, re.Pattern, float]] = []
    for arg in args:
        field, pattern, weight = parse_score_arg(arg)
        rules.append((field, _compile(pattern), weight))
    return rules
