"""CLI helpers for session management."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from logslice.session import (
    DEFAULT_SESSION_DIR,
    delete_session,
    list_sessions,
    load_session,
    save_session,
)


def add_session_args(parser: argparse.ArgumentParser) -> None:
    """Register session-related flags onto *parser*."""
    grp = parser.add_argument_group("session")
    grp.add_argument("--save-session", metavar="NAME", help="Save current options as a named session")
    grp.add_argument("--load-session", metavar="NAME", help="Load options from a saved session")
    grp.add_argument("--list-sessions", action="store_true", help="List saved sessions and exit")
    grp.add_argument("--delete-session", metavar="NAME", help="Delete a named session and exit")


def handle_session_commands(
    args: argparse.Namespace,
    session_dir: Path = DEFAULT_SESSION_DIR,
) -> bool:
    """Handle list/delete session commands. Returns True if the program should exit."""
    if args.list_sessions:
        names = list_sessions(session_dir)
        if names:
            print("\n".join(names))
        else:
            print("No sessions saved.")
        return True

    if args.delete_session:
        removed = delete_session(args.delete_session, session_dir)
        if removed:
            print(f"Deleted session '{args.delete_session}'.")
        else:
            print(f"Session '{args.delete_session}' not found.")
        return True

    return False


def maybe_load_session(args: argparse.Namespace, session_dir: Path = DEFAULT_SESSION_DIR) -> dict[str, Any]:
    """If --load-session is set, return the stored config dict, else {}."""
    if getattr(args, "load_session", None):
        return load_session(args.load_session, session_dir)
    return {}


def maybe_save_session(args: argparse.Namespace, config: dict[str, Any], session_dir: Path = DEFAULT_SESSION_DIR) -> None:
    """If --save-session is set, persist *config*."""
    if getattr(args, "save_session", None):
        path = save_session(args.save_session, config, session_dir)
        print(f"Session saved to {path}")
