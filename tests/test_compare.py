"""Tests for logslice.compare."""

from __future__ import annotations

import pytest

from logslice.compare import (
    align_by_key,
    apply_compare,
    compare_field,
    compare_records,
)


# ---------------------------------------------------------------------------
# compare_field
# ---------------------------------------------------------------------------

def test_compare_field_equal_returns_none():
    left = {"status": "ok", "code": 200}
    right = {"status": "ok", "code": 200}
    assert compare_field(left, right, "status") is None


def test_compare_field_different_returns_tuple():
    left = {"status": "ok"}
    right = {"status": "error"}
    assert compare_field(left, right, "status") == ("ok", "error")


def test_compare_field_missing_on_right():
    left = {"code": 200}
    right = {}
    assert compare_field(left, right, "code") == (200, None)


def test_compare_field_missing_on_both_returns_none():
    left = {}
    right = {}
    assert compare_field(left, right, "code") is None


# ---------------------------------------------------------------------------
# compare_records
# ---------------------------------------------------------------------------

def test_compare_records_no_diffs():
    left = {"a": 1, "b": "x"}
    right = {"a": 1, "b": "x"}
    assert compare_records(left, right, ["a", "b"]) == {}


def test_compare_records_partial_diff():
    left = {"a": 1, "b": "x"}
    right = {"a": 2, "b": "x"}
    result = compare_records(left, right, ["a", "b"])
    assert result == {"a": (1, 2)}


def test_compare_records_all_diff():
    left = {"a": 1, "b": "x"}
    right = {"a": 2, "b": "y"}
    result = compare_records(left, right, ["a", "b"])
    assert set(result.keys()) == {"a", "b"}


# ---------------------------------------------------------------------------
# align_by_key
# ---------------------------------------------------------------------------

def test_align_by_key_matches_correctly():
    left = [{"id": "a", "v": 1}, {"id": "b", "v": 2}]
    right = [{"id": "a", "v": 9}, {"id": "c", "v": 3}]
    pairs = list(align_by_key(left, right, "id"))
    assert len(pairs) == 1
    l, r = pairs[0]
    assert l["id"] == "a"
    assert r["v"] == 9


def test_align_by_key_no_match_yields_nothing():
    left = [{"id": "x"}]
    right = [{"id": "y"}]
    assert list(align_by_key(left, right, "id")) == []


def test_align_by_key_missing_key_skipped():
    left = [{"id": "a"}, {"other": "b"}]
    right = [{"id": "a", "v": 1}]
    pairs = list(align_by_key(left, right, "id"))
    assert len(pairs) == 1


# ---------------------------------------------------------------------------
# apply_compare
# ---------------------------------------------------------------------------

def test_apply_compare_emits_only_differing():
    left = [{"id": "1", "score": 10}, {"id": "2", "score": 20}]
    right = [{"id": "1", "score": 10}, {"id": "2", "score": 99}]
    results = list(apply_compare(left, right, key="id", fields=["score"]))
    assert len(results) == 1
    assert results[0]["id"] == "2"


def test_apply_compare_tag_contains_diff_detail():
    left = [{"id": "1", "level": "info"}]
    right = [{"id": "1", "level": "error"}]
    results = list(apply_compare(left, right, key="id", fields=["level"]))
    diff = results[0]["_diff"]
    assert diff["level"] == {"left": "info", "right": "error"}


def test_apply_compare_custom_tag():
    left = [{"id": "1", "x": 1}]
    right = [{"id": "1", "x": 2}]
    results = list(apply_compare(left, right, key="id", fields=["x"], tag="changes"))
    assert "changes" in results[0]


def test_apply_compare_does_not_mutate_original():
    rec = {"id": "1", "v": 5}
    left = [rec]
    right = [{"id": "1", "v": 99}]
    list(apply_compare(left, right, key="id", fields=["v"]))
    assert "_diff" not in rec
