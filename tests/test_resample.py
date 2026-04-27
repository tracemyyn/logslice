"""Tests for logslice.resample and logslice.cli_resample."""

from __future__ import annotations

import argparse
import pytest

from logslice.resample import _floor_to_bucket, resample_records
from logslice.cli_resample import add_resample_args, apply_resample_args


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rec(ts: float, **kwargs) -> dict:
    return {"ts": str(ts), **{k: v for k, v in kwargs.items()}}


# ---------------------------------------------------------------------------
# _floor_to_bucket
# ---------------------------------------------------------------------------

def test_floor_ts_aligns_to_60s():
    assert _floor_to_bucket(90.0, 60) == 60.0


def test_floor_ts_already_on_boundary():
    assert _floor_to_bucket(120.0, 60) == 120.0


def test_floor_ts_small_interval():
    assert _floor_to_bucket(13.9, 5) == 10.0


# ---------------------------------------------------------------------------
# resample_records
# ---------------------------------------------------------------------------

def test_resample_empty_returns_empty():
    result = list(resample_records([], interval=60))
    assert result == []


def test_resample_invalid_interval_raises():
    with pytest.raises(ValueError, match="interval must be"):
        list(resample_records([], interval=0))


def test_resample_single_bucket_count():
    recs = [_rec(10.0, latency=5), _rec(20.0, latency=15)]
    result = list(resample_records(recs, interval=60, fields=["latency"]))
    assert len(result) == 1
    assert result[0]["count"] == 2


def test_resample_single_bucket_aggregates():
    recs = [_rec(10.0, latency=5.0), _rec(20.0, latency=15.0)]
    result = list(resample_records(recs, interval=60, fields=["latency"]))
    row = result[0]
    assert row["sum_latency"] == 20.0
    assert row["mean_latency"] == 10.0
    assert row["min_latency"] == 5.0
    assert row["max_latency"] == 15.0


def test_resample_two_buckets():
    recs = [_rec(10.0, v=1), _rec(70.0, v=3)]
    result = list(resample_records(recs, interval=60, fields=["v"]))
    assert len(result) == 2
    assert result[0]["bucket"] == 0.0
    assert result[1]["bucket"] == 60.0


def test_resample_missing_ts_skipped():
    recs = [{"msg": "no timestamp", "v": 1}, _rec(5.0, v=2)]
    result = list(resample_records(recs, interval=60, fields=["v"]))
    assert result[0]["count"] == 1


def test_resample_non_numeric_field_skipped():
    recs = [_rec(5.0, level="error")]
    result = list(resample_records(recs, interval=60, fields=["level"]))
    assert "sum_level" not in result[0]


def test_resample_buckets_sorted():
    recs = [_rec(130.0, v=1), _rec(10.0, v=2), _rec(70.0, v=3)]
    result = list(resample_records(recs, interval=60, fields=["v"]))
    buckets = [r["bucket"] for r in result]
    assert buckets == sorted(buckets)


# ---------------------------------------------------------------------------
# cli_resample
# ---------------------------------------------------------------------------

def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"resample": None, "resample_fields": None, "resample_ts": "ts"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_resample_args_registers_resample():
    parser = argparse.ArgumentParser()
    add_resample_args(parser)
    args = parser.parse_args(["--resample", "60"])
    assert args.resample == 60


def test_add_resample_args_registers_fields():
    parser = argparse.ArgumentParser()
    add_resample_args(parser)
    args = parser.parse_args(["--resample", "60", "--resample-fields", "latency", "size"])
    assert args.resample_fields == ["latency", "size"]


def test_apply_resample_no_flag_passthrough():
    recs = [{"msg": "hello"}, {"msg": "world"}]
    args = _make_args(resample=None)
    result = list(apply_resample_args(args, iter(recs)))
    assert result == recs


def test_apply_resample_flag_produces_buckets():
    recs = [_rec(5.0, v=1), _rec(10.0, v=3)]
    args = _make_args(resample=60, resample_fields=["v"], resample_ts="ts")
    result = list(apply_resample_args(args, iter(recs)))
    assert len(result) == 1
    assert result[0]["count"] == 2
