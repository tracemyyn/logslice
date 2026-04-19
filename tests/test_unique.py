"""Tests for logslice.unique."""
import pytest
from logslice.unique import unique_by, unique_by_value, count_unique, apply_unique


def _recs():
    return [
        {"level": "info", "svc": "api"},
        {"level": "error", "svc": "api"},
        {"level": "info", "svc": "worker"},
        {"level": "info", "svc": "api"},   # duplicate of first
        {"level": "error", "svc": "db"},
    ]


def test_unique_by_single_field():
    result = list(unique_by(_recs(), ["level"]))
    assert len(result) == 2
    assert result[0]["level"] == "info"
    assert result[1]["level"] == "error"


def test_unique_by_two_fields():
    result = list(unique_by(_recs(), ["level", "svc"]))
    # (info,api), (error,api), (info,worker), (error,db) => 4 unique
    assert len(result) == 4


def test_unique_by_value_alias():
    result = list(unique_by_value(_recs(), "svc"))
    svcs = [r["svc"] for r in result]
    assert svcs == ["api", "worker", "db"]


def test_unique_preserves_first_occurrence():
    recs = [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"}]
    result = list(unique_by(recs, ["id"]))
    assert result[0]["v"] == "a"
    assert result[1]["v"] == "c"


def test_count_unique_basic():
    assert count_unique(_recs(), ["level"]) == 2


def test_count_unique_two_fields():
    assert count_unique(_recs(), ["level", "svc"]) == 4


def test_count_unique_empty():
    assert count_unique([], ["level"]) == 0


def test_apply_unique_no_fields_passthrough():
    recs = _recs()
    result = list(apply_unique(recs, None))
    assert len(result) == len(recs)


def test_apply_unique_empty_list_passthrough():
    recs = _recs()
    result = list(apply_unique(recs, []))
    assert len(result) == len(recs)


def test_apply_unique_with_fields():
    result = list(apply_unique(_recs(), ["level"]))
    assert len(result) == 2


def test_unique_missing_field_treated_as_none():
    recs = [{"a": 1}, {"a": 1}, {"b": 2}]
    result = list(unique_by(recs, ["a"]))
    # (1,) and (None,) are distinct
    assert len(result) == 2
