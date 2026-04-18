"""Output formatting for logslice results."""

import json
import sys
from typing import Any, Dict, IO, Optional


SUPPORTED_FORMATS = ("json", "logfmt", "pretty")


def format_json(record: Dict[str, Any]) -> str:
    """Serialize record as compact JSON."""
    return json.dumps(record, default=str)


def format_logfmt(record: Dict[str, Any]) -> str:
    """Serialize record as logfmt key=value pairs."""
    parts = []
    for key, value in record.items():
        str_val = str(value) if not isinstance(value, str) else value
        if " " in str_val or "=" in str_val or '"' in str_val:
            str_val = '"' + str_val.replace('"', '\\"') + '"'
        parts.append(f"{key}={str_val}")
    return " ".join(parts)


def format_pretty(record: Dict[str, Any]) -> str:
    """Serialize record as indented JSON for human readability."""
    return json.dumps(record, indent=2, default=str)


def format_record(record: Dict[str, Any], fmt: str = "json") -> str:
    """Format a single record according to the requested format.

    Args:
        record: Parsed log record dict.
        fmt: One of 'json', 'logfmt', 'pretty'.

    Returns:
        Formatted string representation.

    Raises:
        ValueError: If fmt is not a supported format.
    """
    if fmt == "json":
        return format_json(record)
    elif fmt == "logfmt":
        return format_logfmt(record)
    elif fmt == "pretty":
        return format_pretty(record)
    else:
        raise ValueError(f"Unsupported output format: {fmt!r}. Choose from {SUPPORTED_FORMATS}.")


def write_record(
    record: Dict[str, Any],
    fmt: str = "json",
    dest: Optional[IO[str]] = None,
) -> None:
    """Format and write a record to *dest* (defaults to stdout)."""
    if dest is None:
        dest = sys.stdout
    dest.write(format_record(record, fmt) + "\n")
