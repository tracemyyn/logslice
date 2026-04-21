"""Tests for logslice.score."""
import re
import pytest
from logslice.score import (
    build_rules,
    parse_score_arg,
    score_record,
    score_records,
)


# ---------------------------------------------------------------------------
# parse_score_arg
# ---------------------------------------------------------------------------

def test_parse_score_arg_two_parts():
    field, pattern, weight = parse_score_arg("level:error")
    assert field == "level"
    assert pattern == "error"
    assert weight == 1.0


def test_parse_score_arg_three_parts():
    field, pattern, weight = parse_score_arg("msg:timeout:2.5")
    assert field == "msg"
    assert pattern == "timeout"
    assert weight == 2.5


def test_parse_score_arg_pattern_with_colon():
    # third segment becomes the weight; pattern itself may not contain colons
    field, pattern, weight = parse_score_arg("url:https:3")
    assert field == "url"
    assert pattern == "https"
    assert weight == 3.0


def test_parse_score_arg_too_few_parts_raises():
    with pytest.raises(ValueError, match="Invalid score rule"):
        parse_score_arg("onlyone")


def test_parse_score_arg_zero_weight_raises():
    with pytest.raises(ValueError, match="Weight must be positive"):
        parse_score_arg("level:error:0")


def test_parse_score_arg_negative_weight_raises():
    with pytest.raises(ValueError, match="Weight must be positive"):
        parse_score_arg("level:error:-1")


# ---------------------------------------------------------------------------
# score_record
# ---------------------------------------------------------------------------

def _rules(*args):
    return build_rules(list(args))


def test_score_record_single_match():
    rec = {"level": "error", "msg": "disk full"}
    rules = _rules("level:error")
    assert score_record(rec, rules) == pytest.approx(1.0)


def test_score_record_no_match_returns_zero():
    rec = {"level": "info", "msg": "ok"}
    rules = _rules("level:error")
    assert score_record(rec, rules) == pytest.approx(0.0)


def test_score_record_multiple_rules_sum_weights():
    rec = {"level": "error", "msg": "timeout"}
    rules = _rules("level:error:2", "msg:timeout:3")
    assert score_record(rec, rules) == pytest.approx(5.0)


def test_score_record_missing_field_skipped():
    rec = {"msg": "timeout"}
    rules = _rules("level:error:2", "msg:timeout:3")
    assert score_record(rec, rules) == pytest.approx(3.0)


def test_score_record_case_insensitive():
    rec = {"level": "ERROR"}
    rules = _rules("level:error")
    assert score_record(rec, rules) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# score_records
# ---------------------------------------------------------------------------

def test_score_records_annotates_field():
    recs = [{"level": "error"}, {"level": "info"}]
    rules = _rules("level:error")
    out = list(score_records(recs, rules))
    assert out[0]["_score"] == pytest.approx(1.0)
    assert out[1]["_score"] == pytest.approx(0.0)


def test_score_records_threshold_filters():
    recs = [{"level": "error"}, {"level": "info"}]
    rules = _rules("level:error")
    out = list(score_records(recs, rules, threshold=1.0))
    assert len(out) == 1
    assert out[0]["level"] == "error"


def test_score_records_custom_score_field():
    recs = [{"level": "error"}]
    rules = _rules("level:error")
    out = list(score_records(recs, rules, score_field="relevance"))
    assert "relevance" in out[0]
    assert "_score" not in out[0]


def test_score_records_does_not_mutate_original():
    rec = {"level": "error"}
    rules = _rules("level:error")
    out = list(score_records([rec], rules))
    assert "_score" not in rec
