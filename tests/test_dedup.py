"""Tests for logslice.dedup."""
import pytest

from logslice.dedup import _record_key, count_duplicates, dedup_records


R1 = {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}
R2 = {"level": "error", "msg": "failed", "ts": "2024-01-01T00:01:00Z"}
R3 = {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}  # dup of R1
R4 = {"level": "info", "msg": "started", "ts": "2024-01-01T00:02:00Z"}  # same level+msg, diff ts


def test_record_key_same_content_equal():
    assert _record_key(R1) == _record_key(R3)


def test_record_key_different_content_differ():
    assert _record_key(R1) != _record_key(R2)


def test_record_key_subset_fields():
    key_a = _record_key(R1, fields=["level", "msg"])
    key_b = _record_key(R4, fields=["level", "msg"])
    assert key_a == key_b


def test_dedup_keep_first_removes_exact_duplicate():
    result = list(dedup_records([R1, R2, R3]))
    assert len(result) == 2
    assert R1 in result
    assert R2 in result


def test_dedup_keep_first_preserves_order():
    result = list(dedup_records([R2, R1, R3]))
    assert result[0] == R2
    assert result[1] == R1


def test_dedup_keep_last_returns_last_occurrence():
    r1_copy = dict(R1)
    r1_modified = dict(R1)
    r1_modified["extra"] = "yes"  # different record but same key fields
    # Use field-based dedup so both match on level+msg+ts
    result = list(dedup_records([r1_copy, R2, r1_modified], keep="last"))
    # r1_modified is the last with same full-record key — but they differ, so both kept
    # Use field subset to force collision
    result2 = list(dedup_records([R1, R2, R4], fields=["level", "msg"], keep="last"))
    assert len(result2) == 2
    assert R4 in result2  # last 'info/started'
    assert R2 in result2


def test_dedup_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        list(dedup_records([R1], keep="middle"))


def test_dedup_empty_input():
    assert list(dedup_records([])) == []


def test_count_duplicates_basic():
    assert count_duplicates([R1, R2, R3]) == 1


def test_count_duplicates_no_dups():
    assert count_duplicates([R1, R2]) == 0


def test_count_duplicates_field_subset():
    # R1 and R4 share level+msg
    assert count_duplicates([R1, R2, R4], fields=["level", "msg"]) == 1
