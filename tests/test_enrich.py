"""Tests for logslice.enrich."""

from __future__ import annotations

import pytest

from logslice.enrich import (
    enrich_static,
    enrich_copy,
    enrich_extract,
    enrich_concat,
    apply_enrichments,
    parse_enrich_arg,
)


def _rec(**kw):
    return dict(kw)


# --- enrich_static ---

def test_enrich_static_adds_field():
    r = enrich_static(_rec(a=1), "env", "prod")
    assert r["env"] == "prod"


def test_enrich_static_does_not_overwrite():
    r = enrich_static(_rec(env="dev"), "env", "prod")
    assert r["env"] == "dev"


def test_enrich_static_does_not_mutate():
    original = _rec(a=1)
    enrich_static(original, "env", "prod")
    assert "env" not in original


# --- enrich_copy ---

def test_enrich_copy_copies_value():
    r = enrich_copy(_rec(service="api"), "service", "svc")
    assert r["svc"] == "api"


def test_enrich_copy_missing_src_noop():
    r = enrich_copy(_rec(a=1), "service", "svc")
    assert "svc" not in r


def test_enrich_copy_does_not_overwrite_dst():
    r = enrich_copy(_rec(service="api", svc="existing"), "service", "svc")
    assert r["svc"] == "existing"


# --- enrich_extract ---

def test_enrich_extract_captures_group():
    r = enrich_extract(_rec(msg="error 404 not found"), "msg", "code", r"(\d{3})")
    assert r["code"] == "404"


def test_enrich_extract_no_match_noop():
    r = enrich_extract(_rec(msg="hello world"), "msg", "code", r"(\d{3})")
    assert "code" not in r


def test_enrich_extract_missing_src_noop():
    r = enrich_extract(_rec(a=1), "msg", "code", r"(\d+)")
    assert "code" not in r


def test_enrich_extract_no_group_uses_full_match():
    r = enrich_extract(_rec(msg="status:ok"), "msg", "tag", r"status:\w+")
    assert r["tag"] == "status:ok"


# --- enrich_concat ---

def test_enrich_concat_joins_fields():
    r = enrich_concat(_rec(host="web1", pid="42"), "id", ["host", "pid"], sep="-")
    assert r["id"] == "web1-42"


def test_enrich_concat_skips_missing_fields():
    r = enrich_concat(_rec(host="web1"), "id", ["host", "pid"], sep="-")
    assert r["id"] == "web1"


def test_enrich_concat_all_missing_noop():
    r = enrich_concat(_rec(a=1), "id", ["host", "pid"])
    assert "id" not in r


# --- apply_enrichments ---

def test_apply_enrichments_chains_rules():
    records = [_rec(service="api", msg="error 503")]
    rules = [
        ("static", "env", "prod"),
        ("copy", "service", "svc"),
        ("extract", "msg", "code", r"(\d{3})"),
    ]
    result = list(apply_enrichments(records, rules))
    assert result[0]["env"] == "prod"
    assert result[0]["svc"] == "api"
    assert result[0]["code"] == "503"


def test_apply_enrichments_empty_rules_passthrough():
    records = [_rec(a=1), _rec(b=2)]
    result = list(apply_enrichments(records, []))
    assert result == records


# --- parse_enrich_arg ---

def test_parse_enrich_arg_static():
    rule = parse_enrich_arg("static:env:production")
    assert rule == ("static", "env", "production")


def test_parse_enrich_arg_extract_with_pattern():
    rule = parse_enrich_arg(r"extract:code:msg:(\d{3})")
    assert rule[0] == "extract"
    assert rule[3] == r"(\d{3})"


def test_parse_enrich_arg_too_few_parts_raises():
    with pytest.raises(ValueError):
        parse_enrich_arg("static:only_one")
