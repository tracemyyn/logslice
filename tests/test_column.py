"""Tests for logslice.column."""
import pytest
from logslice.column import (
    select_columns,
    reorder_columns,
    exclude_columns,
    column_names,
    apply_column_args,
)


@pytest.fixture
def rec():
    return {"ts": "2024-01-01", "level": "info", "msg": "hello", "host": "web1"}


def test_select_columns_returns_subset(rec):
    result = select_columns(rec, ["ts", "msg"])
    assert list(result.keys()) == ["ts", "msg"]
    assert result["ts"] == rec["ts"]


def test_select_columns_missing_key_skipped(rec):
    result = select_columns(rec, ["ts", "nonexistent"])
    assert "nonexistent" not in result
    assert "ts" in result


def test_select_columns_preserves_order(rec):
    result = select_columns(rec, ["msg", "ts"])
    assert list(result.keys()) == ["msg", "ts"]


def test_exclude_columns_removes_keys(rec):
    result = exclude_columns(rec, ["level", "host"])
    assert "level" not in result
    assert "host" not in result
    assert "ts" in result


def test_exclude_columns_missing_key_ok(rec):
    result = exclude_columns(rec, ["nonexistent"])
    assert result == rec


def test_reorder_columns_puts_first_keys_first(rec):
    result = reorder_columns(rec, ["msg", "level"])
    keys = list(result.keys())
    assert keys[0] == "msg"
    assert keys[1] == "level"


def test_reorder_columns_includes_all_keys(rec):
    result = reorder_columns(rec, ["msg"])
    assert set(result.keys()) == set(rec.keys())


def test_reorder_columns_unknown_first_key_ignored(rec):
    result = reorder_columns(rec, ["ghost", "ts"])
    assert list(result.keys())[0] == "ts"


def test_column_names_unique_ordered():
    recs = [{"a": 1, "b": 2}, {"b": 3, "c": 4}, {"a": 5}]
    assert column_names(recs) == ["a", "b", "c"]


def test_column_names_empty():
    assert column_names([]) == []


def test_apply_column_args_select():
    recs = [{"a": 1, "b": 2, "c": 3}]
    result = apply_column_args(recs, select=["a", "c"])
    assert list(result[0].keys()) == ["a", "c"]


def test_apply_column_args_exclude():
    recs = [{"a": 1, "b": 2, "c": 3}]
    result = apply_column_args(recs, exclude=["b"])
    assert "b" not in result[0]


def test_apply_column_args_reorder():
    recs = [{"a": 1, "b": 2, "c": 3}]
    result = apply_column_args(recs, reorder=["c", "a"])
    keys = list(result[0].keys())
    assert keys[0] == "c"
    assert keys[1] == "a"


def test_apply_column_args_combined():
    recs = [{"ts": "t", "level": "info", "msg": "hi", "host": "h"}]
    result = apply_column_args(recs, select=["ts", "level", "msg"], reorder=["msg"])
    assert list(result[0].keys())[0] == "msg"
    assert "host" not in result[0]
