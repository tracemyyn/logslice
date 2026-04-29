"""CLI integration for the rename feature."""

from __future__ import annotations

import argparse
from typing import Iterable

from logslice.rename import apply_rename, parse_rename_args


def add_rename_args(parser: argparse.ArgumentParser) -> None:
    """Register rename-related flags on *parser*."""
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Rename a field: --rename old_name=new_name (repeatable).",
    )
    parser.add_argument(
        "--rename-prefix",
        metavar="OLD:NEW",
        default=None,
        help="Replace a key prefix across all fields, e.g. --rename-prefix log_:event_.",
    )
    parser.add_argument(
        "--rename-regex",
        metavar="PATTERN:REPLACEMENT",
        default=None,
        help="Rename fields whose names match PATTERN, substituting REPLACEMENT.",
    )


def _parse_prefix_arg(value: str) -> tuple[str, str]:
    parts = value.split(":", 1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"--rename-prefix expects OLD:NEW, got {value!r}"
        )
    return parts[0], parts[1]


def apply_rename_args(args: argparse.Namespace, records: Iterable[dict]) -> Iterable[dict]:
    """Apply rename operations described by *args* to *records*.

    Returns *records* unchanged when no rename flags are set.
    """
    mapping = parse_rename_args(args.rename) if args.rename else None

    prefix_old = prefix_new = None
    if args.rename_prefix:
        prefix_old, prefix_new = _parse_prefix_arg(args.rename_prefix)

    regex = regex_repl = None
    if args.rename_regex:
        parts = args.rename_regex.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"--rename-regex expects PATTERN:REPLACEMENT, got {args.rename_regex!r}")
        regex, regex_repl = parts

    if not mapping and prefix_old is None and regex is None:
        return records

    return apply_rename(
        records,
        mapping=mapping,
        prefix_old=prefix_old,
        prefix_new=prefix_new,
        regex=regex,
        regex_replacement=regex_repl or "",
    )
