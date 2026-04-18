"""Tests for logslice.transform."""

import pytest

from logslice.transform import (
    add_field,
    apply_transforms,
    drop_fields,
    keep_fields,
    parse_rename_arg,
    rename_fields,
)

RECORD = {"ts": "2024-01-01T00:00:00Z", "level": "info", "msg": "hello", "host": "web-1"}


def test_rename_fields_basic():
    result = rename_fields(RECORD, {"msg": "message"})
    assert "message" in result
    assert "msg" not in result
    assert result["message"] == "hello"


def test_rename_fields_unknown_key_unchanged():
    result = rename_fields(RECORD, {"nonexistent": "x"})
    assert result == RECORD


def test_drop_fields_removes_keys():
    result = drop_fields(RECORD, ["host", "level"])
    assert "host" not in result
    assert "level" not in result
    assert "ts" in result


def test_drop_fields_missing_key_ok():
    result = drop_fields(RECORD, ["missing"])
    assert result == RECORD


def test_keep_fields_only_specified():
    result = keep_fields(RECORD, ["ts", "msg"])
    assert set(result.keys()) == {"ts", "msg"}


def test_keep_fields_empty_list():
    result = keep_fields(RECORD, [])
    assert result == {}


def test_add_field_new_key():
    result = add_field(RECORD, "env", "prod")
    assert result["env"] == "prod"
    assert "env" not in RECORD  # original unchanged


def test_apply_transforms_all_steps():
    result = apply_transforms(
        RECORD,
        rename={"msg": "message"},
        drop=["host"],
        keep=["ts", "message"],
    )
    assert set(result.keys()) == {"ts", "message"}


def test_apply_transforms_no_ops():
    result = apply_transforms(RECORD)
    assert result == RECORD


def test_parse_rename_arg_single():
    assert parse_rename_arg("msg=message") == {"msg": "message"}


def test_parse_rename_arg_multiple():
    mapping = parse_rename_arg("msg=message,ts=timestamp")
    assert mapping == {"msg": "message", "ts": "timestamp"}


def test_parse_rename_arg_invalid_raises():
    with pytest.raises(ValueError, match="Invalid rename pair"):
        parse_rename_arg("badvalue")
