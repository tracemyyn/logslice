"""Tests for logslice.redact."""

import pytest
from logslice.redact import redact_fields, redact_pattern, apply_redactions

_MASK = "***"


def test_redact_fields_masks_specified():
    rec = {"user": "alice", "msg": "hello", "token": "secret"}
    out = redact_fields(rec, ["token"])
    assert out["token"] == _MASK
    assert out["user"] == "alice"


def test_redact_fields_missing_field_ok():
    rec = {"msg": "hello"}
    out = redact_fields(rec, ["password"])
    assert out == {"msg": "hello"}


def test_redact_fields_does_not_mutate_original():
    rec = {"token": "secret"}
    redact_fields(rec, ["token"])
    assert rec["token"] == "secret"


def test_redact_fields_multiple():
    rec = {"a": "1", "b": "2", "c": "3"}
    out = redact_fields(rec, ["a", "c"])
    assert out["a"] == _MASK
    assert out["c"] == _MASK
    assert out["b"] == "2"


def test_redact_pattern_replaces_match():
    rec = {"msg": "token=abc123 here"}
    out = redact_pattern(rec, r"token=\w+")
    assert out["msg"] == "*** here"


def test_redact_pattern_no_match_unchanged():
    rec = {"msg": "nothing sensitive"}
    out = redact_pattern(rec, r"password=\S+")
    assert out["msg"] == "nothing sensitive"


def test_redact_pattern_non_string_value_unchanged():
    rec = {"count": 42, "msg": "hi"}
    out = redact_pattern(rec, r"\d+")
    assert out["count"] == 42


def test_redact_pattern_custom_replacement():
    rec = {"email": "user@example.com"}
    out = redact_pattern(rec, r"[^@]+@[^@]+", replacement="[REDACTED]")
    assert out["email"] == "[REDACTED]"


def test_apply_redactions_fields_and_pattern():
    records = [
        {"user": "bob", "msg": "key=xyz", "level": "info"},
        {"user": "alice", "msg": "normal", "level": "warn"},
    ]
    out = list(apply_redactions(records, fields=["user"], pattern=r"key=\w+"))
    assert out[0]["user"] == _MASK
    assert out[0]["msg"] == "***"
    assert out[1]["user"] == _MASK
    assert out[1]["msg"] == "normal"


def test_apply_redactions_no_ops_returns_unchanged():
    records = [{"a": "1"}]
    out = list(apply_redactions(records))
    assert out == [{"a": "1"}]
