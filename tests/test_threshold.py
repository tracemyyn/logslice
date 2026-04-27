"""Tests for logslice.threshold."""
from __future__ import annotations

import pytest

from logslice.threshold import (
    apply_thresholds,
    check_threshold,
    parse_threshold_arg,
)


# ---------------------------------------------------------------------------
# parse_threshold_arg
# ---------------------------------------------------------------------------

def test_parse_threshold_arg_valid_gt():
    field, op, val = parse_threshold_arg("latency:gt:200")
    assert field == "latency"
    assert op == "gt"
    assert val == 200.0


def test_parse_threshold_arg_float_threshold():
    _, _, val = parse_threshold_arg("ratio:lte:0.5")
    assert val == pytest.approx(0.5)


def test_parse_threshold_arg_negative_threshold():
    _, _, val = parse_threshold_arg("temp:lt:-10")
    assert val == -10.0


def test_parse_threshold_arg_wrong_parts_raises():
    with pytest.raises(ValueError, match="Invalid threshold"):
        parse_threshold_arg("latency:gt")


def test_parse_threshold_arg_unknown_op_raises():
    with pytest.raises(ValueError, match="Unknown operator"):
        parse_threshold_arg("latency:between:100")


# ---------------------------------------------------------------------------
# check_threshold
# ---------------------------------------------------------------------------

def test_check_threshold_gt_true():
    assert check_threshold({"ms": "300"}, "ms", "gt", 200.0) is True


def test_check_threshold_gt_false():
    assert check_threshold({"ms": "100"}, "ms", "gt", 200.0) is False


def test_check_threshold_missing_field_returns_none():
    assert check_threshold({}, "ms", "gt", 100.0) is None


def test_check_threshold_non_numeric_returns_none():
    assert check_threshold({"ms": "fast"}, "ms", "gt", 100.0) is None


def test_check_threshold_eq_integer():
    assert check_threshold({"code": 200}, "code", "eq", 200.0) is True


# ---------------------------------------------------------------------------
# apply_thresholds
# ---------------------------------------------------------------------------

def _recs():
    return [
        {"svc": "api", "ms": "500"},
        {"svc": "db", "ms": "50"},
        {"svc": "cache", "ms": "150"},
    ]


def test_apply_thresholds_tags_triggered():
    rules = [("ms", "gt", 200.0)]
    out = list(apply_thresholds(_recs(), rules))
    assert out[0]["_threshold"] == "ms:gt:200"
    assert "_threshold" not in out[1]
    assert "_threshold" not in out[2]


def test_apply_thresholds_only_triggered_filters():
    rules = [("ms", "gt", 200.0)]
    out = list(apply_thresholds(_recs(), rules, only_triggered=True))
    assert len(out) == 1
    assert out[0]["svc"] == "api"


def test_apply_thresholds_custom_tag_field():
    rules = [("ms", "lt", 100.0)]
    out = list(apply_thresholds(_recs(), rules, tag_field="alert"))
    tagged = [r for r in out if "alert" in r]
    assert len(tagged) == 1
    assert tagged[0]["svc"] == "db"


def test_apply_thresholds_multiple_rules_combined():
    rules = [("ms", "gt", 400.0), ("ms", "lt", 60.0)]
    out = list(apply_thresholds(_recs(), rules, only_triggered=True))
    assert len(out) == 2
    svcs = {r["svc"] for r in out}
    assert svcs == {"api", "db"}


def test_apply_thresholds_does_not_mutate_original():
    original = {"ms": "500"}
    rules = [("ms", "gt", 100.0)]
    list(apply_thresholds([original], rules))
    assert "_threshold" not in original
