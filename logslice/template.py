"""Simple Go-style template rendering for log records."""
from __future__ import annotations
import re
from typing import Any

_FIELD_RE = re.compile(r"\{(\w+)(?::([^}]*))?\}")


def render_template(template: str, record: dict[str, Any]) -> str:
    """Render a template string against a log record.

    Fields are referenced as {field} or {field:default}.
    Unknown fields with no default are left as empty string.
    """
    def _replace(m: re.Match) -> str:
        key, default = m.group(1), m.group(2)
        value = record.get(key)
        if value is None:
            return default if default is not None else ""
        return str(value)

    return _FIELD_RE.sub(_replace, template)


def compile_template(template: str):
    """Return a callable that renders *template* against a record dict."""
    def _render(record: dict[str, Any]) -> str:
        return render_template(template, record)
    return _render


def list_template_fields(template: str) -> list[str]:
    """Return the field names referenced in *template* (preserving order, deduped)."""
    seen: list[str] = []
    for m in _FIELD_RE.finditer(template):
        key = m.group(1)
        if key not in seen:
            seen.append(key)
    return seen
