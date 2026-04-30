"""Tests for logslice.excerpt."""
import pytest

from logslice.excerpt import (
    excerpt_records,
    excerpt_by_fraction,
    parse_excerpt_arg,
)


def _recs(n: int = 6) -> list[dict]:
    return [{"i": i, "msg": f"line {i}"} for i in range(n)]


# ---------------------------------------------------------------------------
# excerpt_records
# ---------------------------------------------------------------------------

def test_excerpt_default_returns_all():
    recs = _recs(4)
    assert list(excerpt_records(recs)) == recs


def test_excerpt_start_only():
    result = list(excerpt_records(_recs(6), start=3))
    assert [r["i"] for r in result] == [3, 4, 5]


def test_excerpt_end_only():
    result = list(excerpt_records(_recs(6), start=0, end=3))
    assert [r["i"] for r in result] == [0, 1, 2]


def test_excerpt_start_and_end():
    result = list(excerpt_records(_recs(6), start=2, end=5))
    assert [r["i"] for r in result] == [2, 3, 4]


def test_excerpt_end_beyond_length():
    result = list(excerpt_records(_recs(4), start=0, end=100))
    assert len(result) == 4


def test_excerpt_empty_range():
    result = list(excerpt_records(_recs(6), start=3, end=3))
    assert result == []


def test_excerpt_negative_start_raises():
    with pytest.raises(ValueError, match="start must be"):
        list(excerpt_records(_recs(4), start=-1))


def test_excerpt_end_less_than_start_raises():
    with pytest.raises(ValueError, match="end must be >= start"):
        list(excerpt_records(_recs(4), start=3, end=1))


def test_excerpt_empty_input():
    assert list(excerpt_records([], start=0, end=5)) == []


# ---------------------------------------------------------------------------
# excerpt_by_fraction
# ---------------------------------------------------------------------------

def test_fraction_full_range():
    recs = _recs(10)
    assert excerpt_by_fraction(recs, 0.0, 1.0) == recs


def test_fraction_first_half():
    result = excerpt_by_fraction(_recs(10), 0.0, 0.5)
    assert [r["i"] for r in result] == [0, 1, 2, 3, 4]


def test_fraction_second_half():
    result = excerpt_by_fraction(_recs(10), 0.5, 1.0)
    assert [r["i"] for r in result] == [5, 6, 7, 8, 9]


def test_fraction_invalid_from_raises():
    with pytest.raises(ValueError, match="from_pct"):
        excerpt_by_fraction(_recs(4), from_pct=-0.1)


def test_fraction_invalid_to_raises():
    with pytest.raises(ValueError, match="to_pct"):
        excerpt_by_fraction(_recs(4), to_pct=1.5)


def test_fraction_to_less_than_from_raises():
    with pytest.raises(ValueError, match="to_pct must be"):
        excerpt_by_fraction(_recs(4), from_pct=0.7, to_pct=0.3)


# ---------------------------------------------------------------------------
# parse_excerpt_arg
# ---------------------------------------------------------------------------

def test_parse_excerpt_both():
    assert parse_excerpt_arg("2:8") == (2, 8)


def test_parse_excerpt_open_end():
    assert parse_excerpt_arg("5:") == (5, None)


def test_parse_excerpt_zero_start():
    assert parse_excerpt_arg("0:10") == (0, 10)


def test_parse_excerpt_missing_colon_raises():
    with pytest.raises(ValueError, match="excerpt must be"):
        parse_excerpt_arg("42")


def test_parse_excerpt_invalid_start_raises():
    with pytest.raises(ValueError, match="invalid start"):
        parse_excerpt_arg("abc:10")


def test_parse_excerpt_invalid_end_raises():
    with pytest.raises(ValueError, match="invalid end"):
        parse_excerpt_arg("2:xyz")
