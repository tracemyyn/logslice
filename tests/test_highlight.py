"""Tests for logslice.highlight."""

import pytest
from logslice.highlight import (
    colorize,
    highlight_level,
    highlight_matches,
    highlight_fields,
    ANSI_RESET,
    COLORS,
)


def test_colorize_wraps_with_codes():
    result = colorize("hello", "red")
    assert COLORS["red"] in result
    assert ANSI_RESET in result
    assert "hello" in result


def test_colorize_unknown_color_returns_plain():
    result = colorize("hello", "ultraviolet")
    assert result == "hello"


def test_colorize_bold_includes_bold_code():
    result = colorize("hi", "green", bold=True)
    assert "\033[1m" in result


def test_highlight_level_error():
    record = {"level": "error", "msg": "boom"}
    assert highlight_level(record) == "red"


def test_highlight_level_warn():
    record = {"level": "warn"}
    assert highlight_level(record) == "yellow"


def test_highlight_level_info():
    record = {"severity": "INFO"}
    assert highlight_level(record) == "green"


def test_highlight_level_missing_returns_none():
    record = {"msg": "no level here"}
    assert highlight_level(record) is None


def test_highlight_level_unknown_value_returns_none():
    record = {"level": "verbose"}
    assert highlight_level(record) is None


def test_highlight_matches_wraps_occurrences():
    result = highlight_matches("foo bar foo", "foo")
    assert result.count(ANSI_RESET) == 2


def test_highlight_matches_no_pattern_returns_original():
    text = "unchanged text"
    assert highlight_matches(text, "") == text


def test_highlight_matches_no_match_returns_original():
    text = "hello world"
    result = highlight_matches(text, "zzz")
    assert result == text


def test_highlight_fields_colorizes_field():
    record = {"level": "info", "msg": "ok"}
    result = highlight_fields(record, ["level"])
    assert ANSI_RESET in result["level"]
    assert result["msg"] == "ok"


def test_highlight_fields_missing_field_ignored():
    record = {"msg": "hi"}
    result = highlight_fields(record, ["nonexistent"])
    assert result == record


def test_highlight_fields_does_not_mutate_original():
    record = {"level": "debug"}
    highlight_fields(record, ["level"])
    assert ANSI_RESET not in record["level"]
