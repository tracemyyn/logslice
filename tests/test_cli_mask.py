"""Tests for logslice.cli_mask."""

import argparse
import pytest
from logslice.cli_mask import add_mask_args, apply_mask_args


def _make_args(**kwargs):
    ns = argparse.Namespace(mask=[], mask_preset=[], mask_char="*")
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_mask_args_registers_mask():
    p = argparse.ArgumentParser()
    add_mask_args(p)
    args = p.parse_args(["--mask", "email:[^@]+(?=@)"])
    assert args.mask == ["email:[^@]+(?=@)"]


def test_add_mask_args_registers_preset():
    p = argparse.ArgumentParser()
    add_mask_args(p)
    args = p.parse_args(["--mask-preset", "user:email"])
    assert args.mask_preset == ["user:email"]


def test_add_mask_args_registers_char():
    p = argparse.ArgumentParser()
    add_mask_args(p)
    args = p.parse_args(["--mask-char", "#"])
    assert args.mask_char == "#"


def test_apply_mask_args_no_flags_passthrough():
    records = [{"email": "a@b.com"}]
    args = _make_args()
    result = apply_mask_args(records, args)
    assert result == records


def test_apply_mask_args_regex_flag():
    records = [{"secret": "pass1234"}]
    args = _make_args(mask=["secret:\\d+"])
    result = apply_mask_args(records, args)
    assert result[0]["secret"] == "pass****"


def test_apply_mask_args_regex_flag_custom_char():
    """Masking with a custom mask character should replace matched digits."""
    records = [{"secret": "pass1234"}]
    args = _make_args(mask=["secret:\\d+"], mask_char="#")
    result = apply_mask_args(records, args)
    assert result[0]["secret"] == "pass####"


def test_apply_mask_args_preset_flag():
    records = [{"email": "test@domain.com"}]
    args = _make_args(mask_preset=["email:email"])
    result = apply_mask_args(records, args)
    assert "test" not in result[0]["email"]
    assert result[0]["email"].endswith("@domain.com")


def test_apply_mask_args_invalid_mask_raises():
    records = [{"f": "v"}]
    args = _make_args(mask=["nocolon"])
    with pytest.raises(ValueError):
        apply_mask_args(records, args)
