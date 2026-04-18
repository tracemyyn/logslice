"""Time-based filtering for parsed log entries."""

from datetime import datetime, timezone
from typing import Optional

TIMESTAMP_FIELDS = ("time", "timestamp", "ts", "@timestamp", "datetime")
TIMESTAMP_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
)


def extract_timestamp(entry: dict) -> Optional[datetime]:
    """Extract a datetime from a parsed log entry by checking common fields."""
    for field in TIMESTAMP_FIELDS:
        raw = entry.get(field)
        if raw is None:
            continue
        dt = _parse_timestamp(str(raw))
        if dt is not None:
            return dt
    return None


def _parse_timestamp(value: str) -> Optional[datetime]:
    for fmt in TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def in_range(
    entry: dict,
    start: Optional[datetime],
    end: Optional[datetime],
) -> bool:
    """Return True if the entry's timestamp falls within [start, end].

    Entries without a parseable timestamp are excluded when a range is given.
    """
    if start is None and end is None:
        return True

    ts = extract_timestamp(entry)
    if ts is None:
        return False

    if start and ts < start:
        return False
    if end and ts > end:
        return False
    return True
