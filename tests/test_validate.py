"""Tests for logslice.validate."""
import pytest
from logslice.validate import (
    validate_record,
    apply_validation,
    parse_rule_arg,
)


def _rec(**kw):
    return dict(kw)


# parse_rule_arg

def test_parse_rule_required():
    assert parse_rule_arg("level") == {"required": ["level"]}


def test_parse_rule_type():
    assert parse_rule_arg("status:int") == {"field": "status", "type": "int"}


def test_parse_rule_pattern():
    assert parse_rule_arg("msg~error") == {"field": "msg", "pattern": "error"}


# validate_record

def test_required_field_present():
    assert validate_record({"level": "info"}, [{"required": ["level"]}]) == []


def test_required_field_missing():
    errs = validate_record({}, [{"required": ["level"]}])
    assert any("level" in e for e in errs)


def test_type_check_passes():
    assert validate_record({"code": 200}, [{"field": "code", "type": "int"}]) == []


def test_type_check_fails():
    errs = validate_record({"code": "ok"}, [{"field": "code", "type": "int"}])
    assert errs


def test_type_check_missing_field_no_error():
    assert validate_record({}, [{"field": "code", "type": "int"}]) == []


def test_pattern_check_passes():
    assert validate_record({"msg": "error occurred"}, [{"field": "msg", "pattern": "error"}]) == []


def test_pattern_check_fails():
    errs = validate_record({"msg": "all good"}, [{"field": "msg", "pattern": "error"}])
    assert errs


def test_multiple_rules_accumulate_errors():
    rec = {"msg": "ok"}
    rules = [{"required": ["level"]}, {"field": "msg", "pattern": "error"}]
    errs = validate_record(rec, rules)
    assert len(errs) == 2


# apply_validation

def test_apply_validation_no_rules_returns_all():
    recs = [_rec(level="info"), _rec(level="error")]
    out, inv = apply_validation(recs, [])
    assert out == recs and inv == 0


def test_apply_validation_drop_invalid():
    recs = [_rec(level="info"), _rec()]
    rules = [{"required": ["level"]}]
    out, inv = apply_validation(recs, rules, drop_invalid=True)
    assert len(out) == 1 and inv == 1


def test_apply_validation_tag_field():
    recs = [_rec(), _rec(level="info")]
    rules = [{"required": ["level"]}]
    out, _ = apply_validation(recs, rules, tag_field="_errors")
    assert out[0]["_errors"]  # has errors
    assert out[1]["_errors"] == []


def test_apply_validation_count_invalid():
    recs = [_rec(), _rec(), _rec(level="info")]
    rules = [{"required": ["level"]}]
    _, inv = apply_validation(recs, rules)
    assert inv == 2
