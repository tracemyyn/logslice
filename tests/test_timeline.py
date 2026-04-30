"""Tests for logslice.timeline."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.timeline import (
    _floor_to_bucket,
    build_timeline,
    fill_gaps,
    render_timeline,
    sparkline,
)


def _ts(iso: str) -> str:
    return iso


def _rec(iso: str) -> dict:
    return {"ts": iso, "msg": "hello"}


# ---------------------------------------------------------------------------
# _floor_to_bucket
# ---------------------------------------------------------------------------

def test_floor_ts_aligns_to_60s():
    ts = datetime(2024, 1, 1, 12, 1, 45, tzinfo=timezone.utc)
    result = _floor_to_bucket(ts, 60)
    assert result == datetime(2024, 1, 1, 12, 1, 0, tzinfo=timezone.utc)


def test_floor_ts_already_on_boundary():
    ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert _floor_to_bucket(ts, 60) == ts


# ---------------------------------------------------------------------------
# build_timeline
# ---------------------------------------------------------------------------

def test_build_timeline_empty_returns_empty():
    assert build_timeline([]) == {}


def test_build_timeline_missing_ts_skipped():
    records = [{"msg": "no timestamp"}]
    assert build_timeline(records) == {}


def test_build_timeline_groups_into_buckets():
    records = [
        _rec("2024-01-01T00:00:10Z"),
        _rec("2024-01-01T00:00:50Z"),
        _rec("2024-01-01T00:01:05Z"),
    ]
    tl = build_timeline(records, interval=60)
    assert len(tl) == 2
    counts = list(tl.values())
    assert counts[0] == 2
    assert counts[1] == 1


def test_build_timeline_single_record():
    tl = build_timeline([_rec("2024-06-15T08:30:00Z")], interval=300)
    assert sum(tl.values()) == 1


# ---------------------------------------------------------------------------
# fill_gaps
# ---------------------------------------------------------------------------

def test_fill_gaps_inserts_zeros():
    t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 1, 1, 0, 2, 0, tzinfo=timezone.utc)
    tl = {t0: 3, t2: 5}
    filled = fill_gaps(tl, interval=60)
    assert len(filled) == 3
    t1 = datetime(2024, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
    assert filled[t1] == 0


def test_fill_gaps_empty_returns_empty():
    assert fill_gaps({}) == {}


def test_fill_gaps_no_gaps_unchanged():
    """A timeline with no missing buckets should be returned as-is."""
    t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2024, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
    t2 = datetime(2024, 1, 1, 0, 2, 0, tzinfo=timezone.utc)
    tl = {t0: 1, t1: 2, t2: 3}
    filled = fill_gaps(tl, interval=60)
    assert filled == tl


def test_fill_gaps_preserves_original_counts():
    """Existing counts must not be altered when gaps are filled."""
    t0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t3 = datetime(2024, 1, 1, 0, 3, 0, tzinfo=timezone.utc)
    tl = {t0: 7, t3: 4}
    filled = fill_gaps(tl, interval=60)
    assert filled[t0] == 7
    assert filled[t3] == 4


# ---------------------------------------------------------------------------
# sparkline
# ---------------------------------------------------------------------------

def test_sparkline_empty_returns_empty_string():
    assert sparkline({}) == ""


def test_sparkline_length_matches_bucket_count():
    t0 = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2024, 1, 1, 0, 1, tzinfo=timezone.utc)
    t2 = datetime(2024, 1, 1, 0, 2, tzinfo=timezone.utc)
    tl = {t0: 1, t1: 5, t2: 3}
    assert len(sparkline(tl)) == 3


def test_sparkline_max_bucket_is_full_block():
    t0 = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
  