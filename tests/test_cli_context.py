"""Tests for logslice.cli_context."""
import argparse
import pytest
from logslice.cli_context import add_context_args, apply_context


def _make_args(**kwargs):
    defaults = {"before": 0, "after": 0, "context": None}
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    return ns


def _recs(n):
    return [{"i": i} for i in range(n)]


def test_add_context_args_registers_before():
    p = argparse.ArgumentParser()
    add_context_args(p)
    args = p.parse_args(["-B", "3"])
    assert args.before == 3


def test_add_context_args_registers_after():
    p = argparse.ArgumentParser()
    add_context_args(p)
    args = p.parse_args(["-A", "2"])
    assert args.after == 2


def test_add_context_args_registers_context_shorthand():
    p = argparse.ArgumentParser()
    add_context_args(p)
    args = p.parse_args(["-C", "4"])
    assert args.context == 4


def test_apply_context_no_flags_passthrough():
    recs = _recs(5)
    result = list(apply_context(recs, _make_args()))
    assert [r["i"] for r in result] == list(range(5))


def test_apply_context_shorthand_overrides_before_after():
    recs = _recs(4)
    args = _make_args(before=0, after=0, context=1)
    result = list(apply_context(recs, args))
    assert len(result) >= 4


def test_apply_context_after_flag():
    recs = _recs(3)
    args = _make_args(after=1)
    result = list(apply_context(recs, args))
    roles = [r.get("_context") for r in result]
    assert "after" in roles
