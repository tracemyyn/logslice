"""Tests for logslice.limit and logslice.cli_limit."""
import argparse
import pytest

from logslice.limit import skip_records, limit_records, apply_limit
from logslice.cli_limit import add_limit_args, apply_limit_args


def _recs(n: int = 5):
    return [{"i": i, "msg": f"line {i}"} for i in range(n)]


# --- skip_records ---

def test_skip_zero_returns_all():
    assert list(skip_records(_recs(3), 0)) == _recs(3)


def test_skip_removes_first_n():
    result = list(skip_records(_recs(5), 2))
    assert len(result) == 3
    assert result[0]["i"] == 2


def test_skip_more_than_available_returns_empty():
    assert list(skip_records(_recs(3), 10)) == []


# --- limit_records ---

def test_limit_zero_returns_empty():
    assert list(limit_records(_recs(5), 0)) == []


def test_limit_returns_at_most_n():
    result = list(limit_records(_recs(5), 3))
    assert len(result) == 3
    assert result[-1]["i"] == 2


def test_limit_larger_than_stream_returns_all():
    assert list(limit_records(_recs(3), 100)) == _recs(3)


# --- apply_limit ---

def test_apply_limit_no_args_returns_all():
    assert list(apply_limit(_recs(4))) == _recs(4)


def test_apply_limit_offset_and_limit():
    result = list(apply_limit(_recs(10), offset=3, limit=4))
    assert len(result) == 4
    assert result[0]["i"] == 3
    assert result[-1]["i"] == 6


# --- CLI helpers ---

def _make_args(**kwargs):
    ns = argparse.Namespace(limit=0, offset=0)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_limit_args_registers_limit():
    p = argparse.ArgumentParser()
    add_limit_args(p)
    args = p.parse_args(["--limit", "5"])
    assert args.limit == 5


def test_add_limit_args_registers_offset():
    p = argparse.ArgumentParser()
    add_limit_args(p)
    args = p.parse_args(["--offset", "2"])
    assert args.offset == 2


def test_apply_limit_args_no_flags_passthrough():
    recs = _recs(4)
    result = list(apply_limit_args(_make_args(), iter(recs)))
    assert result == recs


def test_apply_limit_args_applies_limit():
    result = list(apply_limit_args(_make_args(limit=2), iter(_recs(5))))
    assert len(result) == 2


def test_apply_limit_args_applies_offset():
    result = list(apply_limit_args(_make_args(offset=3), iter(_recs(5))))
    assert len(result) == 2
    assert result[0]["i"] == 3
