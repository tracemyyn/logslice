"""Tests for logslice.topn."""
import pytest

from logslice.topn import top_n, bottom_n, iter_top_n


@pytest.fixture()
def _recs():
    return [
        {"host": "a", "latency": 10},
        {"host": "b", "latency": 50},
        {"host": "c", "latency": 30},
        {"host": "d", "latency": 5},
        {"host": "e", "latency": 80},
    ]


def test_top_n_returns_n_records(_recs):
    result = top_n(_recs, "latency", 3)
    assert len(result) == 3


def test_top_n_highest_values_first(_recs):
    result = top_n(_recs, "latency", 3)
    assert [r["host"] for r in result] == ["e", "b", "c"]


def test_top_n_zero_returns_empty(_recs):
    assert top_n(_recs, "latency", 0) == []


def test_top_n_n_larger_than_input(_recs):
    result = top_n(_recs, "latency", 100)
    assert len(result) == len(_recs)


def test_top_n_skips_missing_field_by_default():
    recs = [{"x": 1}, {"latency": 5}, {"latency": 2}]
    result = top_n(recs, "latency", 2)
    assert len(result) == 2


def test_top_n_raises_on_missing_when_not_skipping():
    recs = [{"latency": 5}, {"host": "no-latency"}]
    with pytest.raises(ValueError, match="missing"):
        top_n(recs, "latency", 2, skip_missing=False)


def test_top_n_coerces_string_numbers():
    recs = [{"v": "3"}, {"v": "1"}, {"v": "2"}]
    result = top_n(recs, "v", 2)
    assert result[0]["v"] == "3"
    assert result[1]["v"] == "2"


def test_top_n_invalid_value_skipped_when_skip_missing():
    recs = [{"v": "abc"}, {"v": 10}, {"v": 5}]
    result = top_n(recs, "v", 2)
    assert len(result) == 2


def test_top_n_negative_n_raises(_recs):
    with pytest.raises(ValueError, match="non-negative"):
        top_n(_recs, "latency", -1)


def test_bottom_n_lowest_values_first(_recs):
    result = bottom_n(_recs, "latency", 3)
    assert [r["host"] for r in result] == ["d", "a", "c"]


def test_bottom_n_zero_returns_empty(_recs):
    assert bottom_n(_recs, "latency", 0) == []


def test_bottom_n_skips_missing_field_by_default():
    recs = [{"latency": 1}, {"other": 99}, {"latency": 2}]
    result = bottom_n(recs, "latency", 5)
    assert len(result) == 2


def test_bottom_n_negative_n_raises(_recs):
    with pytest.raises(ValueError, match="non-negative"):
        bottom_n(_recs, "latency", -1)


def test_iter_top_n_yields_in_order(_recs):
    result = list(iter_top_n(_recs, "latency", 2))
    assert result[0]["host"] == "e"
    assert result[1]["host"] == "b"


def test_iter_top_n_reverse_false_gives_bottom(_recs):
    result = list(iter_top_n(_recs, "latency", 2, reverse=False))
    assert result[0]["host"] == "d"
    assert result[1]["host"] == "a"
