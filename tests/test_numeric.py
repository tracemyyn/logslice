"""Tests for logslice.numeric."""
import pytest

from logslice.numeric import (
    apply_numeric_filters,
    numeric_match,
    parse_numeric_arg,
    parse_numeric_args,
)


@pytest.fixture()
def rec():
    return {"latency": "120", "status": "200", "size": "4096"}


def test_parse_numeric_arg_valid():
    field, op, value = parse_numeric_arg("latency:gt:100")
    assert field == "latency"
    assert op == "gt"
    assert value == 100.0


def test_parse_numeric_arg_float_threshold():
    field, op, value = parse_numeric_arg("score:lte:0.95")
    assert value == pytest.approx(0.95)


def test_parse_numeric_arg_wrong_parts_raises():
    with pytest.raises(ValueError, match="Expected field:op:value"):
        parse_numeric_arg("latency:gt")


def test_parse_numeric_arg_unknown_op_raises():
    with pytest.raises(ValueError, match="Unknown op"):
        parse_numeric_arg("latency:between:100")


def test_parse_numeric_arg_non_numeric_value_raises():
    with pytest.raises(ValueError, match="Cannot parse"):
        parse_numeric_arg("latency:gt:fast")


def test_numeric_match_gt_true(rec):
    assert numeric_match(rec, "latency", "gt", 100) is True


def test_numeric_match_gt_false(rec):
    assert numeric_match(rec, "latency", "gt", 200) is False


def test_numeric_match_eq(rec):
    assert numeric_match(rec, "latency", "eq", 120) is True


def test_numeric_match_ne(rec):
    assert numeric_match(rec, "latency", "ne", 999) is True


def test_numeric_match_missing_field_returns_false(rec):
    assert numeric_match(rec, "missing", "gt", 0) is False


def test_numeric_match_non_numeric_value_returns_false():
    assert numeric_match({"x": "abc"}, "x", "gt", 0) is False


def test_apply_numeric_filters_all_pass():
    records = [{"n": "50"}, {"n": "150"}, {"n": "300"}]
    filters = [("n", "gt", 40), ("n", "lt", 200)]
    result = list(apply_numeric_filters(records, filters))
    assert len(result) == 2
    assert result[0]["n"] == "50"
    assert result[1]["n"] == "150"


def test_apply_numeric_filters_empty_filters_yields_all():
    records = [{"n": "1"}, {"n": "2"}]
    result = list(apply_numeric_filters(records, []))
    assert len(result) == 2


def test_parse_numeric_args_multiple():
    parsed = parse_numeric_args(["latency:gte:100", "status:eq:200"])
    assert parsed == [("latency", "gte", 100.0), ("status", "eq", 200.0)]
