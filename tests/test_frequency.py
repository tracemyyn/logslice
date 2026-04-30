"""Tests for logslice.frequency and logslice.cli_frequency."""

import argparse
from collections import Counter

import pytest

from logslice.frequency import count_values, frequency_table, iter_frequency
from logslice.cli_frequency import add_frequency_args, apply_frequency_args


def _recs():
    return [
        {"level": "error", "svc": "auth"},
        {"level": "warn",  "svc": "api"},
        {"level": "error", "svc": "api"},
        {"level": "info",  "svc": "auth"},
        {"level": "error"},
    ]


def test_count_values_basic():
    c = count_values(_recs(), "level")
    assert c["error"] == 3
    assert c["warn"] == 1
    assert c["info"] == 1


def test_count_values_missing_field_skipped():
    c = count_values(_recs(), "svc")
    # 5 records but one has no 'svc'
    assert sum(c.values()) == 4


def test_count_values_unknown_field_returns_empty():
    c = count_values(_recs(), "nonexistent")
    assert len(c) == 0


def test_frequency_table_descending_order():
    c = Counter({"error": 3, "warn": 1, "info": 1})
    rows = frequency_table(c)
    assert rows[0]["value"] == "error"
    assert rows[0]["count"] == 3


def test_frequency_table_pct_sums_to_100():
    c = Counter({"a": 1, "b": 3})
    rows = frequency_table(c)
    total = sum(r["pct"] for r in rows)
    assert abs(total - 100.0) < 0.01


def test_frequency_table_top_limits_rows():
    c = Counter({"x": 5, "y": 3, "z": 1})
    rows = frequency_table(c, top=2)
    assert len(rows) == 2


def test_frequency_table_ascending():
    c = Counter({"error": 3, "warn": 1})
    rows = frequency_table(c, ascending=True)
    assert rows[0]["value"] == "warn"


def test_iter_frequency_yields_dicts():
    rows = list(iter_frequency(_recs(), "level"))
    assert all("value" in r and "count" in r and "pct" in r for r in rows)


# --- CLI helpers ---

def _make_args(**kwargs):
    ns = argparse.Namespace(freq=None, freq_top=None, freq_asc=False)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_frequency_args_registers_freq():
    p = argparse.ArgumentParser()
    add_frequency_args(p)
    args = p.parse_args(["--freq", "level"])
    assert args.freq == "level"


def test_add_frequency_args_registers_top():
    p = argparse.ArgumentParser()
    add_frequency_args(p)
    args = p.parse_args(["--freq", "level", "--freq-top", "5"])
    assert args.freq_top == 5


def test_apply_frequency_args_no_flag_returns_none():
    args = _make_args()
    result = apply_frequency_args(args, iter(_recs()))
    assert result is None


def test_apply_frequency_args_with_flag_returns_iterator():
    args = _make_args(freq="level")
    result = apply_frequency_args(args, iter(_recs()))
    rows = list(result)
    assert len(rows) == 3  # error, warn, info
    assert rows[0]["value"] == "error"
