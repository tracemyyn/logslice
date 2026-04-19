"""Field masking: partially obscure field values (e.g. credit cards, emails)."""

import re
from typing import Dict, Any, List, Optional

_PRESETS: Dict[str, re.Pattern] = {
    "email": re.compile(r"[^@]+(?=@)"),
    "card": re.compile(r"\d(?=\d{4})"),
    "ip": re.compile(r"\d+(?=\.\d+\.\d+$)"),
}


def mask_value(value: str, pattern: re.Pattern, char: str = "*") -> str:
    """Replace matched portion of *value* with *char* repeated to same length."""
    def _replace(m: re.Match) -> str:
        return char * len(m.group())
    return pattern.sub(_replace, value)


def mask_field(
    record: Dict[str, Any],
    field: str,
    pattern: re.Pattern,
    char: str = "*",
) -> Dict[str, Any]:
    """Return a copy of *record* with *field* masked."""
    if field not in record:
        return dict(record)
    result = dict(record)
    result[field] = mask_value(str(result[field]), pattern, char)
    return result


def mask_preset(
    record: Dict[str, Any],
    field: str,
    preset: str,
    char: str = "*",
) -> Dict[str, Any]:
    """Apply a named preset mask to *field* in *record*."""
    if preset not in _PRESETS:
        raise ValueError(f"Unknown mask preset '{preset}'. Choose from: {list(_PRESETS)}")
    return mask_field(record, field, _PRESETS[preset], char)


def apply_masks(
    records: List[Dict[str, Any]],
    specs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply a list of mask specs to every record.

    Each spec is a dict with keys:
      field   – field name
      preset  – (optional) preset name
      pattern – (optional) regex string
      char    – (optional) replacement char, default '*'
    """
    result = []
    compiled = []
    for spec in specs:
        char = spec.get("char", "*")
        if "preset" in spec:
            pat = _PRESETS[spec["preset"]]
        else:
            pat = re.compile(spec["pattern"])
        compiled.append((spec["field"], pat, char))

    for rec in records:
        r = dict(rec)
        for field, pat, char in compiled:
            r = mask_field(r, field, pat, char)
        result.append(r)
    return result
