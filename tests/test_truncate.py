"""Tests for logslice.truncate."""

import pytest

from logslice.truncate import (
    apply_truncate,
    parse_truncate_args,
    truncate_fields,
    truncate_value,
)


def test_truncate_value_short_string_unchanged():
    assert truncate_value("hello", 10) == "hello"


def test_truncate_value_exact_length_unchanged():
    assert truncate_value("hello", 5) == "hello"


def test_truncate_value_long_string_cut():
    result = truncate_value("hello world", 8)
    assert result == "hello..."
    assert len(result) == 8


def test_truncate_value_non_string_unchanged():
    assert truncate_value(42, 3) == 42
    assert truncate_value(3.14, 3) == 3.14
    assert truncate_value(None, 3) is None


def test_truncate_value_custom_marker():
    result = truncate_value("abcdefgh", 6, marker="--")
    assert result == "abcd--"


def test_truncate_value_max_len_smaller_than_marker():
    result = truncate_value("abcdef", 2, marker="...")
    assert result == "..."


def test_truncate_fields_specified_fields():
    rec = {"msg": "a" * 20, "level": "info", "code": "x" * 20}
    out = truncate_fields(rec, ["msg"], 10)
    assert len(out["msg"]) == 10
    assert out["level"] == "info"
    assert out["code"] == "x" * 20


def test_truncate_fields_all_fields_when_none():
    rec = {"a": "x" * 20, "b": "y" * 20}
    out = truncate_fields(rec, None, 5)
    assert out["a"] == "xx..."
    assert out["b"] == "yy..."


def test_truncate_fields_does_not_mutate_original():
    rec = {"msg": "a" * 20}
    truncate_fields(rec, None, 5)
    assert rec["msg"] == "a" * 20


def test_truncate_fields_missing_field_ok():
    rec = {"msg": "hello"}
    out = truncate_fields(rec, ["missing"], 3)
    assert out == rec


def test_truncate_fields_invalid_max_len_raises():
    with pytest.raises(ValueError):
        truncate_fields({"a": "hello"}, None, 0)


def test_apply_truncate_yields_all_records():
    recs = [{"msg": "a" * 20}, {"msg": "short"}]
    out = list(apply_truncate(recs, None, 10))
    assert len(out) == 2
    assert len(out[0]["msg"]) == 10
    assert out[1]["msg"] == "short"


def test_parse_truncate_args_none_returns_none():
    assert parse_truncate_args(None) is None
    assert parse_truncate_args("") is None


def test_parse_truncate_args_comma_separated():
    result = parse_truncate_args("msg, level, code")
    assert result == ["msg", "level", "code"]
