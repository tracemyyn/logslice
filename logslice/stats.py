"""Basic numeric statistics over a field across log records."""
from __future__ import annotations

from typing import Iterable, Optional
import math


def _coerce(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def collect_values(records: Iterable[dict], field: str) -> list[float]:
    """Extract numeric values for *field* from *records*, skipping non-numeric."""
    out = []
    for rec in records:
        v = _coerce(rec.get(field))
        if v is not None:
            out.append(v)
    return out


def compute_stats(values: list[float]) -> dict:
    """Return a dict with count/min/max/mean/stddev/p50/p95/p99."""
    if not values:
        return {"count": 0}
    n = len(values)
    sorted_vals = sorted(values)
    mean = sum(sorted_vals) / n
    variance = sum((x - mean) ** 2 for x in sorted_vals) / n
    stddev = math.sqrt(variance)

    def percentile(p: float) -> float:
        idx = (p / 100) * (n - 1)
        lo, hi = int(idx), min(int(idx) + 1, n - 1)
        return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)

    return {
        "count": n,
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "mean": round(mean, 6),
        "stddev": round(stddev, 6),
        "p50": round(percentile(50), 6),
        "p95": round(percentile(95), 6),
        "p99": round(percentile(99), 6),
    }


def field_stats(records: Iterable[dict], field: str) -> dict:
    """Convenience wrapper: collect values then compute stats."""
    return compute_stats(collect_values(records, field))
