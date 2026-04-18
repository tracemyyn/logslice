"""CLI helpers for the --tail / --follow flags."""

import argparse
import sys
from typing import Optional

from logslice.tail import tail_lines, follow_file
from logslice.output import write_record


def add_tail_args(parser: argparse.ArgumentParser) -> None:
    """Register tail-related arguments onto *parser*."""
    group = parser.add_argument_group("tail")
    group.add_argument(
        "--tail",
        metavar="N",
        type=int,
        default=None,
        help="Print the last N records from the file and exit.",
    )
    group.add_argument(
        "--follow",
        "-f",
        action="store_true",
        default=False,
        help="Follow the file and print new records as they arrive.",
    )
    group.add_argument(
        "--follow-poll",
        metavar="SECONDS",
        type=float,
        default=0.2,
        help="Polling interval in seconds when using --follow (default: 0.2).",
    )


def apply_tail(
    args: argparse.Namespace,
    fmt: str = "json",
    output=None,
) -> bool:
    """Handle --tail / --follow if requested.

    Returns True if a tail action was performed (caller should not continue
    with normal processing), False otherwise.
    """
    if output is None:
        output = sys.stdout

    file_path: Optional[str] = getattr(args, "file", None)
    if file_path is None:
        return False

    if getattr(args, "tail", None) is not None:
        records = tail_lines(file_path, n=args.tail)
        for record in records:
            write_record(record, fmt=fmt, out=output)
        return True

    if getattr(args, "follow", False):
        try:
            for record in follow_file(file_path, poll_interval=args.follow_poll):
                write_record(record, fmt=fmt, out=output)
        except KeyboardInterrupt:
            pass
        return True

    return False
