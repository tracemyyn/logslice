"""Tests for logslice.cli_sort."""

import argparse
import pytest
from logslice.cli_sort import add_sort_args, apply_sort


def _make_args(**kwargs):
    defaults = {"sort_fields": None, "sort_desc": False, "sort_numeric": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _recs():
    return [
        {"level": "info", "ts": "3"},
        {"level": "error", "ts": "1"},
        {"level": "warn", "ts": "2"},
    ]


def test_add_sort_args_registers_sort():
    p = argparse.ArgumentParser()
    add_sort_args(p)
    args = p.parse_args(["--sort", "ts"])
    assert args.sort_fields == ["ts"]


def test_add_sort_args_registers_desc():
    p = argparse.ArgumentParser()
    add_sort_args(p)
    args = p.parse_args(["--sort", "ts", "--sort-desc"])
    assert args.sort_desc is True


def test_add_sort_args_registers_numeric():
    p = argparse.ArgumentParser()
    add_sort_args(p)
    args = p.parse_args(["--sort", "ts", "--sort-numeric"])
    assert args.sort_numeric is True


def test_apply_sort_no_fields_returns_original():
    recs = _recs()
    result = apply_sort(recs, _make_args())
    assert result == recs


def test_apply_sort_sorts_ascending():
    result = apply_sort(_recs(), _make_args(sort_fields=["ts"]))
    assert [r["ts"] for r in result] == ["1", "2", "3"]


def test_apply_sort_sorts_descending():
    result = apply_sort(_recs(), _make_args(sort_fields=["ts"], sort_desc=True))
    assert [r["ts"] for r in result] == ["3", "2", "1"]


def test_apply_sort_numeric():
    recs = [{"n": "10"}, {"n": "9"}, {"n": "100"}]
    result = apply_sort(recs, _make_args(sort_fields=["n"], sort_numeric=True))
    assert [r["n"] for r in result] == ["9", "10", "100"]
