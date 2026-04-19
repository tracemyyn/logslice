"""Tests for logslice.sort."""

import pytest
from logslice.sort import sort_records, stable_sort_records


def _recs():
    return [
        {"level": "info", "latency": "30", "msg": "c"},
        {"level": "error", "latency": "5", "msg": "a"},
        {"level": "warn", "latency": "100", "msg": "b"},
    ]


def test_sort_by_single_field_ascending():
    result = sort_records(_recs(), fields=["msg"])
    assert [r["msg"] for r in result] == ["a", "b", "c"]


def test_sort_by_single_field_descending():
    result = sort_records(_recs(), fields=["msg"], reverse=True)
    assert [r["msg"] for r in result] == ["c", "b", "a"]


def test_sort_numeric_by_latency():
    result = sort_records(_recs(), fields=["latency"], numeric=True)
    assert [r["latency"] for r in result] == ["5", "30", "100"]


def test_sort_lexicographic_latency_differs_from_numeric():
    result = sort_records(_recs(), fields=["latency"], numeric=False)
    # lexicographic: "100" < "30" < "5"
    assert result[0]["latency"] == "100"


def test_sort_no_fields_returns_original_order():
    recs = _recs()
    result = sort_records(recs, fields=[])
    assert result == recs


def test_sort_by_multiple_fields():
    recs = [
        {"level": "info", "msg": "b"},
        {"level": "info", "msg": "a"},
        {"level": "error", "msg": "z"},
    ]
    result = sort_records(recs, fields=["level", "msg"])
    assert result[0] == {"level": "error", "msg": "z"}
    assert result[1]["msg"] == "a"
    assert result[2]["msg"] == "b"


def test_sort_empty_list():
    assert sort_records([], fields=["msg"]) == []


def test_stable_sort_missing_field_sorts_last():
    recs = [
        {"latency": "10"},
        {"msg": "no latency"},
        {"latency": "2"},
    ]
    result = stable_sort_records(recs, field="latency")
    assert result[-1] == {"msg": "no latency"}
    assert result[0]["latency"] == "2"


def test_stable_sort_descending():
    recs = [{"v": "1"}, {"v": "3"}, {"v": "2"}]
    result = stable_sort_records(recs, field="v", reverse=True)
    assert [r["v"] for r in result] == ["3", "2", "1"]
