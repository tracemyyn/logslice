"""CLI helpers for the diff/change-detection feature."""
import argparse
from typing import Iterator, Dict, Any, Optional

from logslice.diff import diff_records, only_changed


def add_diff_args(parser: argparse.ArgumentParser) -> None:
    """Register diff-related flags on *parser*."""
    parser.add_argument(
        "--diff",
        action="store_true",
        default=False,
        help="Annotate each record with fields that changed from the previous record.",
    )
    parser.add_argument(
        "--diff-fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Limit change detection to these fields.",
    )
    parser.add_argument(
        "--diff-only",
        action="store_true",
        default=False,
        help="Output only records where at least one tracked field changed.",
    )


def apply_diff(
    records: Iterator[Dict[str, Any]],
    args: argparse.Namespace,
) -> Iterator[Dict[str, Any]]:
    """Apply diff logic to *records* based on parsed CLI *args*.

    Returns the (possibly transformed) record stream.
    """
    if not (getattr(args, "diff", False) or getattr(args, "diff_only", False)):
        return records

    fields: Optional[list] = getattr(args, "diff_fields", None)

    if getattr(args, "diff_only", False):
        return only_changed(records, fields=fields)

    return diff_records(records, fields=fields)
