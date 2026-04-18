"""Tests for logslice.template."""
import pytest
from logslice.template import render_template, compile_template, list_template_fields


RECORD = {"ts": "2024-01-01T00:00:00Z", "level": "info", "msg": "hello world", "svc": "api"}


def test_render_known_fields():
    result = render_template("{ts} [{level}] {msg}", RECORD)
    assert result == "2024-01-01T00:00:00Z [info] hello world"


def test_render_unknown_field_empty():
    result = render_template("svc={svc} req={request_id}", RECORD)
    assert result == "svc=api req="


def test_render_default_used_when_missing():
    result = render_template("{request_id:n/a}", RECORD)
    assert result == "n/a"


def test_render_default_ignored_when_present():
    result = render_template("{level:debug}", RECORD)
    assert result == "info"


def test_render_literal_text_preserved():
    result = render_template("hello world", RECORD)
    assert result == "hello world"


def test_compile_template_callable():
    render = compile_template("{svc}: {msg}")
    assert render(RECORD) == "api: hello world"


def test_compile_template_reusable():
    render = compile_template("{level}")
    r1 = {"level": "error"}
    r2 = {"level": "warn"}
    assert render(r1) == "error"
    assert render(r2) == "warn"


def test_list_template_fields_order():
    fields = list_template_fields("{ts} {level} {msg}")
    assert fields == ["ts", "level", "msg"]


def test_list_template_fields_deduped():
    fields = list_template_fields("{ts} {ts} {level}")
    assert fields == ["ts", "level"]


def test_list_template_fields_empty():
    assert list_template_fields("no fields here") == []
