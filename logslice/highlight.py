"""Terminal highlighting utilities for logslice output."""

import re
from typing import Any, Dict, List, Optional

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"

COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "n    "cyan": "\    "white": "\033EVEL_COLORS = {
    "error": "red",
": "yellow",
 "green",
    "debug": "cyan",
    "trace": "magenta",
}


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Wrap text in ANSI color codes."""
    code = COLORS.get(color, "")
    if not code:
        return text
    prefix = ANSI_BOLD + code if bold else code
    return f"{prefix}{text}{ANSI_RESET}"


def highlight_level(record: Dict[str, Any]) -> Optional[str]:
    """Return a color name based on the log level field, if present."""
    for key in ("level", "severity", "lvl"):
        val = record.get(key)
        if val:
            return LEVEL_COLORS.get(str(val).lower())
    return None


def highlight_matches(text: str, pattern: str, color: str = "yellow") -> str:
    """Highlight all occurrences of pattern in text."""
    if not pattern:
        return text
    try:
        regex = re.compile(re.escape(pattern))
    except re.error:
        return text
    return regex.sub(lambda m: colorize(m.group(), color, bold=True), text)


def highlight_fields(record: Dict[str, Any], fields: List[str], color: str = "cyan") -> Dict[str, Any]:
    """Return a copy of the record with specified field values colorized."""
    result = dict(record)
    for field in fields:
        if field in result:
            result[field] = colorize(str(result[field]), color, bold=True)
    return result
