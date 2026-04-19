"""Tests for logslice.rate."""
import pytest

from logslice.rate import compute_rate, peak_bucket


def _rec(ts: str, **kwargs) -> dict:
    return {"ts": ts, **kwargs}


# ---- compute_rate -----------------------------------------------------------

def test_compute_rate_empty_returns_empty():
    assert compute_rate([]) == []


def test_compute_rate_missing_ts_skipped():
    records = [{"msg": "no timestamp"}]
    assert compute_rate(records) == []


def test_compute_rate_single_bucket():
    records = [
        _rec("2024-01-01T00:00:10Z"),
        _rec("2024-01-01T00:00:20Z"),
        _rec("2024-01-01T00:00:50Z"),
    ]
    rows = compute_rate(records, interval=60)
    assert len(rows) == 1
    assert rows[0]["count"] == 3
    assert rows[0]["rate"] == round(3 / 60, 4)


def test_compute_rate_two_buckets():
    records = [
        _rec("2024-01-01T00:00:05Z"),
        _rec("2024-01-01T00:01:05Z"),
    ]
    rows = compute_rate(records, interval=60)
    assert len(rows) == 2
    assert rows[0]["count"] == 1
    assert rows[1]["count"] == 1


def test_compute_rate_sorted_ascending():
    records = [
        _rec("2024-01-01T00:02:00Z"),
        _rec("2024-01-01T00:00:00Z"),
    ]
    rows = compute_rate(records, interval=60)
    assert rows[0]["bucket"] < rows[1]["bucket"]


def test_compute_rate_invalid_interval_raises():
    with pytest.raises(ValueError):
        compute_rate([], interval=0)


def test_compute_rate_custom_ts_field():
    records = [{"time": "2024-01-01T00:00:01Z"}, {"time": "2024-01-01T00:00:02Z"}]
    rows = compute_rate(records, interval=60, ts_field="time")
    assert len(rows) == 1
    assert rows[0]["count"] == 2


# ---- peak_bucket ------------------------------------------------------------

def test_peak_bucket_empty_returns_none():
    assert peak_bucket([]) is None


def test_peak_bucket_returns_highest_count():
    rows = [
        {"bucket": 0, "count": 5, "rate": 0.083},
        {"bucket": 60, "count": 12, "rate": 0.2},
        {"bucket": 120, "count": 3, "rate": 0.05},
    ]
    assert peak_bucket(rows)["count"] == 12


def test_peak_bucket_single_row():
    rows = [{"bucket": 0, "count": 7, "rate": 0.116}]
    assert peak_bucket(rows) == rows[0]
