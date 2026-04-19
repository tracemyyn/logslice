"""Tests for logslice.grep."""

import argparse
import pytest
from logslice.grep import grep_record, grep_records, add_grep_args, apply_grep
import re


def _pat(pattern, ignore_case=False):
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


RECS = [
    {"level": "info", "msg": "user logged in", "user": "alice"},
    {"level": "error", "msg": "disk full", "user": "bob"},
    {"level": "warn", "msg": "User session expired", "user": "carol"},
]


def test_grep_record_match():
    assert grep_record(RECS[0], _pat("logged")) is True


def test_grep_record_no_match():
    assert grep_record(RECS[0], _pat("disk")) is False


def test_grep_record_invert():
    assert grep_record(RECS[0], _pat("disk"), invert=True) is True


def test_grep_record_field_restriction():
    # pattern exists in msg but we restrict to level
    assert grep_record(RECS[1], _pat("disk"), fields=["level"]) is False


def test_grep_record_missing_field_skipped():
    assert grep_record(RECS[0], _pat("x"), fields=["nonexistent"]) is False


def test_grep_records_filters_correctly():
    results = list(grep_records(RECS, "error"))
    assert len(results) == 1
    assert results[0]["level"] == "error"


def test_grep_records_ignore_case():
    results = list(grep_records(RECS, "user", ignore_case=True))
    # matches msg containing 'user'/'User' and user field values
    assert len(results) == 3


def test_grep_records_case_sensitive_default():
    results = list(grep_records(RECS, "User"))
    assert len(results) == 1
    assert results[0]["user"] == "carol"


def test_grep_records_invert():
    results = list(grep_records(RECS, "error", invert=True))
    assert all(r["level"] != "error" for r in results)
    assert len(results) == 2


def test_grep_records_field_restriction():
    results = list(grep_records(RECS, "alice", fields=["user"]))
    assert len(results) == 1


def test_add_grep_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_grep_args(parser)
    args = parser.parse_args(["--grep", "foo", "--grep-ignore-case", "--grep-invert"])
    assert args.grep == "foo"
    assert args.grep_ignore_case is True
    assert args.grep_invert is True


def _make_args(**kwargs):
    defaults = {"grep": None, "grep_fields": None, "grep_ignore_case": False, "grep_invert": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_apply_grep_no_pattern_returns_all():
    args = _make_args()
    assert list(apply_grep(RECS, args)) == RECS


def test_apply_grep_filters():
    args = _make_args(grep="disk")
    results = list(apply_grep(RECS, args))
    assert len(results) == 1
    assert results[0]["level"] == "error"
