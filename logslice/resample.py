"""Resample time-series log records into fixed-size time buckets.

Each output record contains the bucket timestamp and aggregated values
(count, sum, mean, min, max) for any numeric fields found in that bucket.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Iterator

from logslice.time_filter import extract_timestamp


def _floor_to_bucket(ts: float, interval: int) -> float:
    """Floor *ts* (epoch seconds) to the nearest *interval*-second boundary."""
    return float(int(ts) // interval * interval)


def resample_records(
    records: Iterable[dict],
    interval: int,
    fields: list[str] | None = None,
    ts_field: str = "ts",
) -> Iterator[dict]:
    """Resample *records* into *interval*-second buckets.

    Args:
        records:   Iterable of parsed log records.
        interval:  Bucket width in seconds (must be >= 1).
        fields:    Numeric fields to aggregate.  If *None*, all numeric
                   fields found in the first record are used.
        ts_field:  Name of the timestamp field (default ``"ts"``).

    Yields:
        One record per non-empty bucket with keys:
        ``bucket``, ``count``, and per-field ``sum``, ``mean``, ``min``,
        ``max`` suffixed with ``_{field}``.
    """
    if interval < 1:
        raise ValueError(f"interval must be >= 1, got {interval}")

    buckets: dict[float, dict] = defaultdict(lambda: {"count": 0, "_values": defaultdict(list)})

    for rec in records:
        ts = extract_timestamp(rec, ts_field)
        if ts is None:
            continue
        bucket_key = _floor_to_bucket(ts, interval)
        slot = buckets[bucket_key]
        slot["count"] += 1
        target_fields = fields or [k for k, v in rec.items() if isinstance(v, (int, float))]
        for f in target_fields:
            val = rec.get(f)
            if isinstance(val, (int, float)):
                slot["_values"][f].append(float(val))

    for bucket_key in sorted(buckets):
        slot = buckets[bucket_key]
        out: dict = {"bucket": bucket_key, "count": slot["count"]}
        for f, vals in slot["_values"].items():
            if vals:
                out[f"sum_{f}"] = sum(vals)
                out[f"mean_{f}"] = sum(vals) / len(vals)
                out[f"min_{f}"] = min(vals)
                out[f"max_{f}"] = max(vals)
        yield out
