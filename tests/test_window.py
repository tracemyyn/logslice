"""Tests for logslice.window."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import pytest

from logslice.window import _floor_ts, tumbling_windows, sliding_windows, window_counts


def _ts(iso: str) -> str:
    return iso


def _rec(ts: str, level: str = "info") -> dict:
    return {"ts": ts, "level": level}


RECS = [
    _rec("2024-01-01T00:00:10Z", "info"),
    _rec("2024-01-01T00:00:50Z", "error"),
    _rec("2024-01-01T00:01:20Z", "info"),
    _rec("2024-01-01T00:01:55Z", "warn"),
    _rec("2024-01-01T00:02:05Z", "error"),
]


def test_floor_ts_aligns_to_boundary():
    ts = datetime(2024, 1, 1, 0, 1, 37, tzinfo=timezone.utc)
    floored = _floor_ts(ts, 60)
    assert floored == datetime(2024, 1, 1, 0, 1, 0, tzinfo=timezone.utc)


def test_floor_ts_already_on_boundary():
    ts = datetime(2024, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
    assert _floor_ts(ts, 60) == ts


def test_tumbling_windows_groups_correctly():
    windows = list(tumbling_windows(RECS, 60))
    assert len(windows) == 3
    _, w0 = windows[0]
    assert len(w0) == 2  # 00:00:10 and 00:00:50


def test_tumbling_windows_skips_no_ts():
    recs = RECS + [{"msg": "no timestamp"}]
    windows = list(tumbling_windows(recs, 60))
    total = sum(len(w) for _, w in windows)
    assert total == len(RECS)


def test_tumbling_windows_empty_input():
    assert list(tumbling_windows([], 60)) == []


def test_sliding_windows_overlap():
    windows = list(sliding_windows(RECS, width_seconds=90, step_seconds=60))
    # First window [00:00, 00:01:30) covers first 3 records
    _, w0 = windows[0]
    assert len(w0) == 3


def test_sliding_windows_empty_input():
    assert list(sliding_windows([], 60, 30)) == []


def test_window_counts_total():
    windows = list(tumbling_windows(RECS, 60))
    counts = list(window_counts(windows))
    assert all("count" in r for r in counts)
    assert sum(r["count"] for r in counts) == len(RECS)


def test_window_counts_by_field():
    windows = list(tumbling_windows(RECS, 60))
    counts = list(window_counts(windows, field="level"))
    assert all("value" in r for r in counts)
    error_rows = [r for r in counts if r["value"] == "error"]
    assert sum(r["count"] for r in error_rows) == 2


def test_window_counts_window_start_is_iso():
    windows = list(tumbling_windows(RECS, 60))
    counts = list(window_counts(windows))
    for r in counts:
        datetime.fromisoformat(r["window_start"])  # should not raise
