"""Tests for logslice.label."""

import pytest

from logslice.label import (
    apply_label,
    label_records,
    parse_label_arg,
    parse_label_args,
)


def _rec(**kw):
    return dict(kw)


# --- parse_label_arg ---

def test_parse_label_arg_valid():
    rule = parse_label_arg("tier:level:error:high")
    assert rule == ("tier", "level", "error", "high")


def test_parse_label_arg_invalid_raises():
    with pytest.raises(ValueError, match="label rule must be"):
        parse_label_arg("bad:format")


def test_parse_label_arg_pattern_with_colon():
    # only split on first 3 colons
    rule = parse_label_arg("tag:msg:foo:bar:baz")
    assert rule == ("tag", "msg", "foo", "bar:baz")


# --- apply_label ---

def test_apply_label_matches_first_rule():
    rules = [("tier", "level", "error", "high"), ("tier", "level", "warn", "medium")]
    rec = _rec(level="error", msg="boom")
    out = apply_label(rec, rules)
    assert out["tier"] == "high"


def test_apply_label_second_rule_when_first_no_match():
    rules = [("tier", "level", "error", "high"), ("tier", "level", "warn", "medium")]
    rec = _rec(level="warn")
    out = apply_label(rec, rules)
    assert out["tier"] == "medium"


def test_apply_label_no_match_no_default():
    rules = [("tier", "level", "error", "high")]
    rec = _rec(level="info")
    out = apply_label(rec, rules)
    assert "tier" not in out


def test_apply_label_no_match_with_default():
    rules = [("tier", "level", "error", "high")]
    rec = _rec(level="info")
    out = apply_label(rec, rules, default="low")
    assert out["tier"] == "low"


def test_apply_label_does_not_mutate_original():
    rules = [("tier", "level", "error", "high")]
    rec = _rec(level="error")
    apply_label(rec, rules)
    assert "tier" not in rec


def test_apply_label_missing_src_field_no_match():
    rules = [("tier", "level", "error", "high")]
    rec = _rec(msg="hello")
    out = apply_label(rec, rules, default="unknown")
    assert out["tier"] == "unknown"


def test_apply_label_regex_pattern():
    rules = [("flag", "msg", r"fail|error", "bad")]
    rec = _rec(msg="connection failure")
    out = apply_label(rec, rules)
    assert out["flag"] == "bad"


# --- label_records ---

def test_label_records_applies_to_all():
    rules = parse_label_args(["env:host:prod:production", "env:host:dev:development"])
    recs = [_rec(host="prod-1"), _rec(host="dev-2"), _rec(host="staging")]
    out = list(label_records(recs, rules, default="other"))
    assert out[0]["env"] == "production"
    assert out[1]["env"] == "development"
    assert out[2]["env"] == "other"
