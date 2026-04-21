"""Tests for logslice.cli_rollup."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

import pytest

from logslice.cli_rollup import add_rollup_args, apply_rollup_args


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "rollup": None,
        "rollup_interval": 60,
        "rollup_op": "sum",
        "rollup_ts": "ts",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _ts(offset: int) -> str:
    return datetime.fromtimestamp(offset, tz=timezone.utc).isoformat()


def _rec(offset: int, value: float) -> dict:
    return {"ts": _ts(offset), "latency": value}


def test_add_rollup_args_registers_rollup():
    p = argparse.ArgumentParser()
    add_rollup_args(p)
    args = p.parse_args(["--rollup", "latency"])
    assert args.rollup == "latency"


def test_add_rollup_args_registers_interval():
    p = argparse.ArgumentParser()
    add_rollup_args(p)
    args = p.parse_args(["--rollup", "x", "--rollup-interval", "300"])
    assert args.rollup_interval == 300


def test_add_rollup_args_registers_op():
    p = argparse.ArgumentParser()
    add_rollup_args(p)
    args = p.parse_args(["--rollup", "x", "--rollup-op", "avg"])
    assert args.rollup_op == "avg"


def test_add_rollup_args_registers_ts_field():
    p = argparse.ArgumentParser()
    add_rollup_args(p)
    args = p.parse_args(["--rollup", "x", "--rollup-ts", "timestamp"])
    assert args.rollup_ts == "timestamp"


def test_apply_rollup_no_flag_passthrough():
    args = _make_args(rollup=None)
    recs = [_rec(5, 1.0), _rec(10, 2.0)]
    result = list(apply_rollup_args(args, recs))
    assert result == recs


def test_apply_rollup_produces_summary_rows():
    args = _make_args(rollup="latency")
    recs = [_rec(5, 3.0), _rec(10, 7.0)]
    result = list(apply_rollup_args(args, recs))
    assert len(result) == 1
    assert result[0]["value"] == pytest.approx(10.0)
    assert result[0]["operation"] == "sum"


def test_apply_rollup_respects_op():
    args = _make_args(rollup="latency", rollup_op="max")
    recs = [_rec(5, 3.0), _rec(10, 9.0)]
    result = list(apply_rollup_args(args, recs))
    assert result[0]["value"] == pytest.approx(9.0)
