"""Tests for logslice.diff."""
import pytest
from logslice.diff import diff_records, only_changed


def _recs():
    return [
        {"level": "info", "msg": "start", "code": 0},
        {"level": "info", "msg": "processing", "code": 0},
        {"level": "error", "msg": "failed", "code": 1},
        {"level": "error", "msg": "failed", "code": 1},
    ]


def test_first_record_has_empty_changed():
    result = list(diff_records(iter(_recs())))
    assert result[0]["_changed"] == []


def test_unchanged_record_has_empty_changed():
    result = list(diff_records(iter(_recs())))
    assert result[3]["_changed"] == []


def test_changed_fields_detected():
    result = list(diff_records(iter(_recs())))
    assert set(result[2]["_changed"]) == {"level", "msg", "code"}


def test_partial_change_detected():
    result = list(diff_records(iter(_recs())))
    # record 1 -> 2: only msg changed
    assert result[1]["_changed"] == ["msg"]


def test_diff_fields_limits_tracking():
    result = list(diff_records(iter(_recs()), fields=["level"]))
    # record 1 -> 2: msg changed but we only track level
    assert result[1]["_changed"] == []
    assert "level" in result[2]["_changed"]


def test_original_keys_preserved():
    result = list(diff_records(iter(_recs())))
    for rec in result:
        assert "level" in rec and "msg" in rec and "code" in rec


def test_only_changed_suppresses_first():
    result = list(only_changed(iter(_recs())))
    # first record always suppressed; record index 1 has msg change
    assert all(r["_changed"] for r in result)


def test_only_changed_count():
    result = list(only_changed(iter(_recs())))
    # records 1 (msg) and 2 (level+msg+code) changed; record 3 identical to 2
    assert len(result) == 2


def test_empty_stream():
    assert list(diff_records(iter([]))) == []
    assert list(only_changed(iter([]))) == []
