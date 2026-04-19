"""Tests for logslice.cli_column."""
import argparse
import pytest
from logslice.cli_column import add_column_args, apply_column_cli


def _make_args(**kwargs):
    args = argparse.Namespace(columns=None, exclude_columns=None, reorder=None)
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


@pytest.fixture
def recs():
    return [
        {"ts": "2024-01-01", "level": "info", "msg": "hello"},
        {"ts": "2024-01-02", "level": "error", "msg": "boom"},
    ]


def test_add_column_args_registers_columns():
    p = argparse.ArgumentParser()
    add_column_args(p)
    args = p.parse_args(["--columns", "ts", "msg"])
    assert args.columns == ["ts", "msg"]


def test_add_column_args_registers_exclude():
    p = argparse.ArgumentParser()
    add_column_args(p)
    args = p.parse_args(["--exclude-columns", "level"])
    assert args.exclude_columns == ["level"]


def test_add_column_args_registers_reorder():
    p = argparse.ArgumentParser()
    add_column_args(p)
    args = p.parse_args(["--reorder", "msg", "ts"])
    assert args.reorder == ["msg", "ts"]


def test_apply_column_cli_no_flags_returns_all(recs):
    args = _make_args()
    result = apply_column_cli(args, recs)
    assert result == recs


def test_apply_column_cli_select(recs):
    args = _make_args(columns=["ts", "msg"])
    result = apply_column_cli(args, recs)
    assert all(set(r.keys()) == {"ts", "msg"} for r in result)


def test_apply_column_cli_exclude(recs):
    args = _make_args(exclude_columns=["level"])
    result = apply_column_cli(args, recs)
    assert all("level" not in r for r in result)


def test_apply_column_cli_reorder(recs):
    args = _make_args(reorder=["msg"])
    result = apply_column_cli(args, recs)
    assert all(list(r.keys())[0] == "msg" for r in result)
