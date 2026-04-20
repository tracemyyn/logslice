"""Tests for logslice.cli_enrich."""

from __future__ import annotations

import argparse
from typing import Any, Dict

import pytest

from logslice.cli_enrich import add_enrich_args, apply_enrich_args

Record = Dict[str, Any]


def _make_args(**kw) -> argparse.Namespace:
    defaults = {"enrich": []}
    defaults.update(kw)
    return argparse.Namespace(**defaults)


def _recs(*dicts):
    return list(dicts)


def test_add_enrich_args_registers_flag():
    parser = argparse.ArgumentParser()
    add_enrich_args(parser)
    args = parser.parse_args(["--enrich", "static:env:prod"])
    assert args.enrich == ["static:env:prod"]


def test_add_enrich_args_multiple_rules():
    parser = argparse.ArgumentParser()
    add_enrich_args(parser)
    args = parser.parse_args(["--enrich", "static:env:prod", "--enrich", "copy:svc:service"])
    assert len(args.enrich) == 2


def test_apply_enrich_args_no_flags_passthrough():
    records = [{"a": 1}, {"b": 2}]
    args = _make_args(enrich=[])
    result = list(apply_enrich_args(records, args))
    assert result == records


def test_apply_enrich_args_static_rule():
    records = [{"a": 1}]
    args = _make_args(enrich=["static:env:production"])
    result = list(apply_enrich_args(records, args))
    assert result[0]["env"] == "production"


def test_apply_enrich_args_copy_rule():
    records = [{"service": "api"}]
    args = _make_args(enrich=["copy:svc:service"])
    result = list(apply_enrich_args(records, args))
    assert result[0]["svc"] == "api"


def test_apply_enrich_args_invalid_rule_raises():
    records = [{"a": 1}]
    args = _make_args(enrich=["badarg"])
    with pytest.raises(ValueError):
        list(apply_enrich_args(records, args))


def test_apply_enrich_args_none_enrich_passthrough():
    records = [{"x": 9}]
    args = argparse.Namespace(enrich=None)
    result = list(apply_enrich_args(records, args))
    assert result == records
