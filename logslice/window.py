"""Tumbling and sliding window aggregation over log records."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Iterable, Iterator, List, Optional

from logslice.time_filter import extract_timestamp


def _floor_ts(ts: datetime, seconds: int) -> datetime:
    """Floor a datetime to the nearest window boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=ts.tzinfo)
    total = int((ts - epoch).total_seconds())
    floored = total - (total % seconds)
    return epoch + timedelta(seconds=floored)


def tumbling_windows(
    records: Iterable[dict],
    width_seconds: int,
) -> Iterator[tuple[datetime, List[dict]]]:
    """Group records into non-overlapping tumbling windows.

    Yields (window_start, [records]) tuples in chronological order.
    Records without a parseable timestamp are skipped.
    """
    buckets: Dict[datetime, List[dict]] = defaultdict(list)
    for record in records:
        ts = extract_timestamp(record)
        if ts is None:
            continue
        key = _floor_ts(ts, width_seconds)
        buckets[key].append(record)
    for key in sorted(buckets):
        yield key, buckets[key]


def sliding_windows(
    records: Iterable[dict],
    width_seconds: int,
    step_seconds: int,
) -> Iterator[tuple[datetime, List[dict]]]:
    """Yield overlapping sliding windows over records.

    Each window covers [start, start + width). Windows advance by step_seconds.
    Records without a timestamp are skipped.
    """
    timed: List[tuple[datetime, dict]] = []
    for record in records:
        ts = extract_timestamp(record)
        if ts is not None:
            timed.append((ts, record))
    if not timed:
        return
    timed.sort(key=lambda x: x[0])
    start = _floor_ts(timed[0][0], step_seconds)
    end_ts = timed[-1][0]
    width = timedelta(seconds=width_seconds)
    step = timedelta(seconds=step_seconds)
    current = start
    while current <= end_ts:
        window_end = current + width
        bucket = [r for ts, r in timed if current <= ts < window_end]
        if bucket:
            yield current, bucket
        current += step


def window_counts(
    windows: Iterable[tuple[datetime, List[dict]]],
    field: Optional[str] = None,
) -> Iterator[dict]:
    """Convert windows to count summary records.

    If *field* is given, count distinct values; otherwise count total records.
    """
    for start, records in windows:
        if field:
            counts: Dict[str, int] = defaultdict(int)
            for r in records:
                val = str(r.get(field, ""))
                counts[val] += 1
            for val, cnt in sorted(counts.items()):
                yield {"window_start": start.isoformat(), "value": val, "count": cnt}
        else:
            yield {"window_start": start.isoformat(), "count": len(records)}
