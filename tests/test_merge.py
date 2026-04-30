"""Tests for logslice.merge and logslice.cli_merge."""

from __future__ import annotations

import argparse
import json
from typing import List

import pytest

from logslice.merge import apply_merge, merge_sorted, merge_unsorted
from logslice.cli_merge import add_merge_args, apply_merge_args


def _rec(ts: str, msg: str) -> dict:
    return {"ts": ts, "msg": msg}


# ---------------------------------------------------------------------------
# merge_sorted
# ---------------------------------------------------------------------------

def test_merge_sorted_single_stream():
    recs = [_rec("2024-01-01T00:00:01Z", "a"), _rec("2024-01-01T00:00:03Z", "b")]
    result = list(apply_merge([recs], sort=True))
    assert result == recs


def test_merge_sorted_two_streams_interleaved():
    a = [_rec("2024-01-01T00:00:01Z", "a1"), _rec("2024-01-01T00:00:04Z", "a2")]
    b = [_rec("2024-01-01T00:00:02Z", "b1"), _rec("2024-01-01T00:00:03Z", "b2")]
    result = list(merge_sorted(a, b))
    msgs = [r["msg"] for r in result]
    assert msgs == ["a1", "b1", "b2", "a2"]


def test_merge_sorted_empty_stream_ignored():
    a = [_rec("2024-01-01T00:00:01Z", "only")]
    result = list(merge_sorted(a, []))
    assert len(result) == 1
    assert result[0]["msg"] == "only"


def test_merge_sorted_all_empty_returns_empty():
    result = list(merge_sorted([], []))
    assert result == []


def test_merge_sorted_missing_ts_appended():
    a = [_rec("2024-01-01T00:00:01Z", "ts")]
    b = [{"msg": "no-ts"}]
    result = list(merge_sorted(a, b))
    # both records must appear
    assert len(result) == 2


# ---------------------------------------------------------------------------
# merge_unsorted
# ---------------------------------------------------------------------------

def test_merge_unsorted_round_robins():
    a = [{"n": 1}, {"n": 3}]
    b = [{"n": 2}, {"n": 4}]
    result = list(merge_unsorted(a, b))
    assert [r["n"] for r in result] == [1, 2, 3, 4]


def test_merge_unsorted_unequal_lengths():
    a = [{"n": 1}, {"n": 2}, {"n": 3}]
    b = [{"n": 10}]
    result = list(merge_unsorted(a, b))
    assert len(result) == 4


# ---------------------------------------------------------------------------
# apply_merge
# ---------------------------------------------------------------------------

def test_apply_merge_no_streams_returns_empty():
    result = list(apply_merge([]))
    assert result == []


def test_apply_merge_no_sort_flag():
    a = [{"n": 1}]
    b = [{"n": 2}]
    result = list(apply_merge([a, b], sort=False))
    assert len(result) == 2


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"merge": None, "merge_no_sort": False, "merge_ts_field": "ts"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_merge_args_registers_merge():
    p = argparse.ArgumentParser()
    add_merge_args(p)
    args = p.parse_args([])
    assert args.merge is None


def test_add_merge_args_registers_no_sort():
    p = argparse.ArgumentParser()
    add_merge_args(p)
    args = p.parse_args(["--merge-no-sort"])
    assert args.merge_no_sort is True


def test_apply_merge_args_no_flag_returns_primary():
    primary = [{"msg": "x"}]
    args = _make_args()
    result = list(apply_merge_args(args, primary))
    assert result == primary


def test_apply_merge_args_with_file(tmp_path):
    extra = tmp_path / "extra.log"
    extra.write_text(json.dumps({"ts": "2024-01-01T00:00:02Z", "msg": "extra"}) + "\n")
    primary = [{"ts": "2024-01-01T00:00:01Z", "msg": "primary"}]
    args = _make_args(merge=[str(extra)])
    result = list(apply_merge_args(args, primary))
    assert len(result) == 2
    assert result[0]["msg"] == "primary"
    assert result[1]["msg"] == "extra"
