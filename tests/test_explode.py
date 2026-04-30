"""Tests for logslice.explode."""

from __future__ import annotations

import pytest

from logslice.explode import explode_field, explode_records, parse_explode_arg


# ---------------------------------------------------------------------------
# explode_field
# ---------------------------------------------------------------------------

def test_explode_field_list_produces_one_record_per_element():
    rec = {"host": "web1", "tags": ["a", "b", "c"]}
    result = explode_field(rec, "tags")
    assert len(result) == 3
    assert [r["tags"] for r in result] == ["a", "b", "c"]


def test_explode_field_preserves_other_keys():
    rec = {"host": "web1", "tags": ["x", "y"]}
    result = explode_field(rec, "tags")
    assert all(r["host"] == "web1" for r in result)


def test_explode_field_non_list_passthrough():
    rec = {"host": "web1", "level": "info"}
    result = explode_field(rec, "tags")
    assert result == [rec]


def test_explode_field_non_list_drop_non_list():
    rec = {"host": "web1", "level": "info"}
    result = explode_field(rec, "tags", drop_non_list=True)
    assert result == []


def test_explode_field_empty_list_passthrough():
    rec = {"host": "web1", "tags": []}
    result = explode_field(rec, "tags")
    assert result == [rec]


def test_explode_field_empty_list_drop_non_list():
    rec = {"host": "web1", "tags": []}
    result = explode_field(rec, "tags", drop_non_list=True)
    assert result == []


def test_explode_field_does_not_mutate_original():
    original_tags = ["a", "b"]
    rec = {"tags": original_tags}
    results = explode_field(rec, "tags")
    results[0]["tags"] = "MUTATED"
    assert rec["tags"] is original_tags


def test_explode_field_single_element_list():
    rec = {"tags": ["only"]}
    result = explode_field(rec, "tags")
    assert len(result) == 1
    assert result[0]["tags"] == "only"


# ---------------------------------------------------------------------------
# explode_records
# ---------------------------------------------------------------------------

def test_explode_records_yields_all_expanded():
    records = [
        {"id": 1, "vals": [10, 20]},
        {"id": 2, "vals": [30]},
    ]
    result = list(explode_records(records, "vals"))
    assert len(result) == 3
    assert [r["vals"] for r in result] == [10, 20, 30]


def test_explode_records_empty_input():
    result = list(explode_records([], "tags"))
    assert result == []


def test_explode_records_mixed_with_drop():
    records = [
        {"id": 1, "tags": ["a", "b"]},
        {"id": 2},  # no tags field
    ]
    result = list(explode_records(records, "tags", drop_non_list=True))
    assert len(result) == 2
    assert all(r["id"] == 1 for r in result)


# ---------------------------------------------------------------------------
# parse_explode_arg
# ---------------------------------------------------------------------------

def test_parse_explode_arg_valid():
    assert parse_explode_arg("tags") == "tags"


def test_parse_explode_arg_none_returns_none():
    assert parse_explode_arg(None) is None


def test_parse_explode_arg_blank_raises():
    with pytest.raises(ValueError, match="blank"):
        parse_explode_arg("   ")
