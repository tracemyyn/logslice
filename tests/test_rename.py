"""Tests for logslice.rename and logslice.cli_rename."""

from __future__ import annotations

import argparse
import pytest

from logslice.rename import (
    apply_rename,
    parse_rename_arg,
    parse_rename_args,
    rename_by_map,
    rename_by_prefix,
    rename_by_regex,
)
from logslice.cli_rename import add_rename_args, apply_rename_args


# ---------------------------------------------------------------------------
# rename_by_map
# ---------------------------------------------------------------------------

def test_rename_by_map_basic():
    rec = {"level": "info", "msg": "hello"}
    assert rename_by_map(rec, {"level": "severity"}) == {"severity": "info", "msg": "hello"}


def test_rename_by_map_unknown_key_unchanged():
    rec = {"a": 1}
    assert rename_by_map(rec, {"b": "c"}) == {"a": 1}


def test_rename_by_map_does_not_mutate():
    rec = {"x": 10}
    rename_by_map(rec, {"x": "y"})
    assert "x" in rec


# ---------------------------------------------------------------------------
# rename_by_prefix
# ---------------------------------------------------------------------------

def test_rename_by_prefix_replaces_matching():
    rec = {"log_level": "warn", "log_msg": "oops", "ts": "now"}
    result = rename_by_prefix(rec, "log_", "event_")
    assert "event_level" in result
    assert "event_msg" in result
    assert "ts" in result


def test_rename_by_prefix_no_match_unchanged():
    rec = {"a": 1}
    assert rename_by_prefix(rec, "x_", "y_") == {"a": 1}


# ---------------------------------------------------------------------------
# rename_by_regex
# ---------------------------------------------------------------------------

def test_rename_by_regex_substitutes():
    rec = {"req_id": 1, "req_ts": 2, "level": "info"}
    result = rename_by_regex(rec, r"^req_", "request_")
    assert "request_id" in result
    assert "request_ts" in result
    assert "level" in result


def test_rename_by_regex_no_match_unchanged():
    rec = {"a": 1}
    assert rename_by_regex(rec, r"^z", "w") == {"a": 1}


# ---------------------------------------------------------------------------
# parse_rename_arg / parse_rename_args
# ---------------------------------------------------------------------------

def test_parse_rename_arg_valid():
    assert parse_rename_arg("old=new") == ("old", "new")


def test_parse_rename_arg_invalid_raises():
    with pytest.raises(ValueError):
        parse_rename_arg("nodivider")


def test_parse_rename_args_multiple():
    mapping = parse_rename_args(["a=b", "c=d"])
    assert mapping == {"a": "b", "c": "d"}


# ---------------------------------------------------------------------------
# apply_rename
# ---------------------------------------------------------------------------

def test_apply_rename_map_only():
    recs = [{"level": "info"}]
    result = list(apply_rename(recs, mapping={"level": "severity"}))
    assert result[0] == {"severity": "info"}


def test_apply_rename_combined():
    recs = [{"log_level": "debug", "ts": "t"}]
    result = list(apply_rename(recs, prefix_old="log_", prefix_new="ev_"))
    assert "ev_level" in result[0]
    assert "ts" in result[0]


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    defaults = {"rename": [], "rename_prefix": None, "rename_regex": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_rename_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_rename_args(parser)
    opts = parser.parse_args([])
    assert opts.rename == []
    assert opts.rename_prefix is None
    assert opts.rename_regex is None


def test_apply_rename_args_no_flags_passthrough():
    recs = [{"a": 1}]
    args = _make_args()
    result = list(apply_rename_args(args, iter(recs)))
    assert result == recs


def test_apply_rename_args_rename_flag():
    recs = [{"level": "info"}]
    args = _make_args(rename=["level=severity"])
    result = list(apply_rename_args(args, iter(recs)))
    assert result[0] == {"severity": "info"}


def test_apply_rename_args_prefix_flag():
    recs = [{"log_msg": "hi", "ts": "t"}]
    args = _make_args(rename_prefix="log_:ev_")
    result = list(apply_rename_args(args, iter(recs)))
    assert "ev_msg" in result[0]
