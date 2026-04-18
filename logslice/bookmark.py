"""Bookmark support: save and resume a byte-offset position in a log file."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

_BOOKMARK_DIR = Path.home() / ".logslice" / "bookmarks"


def _bookmark_path(log_path: str) -> Path:
    safe = log_path.replace("/", "_").replace("\\", "_").strip("_")
    return _BOOKMARK_DIR / f"{safe}.json"


def save_bookmark(log_path: str, offset: int, label: Optional[str] = None) -> Path:
    """Persist *offset* for *log_path*. Returns the bookmark file path."""
    _BOOKMARK_DIR.mkdir(parents=True, exist_ok=True)
    bm = {"log_path": log_path, "offset": offset}
    if label:
        bm["label"] = label
    dest = _bookmark_path(log_path)
    dest.write_text(json.dumps(bm))
    return dest


def load_bookmark(log_path: str) -> dict:
    """Load bookmark for *log_path*. Raises FileNotFoundError if absent."""
    p = _bookmark_path(log_path)
    if not p.exists():
        raise FileNotFoundError(f"No bookmark for {log_path!r}")
    return json.loads(p.read_text())


def delete_bookmark(log_path: str) -> bool:
    """Remove bookmark. Returns True if it existed."""
    p = _bookmark_path(log_path)
    if p.exists():
        p.unlink()
        return True
    return False


def list_bookmarks() -> list[dict]:
    """Return all saved bookmarks sorted by log_path."""
    if not _BOOKMARK_DIR.exists():
        return []
    results = []
    for f in sorted(_BOOKMARK_DIR.glob("*.json")):
        try:
            results.append(json.loads(f.read_text()))
        except (json.JSONDecodeError, OSError):
            pass
    return results


def offset_lines(log_path: str, offset: int):
    """Open *log_path* and yield lines starting at *offset* bytes."""
    with open(log_path, "r", errors="replace") as fh:
        fh.seek(offset)
        yield from fh
