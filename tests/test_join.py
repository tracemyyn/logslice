"""Tests for logslice.join."""
import pytest
from logslice.join import build_index, inner_join, left_join, apply_join


def _left():
    return [
        {"id": "1", "msg": "hello"},
        {"id": "2", "msg": "world"},
        {"id": "3", "msg": "orphan"},
    ]


def _right():
    return [
        {"id": "1", "level": "info"},
        {"id": "2", "level": "error"},
    ]


def test_build_index_groups_by_key():
    idx = build_index(_right(), "id")
    assert "1" in idx and "2" in idx
    assert idx["1"][0]["level"] == "info"


def test_build_index_skips_missing_key():
    recs = [{"x": "a"}, {"id": "1", "x": "b"}]
    idx = build_index(recs, "id")
    assert list(idx.keys()) == ["1"]


def test_inner_join_merges_matching():
    idx = build_index(_right(), "id")
    result = list(inner_join(_left(), idx, "id"))
    assert len(result) == 2
    assert result[0]["msg"] == "hello"
    assert result[0]["right_level"] == "info"


def test_inner_join_excludes_unmatched():
    idx = build_index(_right(), "id")
    result = list(inner_join(_left(), idx, "id"))
    ids = [r["id"] for r in result]
    assert "3" not in ids


def test_inner_join_custom_prefix():
    idx = build_index(_right(), "id")
    result = list(inner_join(_left(), idx, "id", prefix="r_"))
    assert "r_level" in result[0]
    assert "right_level" not in result[0]


def test_left_join_keeps_unmatched():
    idx = build_index(_right(), "id")
    result = list(left_join(_left(), idx, "id"))
    ids = [r["id"] for r in result]
    assert "3" in ids


def test_left_join_unmatched_has_no_right_fields():
    idx = build_index(_right(), "id")
    result = list(left_join(_left(), idx, "id"))
    orphan = next(r for r in result if r["id"] == "3")
    assert "right_level" not in orphan


def test_apply_join_inner():
    result = list(apply_join(_left(), _right(), key="id", how="inner"))
    assert len(result) == 2


def test_apply_join_left():
    result = list(apply_join(_left(), _right(), key="id", how="left"))
    assert len(result) == 3


def test_apply_join_key_not_in_right_returns_empty_for_inner():
    right = [{"other": "x"}]
    result = list(apply_join(_left(), right, key="id", how="inner"))
    assert result == []
