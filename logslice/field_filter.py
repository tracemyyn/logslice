"""Field pattern filtering for parsed log entries."""

import re
from typing import Optional


def matches_pattern(entry: dict, field: str, pattern: str) -> bool:
    """Return True if entry[field] matches the given regex pattern.

    Matching is case-sensitive. Missing fields return False.
    """
    value = entry.get(field)
    if value is None:
        return False
    return bool(re.search(pattern, str(value)))


def apply_filters(entry: dict, filters: list[tuple[str, str]]) -> bool:
    """Apply multiple (field, pattern) filters to an entry.

    All filters must match (AND logic). An empty filter list matches everything.
    """
    return all(matches_pattern(entry, field, pattern) for field, pattern in filters)


def parse_filter_arg(arg: str) -> Optional[tuple[str, str]]:
    """Parse a CLI filter argument of the form 'field=pattern'.

    Returns (field, pattern) tuple or None if the argument is invalid.
    """
    if "=" not in arg:
        return None
    field, _, pattern = arg.partition("=")
    field = field.strip()
    pattern = pattern.strip()
    if not field or not pattern:
        return None
    return field, pattern
