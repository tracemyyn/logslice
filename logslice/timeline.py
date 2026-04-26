"""timeline.py – bucket records into time-based bins and emit a text sparkline."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterable, Dict, List, Optional, Tuple

from logslice.time_filter import extract_timestamp

_SPARKS = " ▁▂▃▄▅▆▇█"


def _floor_to_bucket(ts: datetime, interval: int) -> datetime:
    """Truncate *ts* to the nearest *interval*-second boundary."""
    epoch = int(ts.replace(tzinfo=timezone.utc).timestamp())
    floored = (epoch // interval) * interval
    return datetime.utcfromtimestamp(floored).replace(tzinfo=timezone.utc)


def build_timeline(
    records: Iterable[dict],
    interval: int = 60,
    ts_field: str = "ts",
) -> Dict[datetime, int]:
    """Count records per time bucket.  Returns an ordered dict keyed by bucket."""
    buckets: Dict[datetime, int] = defaultdict(int)
    for rec in records:
        ts = extract_timestamp(rec, ts_field)
        if ts is None:
            continue
        bucket = _floor_to_bucket(ts, interval)
        buckets[bucket] += 1
    return dict(sorted(buckets.items()))


def fill_gaps(
    timeline: Dict[datetime, int], interval: int = 60
) -> Dict[datetime, int]:
    """Insert zero-count buckets for any missing intervals."""
    if not timeline:
        return {}
    keys = sorted(timeline)
    start, end = keys[0], keys[-1]
    filled: Dict[datetime, int] = {}
    cur = start
    while cur <= end:
        filled[cur] = timeline.get(cur, 0)
        from datetime import timedelta
        cur = cur + timedelta(seconds=interval)
    return filled


def sparkline(timeline: Dict[datetime, int]) -> str:
    """Return a single-line unicode sparkline for *timeline* counts."""
    if not timeline:
        return ""
    counts = list(timeline.values())
    max_count = max(counts) or 1
    chars = []
    for c in counts:
        idx = round(c / max_count * (len(_SPARKS) - 1))
        chars.append(_SPARKS[idx])
    return "".join(chars)


def render_timeline(
    timeline: Dict[datetime, int],
    interval: int = 60,
    label_fmt: str = "%H:%M:%S",
) -> List[str]:
    """Return a list of formatted lines: timestamp | bar | count."""
    if not timeline:
        return []
    max_count = max(timeline.values()) or 1
    bar_width = 30
    lines = []
    for bucket, count in sorted(timeline.items()):
        label = bucket.strftime(label_fmt)
        filled = round(count / max_count * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        lines.append(f"{label} |{bar}| {count}")
    return lines
