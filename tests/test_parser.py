import pytest
from logslice.parser import parse_line


def test_parse_json_line():
    line = '{"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}'
    result = parse_line(line)
    assert result == {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}


def test_parse_logfmt_simple():
    line = 'level=info msg=started'
    result = parse_line(line)
    assert result == {"level": "info", "msg": "started"}


def test_parse_logfmt_quoted():
    line = 'level=error msg="something went wrong" code=500'
    result = parse_line(line)
    assert result == {"level": "error", "msg": "something went wrong", "code": "500"}


def test_empty_line_returns_none():
    assert parse_line("") is None
    assert parse_line("   ") is None


def test_invalid_json_falls_back_to_logfmt():
    line = '{bad json} level=warn'
    result = parse_line(line)
    # Falls back to logfmt; logfmt won't parse this cleanly, expect None
    assert result is None


def test_parse_logfmt_single_pair():
    line = "host=localhost"
    result = parse_line(line)
    assert result == {"host": "localhost"}


def test_parse_json_with_nested_fields():
    """JSON lines with nested objects should be parsed and returned as-is."""
    line = '{"level": "debug", "context": {"user": "alice", "id": 42}}'
    result = parse_line(line)
    assert result == {"level": "debug", "context": {"user": "alice", "id": 42}}


def test_parse_logfmt_empty_value():
    """Logfmt keys with empty quoted values should be handled gracefully."""
    line = 'level=info msg=""'
    result = parse_line(line)
    assert result is not None
    assert result.get("level") == "info"
    assert result.get("msg") == ""
