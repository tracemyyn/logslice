"""Tests for logslice.rollup."""
from __future__ import annotations

import pytest

from logslice.rollup import _floor_to_bucket, rollup_records
from datetime import datetime, timezone


def _ts(offset: int) -> str:
    """ISO timestamp *offset* seconds after the Unix epoch."""
    return datetime.fromtimestamp(offset, tz=timezone.utc).isoformat()


def _rec(offset: int, value: float) -> dict:
    return {"ts": _ts(offset), "latency": value}


# ---------------------------------------------------------------------------
# _floor_to_bucket
# ---------------------------------------------------------------------------

def test_floor_ts_aligns_to_60s():
    ts = datetime.fromtimestamp(75, tz=timezone.utc)
    result = _floor_to_bucket(ts, 60)
    assert result == datetime.fromtimestamp(60, tz=timezone.utc)


def test_floor_ts_already_on_boundary():
    ts = datetime.fromtimestamp(120, tz=timezone.utc)
    result = _floor_to_bucket(ts, 60)
    assert result == ts


# ---------------------------------------------------------------------------
# rollup_records
# ---------------------------------------------------------------------------

def test_rollup_sum_single_bucket():
    recs = [_rec(10, 5.0), _rec(20, 3.0), _rec(50, 2.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency"))
    assert len(rows) == 1
    assert rows[0]["value"] == pytest.approx(10.0)
    assert rows[0]["count"] == 3
    assert rows[0]["operation"] == "sum"


def test_rollup_avg_two_buckets():
    recs = [_rec(10, 4.0), _rec(10, 8.0), _rec(70, 6.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency", operation="avg"))
    assert len(rows) == 2
    assert rows[0]["value"] == pytest.approx(6.0)
    assert rows[1]["value"] == pytest.approx(6.0)


def test_rollup_min_max():
    recs = [_rec(5, 1.0), _rec(10, 9.0), _rec(15, 4.0)]
    mins = list(rollup_records(recs, interval=60, agg_field="latency", operation="min"))
    maxs = list(rollup_records(recs, interval=60, agg_field="latency", operation="max"))
    assert mins[0]["value"] == pytest.approx(1.0)
    assert maxs[0]["value"] == pytest.approx(9.0)


def test_rollup_count():
    recs = [_rec(1, 1.0), _rec(2, 2.0), _rec(3, 3.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency", operation="count"))
    assert rows[0]["value"] == pytest.approx(3.0)


def test_rollup_missing_field_skipped():
    recs = [{"ts": _ts(5)}, _rec(10, 2.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency"))
    assert rows[0]["count"] == 1


def test_rollup_missing_ts_skipped():
    recs = [{"latency": 3.0}, _rec(5, 7.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency"))
    assert rows[0]["count"] == 1


def test_rollup_empty_input():
    rows = list(rollup_records([], interval=60, agg_field="latency"))
    assert rows == []


def test_rollup_unknown_operation_raises():
    with pytest.raises(ValueError, match="Unknown rollup operation"):
        list(rollup_records([], interval=60, agg_field="latency", operation="median"))


def test_rollup_buckets_sorted():
    recs = [_rec(70, 1.0), _rec(10, 2.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency"))
    assert rows[0]["bucket"] < rows[1]["bucket"]


def test_rollup_field_name_in_output():
    recs = [_rec(5, 1.0)]
    rows = list(rollup_records(recs, interval=60, agg_field="latency"))
    assert rows[0]["field"] == "latency"
