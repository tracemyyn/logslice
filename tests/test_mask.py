"""Tests for logslice.mask."""

import re
import pytest
from logslice.mask import mask_value, mask_field, mask_preset, apply_masks


def test_mask_value_replaces_matched_chars():
    pat = re.compile(r"\d(?=\d{4})")
    assert mask_value("1234567890123456", pat) == "************3456"


def test_mask_value_no_match_unchanged():
    pat = re.compile(r"X+")
    assert mask_value("hello", pat) == "hello"


def test_mask_value_custom_char():
    pat = re.compile(r"[^@]+(?=@)")
    assert mask_value("alice@example.com", pat, "#") == "#####@example.com"


def test_mask_field_returns_new_dict():
    rec = {"email": "bob@test.com", "level": "info"}
    pat = re.compile(r"[^@]+(?=@)")
    result = mask_field(rec, "email", pat)
    assert result["email"] == "***@test.com"
    assert rec["email"] == "bob@test.com"  # original unchanged


def test_mask_field_missing_field_ok():
    rec = {"level": "info"}
    pat = re.compile(r"\d+")
    result = mask_field(rec, "ip", pat)
    assert result == rec


def test_mask_preset_email():
    rec = {"user": "carol@example.com"}
    result = mask_preset(rec, "user", "email")
    assert result["user"].endswith("@example.com")
    assert "carol" not in result["user"]


def test_mask_preset_unknown_raises():
    with pytest.raises(ValueError, match="Unknown mask preset"):
        mask_preset({"f": "v"}, "f", "nonexistent")


def test_apply_masks_multiple_specs():
    records = [
        {"email": "dave@x.com", "card": "4111111111111111"},
    ]
    specs = [
        {"field": "email", "preset": "email"},
        {"field": "card", "preset": "card"},
    ]
    result = apply_masks(records, specs)
    assert "dave" not in result[0]["email"]
    assert result[0]["card"].endswith("1111")


def test_apply_masks_empty_specs_returns_copy():
    records = [{"a": "1"}]
    result = apply_masks(records, [])
    assert result == records


def test_apply_masks_regex_spec():
    records = [{"token": "Bearer abc123xyz"}]
    specs = [{"field": "token", "pattern": r"(?<=Bearer )\S+"}]
    result = apply_masks(records, specs)
    assert result[0]["token"] == "Bearer *********"
