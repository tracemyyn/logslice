import pytest
from logslice.flatten import flatten_record, unflatten_record, apply_flatten


def test_flatten_simple_nested():
    rec = {"a": {"b": 1, "c": 2}}
    assert flatten_record(rec) == {"a.b": 1, "a.c": 2}


def test_flatten_deep_nested():
    rec = {"x": {"y": {"z": 42}}}
    assert flatten_record(rec) == {"x.y.z": 42}


def test_flatten_flat_record_unchanged():
    rec = {"level": "info", "msg": "hello"}
    assert flatten_record(rec) == rec


def test_flatten_custom_separator():
    rec = {"a": {"b": 99}}
    assert flatten_record(rec, sep="_") == {"a_b": 99}


def test_flatten_max_depth_zero_returns_original():
    rec = {"a": {"b": 1}}
    result = flatten_record(rec, max_depth=0)
    assert result == {"a": {"b": 1}}


def test_flatten_max_depth_one():
    rec = {"a": {"b": {"c": 3}}}
    result = flatten_record(rec, max_depth=1)
    assert result == {"a.b": {"c": 3}}


def test_flatten_mixed_values():
    rec = {"ts": "2024-01-01", "meta": {"host": "srv1", "pid": 42}}
    result = flatten_record(rec)
    assert result == {"ts": "2024-01-01", "meta.host": "srv1", "meta.pid": 42}


def test_unflatten_simple():
    rec = {"a.b": 1, "a.c": 2}
    assert unflatten_record(rec) == {"a": {"b": 1, "c": 2}}


def test_unflatten_deep():
    rec = {"x.y.z": 42}
    assert unflatten_record(rec) == {"x": {"y": {"z": 42}}}


def test_unflatten_flat_record_unchanged():
    rec = {"level": "info", "msg": "hello"}
    assert unflatten_record(rec) == rec


def test_flatten_unflatten_roundtrip():
    original = {"a": {"b": 1}, "c": "val"}
    assert unflatten_record(flatten_record(original)) == original


def test_apply_flatten_list():
    records = [{"a": {"b": i}} for i in range(3)]
    result = apply_flatten(records)
    assert result == [{"a.b": i} for i in range(3)]


def test_apply_flatten_empty_list():
    assert apply_flatten([]) == []
