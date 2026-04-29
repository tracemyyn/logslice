"""interpolate.py — fill gaps in numeric time-series records by interpolating missing values.

Supports linear interpolation between known data points for a specified
numeric field, keyed by timestamp.  Records without a parseable timestamp
or target field are passed through unchanged.
"""

from __future__ import annotations

from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.time_filter import extract_timestamp


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _numeric(value: object) -> Optional[float]:
    """Coerce *value* to float, returning None on failure."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _lerp(t0: float, v0: float, t1: float, v1: float, t: float) -> float:
    """Linear interpolation of *v* at time *t* between two known points."""
    if t1 == t0:
        return v0
    return v0 + (v1 - v0) * (t - t0) / (t1 - t0)


# ---------------------------------------------------------------------------
# Core interpolation logic
# ---------------------------------------------------------------------------

def interpolate_records(
    records: Iterable[dict],
    field: str,
    *,
    method: str = "linear",
    ts_field: str = "ts",
) -> Iterator[dict]:
    """Yield records with *field* interpolated where the value is absent.

    Records are buffered so that forward-looking interpolation can be
    performed.  Records that lack a parseable timestamp are emitted
    immediately without modification.

    Parameters
    ----------
    records:
        Input sequence of parsed log records.
    field:
        The numeric field to interpolate.
    method:
        Interpolation method.  Only ``"linear"`` is currently supported.
    ts_field:
        Override the timestamp field name (default ``"ts"``).
    """
    if method != "linear":
        raise ValueError(f"Unsupported interpolation method: {method!r}")

    # Collect all records into a list so we can look ahead.
    all_records: List[dict] = list(records)

    # Build an index of (position, timestamp, value) for records that have
    # both a valid timestamp and a valid field value.
    anchors: List[Tuple[int, float, float]] = []
    for idx, rec in enumerate(all_records):
        ts = extract_timestamp(rec, ts_field=ts_field)
        if ts is None:
            continue
        val = _numeric(rec.get(field))
        if val is not None:
            anchors.append((idx, ts.timestamp(), val))

    for idx, rec in enumerate(all_records):
        ts = extract_timestamp(rec, ts_field=ts_field)
        if ts is None or _numeric(rec.get(field)) is not None:
            # No interpolation needed — emit as-is.
            yield rec
            continue

        t = ts.timestamp()

        # Find the nearest anchor to the left and right.
        left: Optional[Tuple[int, float, float]] = None
        right: Optional[Tuple[int, float, float]] = None

        for anchor in anchors:
            a_idx, a_t, a_v = anchor
            if a_t <= t:
                if left is None or a_t > left[1]:
                    left = anchor
            else:
                if right is None or a_t < right[1]:
                    right = anchor

        if left is not None and right is not None:
            interpolated = _lerp(left[1], left[2], right[1], right[2], t)
            yield {**rec, field: interpolated}
        elif left is not None:
            # Extrapolate flat from last known value.
            yield {**rec, field: left[2]}
        elif right is not None:
            # Extrapolate flat from next known value.
            yield {**rec, field: right[2]}
        else:
            # No anchors at all — cannot interpolate.
            yield rec


def fill_constant(
    records: Iterable[dict],
    field: str,
    value: object,
) -> Iterator[dict]:
    """Replace absent or null *field* values with a constant *value*."""
    for rec in records:
        if rec.get(field) is None:
            yield {**rec, field: value}
        else:
            yield rec
