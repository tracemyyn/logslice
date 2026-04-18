"""Session: save and replay named filter configurations."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_SESSION_DIR = Path.home() / ".logslice" / "sessions"


def _session_path(name: str, session_dir: Path = DEFAULT_SESSION_DIR) -> Path:
    return session_dir / f"{name}.json"


def save_session(name: str, config: dict[str, Any], session_dir: Path = DEFAULT_SESSION_DIR) -> Path:
    """Persist *config* under *name*. Returns the file path."""
    session_dir.mkdir(parents=True, exist_ok=True)
    path = _session_path(name, session_dir)
    with path.open("w") as fh:
        json.dump(config, fh, indent=2)
    return path


def load_session(name: str, session_dir: Path = DEFAULT_SESSION_DIR) -> dict[str, Any]:
    """Load and return the config saved under *name*.

    Raises FileNotFoundError if the session does not exist.
    """
    path = _session_path(name, session_dir)
    if not path.exists():
        raise FileNotFoundError(f"No session named '{name}' found at {path}")
    with path.open() as fh:
        return json.load(fh)


def list_sessions(session_dir: Path = DEFAULT_SESSION_DIR) -> list[str]:
    """Return sorted list of saved session names."""
    if not session_dir.exists():
        return []
    return sorted(p.stem for p in session_dir.glob("*.json"))


def delete_session(name: str, session_dir: Path = DEFAULT_SESSION_DIR) -> bool:
    """Delete named session. Returns True if deleted, False if not found."""
    path = _session_path(name, session_dir)
    if path.exists():
        path.unlink()
        return True
    return False
