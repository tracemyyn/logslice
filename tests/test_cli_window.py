"""Tests for logslice.cli_window."""
from __future__ import annotations

import argparse
from typing import List

import pytest

from logslice.cli_window import add_window_args, apply_window


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"window": None, "window_step": None, "window_field": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


RECS = [
    {"ts": "2024-01-01T00:00:10Z", "level": "info"},
    {"ts": "2024-01-01T00:00:50Z", "level": "error"},
    {"ts": "2024-01-01T00:01:20Z", "level": "info"},
]


def test_add_window_args_registers_window():
    p = argparse.ArgumentParser()
    add_window_args(p)
    args = p.parse_args(["--window", "60"])
    assert args.window == 60


def test_add_window_args_registers_step():
    p = argparse.ArgumentParser()
    add_window_args(p)
    args = p.parse_args(["--window", "90", "--window-step", "30"])
    assert args.window_step == 30


def test_add_window_args_registers_field():
    p = argparse.ArgumentParser()
    add_window_args(p)
    args = p.parse_args(["--window", "60", "--window-field", "level"])
    assert args.window_field == "level"


def test_apply_window_no_flag_passthrough():
    args = _make_args()
    result = list(apply_window(RECS, args))
    assert result == RECS


def test_apply_window_tumbling_returns_counts():
    args = _make_args(window=60)
    result = list(apply_window(RECS, args))
    assert all("count" in r for r in result)
    assert sum(r["count"] for r in result) == len(RECS)


def test_apply_window_with_field():
    args = _make_args(window=60, window_field="level")
    result = list(apply_window(RECS, args))
    assert all("value" in r for r in result)


def test_apply_window_sliding():
    args = _make_args(window=90, window_step=60)
    result = list(apply_window(RECS, args))
    assert len(result) >= 1
    assert "count" in result[0]
