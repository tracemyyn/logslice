"""Tests for logslice.cli_template."""
import argparse
import pytest
from logslice.cli_template import add_template_args, apply_template


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"template": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


RECORDS = [
    {"ts": "2024-01-01", "level": "info", "msg": "started"},
    {"ts": "2024-01-02", "level": "error", "msg": "failed"},
]


def test_add_template_args_registers_flag():
    parser = argparse.ArgumentParser()
    add_template_args(parser)
    args = parser.parse_args(["--template", "{ts} {msg}"])
    assert args.template == "{ts} {msg}"


def test_apply_template_none_returns_none():
    args = _make_args(template=None)
    assert apply_template(args, RECORDS) is None


def test_apply_template_renders_all_records():
    args = _make_args(template="{ts} [{level}] {msg}")
    lines = apply_template(args, RECORDS)
    assert lines is not None
    assert len(lines) == 2
    assert lines[0] == "2024-01-01 [info] started"
    assert lines[1] == "2024-01-02 [error] failed"


def test_apply_template_missing_field_empty():
    args = _make_args(template="{ts} {request_id}")
    lines = apply_template(args, RECORDS)
    assert lines[0] == "2024-01-01 "


def test_apply_template_empty_records():
    args = _make_args(template="{msg}")
    lines = apply_template(args, [])
    assert lines == []
