"""Tests for cli_dedup helpers."""
import argparse
import pytest

from logslice.cli_dedup import add_dedup_args, apply_dedup


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"dedup": False, "dedup_fields": None, "dedup_keep": "first"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


RECORDS = [
    {"level": "info", "msg": "hello"},
    {"level": "error", "msg": "boom"},
    {"level": "info", "msg": "hello"},  # duplicate
]


def test_add_dedup_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_dedup_args(parser)
    args = parser.parse_args(["--dedup", "--dedup-keep", "last"])
    assert args.dedup is True
    assert args.dedup_keep == "last"


def test_add_dedup_fields_flag():
    parser = argparse.ArgumentParser()
    add_dedup_args(parser)
    args = parser.parse_args(["--dedup-fields", "level", "msg"])
    assert args.dedup_fields == ["level", "msg"]


def test_apply_dedup_no_flags_returns_all():
    args = _make_args()
    result = list(apply_dedup(iter(RECORDS), args))
    assert len(result) == 3


def test_apply_dedup_flag_removes_duplicate():
    args = _make_args(dedup=True)
    result = list(apply_dedup(iter(RECORDS), args))
    assert len(result) == 2


def test_apply_dedup_fields_flag():
    args = _make_args(dedup_fields=["level", "msg"])
    result = list(apply_dedup(iter(RECORDS), args))
    assert len(result) == 2


def test_apply_dedup_keep_last():
    records = [
        {"id": 1, "key": "a"},
        {"id": 2, "key": "b"},
        {"id": 3, "key": "a"},  # dup key
    ]
    args = _make_args(dedup_fields=["key"], dedup_keep="last")
    result = list(apply_dedup(iter(records), args))
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert 3 in ids  # last 'a' kept
    assert 2 in ids
