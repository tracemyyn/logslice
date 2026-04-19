"""Tests for logslice.cast."""
import pytest

from logslice.cast import cast_field, apply_casts, parse_cast_args


def _rec(**kw):
    return dict(kw)


def test_cast_field_str_to_int():
    r = cast_field(_rec(status="200"), "status", "int")
    assert r["status"] == 200
    assert isinstance(r["status"], int)


def test_cast_field_str_to_float():
    r = cast_field(_rec(latency="1.23"), "latency", "float")
    assert abs(r["latency"] - 1.23) < 1e-9


def test_cast_field_to_str():
    r = cast_field(_rec(code=404), "code", "str")
    assert r["code"] == "404"


def test_cast_field_bool_true():
    for val in ("true", "1", "yes"):
        r = cast_field(_rec(flag=val), "flag", "bool")
        assert r["flag"] is True


def test_cast_field_bool_false():
    r = cast_field(_rec(flag="false"), "flag", "bool")
    assert r["flag"] is False


def test_cast_field_missing_key_unchanged():
    rec = _rec(a=1)
    r = cast_field(rec, "missing", "int")
    assert r == rec


def test_cast_field_invalid_value_left_unchanged():
    r = cast_field(_rec(val="abc"), "val", "int")
    assert r["val"] == "abc"


def test_cast_field_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown type"):
        cast_field(_rec(x="1"), "x", "uuid")


def test_cast_field_does_not_mutate_original():
    rec = _rec(n="5")
    cast_field(rec, "n", "int")
    assert rec["n"] == "5"


def test_apply_casts_multiple_specs():
    rec = _rec(status="200", latency="0.5", msg=42)
    r = apply_casts(rec, ["status:int", "latency:float", "msg:str"])
    assert r["status"] == 200
    assert isinstance(r["latency"], float)
    assert r["msg"] == "42"


def test_apply_casts_bad_spec_raises():
    with pytest.raises(ValueError, match="Cast spec must be"):
        apply_casts(_rec(x=1), ["no-colon"])


def test_apply_casts_empty_specs_returns_copy():
    rec = _rec(a=1)
    r = apply_casts(rec, [])
    assert r == rec
    assert r is not rec


def test_parse_cast_args_none_returns_empty():
    assert parse_cast_args(None) == []


def test_parse_cast_args_list_passthrough():
    assert parse_cast_args(["x:int", "y:float"]) == ["x:int", "y:float"]
