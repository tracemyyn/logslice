"""CLI helpers for the --dedup / --dedup-fields options."""
from __future__ import annotations

import argparse
from typing import Iterator

from logslice.dedup import dedup_records


def add_dedup_args(parser: argparse.ArgumentParser) -> None:
    """Attach dedup-related arguments to *parser*."""
    group = parser.add_argument_group("deduplication")
    group.add_argument(
        "--dedup",
        action="store_true",
        default=False,
        help="Remove duplicate log records (exact match on all fields).",
    )
    group.add_argument(
        "--dedup-fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Deduplicate using only these fields as the key.",
    )
    group.add_argument(
        "--dedup-keep",
        choices=("first", "last"),
        default="first",
        help="Which occurrence to keep when deduplicating (default: first).",
    )


def apply_dedup(
    records: Iterator[dict],
    args: argparse.Namespace,
) -> Iterator[dict]:
    """Wrap *records* with dedup logic when requested by *args*.

    Returns the original iterator unchanged when dedup is not requested.
    """
    if not (args.dedup or args.dedup_fields):
        return records

    fields = args.dedup_fields or None
    keep = getattr(args, "dedup_keep", "first")
    return dedup_records(records, fields=fields, keep=keep)
