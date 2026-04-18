"""Tests for logslice.output formatting module."""

import io
import json
import pytest

from logslice.output import format_record, format_json, format_logfmt, format_pretty, write_record


SAMPLE = {"ts": "2024-01-15T10:00:00Z", "level": "info", "msg": "hello world", "code": 200}


def test_format_json_is_valid_json():
    result = format_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed["msg"] == "hello world"
    assert parsed["code"] == 200


def test_format_json_compact_no_newlines():
    result = format_json(SAMPLE)
    assert "\n" not in result


def test_format_logfmt_contains_keys():
    result = format_logfmt(SAMPLE)
    assert "level=info" in result
    assert "code=200" in result


def test_format_logfmt_quotes_values_with_spaces():
    record = {"msg": "hello world", "level": "warn"}
    result = format_logfmt(record)
    assert 'msg="hello world"' in result


def test_format_pretty_is_indented():
    result = format_pretty(SAMPLE)
    assert "\n" in result
    parsed = json.loads(result)
    assert parsed["level"] == "info"


def test_format_record_json():
    result = format_record(SAMPLE, fmt="json")
    assert json.loads(result)["ts"] == "2024-01-15T10:00:00Z"


def test_format_record_logfmt():
    result = format_record(SAMPLE, fmt="logfmt")
    assert "level=info" in result


def test_format_record_pretty():
    result = format_record(SAMPLE, fmt="pretty")
    assert "\n" in result


def test_format_record_unsupported_raises():
    with pytest.raises(ValueError, match="Unsupported output format"):
        format_record(SAMPLE, fmt="csv")


def test_write_record_writes_to_stream():
    buf = io.StringIO()
    write_record(SAMPLE, fmt="json", dest=buf)
    buf.seek(0)
    line = buf.readline()
    assert line.endswith("\n")
    parsed = json.loads(line.strip())
    assert parsed["level"] == "info"


def test_write_record_logfmt_to_stream():
    buf = io.StringIO()
    write_record({"key": "val"}, fmt="logfmt", dest=buf)
    buf.seek(0)
    assert buf.read().strip() == "key=val"
