"""Tests for logslice.aggregator."""

import pytest
from logslice.aggregator import count_by_field, group_by_field, summarise

RECORDS = [
    {"level": "info",  "service": "api",   "user": "alice"},
    {"level": "error", "service": "api",   "user": "bob"},
    {"level": "info",  "service": "worker","user": "alice"},
    {"level": "info",  "service": "api",   "user": "carol"},
    {"level": "warn",  "service": "worker","user": "bob"},
]


def test_count_by_field_basic():
    result = count_by_field(RECORDS, "level")
    counts = dict(result)
    assert counts["info"] == 3
    assert counts["error"] == 1
    assert counts["warn"] == 1


def test_count_by_field_sorted_descending():
    result = count_by_field(RECORDS, "level")
    values = [v for _, v in result]
    assert values == sorted(values, reverse=True)


def test_count_by_field_missing_key():
    records = [{"level": "info"}, {"other": "x"}]
    counts = dict(count_by_field(records, "level"))
    assert counts["<missing>"] == 1
    assert counts["info"] == 1


def test_count_by_field_empty():
    """count_by_field on an empty list should return an empty list."""
    result = count_by_field([], "level")
    assert result == []


def test_count_by_field_single_record():
    """count_by_field with one record returns a single-element list."""
    result = count_by_field([{"level": "debug"}], "level")
    assert result == [("debug", 1)]


def test_group_by_field_keys():
    groups = group_by_field(RECORDS, "service")
    assert set(groups.keys()) == {"api", "worker"}


def test_group_by_field_lengths():
    groups = group_by_field(RECORDS, "service")
    assert len(groups["api"]) == 3
    assert len(groups["worker"]) == 2


def test_group_by_field_missing():
    records = [{"a": 1}, {"b": 2}]
    groups = group_by_field(records, "a")
    assert "<missing>" in groups
    assert len(groups["<missing>"]) == 1


def test_summarise_count():
    summary = summarise(RECORDS, "service")
    by_group = {s["group"]: s for s in summary}
    assert by_group["api"]["count"] == 3
    assert by_group["worker"]["count"] == 2


def test_summarise_unique_field():
    summary = summarise(RECORDS, "service", count_field="user")
    by_group = {s["group"]: s for s in summary}
    # api has alice, bob, carol
    assert by_group["api"]["unique"] == 3
    # worker has alice, bob
    assert by_group["worker"]["unique"] == 2


def test_summarise_no_count_field_has_no_unique_key():
    summary = summarise(RECORDS, "level")
    for entry in summary:
        assert "unique" not in entry


def test_summarise_empty():
    assert summarise([], "level") == []
