import pytest
from datetime import datetime, timezone
from logslice.time_filter import extract_timestamp, in_range
from logslice.field_filter import matches_pattern, apply_filters, parse_filter_arg


# --- time_filter tests ---

def test_extract_timestamp_json_ts():
    entry = {"ts": "2024-06-15T12:00:00Z", "msg": "ok"}
    dt = extract_timestamp(entry)
    assert dt == datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_extract_timestamp_missing_returns_none():
    assert extract_timestamp({"msg": "no time here"}) is None


def test_in_range_within():
    entry = {"ts": "2024-06-15T12:00:00Z"}
    start = datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)
    end = datetime(2024, 6, 15, 13, 0, tzinfo=timezone.utc)
    assert in_range(entry, start, end) is True


def test_in_range_before_start():
    entry = {"ts": "2024-06-15T10:00:00Z"}
    start = datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)
    assert in_range(entry, start, None) is False


def test_in_range_no_bounds():
    assert in_range({"msg": "anything"}, None, None) is True


# --- field_filter tests ---

def test_matches_pattern_true():
    assert matches_pattern({"level": "error"}, "level", "err") is True


def test_matches_pattern_false():
    assert matches_pattern({"level": "info"}, "level", "error") is False


def test_matches_pattern_missing_field():
    assert matches_pattern({}, "level", ".*") is False


def test_apply_filters_all_match():
    entry = {"level": "error", "service": "auth"}
    filters = [("level", "error"), ("service", "auth")]
    assert apply_filters(entry, filters) is True


def test_apply_filters_one_fails():
    entry = {"level": "info", "service": "auth"}
    filters = [("level", "error"), ("service", "auth")]
    assert apply_filters(entry, filters) is False


def test_parse_filter_arg_valid():
    assert parse_filter_arg("level=error") == ("level", "error")


def test_parse_filter_arg_invalid():
    assert parse_filter_arg("levelonly") is None
    assert parse_filter_arg("=pattern") is None
