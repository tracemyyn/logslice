"""rollup.py – aggregate records into time-bucketed rollup rows."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, Iterator, List, Optional

from logslice.time_filter import extract_timestamp


def _floor_to_bucket(ts: datetime, seconds: int) -> datetime:
    """Truncate *ts* down to the nearest *seconds*-wide boundary (UTC)."""
    epoch = int(ts.timestamp())
    floored = (epoch // seconds) * seconds
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def rollup_records(
    records: Iterable[dict],
    interval: int,
    agg_field: str,
    *,
    ts_field: str = "ts",
    operation: str = "sum",
) -> Iterator[dict]:
    """Yield one summary record per time bucket.

    Args:
        records:   input log records.
        interval:  bucket width in seconds.
        agg_field: numeric field to aggregate.
        ts_field:  field used to extract the timestamp.
        operation: one of ``sum``, ``avg``, ``min``, ``max``, ``count``.
    """
    if operation not in {"sum", "avg", "min", "max", "count"}:
        raise ValueError(f"Unknown rollup operation: {operation!r}")

    buckets: Dict[datetime, List[float]] = defaultdict(list)

    for rec in records:
        ts = extract_timestamp(rec, field=ts_field)
        if ts is None:
            continue
        try:
            value = float(rec[agg_field])
        except (KeyError, TypeError, ValueError):
            continue
        bucket = _floor_to_bucket(ts, interval)
        buckets[bucket].append(value)

    for bucket in sorted(buckets):
        values = buckets[bucket]
        if operation == "sum":
            result = sum(values)
        elif operation == "avg":
            result = sum(values) / len(values)
        elif operation == "min":
            result = min(values)
        elif operation == "max":
            result = max(values)
        else:  # count
            result = float(len(values))
        yield {
            "bucket": bucket.isoformat(),
            "count": len(values),
            "field": agg_field,
            "operation": operation,
            "value": result,
        }
