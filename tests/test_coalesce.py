"""Tests for logslice.coalesce."""

import pytest

from logslice.coalesce import (
    apply_coalesce,
    coalesce_field,
    coalesce_value,
    parse_coalesce_arg,
)


# ---------------------------------------------------------------------------
# coalesce_value
# ---------------------------------------------------------------------------

def test_coalesce_value_returns_first_present():
    rec = {"a": None, "b": "hello", "c": "world"}
    assert coalesce_value(rec, ["a", "b", "c"]) == "hello"


def test_coalesce_value_skips_empty_string():
    rec = {"a": "", "b": "ok"}
    assert coalesce_value(rec, ["a", "b"]) == "ok"


def test_coalesce_value_all_absent_returns_default():
    rec = {"x": None}
    assert coalesce_value(rec, ["x", "y"], default="fallback") == "fallback"


def test_coalesce_value_first_field_wins():
    rec = {"a": 1, "b": 2}
    assert coalesce_value(rec, ["a", "b"]) == 1


def test_coalesce_value_missing_key_skipped():
    rec = {"b": "found"}
    assert coalesce_value(rec, ["a", "b"]) == "found"


# ---------------------------------------------------------------------------
# coalesce_field
# ---------------------------------------------------------------------------

def test_coalesce_field_writes_target():
    rec = {"msg": None, "message": "hi"}
    result = coalesce_field(rec, ["msg", "message"], target="text")
    assert result["text"] == "hi"


def test_coalesce_field_does_not_mutate_original():
    rec = {"a": "val"}
    coalesce_field(rec, ["a"], target="out")
    assert "out" not in rec


def test_coalesce_field_drop_sources_removes_them():
    rec = {"a": "x", "b": "y"}
    result = coalesce_field(rec, ["a", "b"], target="out", drop_sources=True)
    assert "a" not in result
    assert "b" not in result
    assert result["out"] == "x"


def test_coalesce_field_target_kept_when_drop_sources():
    """If target of the source fields it should not be removed."""
    rec = {"a": None, "b": "keep"}
    result = coalesce_field(rec, ["a", "b"], target="b", drop_sources=True)
    assert result["b"] == "keep"


# ---------------------------------------------------------------------------
# apply_coalesce
# ---------------------------------------------------------------------------

def test_apply_coalesce_yields_all_records():
    records = [{"a": "1"}, {"b": "2"}, {"a": "3", "b": "4"}]
    results = list(apply_coalesce(records, ["a", "b"], target="out"))
    assert len(results) == 3
    assert results[0]["out"] == "1"
    assert results[1]["out"] == "2"
    assert results[2]["out"] == "3"


# ---------------------------------------------------------------------------
# parse_coalesce_arg
# ---------------------------------------------------------------------------

def test_parse_coalesce_arg_valid():
    sources, target = parse_coalesce_arg("msg,message->text")
    assert sources == ["msg", "message"]
    assert target == "text"


def test_parse_coalesce_arg_single_source():
    sources, target = parse_coalesce_arg("err->error")
    assert sources == ["err"]
    assert target == "error"


def test_parse_coalesce_arg_no_arrow_raises():
    with pytest.raises(ValueError, match="expected"):
        parse_coalesce_arg("a,b,c")


def test_parse_coalesce_arg_empty_target_raises():
    with pytest.raises(ValueError, match="target"):
        parse_coalesce_arg("a,b->")


def test_parse_coalesce_arg_empty_sources_raises():
    with pytest.raises(ValueError, match="source"):
        parse_coalesce_arg("->target")
