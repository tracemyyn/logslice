"""Rate calculation: compute per-time-bucket event rates from records."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from logslice.time_filter import extract_timestamp


def _floor_to_bucket(ts: float, interval: int) -> int:
    """Floor a unix timestamp to the nearest interval boundary."""
    return int(ts // interval) * interval


def compute_rate(
    records: Iterable[dict],
    interval: int = 60,
    ts_field: Optional[str] = None,
) -> List[Dict]:
    """Return one row per time bucket with an event count and rate (events/sec).

    Args:
        records:  Iterable of parsed log records.
        interval: Bucket width in seconds (default 60).
        ts_field: Override timestamp field name.

    Returns:
        List of dicts sorted by bucket with keys:
        ``bucket``, ``count``, ``rate``.
    """
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    buckets: Dict[int, int] = defaultdict(int)
    for rec in records:
        ts = extract_timestamp(rec, field=ts_field)
        if ts is None:
            continue
        key = _floor_to_bucket(ts, interval)
        buckets[key] += 1

    result = []
    for bucket, count in sorted(buckets.items()):
        result.append(
            {
                "bucket": bucket,
                "count": count,
                "rate": round(count / interval, 4),
            }
        )
    return result


def peak_bucket(rate_rows: List[Dict]) -> Optional[Dict]:
    """Return the bucket row with the highest count, or None if empty."""
    if not rate_rows:
        return None
    return max(rate_rows, key=lambda r: r["count"])
