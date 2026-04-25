"""Tests for logslice.split and logslice.cli_split."""
from __future__ import annotations

import argparse
import pytest

from logslice.split import (
    apply_split,
    bucket_sizes,
    split_by_field,
    split_by_pattern,
)
from logslice.cli_split import add_split_args, apply_split_args


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _recs():
    return [
        {"level": "info", "msg": "started"},
        {"level": "error", "msg": "boom"},
        {"level": "info", "msg": "done"},
        {"level": "warn", "msg": "slow"},
        {"msg": "no level"},
    ]


# ---------------------------------------------------------------------------
# split_by_field
# ---------------------------------------------------------------------------

def test_split_by_field_basic():
    buckets = split_by_field(_recs(), "level")
    assert set(buckets.keys()) == {"info", "error", "warn", "__missing__"}
    assert len(buckets["info"]) == 2
    assert len(buckets["error"]) == 1


def test_split_by_field_missing_key_custom():
    buckets = split_by_field(_recs(), "level", missing_key="unknown")
    assert "unknown" in buckets
    assert len(buckets["unknown"]) == 1


def test_split_by_field_all_present():
    records = [{"k": "a"}, {"k": "b"}, {"k": "a"}]
    buckets = split_by_field(records, "k")
    assert "__missing__" not in buckets
    assert len(buckets["a"]) == 2


def test_split_by_field_empty_input():
    assert split_by_field([], "level") == {}


# ---------------------------------------------------------------------------
# split_by_pattern
# ---------------------------------------------------------------------------

def test_split_by_pattern_basic():
    records = [
        {"msg": "connection refused"},
        {"msg": "timeout waiting"},
        {"msg": "all good"},
    ]
    buckets = split_by_pattern(records, "msg", ["conn:refused", "time:timeout"])
    assert "conn" in buckets
    assert "time" in buckets
    assert buckets["other"][0]["msg"] == "all good"


def test_split_by_pattern_first_match_wins():
    records = [{"msg": "error timeout"}]
    buckets = split_by_pattern(
        records, "msg", ["errors:error", "timeouts:timeout"]
    )
    assert "errors" in buckets
    assert "timeouts" not in buckets


def test_split_by_pattern_invalid_spec_raises():
    with pytest.raises(ValueError, match="Invalid split pattern spec"):
        split_by_pattern([], "msg", ["nocolon"])


# ---------------------------------------------------------------------------
# bucket_sizes
# ---------------------------------------------------------------------------

def test_bucket_sizes_counts_correctly():
    buckets = {"a": [{}, {}], "b": [{}]}
    assert bucket_sizes(buckets) == {"a": 2, "b": 1}


# ---------------------------------------------------------------------------
# apply_split
# ---------------------------------------------------------------------------

def test_apply_split_no_field_returns_all():
    recs = [{"x": 1}, {"x": 2}]
    result = apply_split(recs, field=None)
    assert list(result.keys()) == ["all"]
    assert len(result["all"]) == 2


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    ns = argparse.Namespace(
        split_by=None,
        split_patterns=None,
        split_missing="__missing__",
    )
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_split_args_registers_split_by():
    p = argparse.ArgumentParser()
    add_split_args(p)
    args = p.parse_args(["--split-by", "level"])
    assert args.split_by == "level"


def test_add_split_args_registers_pattern():
    p = argparse.ArgumentParser()
    add_split_args(p)
    args = p.parse_args(["--split-by", "msg", "--split-pattern", "errs:error"])
    assert args.split_patterns == ["errs:error"]


def test_apply_split_args_no_flags_returns_all():
    recs = [{"a": 1}, {"a": 2}]
    result = apply_split_args(_make_args(), recs)
    assert "all" in result
    assert len(result["all"]) == 2


def test_apply_split_args_by_field():
    recs = [{"env": "prod"}, {"env": "dev"}, {"env": "prod"}]
    args = _make_args(split_by="env")
    result = apply_split_args(args, recs)
    assert len(result["prod"]) == 2
    assert len(result["dev"]) == 1
